#!/bin/bash

# Script de ejecución del sistema: API + Dashboard Visual
echo "🚀 Iniciando Sistema de Agentes Inteligentes..."

# Verificar entorno virtual
if [ ! -d ".venv" ]; then
    echo "❌ Error: No se encontró el entorno virtual. Ejecuta primero ./setup_env.sh"
    exit 1
fi

source .venv/bin/activate

# Crear directorios de logs si no existen
mkdir -p logs memory_store

echo "📡 Iniciando servidor API (FastAPI) en segundo plano..."
python src/api/server.py > logs/api.log 2>&1 &
API_PID=$!
echo "✅ API iniciada con PID: $API_PID"

# Esperar un momento para que la API arranque
sleep 3

echo "🖥️  Iniciando Dashboard Visual (Gradio)..."
echo "   - Monitor de tareas en tiempo real"
echo "   - Logs del sistema"
echo "   - Visualización de memoria y aprendizaje"
echo ""
python src/gui/dashboard.py

# Limpieza al finalizar (si se interrumpe con Ctrl+C)
trap "kill $API_PID 2>/dev/null; echo '🛑 Sistema detenido.'; exit" INT TERM EXIT
