"""
MCP Client

Cliente para Model Context Protocol (MCP) que permite integrar
herramientas y servidores externos con el sistema de agentes.
"""

import asyncio
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import subprocess
import websockets


@dataclass
class MCPTool:
    """Herramienta MCP disponible"""
    name: str
    description: str
    input_schema: Dict[str, Any]


class MCPClient:
    """
    Cliente para conectarse a servidores MCP
    
    Permite usar herramientas externas mediante el protocolo MCP,
    incluyendo filesystem, bases de datos, APIs, etc.
    """
    
    def __init__(
        self,
        name: str,
        command: Optional[str] = None,
        args: Optional[List[str]] = None,
        env: Optional[Dict[str, str]] = None,
        server_url: Optional[str] = None
    ):
        self.name = name
        self.command = command
        self.args = args or []
        self.env = env or {}
        self.server_url = server_url
        
        self.tools: List[MCPTool] = []
        self.process: Optional[subprocess.Popen] = None
        self.websocket: Optional[websockets.WebSocketClientProtocol] = None
        self.message_id = 0
        
    async def connect(self):
        """Conectar al servidor MCP"""
        if self.server_url:
            # Conexión vía WebSocket
            try:
                self.websocket = await websockets.connect(self.server_url)
                await self._initialize()
            except Exception as e:
                print(f"Error connecting to MCP server {self.server_url}: {e}")
        elif self.command:
            # Iniciar proceso local
            try:
                self.process = subprocess.Popen(
                    [self.command] + self.args,
                    env={**self.env},
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                await self._initialize()
            except Exception as e:
                print(f"Error starting MCP process {self.command}: {e}")
    
    async def _initialize(self):
        """Inicializar conexión y obtener herramientas disponibles"""
        # Enviar mensaje de inicialización
        init_message = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "sistema-agentes",
                    "version": "1.0.0"
                }
            }
        }
        
        await self._send_message(init_message)
        
        # Obtener lista de herramientas
        await self.list_tools()
    
    def _next_id(self) -> int:
        """Generar ID único para mensaje"""
        self.message_id += 1
        return self.message_id
    
    async def _send_message(self, message: dict):
        """Enviar mensaje al servidor MCP"""
        if self.websocket:
            await self.websocket.send(json.dumps(message))
        elif self.process and self.process.stdin:
            self.process.stdin.write((json.dumps(message) + "\n").encode())
            self.process.stdin.flush()
    
    async def _receive_message(self) -> Optional[dict]:
        """Recibir mensaje del servidor MCP"""
        if self.websocket:
            try:
                response = await self.websocket.recv()
                return json.loads(response)
            except:
                return None
        elif self.process and self.process.stdout:
            line = self.process.stdout.readline()
            if line:
                return json.loads(line.decode())
        return None
    
    async def list_tools(self) -> List[MCPTool]:
        """Obtener lista de herramientas disponibles"""
        message = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/list",
            "params": {}
        }
        
        await self._send_message(message)
        response = await self._receive_message()
        
        self.tools = []
        if response and "result" in response:
            for tool_data in response["result"].get("tools", []):
                tool = MCPTool(
                    name=tool_data.get("name", ""),
                    description=tool_data.get("description", ""),
                    input_schema=tool_data.get("inputSchema", {})
                )
                self.tools.append(tool)
        
        return self.tools
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Llamar a una herramienta MCP
        
        Args:
            tool_name: Nombre de la herramienta
            arguments: Argumentos para la herramienta
            
        Returns:
            Resultado de la ejecución
        """
        message = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        await self._send_message(message)
        response = await self._receive_message()
        
        if response and "result" in response:
            return response["result"]
        elif response and "error" in response:
            return {"error": response["error"]}
        else:
            return {"error": "No response from MCP server"}
    
    async def read_resource(self, uri: str) -> str:
        """Leer recurso desde el servidor MCP"""
        message = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "resources/read",
            "params": {
                "uri": uri
            }
        }
        
        await self._send_message(message)
        response = await self._receive_message()
        
        if response and "result" in response:
            return response["result"].get("contents", "")
        return ""
    
    async def close(self):
        """Cerrar conexión y limpiar recursos"""
        if self.websocket:
            await self.websocket.close()
        
        if self.process:
            self.process.terminate()
            self.process.wait(timeout=5)


# Función de conveniencia
async def create_mcp_client(
    name: str,
    **kwargs
) -> MCPClient:
    """Crear y conectar un cliente MCP"""
    client = MCPClient(name=name, **kwargs)
    await client.connect()
    return client
