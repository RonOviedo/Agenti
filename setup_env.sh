#!/bin/bash

# Script de configuración del entorno para el Sistema de Agentes Inteligentes
# Compatible con Linux/Mac y WSL en Windows

echo "🚀 Iniciando configuración del entorno..."

# 1. Crear entorno virtual si no existe
if [ ! -d ".venv" ]; then
    echo "📦 Creando entorno virtual (.venv)..."
    python3 -m venv .venv
else
    echo "✅ Entorno virtual ya existente."
fi

# 2. Activar entorno virtual
echo "⚡ Activando entorno virtual..."
source .venv/bin/activate

# 3. Actualizar pip
echo "🔄 Actualizando pip..."
pip install --upgrade pip

# 4. Instalar dependencias
echo "📥 Instalando dependencias desde requirements.txt..."
pip install -r requirements.txt

# 5. Verificar Ollama
echo "🦙 Verificando instalación de Ollama..."
if command -v ollama &> /dev/null; then
    echo "✅ Ollama detectado."
    echo "📋 Modelos disponibles actualmente:"
    ollama list
else
    echo "⚠️  ADVERTENCIA: Ollama no encontrado en el PATH."
    echo "   Por favor instala Ollama desde https://ollama.com y asegúrate de tener los modelos descargados."
fi

# 6. Crear archivo de configuración si no existe
if [ ! -f "config.yaml" ]; then
    echo "📝 Copiando configuración de ejemplo..."
    cp config.example.yaml config.yaml
    echo "✅ config.yaml creado. Por favor edítalo si necesitas cambiar puertos o rutas."
else
    echo "✅ config.yaml ya existe."
fi

# 7. Crear directorios necesarios
mkdir -p logs memory_store uploads downloads

echo ""
echo "=========================================="
echo "✅ Configuración completada exitosamente!"
echo "=========================================="
echo ""
echo "Siguientes pasos:"
echo "1. Revisa 'config.yaml' para ajustar los modelos si lo deseas."
echo "2. Ejecuta './run_system.sh' para iniciar la API y el Dashboard."
echo ""
echo "Para activar el entorno manualmente en el futuro:"
echo "   source .venv/bin/activate"
echo ""
