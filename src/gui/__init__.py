"""
GUI Module

Interfaz gráfica web usando Gradio para interactuar con el sistema de agentes.
"""

from .gradio_app import create_gradio_app, run_gradio

__all__ = ['create_gradio_app', 'run_gradio']
