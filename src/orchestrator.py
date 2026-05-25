"""
Sistema de Agentes Inteligentes Distribuidos

Orquestador principal que coordina múltiples agentes especializados
usando LangChain Deep Agents, MCP y MemPalace para memoria persistente.
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
import yaml
import asyncio
from pathlib import Path

from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, END

from .memory.mempalace_memory import MemPalaceMemory
from .tools.mcp_client import MCPClient
from .tools.visual_primitives import VisualPrimitives


class AgentConfig(BaseModel):
    """Configuración de un agente individual"""
    name: str
    model: str
    description: str
    tools: List[str] = Field(default_factory=list)
    max_iterations: int = 10
    temperature: float = 0.7
    context_window: int = 128000


class SystemState(BaseModel):
    """Estado global del sistema de agentes"""
    messages: List[Dict[str, Any]] = Field(default_factory=list)
    current_agent: Optional[str] = None
    subagent_results: Dict[str, Any] = Field(default_factory=dict)
    memory_context: Dict[str, Any] = Field(default_factory=dict)
    visual_data: Optional[Dict[str, Any]] = None


class AgentOrchestrator:
    """
    Orquestador principal del sistema de agentes
    
    Coordina agentes especializados usando:
    - LangChain Deep Agents para sub-agentes
    - MCP para integración con herramientas externas
    - MemPalace para memoria persistente
    - Visual Primitives para procesamiento de imágenes
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
        self.agents: Dict[str, Any] = {}
        self.mcp_clients: Dict[str, MCPClient] = {}
        self.memory = None
        self.visual_primitives = VisualPrimitives()
        
        self._initialize_agents()
        self._initialize_memory()
        self._initialize_mcp()
        
    def _load_config(self, config_path: str) -> dict:
        """Cargar configuración desde YAML"""
        path = Path(config_path)
        if not path.exists():
            raise FileNotFoundError(f"Config file not found: {config_path}")
        
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    
    def _initialize_agents(self):
        """Inicializar todos los agentes según configuración"""
        models_config = self.config.get('models', {})
        
        # Agente principal
        primary_config = models_config.get('primary', {})
        self.agents['primary'] = self._create_agent(
            name="primary_router",
            model=primary_config.get('name', 'glm4:9b-chat-q4_K_M'),
            description="Agente principal que enruta tareas a sub-agentes especializados",
            tools=['mcp', 'filesystem', 'shell'],
            temperature=0.7
        )
        
        # Sub-agentes especializados
        subagents_config = models_config.get('subagents', [])
        for idx, subagent in enumerate(subagents_config):
            agent_name = f"subagent_{idx}"
            self.agents[agent_name] = self._create_agent(
                name=subagent.get('name', agent_name),
                model=subagent.get('name', 'glm-edge:1.5b-chat'),
                description=subagent.get('description', 'Sub-agente especializado'),
                tools=subagent.get('tools', []),
                temperature=0.5
            )
        
        # Agente visual (si está configurado)
        vision_config = models_config.get('vision', {})
        if vision_config.get('enabled', True):
            self.agents['vision'] = self._create_agent(
                name="vision_specialist",
                model=vision_config.get('name', 'internvl2:8b'),
                description="Especialista en procesamiento visual, OCR y detección de objetos",
                tools=['opencv', 'yolo', 'tesseract', 'glm-ocr'],
                temperature=0.3
            )
    
    def _create_agent(self, name: str, model: str, description: str, 
                     tools: List[str], temperature: float = 0.7):
        """Crear un agente LangChain con herramientas"""
        llm = ChatOllama(
            model=model,
            temperature=temperature,
            num_ctx=self.config.get('models', {}).get('primary', {}).get('context_length', 128000)
        )
        
        # Cargar herramientas
        loaded_tools = self._load_tools(tools)
        
        # Crear prompt del sistema
        system_prompt = f"""Eres {name}. {description}

Tus capacidades incluyen:
{chr(10).join(['- ' + tool for tool in tools])}

Usa MemPalace para recordar interacciones previas y preferencias del usuario.
Para tareas visuales, usa las primitivas visuales antes de razonar.
Coordina con otros agentes cuando sea necesario mediante MCP.
"""
        
        return {
            'llm': llm,
            'tools': loaded_tools,
            'system_prompt': system_prompt,
            'name': name,
            'description': description
        }
    
    def _load_tools(self, tool_names: List[str]):
        """Cargar herramientas dinámicamente"""
        from .tools import load_tool
        
        tools = []
        for tool_name in tool_names:
            try:
                tool = load_tool(tool_name)
                tools.append(tool)
            except Exception as e:
                print(f"Warning: Could not load tool {tool_name}: {e}")
        
        return tools
    
    def _initialize_memory(self):
        """Inicializar MemPalace para memoria persistente"""
        memory_config = self.config.get('memory', {}).get('mempalace', {})
        
        if memory_config.get('enabled', True):
            self.memory = MemPalaceMemory(
                persist_path=memory_config.get('persist_path', './data/memory'),
                episodic_enabled=memory_config.get('episodic_memory', {}).get('enabled', True),
                semantic_enabled=memory_config.get('semantic_memory', {}).get('enabled', True),
                agent_id="orchestrator_main",
                max_entries=memory_config.get('episodic_memory', {}).get('max_entries', 5000),
                retention_days=memory_config.get('episodic_memory', {}).get('retention_days', 90)
            )
    
    def _initialize_mcp(self):
        """Inicializar clientes MCP para herramientas externas"""
        mcp_config = self.config.get('mcp', {})
        
        for server_name, server_config in mcp_config.get('servers', {}).items():
            try:
                client = MCPClient(
                    name=server_name,
                    command=server_config.get('command'),
                    args=server_config.get('args', []),
                    env=server_config.get('env', {})
                )
                self.mcp_clients[server_name] = client
            except Exception as e:
                print(f"Warning: Could not initialize MCP client {server_name}: {e}")
    
    async def process_message(self, message: str, user_id: str = "default",
                            image_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Procesar un mensaje del usuario
        
        Args:
            message: Mensaje de texto del usuario
            user_id: Identificador del usuario para contexto de memoria
            image_path: Ruta opcional a imagen para procesamiento visual
            
        Returns:
            Dict con respuesta y metadata
        """
        # Recuperar contexto de memoria
        memory_context = {}
        if self.memory:
            memory_context = await self.memory.retrieve_context(
                query=message,
                user_id=user_id,
                top_k=5
            )
        
        # Procesar imagen si existe
        visual_data = None
        if image_path:
            visual_data = await self.visual_primitives.process_image(image_path)
        
        # Determinar qué agente debe manejar la tarea
        router_result = await self._route_task(message, visual_data, memory_context)
        
        # Ejecutar el agente seleccionado
        result = await self._execute_agent(
            agent_name=router_result['selected_agent'],
            message=message,
            visual_data=visual_data,
            memory_context=memory_context
        )
        
        # Guardar en memoria
        if self.memory:
            await self.memory.store_interaction(
                user_id=user_id,
                query=message,
                response=result.get('response', ''),
                metadata={
                    'agent_used': router_result['selected_agent'],
                    'visual_processed': image_path is not None,
                    'timestamp': asyncio.get_event_loop().time()
                }
            )
        
        return result
    
    async def _route_task(self, message: str, visual_data: Optional[Dict],
                         memory_context: Dict) -> Dict[str, Any]:
        """Determinar qué agente debe manejar la tarea"""
        
        # Si hay datos visuales, usar agente visual
        if visual_data:
            return {'selected_agent': 'vision', 'reason': 'Visual input detected'}
        
        # Usar agente principal para enrutamiento
        primary = self.agents.get('primary')
        if not primary:
            return {'selected_agent': 'primary', 'reason': 'Default'}
        
        # Análisis simple de palabras clave para enrutamiento
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['imagen', 'foto', 'ver', 'detectar', 'ocr']):
            return {'selected_agent': 'vision', 'reason': 'Visual keywords detected'}
        elif any(word in message_lower for word in ['código', 'programar', 'python', 'script']):
            return {'selected_agent': 'subagent_0', 'reason': 'Coding task detected'}
        else:
            return {'selected_agent': 'primary', 'reason': 'General task'}
    
    async def _execute_agent(self, agent_name: str, message: str,
                           visual_data: Optional[Dict],
                           memory_context: Dict) -> Dict[str, Any]:
        """Ejecutar un agente específico"""
        agent = self.agents.get(agent_name)
        
        if not agent:
            return {'error': f'Agent {agent_name} not found'}
        
        # Construir mensajes
        messages = [
            SystemMessage(content=agent['system_prompt']),
            HumanMessage(content=message)
        ]
        
        # Agregar contexto visual si existe
        if visual_data:
            visual_summary = self.visual_primitives.create_summary(visual_data)
            messages.insert(1, HumanMessage(content=f"Contexto visual: {visual_summary}"))
        
        # Agregar contexto de memoria
        if memory_context:
            memory_str = "\n".join([
                f"- {entry}" for entry in memory_context.get('entries', [])
            ])
            messages.insert(1, HumanMessage(content=f"Memoria relevante:\n{memory_str}"))
        
        # Ejecutar LLM
        try:
            response = await agent['llm'].ainvoke(messages)
            
            return {
                'response': response.content,
                'agent_used': agent_name,
                'metadata': {
                    'model': agent['llm'].model,
                    'visual_data': visual_data is not None,
                    'memory_entries': len(memory_context.get('entries', []))
                }
            }
        except Exception as e:
            return {'error': str(e), 'agent_used': agent_name}
    
    def get_available_agents(self) -> List[Dict[str, str]]:
        """Obtener lista de agentes disponibles"""
        return [
            {
                'name': agent_data['name'],
                'description': agent_data['description'],
                'model': str(agent_data['llm'].model)
            }
            for agent_name, agent_data in self.agents.items()
        ]
    
    async def close(self):
        """Cerrar conexiones y limpiar recursos"""
        if self.memory:
            await self.memory.close()
        
        for mcp_client in self.mcp_clients.values():
            await mcp_client.close()


# Función de conveniencia para crear orquestador
def create_orchestrator(config_path: str = "config.yaml") -> AgentOrchestrator:
    """Crear una instancia del orquestador de agentes"""
    return AgentOrchestrator(config_path=config_path)
