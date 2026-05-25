# 🚀 CÓMO HACER FUNCIONAR ESTE SISTEMA - GUÍA PASO A PASO

Esta guía te llevará desde cero hasta tener el sistema completamente operativo.

---

## 📋 REQUISITOS PREVIOS

Antes de empezar, asegúrate de tener:

1. **Linux/Mac/WSL** (Windows Subsystem for Linux)
2. **Python 3.10+** instalado
3. **Ollama** instalado y corriendo
4. **GPU NVIDIA** (recomendado RTX 3090 24GB o similar)
5. **16GB RAM mínimo** (32GB recomendado)
6. **50GB espacio libre** en disco

---

## 🔧 PASO 1: INSTALAR OLLAMA

### En Linux:
```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### En Mac:
```bash
brew install ollama
```

### En Windows (WSL):
1. Instala WSL2 desde Microsoft Store
2. Dentro de WSL, ejecuta el comando de Linux

### Verificar instalación:
```bash
ollama --version
# Debería mostrar algo como: ollama version 0.5.x
```

### Iniciar servicio (si no arranca automático):
```bash
ollama serve
# Déjalo corriendo en una terminal aparte
```

---

## 📥 PASO 2: DESCARGAR MODELOS

Ejecuta estos comandos uno por uno (puede tardar 10-30 minutos según tu internet):

```bash
# Modelo principal (equilibrado)
ollama pull qwen3.5:latest

# Modelo de razonamiento profundo
ollama pull deepseek-r1:latest

# Modelo de visión
ollama pull qwen3-vl:latest

# Modelo OCR especializado
ollama pull glm-ocr:latest

# Modelo asistente general
ollama pull gemma4:latest

# Modelo OCR rápido
ollama pull deepseek-ocr:latest
```

### Verificar modelos descargados:
```bash
ollama list
```

Deberías ver una salida similar a:
```
NAME                    ID              SIZE      MODIFIED
qwen3.5:latest          6488c96fa5fa    6.6 GB    2 months ago
deepseek-r1:latest      6995872bfe4c    5.2 GB    11 days ago
qwen3-vl:latest         901cae73216e    6.1 GB    2 months ago
glm-ocr:latest          6effedd0dc8a    2.2 GB    3 weeks ago
gemma4:latest           c6eb396dbd59    9.6 GB    2 days ago
deepseek-ocr:latest     0e7b018b8a22    6.7 GB    11 days ago
```

**Total usado: ~36 GB** (bien para RTX 3090 de 24GB porque no se cargan todos simultáneamente)

---

## 📁 PASO 3: CLONAR/ENTRAR AL PROYECTO

Si ya tienes los archivos en `/workspace`:

```bash
cd /workspace
ls -la
# Deberías ver: README.md, setup_env.sh, run_system.sh, requirements.txt, etc.
```

---

## 🐍 PASO 4: CREAR ENTORNO VIRTUAL E INSTALAR DEPENDENCIAS

### Ejecutar script de configuración:

```bash
# Dar permisos de ejecución
chmod +x setup_env.sh

# Ejecutar script (crea .venv e instala todo)
./setup_env.sh
```

El script hará automáticamente:
1. ✅ Crea entorno virtual en `.venv/`
2. ✅ Actualiza pip
3. ✅ Instala todas las dependencias de `requirements.txt`
4. ✅ Verifica Ollama
5. ✅ Copia `config.example.yaml` a `config.yaml`
6. ✅ Crea directorios necesarios (`logs/`, `memory_store/`, etc.)

### Si hay errores con pip:

```bash
# Actualizar pip manualmente
python3 -m pip install --upgrade pip

# Reintentar instalación
pip install -r requirements.txt
```

---

## ⚙️ PASO 5: CONFIGURAR EL SISTEMA (OPCIONAL)

El archivo `config.yaml` ya tiene valores por defecto funcionales.

### Si quieres personalizar:

```bash
nano config.yaml
# o
code config.yaml
# o cualquier editor
```

### Configuración típica para RTX 3090 24GB:

```yaml
models:
  default: "qwen3.5:latest"        # 6.6 GB - Usado la mayoría del tiempo
  reasoning: "deepseek-r1:latest"  # 5.2 GB - Para problemas complejos
  vision: "qwen3-vl:latest"        # 6.1 GB - Para imágenes
  ocr: "glm-ocr:latest"            # 2.2 GB - Para texto en imágenes
  assistant: "gemma4:latest"       # 9.6 GB - Para chat general
  
