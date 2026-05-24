"""
Gradio App

Interfaz web interactiva para el sistema de agentes usando Gradio.
"""

import gradio as gr
from typing import Dict, Any, Optional
from pathlib import Path
import asyncio

from ..orchestrator import AgentOrchestrator


class AgentChatbot:
    """Chatbot con interfaz Gradio"""
    
    def __init__(self, orchestrator: Optional[AgentOrchestrator] = None):
        self.orchestrator = orchestrator
        self.history: Dict[str, list] = {}  # Historial por usuario
    
    async def initialize(self):
        """Inicializar orquestador"""
        if not self.orchestrator:
            self.orchestrator = AgentOrchestrator()
    
    async def chat(
        self,
        message: str,
        history: list,
        user_id: str = "default",
        image: Optional[str] = None
    ):
        """
        Procesar mensaje y devolver respuesta
        
        Args:
            message: Mensaje del usuario
            history: Historial de conversación
            user_id: ID del usuario
            image: Ruta a imagen opcional
            
        Returns:
            Nuevo historial actualizado
        """
        if not self.orchestrator:
            await self.initialize()
        
        # Determinar ruta de imagen
        image_path = None
        if image and Path(image).exists():
            image_path = image
        
        # Procesar mensaje
        result = await self.orchestrator.process_message(
            message=message,
            user_id=user_id,
            image_path=image_path
        )
        
        # Obtener respuesta
        response = result.get("response", "Lo siento, ocurrió un error.")
        agent_used = result.get("agent_used", "unknown")
        metadata = result.get("metadata", {})
        
        # Agregar metadata a la respuesta
        if metadata:
            model = metadata.get("model", "unknown")
            visual = "👁️" if metadata.get("visual_data") else ""
            memory = f"💾 {metadata.get('memory_entries', 0)} recuerdos" if metadata.get("memory_entries", 0) > 0 else ""
            
            response += f"\n\n---\n*Agente: {agent_used} | Modelo: {model} {visual} {memory}*"
        
        # Actualizar historial
        history.append((message, response))
        
        return history
    
    def get_agents_list(self):
        """Obtener lista de agentes disponibles"""
        if not self.orchestrator:
            return "No initialized"
        
        agents = self.orchestrator.get_available_agents()
        return "\n".join([f"• {a['name']}: {a['description']}" for a in agents])


def create_gradio_app(orchestrator: Optional[AgentOrchestrator] = None) -> gr.Blocks:
    """Crear aplicación Gradio"""
    
    chatbot = AgentChatbot(orchestrator=orchestrator)
    
    with gr.Blocks(
        title="Sistema de Agentes Inteligentes",
        theme=gr.themes.Soft(),
        css="""
        .gradio-container {max-width: 1200px !important;}
        .agent-info {font-size: 0.9em; color: #666;}
        """
    ) as app:
        
        gr.Markdown("""
        # 🤖 Sistema de Agentes Inteligentes Distribuidos
        
        Interfaz multi-modal con memoria persistente. Sube imágenes, haz preguntas, 
        y el sistema usará el agente adecuado con herramientas especializadas.
        """)
        
        with gr.Row():
            with gr.Column(scale=3):
                chat_interface = gr.ChatInterface(
                    fn=lambda msg, hist, uid, img: asyncio.run(
                        chatbot.chat(msg, hist, uid, img)
                    ),
                    additional_inputs=[
                        gr.Textbox(
                            label="User ID",
                            value="default",
                            placeholder="Identificador para memoria"
                        ),
                        gr.Image(
                            label="Imagen (opcional)",
                            type="filepath"
                        )
                    ],
                    description="Chatea con agentes especializados. Usa 👁️ para visión, 💾 para memoria.",
                    examples=[
                        ["¿Qué puedes hacer?", None, "default"],
                        ["Analiza esta imagen y dime qué ves", "./examples/sample.jpg", "default"],
                        ["Recuerdas lo que hablamos ayer?", None, "user123"],
                        ["Escribe un script en Python para analizar datos", None, "coder"],
                    ]
                )
            
            with gr.Column(scale=1):
                gr.Markdown("### Estado del Sistema")
                
                status_box = gr.JSON(
                    label="Estado",
                    value={"status": "ready", "agents_loaded": True}
                )
                
                agents_info = gr.Textbox(
                    label="Agentes Disponibles",
                    lines=10,
                    interactive=False,
                    value=chatbot.get_agents_list()
                )
                
                refresh_btn = gr.Button("🔄 Actualizar Estado")
                
                def update_status():
                    if chatbot.orchestrator:
                        agents = chatbot.orchestrator.get_available_agents()
                        return {
                            "status": "running",
                            "agents_count": len(agents),
                            "memory_enabled": chatbot.orchestrator.memory is not None
                        }, chatbot.get_agents_list()
                    return {"status": "not_initialized"}, "No agents loaded"
                
                refresh_btn.click(
                    fn=update_status,
                    outputs=[status_box, agents_info]
                )
        
        gr.Markdown("""
        ---
        ### Características:
        - **👁️ Visual Primitives**: OCR, detección de objetos, análisis de escenas
        - **💾 MemPalace**: Memoria episódica y semántica persistente
        - **🔧 MCP Tools**: Integración con herramientas externas
        - **🤖 Multi-Agente**: Enrutamiento automático según tarea
        """)
    
    return app


async def run_gradio(
    host: str = "0.0.0.0",
    port: int = 7860,
    share: bool = False,
    **kwargs
):
    """Ejecutar aplicación Gradio"""
    app = create_gradio_app()
    app.launch(
        server_name=host,
        server_port=port,
        share=share,
        **kwargs
    )


# Crear app por defecto
app = create_gradio_app()
