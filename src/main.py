#!/usr/bin/env python3
"""
Main Entry Point

Punto de entrada principal para ejecutar el sistema de agentes.
Soporta modo API, GUI (Gradio), o CLI.
"""

import argparse
import asyncio
import sys
from pathlib import Path


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description="Sistema de Agentes Inteligentes Distribuidos",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  %(prog)s api              # Iniciar servidor API REST
  %(prog)s gui              # Iniciar interfaz Gradio web
  %(prog)s cli              # Modo consola interactivo
  %(prog)s --port 9000      # API en puerto personalizado
        """
    )
    
    parser.add_argument(
        'mode',
        choices=['api', 'gui', 'cli'],
        default='api',
        nargs='?',
        help='Modo de ejecución: api, gui, o cli'
    )
    
    parser.add_argument(
        '--host',
        type=str,
        default='0.0.0.0',
        help='Host para el servidor (default: 0.0.0.0)'
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='Puerto para el servidor (default: 8000)'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Ruta al archivo de configuración (default: config.yaml)'
    )
    
    parser.add_argument(
        '--reload',
        action='store_true',
        help='Recargar automáticamente en desarrollo'
    )
    
    args = parser.parse_args()
    
    # Validar archivo de configuración
    config_path = Path(args.config)
    if not config_path.exists():
        print(f"⚠️  Advertencia: Archivo de configuración no encontrado: {config_path}")
        print("   Se usará configuración por defecto.")
    
    print(f"🤖 Sistema de Agentes Inteligentes v1.0.0")
    print(f"   Modo: {args.mode.upper()}")
    print(f"   Host: {args.host}")
    print(f"   Puerto: {args.port}")
    print()
    
    if args.mode == 'api':
        run_api(args.host, args.port, args.reload)
    elif args.mode == 'gui':
        run_gui(args.host, args.port)
    elif args.mode == 'cli':
        run_cli()


def run_api(host: str, port: int, reload: bool = False):
    """Ejecutar servidor API FastAPI"""
    import uvicorn
    
    print(f"🚀 Iniciando servidor API en http://{host}:{port}")
    print(f"   Docs: http://{host}:{port}/docs")
    print()
    
    uvicorn.run(
        "src.api.server:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


def run_gui(host: str, port: int):
    """Ejecutar interfaz Gradio"""
    from src.gui.gradio_app import create_gradio_app
    
    print(f"🎨 Iniciando interfaz Gradio en http://{host}:{port}")
    print()
    
    app = create_gradio_app()
    app.launch(
        server_name=host,
        server_port=port,
        share=False
    )


async def cli_loop():
    """Bucle CLI interactivo"""
    from src.orchestrator import create_orchestrator
    
    print("💬 Modo CLI interactivo")
    print("   Escribe 'salir' para terminar")
    print()
    
    orchestrator = create_orchestrator()
    user_id = "cli_user"
    
    try:
        while True:
            try:
                user_input = input("👤 Tú: ").strip()
            except EOFError:
                break
            
            if not user_input:
                continue
            
            if user_input.lower() in ['salir', 'exit', 'quit']:
                print("👋 ¡Hasta luego!")
                break
            
            # Procesar mensaje
            print("🤖 Pensando...", end="\r")
            
            result = await orchestrator.process_message(
                message=user_input,
                user_id=user_id
            )
            
            if "error" in result:
                print(f"❌ Error: {result['error']}")
            else:
                response = result.get("response", "")
                agent = result.get("agent_used", "unknown")
                
                print(f"🤖 Agente ({agent}): {response}")
                print()
    
    finally:
        await orchestrator.close()


def run_cli():
    """Ejecutar modo CLI"""
    try:
        asyncio.run(cli_loop())
    except KeyboardInterrupt:
        print("\n👋 Interrumpido por usuario")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