memory:
  enabled: true
  path: "./memory_store"
  episodic_max_entries: 5000
  semantic_enabled: true
```

**Nota:** No uses `qwen3.6:latest` (23 GB) a menos que cierres todos los demás modelos, ya que dejaría solo 1 GB libre para el sistema.

---

## ▶️ PASO 6: INICIAR EL SISTEMA

### Método recomendado (API + Dashboard):

```bash
# Activar entorno virtual
source .venv/bin/activate

# Dar permisos y ejecutar
chmod +x run_system.sh
./run_system.sh
```

Esto iniciará:
1. 📡 **Servidor API** en http://localhost:8000 (segundo plano)
2. 🖥️ **Dashboard Visual** en http://localhost:7860 (primer plano)

### Verás algo como:

```
🚀 Iniciando Sistema de Agentes Inteligentes...
⚡ Activando entorno virtual...
📡 Iniciando servidor API (FastAPI) en segundo plano...
✅ API iniciada con PID: 12345
🖥️  Iniciando Dashboard Visual (Gradio)...
   - Monitor de tareas en tiempo real
   - Logs del sistema
   - Visualización de memoria y aprendizaje

Running on local URL:  http://0.0.0.0:7860
```

---

## 🌐 PASO 7: ACCEDER AL DASHBOARD

Abre tu navegador y ve a:

### Dashboard Principal:
```
http://localhost:7860
```

Verás:
- 📊 **Estado del Sistema**: Indicador verde/rojo
- ➕ **Nueva Tarea**: Formulario para enviar tareas
- 🔄 **Tareas Activas**: Lista de tareas en ejecución
- 📜 **Logs del Sistema**: Mensajes en tiempo real
- 🧠 **Memoria y Aprendizaje**: Lo que el sistema ha aprendido

### API Documentation (Swagger):
```
http://localhost:8000/docs
```

Desde aquí puedes probar todos los endpoints interactivamente.

---

## 🎯 PASO 8: TU PRIMERA TAREA

### Desde el Dashboard (recomendado):

1. Abre http://localhost:7860
2. En **"Selecciona un Agente"**, elige: `🔍 Investigador (qwen3.5)`
3. En **"Descripción de la Tarea"**, escribe:
   ```
   Busca información sobre las últimas noticias de inteligencia artificial y resume los 3 puntos más importantes.
   ```
4. Prioridad: `normal`
5. Click en **"🚀 Ejecutar Tarea"**
6. Deberías ver: `✅ Tarea creada exitosamente! ID: task_20250101_120000_1234`

### Monitorear la tarea:

1. Mira la sección **"Tareas Activas"** - debería aparecer tu tarea
2. Revisa **"Logs del Sistema"** - verás mensajes de progreso
3. Después de completada, revisa **"Memoria y Aprendizaje"** - podría haber nuevo aprendizaje

### Desde la API (alternativa):

```bash
curl -X POST "http://localhost:8000/tasks/create" \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "researcher",
    "description": "Explica qué es un transformer en machine learning",
    "priority": "normal"
  }'
```

---

## 🧪 PASO 9: PROBAR AGENTES ESPECIALIZADOS

### Agente de Visión (qwen3-vl):

1. Coloca una imagen en `uploads/ejemplo.jpg`
2. Envía tarea:
   - Agente: `👁️ Visión Computacional (qwen3-vl)`
   - Descripción: `Describe lo que ves en esta imagen: uploads/ejemplo.jpg`

### Agente OCR (glm-ocr):

1. Coloca una imagen con texto en `uploads/documento.jpg`
2. Envía tarea:
   - Agente: `📄 OCR Especializado (glm-ocr)`
   - Descripción: `Extrae todo el texto de esta imagen: uploads/documento.jpg`

### Agente de Razonamiento (deepseek-r1):

1. Envía tarea:
   - Agente: `🧠 Razonamiento Profundo (deepseek-r1)`
   - Descripción: `Resuelve este problema lógico: Si todos los A son B, y algunos B son C, ¿podemos concluir que algunos A son C? Explica tu razonamiento paso a paso.`

---

## 🛑 CÓMO DETENER EL SISTEMA

### Detener dashboard:
```
Presiona Ctrl+C en la terminal donde corre run_system.sh
```

### Detener API (si quedó corriendo):
```bash
pkill -f "python src/api/server.py"
```

### Ver procesos Python activos:
```bash
ps aux | grep python
```

---

## 🔍 SOLUCIÓN DE PROBLEMAS COMUNES

### ❌ "Ollama no responde"

```bash
# Verificar si está corriendo
pgrep -a ollama

