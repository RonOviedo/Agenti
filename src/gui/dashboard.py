"""
Dashboard Visual del Sistema de Agentes
- Monitor de tareas en ejecución
- Logs en tiempo real
- Visualización de memoria y aprendizaje (MemPalace)
"""

import gradio as gr
import requests
import json
import os
from datetime import datetime
from collections import deque

API_URL = "http://localhost:8000"

# Colas para logs y eventos
log_queue = deque(maxlen=100)
task_queue = deque(maxlen=50)
memory_insights = []

def get_system_status():
    """Obtener estado actual del sistema"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        if response.status_code == 200:
            return "🟢 Sistema Operativo"
    except:
        pass
    return "🔴 Sistema Desconectado"

def get_active_tasks():
    """Obtener tareas en ejecución"""
    try:
        response = requests.get(f"{API_URL}/tasks/active", timeout=2)
        if response.status_code == 200:
            tasks = response.json()
            if not tasks:
                return "No hay tareas activas actualmente."
            
            output = ""
            for task in tasks:
                status_icon = "🔄" if task.get("status") == "running" else "⏳"
                output += f"{status_icon} **{task.get('id', 'N/A')}**: {task.get('description', 'Sin descripción')}\n"
                output += f"   Estado: `{task.get('status', 'unknown')}` | Agente: `{task.get('agent', 'N/A')}`\n"
                output += f"   Iniciado: {task.get('started_at', 'N/A')}\n\n"
            return output
    except Exception as e:
        return f"Error al obtener tareas: {str(e)}"
    return "No se pudo conectar con la API."

def get_recent_logs():
    """Obtener logs recientes"""
    try:
        response = requests.get(f"{API_URL}/logs/recent?limit=50", timeout=2)
        if response.status_code == 200:
            logs = response.json()
            output = ""
            for log in logs:
                timestamp = log.get("timestamp", "")
                level = log.get("level", "INFO")
                message = log.get("message", "")
                
                # Colorear según nivel
                if level == "ERROR":
                    output += f"🔴 `{timestamp}` [{level}] {message}\n"
                elif level == "WARNING":
                    output += f"🟡 `{timestamp}` [{level}] {message}\n"
                elif level == "SUCCESS":
                    output += f"🟢 `{timestamp}` [{level}] {message}\n"
                else:
                    output += f"⚪ `{timestamp}` [{level}] {message}\n"
            return output
    except Exception as e:
        return f"Error al obtener logs: {str(e)}"
    return "No se pudo conectar con la API."

def get_memory_insights():
    """Obtener información sobre lo que el sistema ha aprendido"""
    try:
        response = requests.get(f"{API_URL}/memory/insights", timeout=2)
        if response.status_code == 200:
            data = response.json()
            output = "## 🧠 Memoria y Aprendizaje del Sistema\n\n"
            
            # Estadísticas
            stats = data.get("stats", {})
            output += f"- **Total de recuerdos episódicos**: {stats.get('episodic_count', 0)}\n"
            output += f"- **Conceptos semánticos**: {stats.get('semantic_count', 0)}\n"
            output += f"- **Preferencias de usuario**: {stats.get('preferences_count', 0)}\n"
            output += f"- **Sesiones recordadas**: {stats.get('sessions_count', 0)}\n\n"
            
            # Aprendizajes recientes
            learnings = data.get("recent_learnings", [])
            if learnings:
                output += "### 💡 Aprendizajes Recientes\n"
                for learning in learnings[-5:]:
                    output += f"- {learning.get('content', '')} *(Confianza: {learning.get('confidence', 0):.2f})*\n"
            
            # Contextos activos
            contexts = data.get("active_contexts", [])
            if contexts:
                output += "\n### 📂 Contextos Activos\n"
                for ctx in contexts:
                    output += f"- **{ctx.get('name', 'Unknown')}**: {ctx.get('description', '')}\n"
            
            return output
    except Exception as e:
        return f"Error al obtener memoria: {str(e)}"
    return "No se pudo conectar con la API."

def send_task(agent_type, task_description, priority="normal"):
    """Enviar una nueva tarea al sistema"""
    try:
        payload = {
            "agent_type": agent_type,
            "description": task_description,
            "priority": priority,
            "metadata": {
                "source": "dashboard",
                "timestamp": datetime.now().isoformat()
            }
        }
        response = requests.post(f"{API_URL}/tasks/create", json=payload, timeout=5)
        if response.status_code == 200:
            result = response.json()
            return f"✅ Tarea creada exitosamente!\nID: `{result.get('task_id', 'N/A')}`\nEstado: {result.get('status', 'unknown')}"
        else:
            return f"❌ Error al crear tarea: {response.text}"
    except Exception as e:
        return f"❌ Error de conexión: {str(e)}"

def refresh_all():
    """Actualizar toda la información del dashboard"""
    status = get_system_status()
    tasks = get_active_tasks()
    logs = get_recent_logs()
    memory = get_memory_insights()
    return status, tasks, logs, memory

# Crear interfaz Gradio
with gr.Blocks(title="🤖 Dashboard de Agentes Inteligentes", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 🤖 Dashboard de Control del Sistema de Agentes")
    gr.Markdown("Monitoriza tareas, logs y el aprendizaje del sistema en tiempo real.")
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 📊 Estado del Sistema")
            status_box = gr.Textbox(label="Estado", value=get_system_status(), interactive=False)
            
            gr.Markdown("### ➕ Nueva Tarea")
            with gr.Group():
                agent_dropdown = gr.Dropdown(
                    choices=[
                        ("🔍 Investigador (qwen3.5)", "researcher"),
                        ("🧠 Razonamiento Profundo (deepseek-r1)", "reasoner"),
                        ("👁️ Visión Computacional (qwen3-vl)", "vision"),
                        ("📄 OCR Especializado (glm-ocr)", "ocr"),
                        ("💬 Asistente General (gemma4)", "assistant"),
                        ("⚡ Rápido/Eficiencia (deepseek-ocr)", "fast")
                    ],
                    label="Selecciona un Agente",
                    value="researcher"
                )
                task_input = gr.Textbox(
                    label="Descripción de la Tarea",
                    placeholder="Ej: Analiza las imágenes en la carpeta uploads y extrae todo el texto...",
                    lines=3
                )
                priority_select = gr.Radio(
                    choices=["low", "normal", "high", "critical"],
                    value="normal",
                    label="Prioridad"
                )
                submit_btn = gr.Button("🚀 Ejecutar Tarea", variant="primary")
                task_result = gr.Textbox(label="Resultado", interactive=False)
            
            submit_btn.click(
                fn=send_task,
                inputs=[agent_dropdown, task_input, priority_select],
                outputs=task_result
            )
        
        with gr.Column(scale=1):
            gr.Markdown("### 🔄 Tareas Activas")
            tasks_box = gr.Textbox(label="Tareas en Ejecución", value=get_active_tasks(), lines=10, interactive=False)
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 📜 Logs del Sistema")
            logs_box = gr.Textbox(label="Logs Recientes", value=get_recent_logs(), lines=15, interactive=False, max_lines=50)
        
        with gr.Column(scale=1):
            gr.Markdown("### 🧠 Memoria y Aprendizaje")
            memory_box = gr.Markdown(value=get_memory_insights())
    
    # Botón de refresh
    refresh_btn = gr.Button("🔄 Actualizar Todo", variant="secondary")
    refresh_btn.click(
        fn=refresh_all,
        inputs=[],
        outputs=[status_box, tasks_box, logs_box, memory_box]
    )
    
    # Auto-refresh cada 5 segundos (opcional, puede desactivarse si es muy pesado)
    # demo.load(fn=refresh_all, inputs=[], outputs=[status_box, tasks_box, logs_box, memory_box], every=5)

if __name__ == "__main__":
    print("🖥️  Iniciando Dashboard en http://localhost:7860")
    demo.launch(server_name="0.0.0.0", server_port=7860, share=False)
