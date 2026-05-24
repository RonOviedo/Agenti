# Sistema de Agentes Inteligentes Distribuidos

<div align="center">
  <h3>Un sistema de agentes multi-modal que crece contigo, ejecutándose localmente en tu hardware</h3>
</div>

<div align="center">
  <a href="#características"><img src="https://img.shields.io/badge/features-multi--modal-blue" alt="Features"></a>
  <a href="#modelos-soportados"><img src="https://img.shields.io/badge/models-local%20LLMs-green" alt="Models"></a>
  <a href="#hardware-recomendado"><img src="https://img.shields.io/badge/GPU-RTX%203090%2024GB-orange" alt="GPU"></a>
  <a href="LICENSE"><img src="https://img.shields.io/pypi/l/mit" alt="License"></a>
</div>

---

## 📖 Descripción General

Este sistema es un **harness de agentes autónomos** de código abierto que combina lo mejor de [LangChain Deep Agents](https://docs.langchain.com/oss/python/deepagents/overview) y [Hermes Agent](https://hermes-agent.nousresearch.com/) para crear una plataforma de agentes que:

- **Se ejecuta localmente** en tu hardware sin dependencia de APIs externas
- **Aprende y evoluciona** con el uso mediante memoria persistente y habilidades auto-generadas
- **Procesa información multi-modal** (texto, imagen, voz) usando herramientas open source
- **Se adapta a cada máquina** seleccionando automáticamente el LLM óptimo según los recursos disponibles

---

## ✨ Características Principales

### 🧠 Núcleo de Agentes (Deep Agents)

Basado en la arquitectura de LangChain Deep Agents, el sistema incluye:

| Característica | Descripción |
|---------------|-------------|
| **Sub-agentes** | Delegación de tareas a agentes con ventanas de contexto aisladas para trabajo paralelo sin contaminación de contexto |
| **Filesystem pluggable** | Lectura, escritura, edición y búsqueda sobre backends locales, sandboxeados o remotos |
| **Gestión de contexto** | Resumen automático de conversaciones largas y offload de salidas de herramientas a disco |
| **Acceso a shell** | Ejecución de comandos en el sandbox de tu elección (local, Docker, SSH, Singularity, Modal) |
| **Memoria persistente con MemPalace** | Sistema de memoria episódica y semántica inspirado en [MemPalace](https://github.com/rohitguptab/MeMPalace) para contexto persistente entre sesiones, permitiendo que cada agente recuerde interacciones pasadas, preferencias del usuario y conocimientos adquiridos |
| **Human-in-the-loop** | Aprobación, edición o rechazo de llamadas a herramientas antes de ejecutarlas |
| **Skills reutilizables** | Comportamientos que el agente puede cargar bajo demanda |
| **Herramientas MCP** | Integración nativa con cualquier servidor MCP (Model Context Protocol) |

### 🛠️ Herramientas Abiertas (Hermes-style)

Inspirado en el core de Hermes Agent, el sistema integra herramientas open source para procesamiento local:

#### 🎯 Visión por Computador
- **OpenCV** - Procesamiento de imágenes en tiempo real, detección de movimiento, seguimiento de objetos
- **YOLO** (You Only Look Once) - Detección de objetos de alta precisión con modelos pre-entrenados
- **Tesseract OCR** - Reconocimiento óptico de caracteres para digitalización de documentos

#### 🗣️ Procesamiento de Audio
- **Whisper.cpp** - Transcripción de voz a texto ejecutándose localmente
- **Piper TTS** - Síntesis de voz neural de alta calidad
- **Vosk** - Reconocimiento de voz offline multilingüe

#### 📡 Comunicación
- **Telegram Bot API** - Interfaz de mensajería asíncrona
- **Discord.py** - Integración con servidores Discord
- **Slack SDK** - Conexión con workspaces de Slack
- **Email (IMAP/SMTP)** - Lectura y envío de correos electrónicos

### 👁️ Visual Primitives

El sistema incorpora **primitivas visuales** para procesamiento y aprovechamiento de información visual antes de interactuar con el LLM:

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Entrada       │     │  Visual          │     │   LLM           │
│   Visual        │────▶│  Primitives      │────▶│   Reasoning     │
│   (Imagen/Video)│     │  (Pre-proceso)   │     │   (Decisión)    │
└─────────────────┘     └──────────────────┘     └─────────────────┘
                              │
                              ▼
                    ┌──────────────────┐
                    │  Extracción de   │
                    │  Características │
                    │  - OCR           │
                    │  - Detección     │
                    │  - Segmentación  │
                    │  - Clasificación │
                    └──────────────────┘
```

**Flujo de procesamiento visual:**
1. **Captura** - Imagen o frame de video desde cámara, archivo o stream
2. **Pre-procesamiento** - Normalización, reducción de ruido, ajuste de contraste (OpenCV)
3. **Extracción** - Detección de objetos (YOLO), texto (Tesseract/GLM-OCR), escenas
4. **Compresión semántica** - Conversión de datos visuales a representaciones textuales densas
5. **Razonamiento** - El LLM recibe la representación comprimida + contexto para tomar decisiones
6. **Acción** - El agente ejecuta herramientas o responde basado en el análisis visual

### 🔄 Automatizaciones Programadas

- **Cron en lenguaje natural** - Programa reportes, backups y briefings usando descripciones en lenguaje natural
- **Gateway de automatización** - Ejecución desatendida de flujos de trabajo complejos
- **Trigger-based actions** - Acciones desencadenadas por eventos del sistema, mensajes o cambios en archivos

---

## 🤖 Modelos Soportados

### Selección Automática por Hardware

El sistema detecta automáticamente el hardware disponible y selecciona el LLM adecuado:

| Hardware | LLM Recomendado | VRAM Requerida | Casos de Uso |
|----------|----------------|----------------|--------------|
| **RTX 3090 (24GB)** | GLM-Edge-1.5B-Chat / GLM-4-9B-Chat | 8-18 GB | Agente principal, razonamiento complejo |
| **RTX 3090 (24GB)** | GLM-OCR / InternVL2-8B | 12-20 GB | Procesamiento visual, OCR multi-modal |
| **RTX 3080 (10GB)** | Qwen2.5-7B-Instruct / Phi-3.5-mini | 6-10 GB | Sub-agentes especializados |
| **RTX 3060 (12GB)** | Llama-3.1-8B-Instruct / Gemma-2-9B | 8-12 GB | Agente principal ligero |
| **CPU only** | Phi-3.5-mini / Qwen2.5-1.5B | 2-4 GB | Sub-agentes de tareas simples |

### Modelos GLM para RTX 3090 24GB

Para una GPU RTX 3090 con 24GB de VRAM, recomendamos:

#### LLM Principal
- **GLM-4-9B-Chat** (`THUDM/glm-4-9b-chat`)
  - 9 mil millones de parámetros
  - ~18GB VRAM en FP16, ~9GB en INT4
  - Excelente para razonamiento general y tool calling
  - Soporte nativo para contexto extendido (128K)

#### LLM para Sub-agentes
- **GLM-Edge-1.5B-Chat** (`THUDM/glm-edge-1.5b-chat`)
  - 1.5 mil millones de parámetros
  - ~3GB VRAM en FP16, ~1.5GB en INT4
  - Ideal para delegación de tareas simples
  - Múltiples instancias pueden correr en paralelo

#### Modelos Multi-modales (Visión + OCR)
- **GLM-4V-9B** (`THUDM/glm-4v-9b`)
  - Modelo vision-language integrado
  - ~20GB VRAM en FP16, ~10GB en INT4
  - Comprensión de imágenes, diagramas, capturas de pantalla
  
- **InternVL2-8B** (`OpenGVLab/InternVL2-8B`)
  - Alternativa ligera para visión
  - ~16GB VRAM en FP16, ~8GB en INT4
  - OCR integrado, detección de texto en escenas

#### OCR Especializado
- **GLM-OCR** (modelo dedicado)
  - Optimizado para reconocimiento de texto
  - ~12GB VRAM
  - Alta precisión en documentos escaneados, manuscritos

### Backend de Inferencia

El sistema soporta múltiples backends de inferencia:

| Backend | Ventajas | Configuración recomendada |
|---------|----------|---------------------------|
| **Ollama** | Fácil instalación, cuantización automática | `ollama run glm4:9b-chat-q4_K_M` |
| **vLLM** | Máximo throughput, PagedAttention | `--gpu-memory-utilization 0.9 --quantization awq` |
| **llama.cpp** | Ejecución CPU/GPU híbrida, GGUF | `glm-4-9b-chat-Q4_K_M.gguf` |
| **Text Generation Inference** | Producción, batching dinámico | Docker con CUDA habilitado |
| **SGLang** | Optimizado para visión + lenguaje | `--mem-fraction-static 0.9` |

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           CAPA DE INTERFAZ                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │ Telegram │  │ Discord  │  │   CLI    │  │   Web    │  │   Email  │ │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘ │
└───────┼─────────────┼─────────────┼─────────────┼─────────────┼────────┘
        │             │             │             │             │
        └─────────────┴─────────────┼─────────────┴─────────────┘
                                    │
┌───────────────────────────────────▼────────────────────────────────────┐
│                         ORQUESTADOR DE AGENTES                          │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                     Agente Principal (Router)                     │  │
│  │         GLM-4-9B-Chat (RTX 3090) - Planificación y decisión      │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                    │                                    │
│         ┌──────────────────────────┼──────────────────────────┐        │
│         │                          │                          │        │
│         ▼                          ▼                          ▼        │
│  ┌─────────────┐            ┌─────────────┐            ┌─────────────┐ │
│  │ Sub-agente  │            │ Sub-agente  │            │ Sub-agente  │ │
│  │   Código    │            │   Visual    │            │   Datos     │ │
│  │ GLM-Edge-1B │            │ InternVL-8B │            │ GLM-Edge-1B │ │
│  └──────┬──────┘            └──────┬──────┘            └──────┬──────┘ │
└─────────┼──────────────────────────┼──────────────────────────┼────────┘
          │                          │                          │
┌─────────▼──────────────────────────▼──────────────────────────▼────────┐
│                      CAPA DE HERRAMIENTAS (TOOLS)                       │
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────┐│
│  │  OpenCV    │ │    YOLO    │ │  Tesseract │ │   Whisper  │ │ Shell  ││
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘ └────────┘│
│  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────┐│
│  │  Filesystem│ │    SQLite  │ │    MCP     │ │   Browser  │ │  Git   ││
│  └────────────┘ └────────────┘ └────────────┘ └────────────┘ └────────┘│
└─────────────────────────────────────────────────────────────────────────┘
          │                          │                          │
┌─────────▼──────────────────────────▼──────────────────────────▼────────┐
│                        CAPA DE MEMORIA PERSISTENTE                      │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐         │
│  │ Vector Store    │  │ Skill Library   │  │ Conversation DB │         │
│  │ (Chroma/Qdrant) │  │ (JSON/SQLite)   │  │   (PostgreSQL)  │         │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘         │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │              MemPalace: Memoria Episódica y Semántica            │   │
│  │  - Recall de interacciones pasadas entre sesiones               │   │
│  │  - Preferencias del usuario persistentes                        │   │
│  │  - Conocimientos adquiridos durante el uso                      │   │
│  │  - Contexto específico por agente y tarea                       │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🚀 Instalación

### Requisitos Previos

- **GPU**: NVIDIA con ≥8GB VRAM (RTX 3060 o superior recomendado)
- **CUDA**: 12.0 o superior
- **Python**: 3.10 - 3.12
- **RAM**: 16GB mínimo, 32GB recomendado
- **Almacenamiento**: 50GB libres para modelos y caché
- **Node.js**: 18+ (para servidores MCP)

### Instalación Rápida

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/sistema-agentes.git
cd sistema-agentes

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Instalar Ollama (Linux)
curl -fsSL https://ollama.com/install.sh | sh

# Descargar modelos recomendados para RTX 3090
ollama pull qwen3.5:latest        # Agente principal (6.6 GB) ⭐
ollama pull deepseek-r1:latest    # Razonamiento (5.2 GB)
ollama pull qwen3-vl:latest       # Visión multi-modal (6.1 GB)
ollama pull glm-ocr:latest        # OCR ligero (2.2 GB)
ollama pull gemma4:latest         # Alternativa general (9.6 GB)

# Copiar configuración de ejemplo
cp config.example.yaml config.yaml
```

### Ejecución del Sistema

El sistema puede ejecutarse en tres modos:

```bash
# Modo API (servidor REST + WebSocket)
python -m src.main api --port 8000

# Modo GUI (interfaz web Gradio)
python -m src.main gui --port 7860

# Modo CLI (consola interactiva)
python -m src.main cli

# Ver todos los modelos disponibles en tu sistema
ollama list
```

### Comandos de la API

Una vez iniciado el servidor API (`http://localhost:8000`):

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/` | GET | Información del servicio |
| `/health` | GET | Verificar estado del servicio |
| `/agents` | GET | Listar agentes disponibles |
| `/chat` | POST | Enviar mensaje al agente |
| `/chat/upload` | POST | Enviar mensaje con imagen |
| `/ws/{user_id}` | WebSocket | Comunicación en tiempo real |
| `/memory/{user_id}` | GET | Obtener memoria del usuario |

### Ejemplo de uso con cURL

```bash
# Chat simple
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "¿Qué puedes hacer?", "user_id": "usuario1"}'

# Subir imagen para análisis visual
curl -X POST http://localhost:8000/chat/upload \
  -F "message=Analiza esta imagen" \
  -F "user_id=usuario1" \
  -F "file=@documento.jpg"
```

### Archivo de Configuración (`config.yaml`)

```yaml
hardware:
  gpu: "NVIDIA GeForce RTX 3090"
  vram_gb: 24
  cpu_cores: 12
  ram_gb: 64

models:
  primary:
    name: "glm4:9b-chat-q4_K_M"
    backend: "ollama"
    context_length: 128000
    gpu_layers: 50  # Capas en GPU
    
  subagents:
    - name: "glm-edge:1.5b-chat"
      backend: "ollama"
      max_instances: 4
      
  vision:
    name: "internvl2:8b"
    backend: "ollama"
    ocr_enabled: true

tools:
  enabled:
    - opencv
    - yolo
    - tesseract
    - whisper
    - browser
    - shell
    - filesystem
    
  yolo:
    model: "yolov8x.pt"  # o yolov8n.pt para menos VRAM
    
  tesseract:
    lang: "eng+spa"
    oem: 3
    
  whisper:
    model: "medium"  # tiny, base, small, medium, large

memory:
  vector_store: "chroma"
  persist_path: "./data/memory"
  max_history: 1000
  
  # Configuración de MemPalace para memoria episódica y semántica
  mempalace:
    enabled: true
    episodic_memory:
      enabled: true
      max_entries: 5000
      retention_days: 90
    semantic_memory:
      enabled: true
      knowledge_graph: true
      concept_linking: true
    agent_specific:
      enabled: true
      isolated_contexts: true
    user_preferences:
      enabled: true
      persist_path: "./data/preferences.yaml"

sandbox:
  default: "docker"
  backends:
    - local
    - docker
    - ssh
```

---

## 💻 Uso Básico

### Ejemplo: Agente con Herramientas Visuales y MemPalace

```python
from sistema_agentes import create_agent
from sistema_agentes.tools import OpenCVTool, YOLOTool, TesseractOCR
from sistema_agentes.memory import MemPalaceMemory

# Crear agente principal con memoria episódica y semántica
agent = create_agent(
    model="ollama/glm4:9b-chat-q4_K_M",
    tools=[
        OpenCVTool(),
        YOLOTool(model="yolov8m.pt"),
        TesseractOCR(languages=["spa", "eng"]),
    ],
    memory=MemPalaceMemory(
        persist_path="./data/memory",
        episodic_enabled=True,
        semantic_enabled=True,
        agent_id="vision_agent_01",
    ),
    system_prompt="""Eres un asistente multi-modal capaz de analizar imágenes,
    detectar objetos y extraer texto. Usa las herramientas visuales antes de
    responder preguntas sobre contenido visual. Recuerda las preferencias del
    usuario y el contexto de interacciones anteriores.""",
)

# Ejecutar tarea con entrada visual
result = agent.invoke({
    "messages": [
        {"role": "user", "content": "Analiza esta imagen y dime qué objetos ves y qué texto contiene"},
        {"role": "user", "content_type": "image", "path": "./imagenes/documento.jpg"}
    ]
})

print(result["response"])
```

### Ejemplo: Sub-agentes Paralelos

```python
from sistema_agentes import create_agent, SubAgent

# Definir sub-agentes especializados
coding_agent = SubAgent(
    name="coding_specialist",
    model="ollama/glm-edge:1.5b-chat",
    tools=["shell", "filesystem", "git"],
    description="Experto en escribir y ejecutar código Python"
)

vision_agent = SubAgent(
    name="vision_specialist",
    model="ollama/internvl2:8b",
    tools=["opencv", "yolo", "tesseract"],
    description="Experto en procesamiento de imágenes y OCR"
)

# Agente principal que coordina
main_agent = create_agent(
    model="ollama/glm4:9b-chat-q4_K_M",
    subagents=[coding_agent, vision_agent],
    enable_parallel_execution=True,
)

# El agente principal delegará automáticamente
result = main_agent.invoke({
    "messages": "Extrae todo el texto de estas 10 imágenes y guarda los resultados en un CSV"
})
```

### Ejemplo: Automatización Programada

```python
from sistema_agentes.scheduler import schedule_task

# Programar reporte diario en lenguaje natural
schedule_task(
    description="Todos los días a las 8 AM, analiza las noticias del día y envía un resumen por Telegram",
    agent=main_agent,
    tools=["browser", "telegram"],
)

# Programar backup semanal
schedule_task(
    description="Cada domingo a las 3 AM, haz backup de la base de datos y súbelo a Google Drive",
    agent=main_agent,
    tools=["shell", "filesystem"],
)
```

---

## 🔧 Herramientas Disponibles

### Herramientas Visuales

| Herramienta | Descripción | VRAM | Uso |
|------------|-------------|------|-----|
| `OpenCVTool` | Procesamiento básico de imágenes | ~1GB | Filtros, transformaciones, detección de bordes |
| `YOLOTool` | Detección de objetos en tiempo real | 2-6GB | Identificar personas, vehículos, objetos |
| `TesseractOCR` | Reconocimiento óptico de caracteres | ~500MB | Extraer texto de documentos escaneados |
| `GLMOCRTool` | OCR neuronal de alta precisión | 8-12GB | Documentos complejos, manuscritos |
| `SegmentAnything` | Segmentación de imágenes | 4-8GB | Aislar objetos específicos |

### Herramientas de Audio

| Herramienta | Descripción | VRAM/RAM | Uso |
|------------|-------------|----------|-----|
| `WhisperTool` | Transcripción voz a texto | 1-4GB | Transcribir reuniones, notas de voz |
| `PiperTTS` | Síntesis de voz neural | CPU | Leer respuestas en voz alta |
| `VoiceActivityDetection` | Detección de voz activa | CPU | Grabar solo cuando hay habla |

### Herramientas de Sistema

| Herramienta | Descripción | Uso |
|------------|-------------|-----|
| `ShellTool` | Ejecutar comandos bash | Automatización, gestión de archivos |
| `FileSystemTool` | Leer/escribir/archivos | Gestión documental |
| `BrowserTool` | Navegación web headless | Búsqueda, scraping controlado |
| `GitTool` | Operaciones Git | Control de versiones |
| `DatabaseTool` | Consultas SQL/NoSQL | Gestión de datos |

### Herramientas de Comunicación

| Herramienta | Descripción | Config |
|------------|-------------|--------|
| `TelegramBot` | Enviar/recibir mensajes | Token de bot |
| `DiscordBot` | Integración Discord | Token, guild ID |
| `EmailTool` | IMAP/SMTP | Credenciales email |
| `SlackBot` | Mensajería Slack | Token, channel ID |

---

## 🧠 Memoria y Aprendizaje

### Tipos de Memoria

1. **Memoria de Corto Plazo** - Contexto de conversación actual (hasta 128K tokens)
2. **Memoria de Largo Plazo** - Vector store con embeddings de interacciones pasadas
3. **Skill Library** - Biblioteca de habilidades aprendidas/auto-generadas
4. **Project Memory** - Contexto específico por proyecto/cliente

### Generación Automática de Skills

El sistema puede crear nuevas habilidades basadas en patrones exitosos:

```python
# El agente identifica un patrón repetitivo
# y crea una skill reutilizable automáticamente

@skill(
    name="analizar_factura",
    description="Extrae información estructurada de facturas PDF",
    triggers=["factura", "invoice", "recibo"]
)
async def analizar_factura_skill(context):
    # 1. Usar OCR para extraer texto
    texto = await context.tools.tesseract.run(context.input_image)
    
    # 2. Parsear con LLM
    datos = await context.llm.extract_structured(
        texto,
        schema={"proveedor": str, "total": float, "fecha": str}
    )
    
    # 3. Guardar en base de datos
    await context.db.insert("facturas", datos)
    
    return datos
```

---

## 🔒 Seguridad y Sandboxing

### Backends de Sandbox Disponibles

| Backend | Aislamiento | Casos de Uso |
|---------|-------------|--------------|
| **Local** | Ninguno | Desarrollo, confianza total |
| **Docker** | Contenedores | Producción, multi-tenant |
| **SSH** | Máquina remota | Ejecución en servidor dedicado |
| **Singularity** | HPC, científico | Clusters, supercomputación |
| **Modal** | Cloud serverless | Escalado elástico |

### Políticas de Permisos

```yaml
permissions:
  filesystem:
    allowed_paths:
      - ./projects/*
      - ./data/*
    denied_paths:
      - /etc/*
      - /root/*
      
  network:
    allowed_domains:
      - api.github.com
      - docs.python.org
    blocked_domains:
      - "*.malicious.com"
      
  shell:
    allowed_commands:
      - python
      - pip
      - git
      - ls
      - cat
    denied_commands:
      - rm -rf /
      - sudo
      - curl | bash
      
  require_approval:
    - destructive_operations: true
    - network_access: true
    - external_apis: true
```

---

## 📊 Monitoreo y Debugging

### LangSmith Integration

```python
from langsmith import Client

client = Client()

# Habilitar tracing automático
agent = create_agent(
    model="ollama/glm4:9b-chat",
    tools=[...],
    tracing_config={
        "project_name": "sistema-agentes-prod",
        "client": client,
    }
)
```

### Logs Estructurados

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('./logs/agent.log'),
        logging.StreamHandler()
    ]
)
```

---

## 🎯 Casos de Uso

### 1. Asistente Personal Multi-modal
- Recibe mensajes por Telegram/WhatsApp
- Procesa imágenes enviadas (OCR, detección de objetos)
- Transcribe notas de voz
- Agenda recordatorios y tareas

### 2. Analista de Documentos
- Procesa lotes de documentos escaneados
- Extrae texto con OCR neuronal
- Clasifica y organiza en carpetas
- Genera resúmenes ejecutivos

### 3. Monitor de Sistemas
- Observa dashboards y capturas de pantalla
- Detecta anomalías visuales (gráficos, alertas)
- Ejecuta scripts de remediación
- Notifica por Slack/Discord

### 4. Desarrollador Asistido
- Lee issues de GitHub
- Escribe y prueba código
- Ejecuta tests en sandbox
- Crea pull requests automáticos

### 5. Investigador Académico
- Busca papers en arXiv
- Extrae figuras y tablas de PDFs
- Resume hallazgos clave
- Organiza bibliografía

---

## 🤝 Contribuir

Las contribuciones son bienvenidas! Ver [CONTRIBUTING.md](CONTRIBUTING.md) para:

- Reportar bugs
- Sugerir características
- Enviar pull requests
- Mejorar documentación

---

## 📄 Licencia

MIT License - ver [LICENSE](LICENSE) para detalles.

---

## 🙏 Agradecimientos

- [LangChain Deep Agents](https://github.com/langchain-ai/deepagents) - Inspiración para el harness de agentes
- [Hermes Agent](https://hermes-agent.nousresearch.com/) - Modelo de herramientas abiertas y skills persistentes
- [MemPalace](https://github.com/rohitguptab/MeMPalace) - Sistema de memoria episódica y semántica para LLMs
- [THUDM](https://github.com/THUDM) - Modelos GLM de código abierto
- [Ultralytics](https://ultralytics.com/) - YOLO para detección de objetos
- [Tesseract](https://github.com/tesseract-ocr/tesseract) - OCR open source

---

## 📞 Comunidad

- **Discord**: [Únete a nuestro servidor](https://discord.gg/tu-server)
- **Twitter/X**: [@tu_usuario](https://twitter.com/tu_usuario)
- **Forum**: [forum.langchain.com](https://forum.langchain.com/)

---

<div align="center">
  <strong>Construido con ❤️ para la comunidad de AI open source</strong>
</div>
