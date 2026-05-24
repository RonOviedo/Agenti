"""
FastAPI Server

API REST y WebSocket para el sistema de agentes.
"""

from fastapi import FastAPI, WebSocket, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import asyncio
import json
from pathlib import Path
import uuid

from ..orchestrator import AgentOrchestrator


class ChatMessage(BaseModel):
    """Mensaje de chat para la API"""
    message: str
    user_id: str = "default"
    image_path: Optional[str] = None


class AgentResponse(BaseModel):
    """Respuesta del agente"""
    response: str
    agent_used: str
    metadata: Dict[str, Any]


def create_app(orchestrator: Optional[AgentOrchestrator] = None) -> FastAPI:
    """Crear aplicación FastAPI"""
    
    app = FastAPI(
        title="Sistema de Agentes Inteligentes",
        description="API para el sistema de agentes multi-modal con memoria persistente",
        version="1.0.0"
    )
    
    # CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Estado global
    app.state.orchestrator = orchestrator
    app.state.active_connections: Dict[str, WebSocket] = {}
    
    @app.on_event("startup")
    async def startup_event():
        """Inicializar orquestador al iniciar"""
        if not app.state.orchestrator:
            app.state.orchestrator = AgentOrchestrator()
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Limpiar recursos al cerrar"""
        if app.state.orchestrator:
            await app.state.orchestrator.close()
    
    @app.get("/")
    async def root():
        """Endpoint raíz"""
        return {
            "name": "Sistema de Agentes Inteligentes",
            "version": "1.0.0",
            "status": "running"
        }
    
    @app.get("/health")
    async def health_check():
        """Verificar salud del servicio"""
        return {"status": "healthy"}
    
    @app.get("/agents")
    async def list_agents():
        """Listar agentes disponibles"""
        if not app.state.orchestrator:
            raise HTTPException(status_code=503, detail="Orchestrator not initialized")
        
        agents = app.state.orchestrator.get_available_agents()
        return {"agents": agents}
    
    @app.post("/chat", response_model=AgentResponse)
    async def chat(message: ChatMessage):
        """
        Enviar mensaje al agente
        
        Args:
            message: Mensaje con texto, user_id y ruta opcional a imagen
            
        Returns:
            Respuesta del agente
        """
        if not app.state.orchestrator:
            raise HTTPException(status_code=503, detail="Orchestrator not initialized")
        
        try:
            result = await app.state.orchestrator.process_message(
                message=message.message,
                user_id=message.user_id,
                image_path=message.image_path
            )
            
            if "error" in result:
                raise HTTPException(status_code=500, detail=result["error"])
            
            return AgentResponse(
                response=result.get("response", ""),
                agent_used=result.get("agent_used", "unknown"),
                metadata=result.get("metadata", {})
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/chat/upload")
    async def chat_with_upload(
        message: str = Form(...),
        user_id: str = Form("default"),
        file: Optional[UploadFile] = File(None)
    ):
        """
        Enviar mensaje con archivo adjunto (imagen)
        
        Args:
            message: Mensaje de texto
            user_id: ID del usuario
            file: Archivo de imagen opcional
            
        Returns:
            Respuesta del agente
        """
        if not app.state.orchestrator:
            raise HTTPException(status_code=503, detail="Orchestrator not initialized")
        
        image_path = None
        
        # Guardar archivo temporalmente
        if file:
            upload_dir = Path("./uploads")
            upload_dir.mkdir(exist_ok=True)
            
            file_extension = file.filename.split(".")[-1] if file.filename else "jpg"
            temp_filename = f"{uuid.uuid4()}.{file_extension}"
            image_path = str(upload_dir / temp_filename)
            
            with open(image_path, "wb") as f:
                content = await file.read()
                f.write(content)
        
        try:
            result = await app.state.orchestrator.process_message(
                message=message,
                user_id=user_id,
                image_path=image_path
            )
            
            # Limpiar archivo temporal
            if image_path and Path(image_path).exists():
                Path(image_path).unlink()
            
            if "error" in result:
                raise HTTPException(status_code=500, detail=result["error"])
            
            return JSONResponse(content=result)
        except Exception as e:
            # Limpiar archivo en caso de error
            if image_path and Path(image_path).exists():
                Path(image_path).unlink()
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.websocket("/ws/{user_id}")
    async def websocket_endpoint(websocket: WebSocket, user_id: str):
        """
        Endpoint WebSocket para comunicación en tiempo real
        
        Permite streaming de respuestas y comunicación bidireccional
        """
        await websocket.accept()
        
        app.state.active_connections[user_id] = websocket
        
        try:
            while True:
                # Recibir mensaje
                data = await websocket.receive_text()
                
                try:
                    message_data = json.loads(data)
                    message = message_data.get("message", "")
                    image_path = message_data.get("image_path")
                    
                    if not app.state.orchestrator:
                        await websocket.send_json({"error": "Orchestrator not initialized"})
                        continue
                    
                    # Procesar mensaje
                    result = await app.state.orchestrator.process_message(
                        message=message,
                        user_id=user_id,
                        image_path=image_path
                    )
                    
                    # Enviar respuesta
                    await websocket.send_json(result)
                    
                except json.JSONDecodeError:
                    # Tratar como texto plano
                    if app.state.orchestrator:
                        result = await app.state.orchestrator.process_message(
                            message=data,
                            user_id=user_id
                        )
                        await websocket.send_json(result)
                    else:
                        await websocket.send_json({"error": "Orchestrator not initialized"})
                        
        except Exception as e:
            print(f"WebSocket error for user {user_id}: {e}")
        finally:
            # Remover conexión
            if user_id in app.state.active_connections:
                del app.state.active_connections[user_id]
    
    @app.get("/memory/{user_id}")
    async def get_user_memory(user_id: str, limit: int = 10):
        """Obtener memoria del usuario"""
        if not app.state.orchestrator or not app.state.orchestrator.memory:
            raise HTTPException(status_code=503, detail="Memory not initialized")
        
        try:
            context = await app.state.orchestrator.memory.retrieve_context(
                query="",
                user_id=user_id,
                top_k=limit
            )
            
            return context
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/memory/preference")
    async def set_preference(user_id: str = Form(...), key: str = Form(...), value: str = Form(...)):
        """Actualizar preferencia de usuario"""
        if not app.state.orchestrator or not app.state.orchestrator.memory:
            raise HTTPException(status_code=503, detail="Memory not initialized")
        
        try:
            # Intentar parsear valor como JSON
            try:
                parsed_value = json.loads(value)
            except json.JSONDecodeError:
                parsed_value = value
            
            await app.state.orchestrator.memory.update_preference(key, parsed_value)
            
            return {"status": "success", "key": key, "value": parsed_value}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    return app


async def run_server(host: str = "0.0.0.0", port: int = 8000, **kwargs):
    """Ejecutar servidor UVicorn"""
    import uvicorn
    
    config = uvicorn.Config(
        "src.api.server:app",
        host=host,
        port=port,
        **kwargs
    )
    server = uvicorn.Server(config)
    await server.serve()


# Crear app por defecto para uvicorn
app = create_app()
