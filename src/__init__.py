"""
Sistema de Agentes Inteligentes Distribuidos

Package principal del sistema de agentes.
"""

from .orchestrator import AgentOrchestrator, create_orchestrator

__version__ = "1.0.0"
__all__ = ['AgentOrchestrator', 'create_orchestrator']