"""
Tool Loader

Cargador dinámico de herramientas para el sistema de agentes.
"""

from typing import Any, Optional


def load_tool(tool_name: str) -> Optional[Any]:
    """
    Cargar herramienta por nombre
    
    Args:
        tool_name: Nombre de la herramienta a cargar
        
    Returns:
        Instancia de la herramienta o None si no está disponible
    """
    
    if tool_name == 'opencv':
        try:
            from .opencv_tool import OpenCVTool
            return OpenCVTool()
        except Exception as e:
            print(f"Could not load OpenCV tool: {e}")
            return None
    
    elif tool_name == 'yolo':
        try:
            from .yolo_tool import YOLOTool
            return YOLOTool()
        except Exception as e:
            print(f"Could not load YOLO tool: {e}")
            return None
    
    elif tool_name == 'tesseract' or tool_name == 'ocr':
        try:
            from .tesseract_tool import TesseractOCR
            return TesseractOCR()
        except Exception as e:
            print(f"Could not load Tesseract tool: {e}")
            return None
    
    elif tool_name == 'glm-ocr':
        try:
            from .glm_ocr_tool import GLMOCR
            return GLMOCR()
        except Exception as e:
            print(f"Could not load GLM-OCR tool: {e}")
            return None
    
    elif tool_name == 'whisper':
        try:
            from .whisper_tool import WhisperTool
            return WhisperTool()
        except Exception as e:
            print(f"Could not load Whisper tool: {e}")
            return None
    
    elif tool_name == 'filesystem' or tool_name == 'file':
        try:
            from .filesystem_tool import FilesystemTool
            return FilesystemTool()
        except Exception as e:
            print(f"Could not load Filesystem tool: {e}")
            return None
    
    elif tool_name == 'shell':
        try:
            from .shell_tool import ShellTool
            return ShellTool()
        except Exception as e:
            print(f"Could not load Shell tool: {e}")
            return None
    
    elif tool_name == 'browser':
        try:
            from .browser_tool import BrowserTool
            return BrowserTool()
        except Exception as e:
            print(f"Could not load Browser tool: {e}")
            return None
    
    elif tool_name == 'git':
        try:
            from .git_tool import GitTool
            return GitTool()
        except Exception as e:
            print(f"Could not load Git tool: {e}")
            return None
    
    elif tool_name == 'mcp':
        # MCP se carga desde el orquestador
        return None
    
    else:
        print(f"Unknown tool: {tool_name}")
        return None


def get_available_tools() -> list:
    """Obtener lista de herramientas disponibles"""
    return [
        'opencv',
        'yolo',
        'tesseract',
        'glm-ocr',
        'whisper',
        'filesystem',
        'shell',
        'browser',
        'git',
        'mcp'
    ]
