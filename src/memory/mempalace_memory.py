"""
MemPalace Memory Implementation

Sistema de memoria persistente episódica y semántica para agentes.
Permite recordar interacciones pasadas, preferencias del usuario
y conocimientos adquiridos durante el uso.
"""

import json
import asyncio
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import chromadb
from chromadb.config import Settings


@dataclass
class EpisodicMemory:
    """Memoria episódica: eventos específicos con timestamp"""
    id: str
    user_id: str
    query: str
    response: str
    timestamp: float
    agent_used: str
    metadata: Dict[str, Any]


@dataclass
class SemanticMemory:
    """Memoria semántica: conceptos y relaciones"""
    concept: str
    description: str
    related_concepts: List[str]
    confidence: float
    sources: List[str]


class MemPalaceMemory:
    """
    Implementación de MemPalace para memoria persistente de agentes
    
    Características:
    - Memoria episódica: Almacena interacciones específicas
    - Memoria semántica: Grafo de conocimiento conceptual
    - Contexto por agente: Aislamiento de contextos
    - Preferencias de usuario: Configuración persistente
    """
    
    def __init__(
        self,
        persist_path: str = "./data/memory",
        episodic_enabled: bool = True,
        semantic_enabled: bool = True,
        agent_id: str = "default",
        max_entries: int = 5000,
        retention_days: int = 90
    ):
        self.persist_path = Path(persist_path)
        self.agent_id = agent_id
        self.max_entries = max_entries
        self.retention_days = retention_days
        
        # Crear directorios
        self.persist_path.mkdir(parents=True, exist_ok=True)
        
        # Inicializar ChromaDB para memoria episódica
        self.episodic_enabled = episodic_enabled
        self.semantic_enabled = semantic_enabled
        
        if episodic_enabled:
            self.episodic_client = chromadb.PersistentClient(
                path=str(self.persist_path / "episodic"),
                settings=Settings(anonymized_telemetry=False)
            )
            self.episodic_collection = self.episodic_client.get_or_create_collection(
                name=f"episodic_{agent_id}",
                metadata={"description": "Episodic memory for agent interactions"}
            )
        
        if semantic_enabled:
            self.semantic_client = chromadb.PersistentClient(
                path=str(self.persist_path / "semantic"),
                settings=Settings(anonymized_telemetry=False)
            )
            self.semantic_collection = self.semantic_client.get_or_create_collection(
                name=f"semantic_{agent_id}",
                metadata={"description": "Semantic knowledge graph"}
            )
        
        # Archivo de preferencias
        self.preferences_path = self.persist_path / f"preferences_{agent_id}.json"
        self.user_preferences = self._load_preferences()
        
        # Archivo de grafo semántico
        self.graph_path = self.persist_path / f"graph_{agent_id}.json"
        self.concept_graph = self._load_graph()
    
    def _load_preferences(self) -> Dict[str, Any]:
        """Cargar preferencias de usuario desde archivo"""
        if self.preferences_path.exists():
            with open(self.preferences_path, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_preferences(self):
        """Guardar preferencias de usuario"""
        with open(self.preferences_path, 'w') as f:
            json.dump(self.user_preferences, f, indent=2)
    
    def _load_graph(self) -> Dict[str, Any]:
        """Cargar grafo de conocimiento semántico"""
        if self.graph_path.exists():
            with open(self.graph_path, 'r') as f:
                return json.load(f)
        return {"concepts": {}, "relations": []}
    
    def _save_graph(self):
        """Guardar grafo de conocimiento semántico"""
        with open(self.graph_path, 'w') as f:
            json.dump(self.concept_graph, f, indent=2)
    
    async def store_interaction(
        self,
        user_id: str,
        query: str,
        response: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Almacenar una interacción en memoria episódica
        
        Args:
            user_id: Identificador del usuario
            query: Pregunta o comando del usuario
            response: Respuesta del agente
            metadata: Metadata adicional (agente usado, timestamp, etc.)
        """
        if not self.episodic_enabled:
            return
        
        import uuid
        entry_id = str(uuid.uuid4())
        timestamp = datetime.now().timestamp()
        
        # Crear documento para ChromaDB
        document = f"User: {query}\nAssistant: {response}"
        
        metadata_dict = {
            "user_id": user_id,
            "query": query[:500],  # Truncar para metadata
            "agent_used": metadata.get('agent_used', 'unknown') if metadata else 'unknown',
            "timestamp": timestamp,
            **(metadata or {})
        }
        
        # Agregar a colección
        self.episodic_collection.add(
            ids=[entry_id],
            documents=[document],
            metadatas=[metadata_dict]
        )
        
        # Extraer conceptos para memoria semántica
        if self.semantic_enabled:
            await self._extract_concepts(query, response, user_id)
        
        # Limpiar entradas antiguas
        await self._cleanup_old_entries()
    
    async def _extract_concepts(self, query: str, response: str, user_id: str):
        """Extraer conceptos clave para memoria semántica"""
        # Implementación simplificada - en producción usaría NLP
        words = set((query + " " + response).lower().split())
        
        # Filtrar palabras comunes
        stop_words = {'el', 'la', 'los', 'las', 'un', 'una', 'de', 'que', 'en', 'es'}
        concepts = [w for w in words if len(w) > 3 and w not in stop_words]
        
        for concept in concepts[:10]:  # Limitar a 10 conceptos
            if concept not in self.concept_graph["concepts"]:
                self.concept_graph["concepts"][concept] = {
                    "description": f"Concepto relacionado con: {query[:100]}",
                    "count": 1,
                    "related": [],
                    "last_seen": datetime.now().isoformat()
                }
            else:
                self.concept_graph["concepts"][concept]["count"] += 1
                self.concept_graph["concepts"][concept]["last_seen"] = datetime.now().isoformat()
        
        self._save_graph()
    
    async def _cleanup_old_entries(self):
        """Eliminar entradas más antiguas que retention_days"""
        cutoff_time = datetime.now() - timedelta(days=self.retention_days)
        cutoff_timestamp = cutoff_time.timestamp()
        
        # Obtener todas las entradas
        all_entries = self.episodic_collection.get(include=["metadatas"])
        
        entries_to_delete = []
        for i, metadata in enumerate(all_entries.get('metadatas', [])):
            if metadata.get('timestamp', 0) < cutoff_timestamp:
                entries_to_delete.append(all_entries['ids'][i])
        
        # Eliminar si excede máximo
        current_count = self.episodic_collection.count()
        if current_count > self.max_entries:
            # Ordenar por timestamp y eliminar los más antiguos
            sorted_entries = sorted(
                [(id_, m.get('timestamp', 0)) 
                 for id_, m in zip(all_entries['ids'], all_entries.get('metadatas', []))],
                key=lambda x: x[1]
            )
            entries_to_delete.extend([e[0] for e in sorted_entries[:current_count - self.max_entries]])
        
        if entries_to_delete:
            self.episodic_collection.delete(ids=entries_to_delete)
    
    async def retrieve_context(
        self,
        query: str,
        user_id: str = "default",
        top_k: int = 5
    ) -> Dict[str, Any]:
        """
        Recuperar contexto relevante de la memoria
        
        Args:
            query: Pregunta o tema de búsqueda
            user_id: Filtrar por usuario específico
            top_k: Número de resultados a devolver
            
        Returns:
            Dict con entradas episódicas y conceptos semánticos relevantes
        """
        results = {
            "episodic_entries": [],
            "semantic_concepts": [],
            "user_preferences": self.user_preferences
        }
        
        # Búsqueda episódica
        if self.episodic_enabled:
            try:
                episodic_results = self.episodic_collection.query(
                    query_texts=[query],
                    n_results=min(top_k * 2, self.episodic_collection.count())
                )
                
                for i, doc in enumerate(episodic_results.get('documents', [[]])[0]):
                    metadata = episodic_results.get('metadatas', [[]])[0][i]
                    
                    # Filtrar por user_id si se especifica
                    if user_id != "default" and metadata.get('user_id') != user_id:
                        continue
                    
                    results["episodic_entries"].append({
                        "content": doc,
                        "metadata": metadata
                    })
                
                results["episodic_entries"] = results["episodic_entries"][:top_k]
            except Exception as e:
                print(f"Error retrieving episodic memory: {e}")
        
        # Búsqueda semántica
        if self.semantic_enabled:
            try:
                # Buscar conceptos relacionados
                query_words = set(query.lower().split())
                related_concepts = []
                
                for concept, data in self.concept_graph.get("concepts", {}).items():
                    if any(word in concept for word in query_words):
                        related_concepts.append({
                            "concept": concept,
                            "description": data.get("description", ""),
                            "confidence": min(data.get("count", 1) / 10, 1.0)
                        })
                
                # Ordenar por confianza
                related_concepts.sort(key=lambda x: x["confidence"], reverse=True)
                results["semantic_concepts"] = related_concepts[:top_k]
            except Exception as e:
                print(f"Error retrieving semantic memory: {e}")
        
        return results
    
    async def update_preference(self, key: str, value: Any):
        """Actualizar preferencia de usuario"""
        self.user_preferences[key] = value
        self._save_preferences()
    
    async def get_preference(self, key: str, default: Any = None) -> Any:
        """Obtener preferencia de usuario"""
        return self.user_preferences.get(key, default)
    
    async def close(self):
        """Cerrar conexiones y guardar estado"""
        self._save_preferences()
        self._save_graph()
        # ChromaDB no requiere cierre explícito


# Función de conveniencia
def create_memory(
    persist_path: str = "./data/memory",
    agent_id: str = "default",
    **kwargs
) -> MemPalaceMemory:
    """Crear instancia de MemPalaceMemory"""
    return MemPalaceMemory(
        persist_path=persist_path,
        agent_id=agent_id,
        **kwargs
    )
