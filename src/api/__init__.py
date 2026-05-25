"""
API Module

FastAPI server para exponer el sistema de agentes como API REST y WebSocket.
"""

from .server import create_app, run_server

__all__ = ['create_app', 'run_server']