# Si no está, iniciar
ollama serve &

# Probar conexión
curl http://localhost:11434/api/tags
```

### ❌ "Model not found"

```bash
# Verificar modelos instalados
ollama list

# Si falta alguno, descargar
ollama pull qwen3.5:latest
```

### ❌ "CUDA out of memory"

1. Cierra otras aplicaciones que usen GPU
2. Usa modelos más pequeños en `config.yaml`
3. Reduce `max_context_length` en la configuración

### ❌ "ModuleNotFoundError: No module named 'xxx'"

```bash
# Activar entorno virtual
source .venv/bin/activate

# Reinstalar dependencias
pip install -r requirements.txt --force-reinstall
```

### ❌ Dashboard no carga en el navegador

1. Verifica que la API esté corriendo:
   ```bash
   curl http://localhost:8000/health
   ```
2. Verifica logs:
   ```bash
   tail -f logs/api.log
   ```
3. Reinicia el sistema:
   ```bash
   ./run_system.sh
   ```

### ❌ La memoria no guarda aprendizajes

```bash
# Verificar permisos del directorio
ls -la memory_store/

# Si es necesario, dar permisos
chmod 755 memory_store/
```

---

## 📊 MONITOREO DEL SISTEMA

### Ver uso de GPU en tiempo real:
```bash
watch -n 1 nvidia-smi
```

### Ver uso de VRAM por proceso:
```bash
nvidia-smi pmon -i 0
```

### Ver logs en tiempo real:
```bash
tail -f logs/api.log
```

### Ver tareas activas:
```bash
curl http://localhost:8000/tasks/active | jq
```

### Ver estadísticas de memoria:
```bash
curl http://localhost:8000/memory/insights | jq
```

---

## 🎓 SIGUIENTES PASOS

Una vez que el sistema esté funcionando:

1. **Explora el Dashboard**: Familiarízate con todas las secciones
2. **Prueba diferentes agentes**: Cada uno tiene fortalezas distintas
3. **Configura MCP Servers**: Para conectar con filesystem, GitHub, etc.
4. **Integra con Telegram/Discord**: Para recibir instrucciones por mensajería
5. **Personaliza MemPalace**: Ajusta parámetros de memoria según tus necesidades
6. **Crea tus propios tools**: Añade herramientas personalizadas en `src/tools/`

---

## 📞 SOPORTE Y RECURSOS

### Documentación adicional:
- LangChain Deep Agents: https://docs.langchain.com/oss/python/deepagents/overview
- Hermes Agent: https://hermes-agent.nousresearch.com/
- MemPalace: [documentación del proyecto]
- Ollama: https://ollama.com/docs

### Comandos de ayuda rápida:

```bash
# Resumen del estado del sistema
echo "=== ESTADO DEL SISTEMA ==="
echo "Ollama:" && ollama list | head -10
echo ""
echo "API Health:" && curl -s http://localhost:8000/health | jq
echo ""
echo "Procesos Python:" && ps aux | grep "[p]ython" | wc -l
echo "========================="
```

---

## ✅ CHECKLIST FINAL

Antes de considerar el sistema como "en producción":

- [ ] Ollama instalado y corriendo
- [ ] Todos los modelos descargados (`ollama list`)
- [ ] Entorno virtual creado (`.venv/` existe)
- [ ] Dependencias instaladas sin errores
- [ ] `config.yaml` configurado correctamente
- [ ] API responde en http://localhost:8000/health
- [ ] Dashboard carga en http://localhost:7860
- [ ] Primera tarea ejecutada exitosamente
- [ ] Logs mostrando actividad
- [ ] Memoria guardando aprendizajes

**¡Si marcaste todo, estás listo! 🎉**

---

*Última actualización: Enero 2025*
*Versión del sistema: 1.0.0*
