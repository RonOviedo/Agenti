"""
Visual Primitives

Módulo para procesamiento de información visual antes de enviarla al LLM.
Incluye OCR, detección de objetos, y extracción de características.
"""

import asyncio
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import base64


@dataclass
class VisualResult:
    """Resultado de procesamiento visual"""
    objects_detected: List[Dict[str, Any]]
    text_extracted: str
    scene_description: str
    dominant_colors: List[str]
    image_dimensions: tuple
    confidence_scores: Dict[str, float]


class VisualPrimitives:
    """
    Primitivas visuales para pre-procesamiento de imágenes
    
    Procesamiento que ocurre ANTES de enviar datos al LLM:
    - Detección de objetos (YOLO)
    - OCR (Tesseract / GLM-OCR)
    - Extracción de características (OpenCV)
    - Compresión semántica
    """
    
    def __init__(self):
        self.opencv_available = False
        self.yolo_available = False
        self.tesseract_available = False
        self.glm_ocr_available = False
        
        self._initialize_libraries()
    
    def _initialize_libraries(self):
        """Inicializar bibliotecas de visión por computador"""
        try:
            import cv2
            self.cv2 = cv2
            self.opencv_available = True
        except ImportError:
            print("Warning: OpenCV not available")
        
        try:
            from ultralytics import YOLO
            # Intentar cargar modelo YOLOv8 nano (más ligero)
            self.yolo_model = YOLO('yolov8n.pt')
            self.yolo_available = True
        except Exception as e:
            print(f"Warning: YOLO not available: {e}")
        
        try:
            import pytesseract
            self.pytesseract = pytesseract
            self.tesseract_available = True
        except ImportError:
            print("Warning: Tesseract not available")
    
    async def process_image(self, image_path: str) -> Optional[VisualResult]:
        """
        Procesar imagen completa con todas las primitivas disponibles
        
        Args:
            image_path: Ruta a la imagen
            
        Returns:
            VisualResult con todos los datos extraídos
        """
        path = Path(image_path)
        if not path.exists():
            return None
        
        result = VisualResult(
            objects_detected=[],
            text_extracted="",
            scene_description="",
            dominant_colors=[],
            image_dimensions=(0, 0),
            confidence_scores={}
        )
        
        # Cargar imagen
        if self.opencv_available:
            image = self.cv2.imread(str(path))
            if image is not None:
                result.image_dimensions = (image.shape[1], image.shape[0])
                
                # Procesamiento en paralelo
                tasks = []
                
                # Detección de objetos
                if self.yolo_available:
                    tasks.append(self._detect_objects(image))
                
                # Extracción de texto (OCR)
                if self.tesseract_available:
                    tasks.append(self._extract_text(image))
                
                # Colores dominantes
                tasks.append(self._extract_colors(image))
                
                # Ejecutar tareas
                if tasks:
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    for res in results:
                        if isinstance(res, dict):
                            if 'objects' in res:
                                result.objects_detected = res['objects']
                                result.confidence_scores['object_detection'] = res.get('confidence', 0.0)
                            elif 'text' in res:
                                result.text_extracted = res['text']
                                result.confidence_scores['ocr'] = res.get('confidence', 0.0)
                            elif 'colors' in res:
                                result.dominant_colors = res['colors']
                
                # Generar descripción de escena
                result.scene_description = self._generate_scene_description(result)
        
        return result
    
    async def _detect_objects(self, image) -> Dict[str, Any]:
        """Detectar objetos usando YOLO"""
        try:
            # Ejecutar YOLO
            results = self.yolo_model(image, verbose=False, conf=0.5)
            
            objects = []
            avg_confidence = 0.0
            
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    bbox = box.xyxy[0].tolist()
                    
                    objects.append({
                        'class': self.yolo_model.names[cls],
                        'class_id': cls,
                        'confidence': conf,
                        'bbox': {
                            'x1': bbox[0],
                            'y1': bbox[1],
                            'x2': bbox[2],
                            'y2': bbox[3]
                        }
                    })
                    avg_confidence += conf
            
            if objects:
                avg_confidence /= len(objects)
            
            return {'objects': objects, 'confidence': avg_confidence}
        except Exception as e:
            print(f"Error in object detection: {e}")
            return {'objects': [], 'confidence': 0.0}
    
    async def _extract_text(self, image) -> Dict[str, Any]:
        """Extraer texto usando Tesseract OCR"""
        try:
            # Convertir a escala de grises para mejor OCR
            gray = self.cv2.cvtColor(image, self.cv2.COLOR_BGR2GRAY)
            
            # Aplicar umbralización
            _, thresh = self.cv2.threshold(gray, 0, 255, self.cv2.THRESH_BINARY + self.cv2.THRESH_OTSU)
            
            # OCR con Tesseract
            text = self.pytesseract.image_to_string(thresh, lang='eng+spa')
            
            # Calcular confianza promedio
            data = self.pytesseract.image_to_data(thresh, output_type=self.pytesseract.Output.DICT)
            confidences = [c for c in data['conf'] if c > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
            
            return {'text': text.strip(), 'confidence': avg_confidence / 100.0}
        except Exception as e:
            print(f"Error in OCR: {e}")
            return {'text': '', 'confidence': 0.0}
    
    async def _extract_colors(self, image) -> Dict[str, Any]:
        """Extraer colores dominantes"""
        try:
            # Convertir a RGB
            rgb = self.cv2.cvtColor(image, self.cv2.COLOR_BGR2RGB)
            
            # Reshape para k-means
            pixels = rgb.reshape(-1, 3)
            
            # K-means simple para 5 colores dominantes
            from sklearn.cluster import KMeans
            kmeans = KMeans(n_clusters=5, random_state=42, n_init=10)
            kmeans.fit(pixels)
            
            # Obtener colores centrales
            colors = kmeans.cluster_centers_.astype(int)
            
            # Convertir a hex
            hex_colors = []
            for color in colors:
                hex_color = '#{:02x}{:02x}{:02x}'.format(color[0], color[1], color[2])
                hex_colors.append(hex_color)
            
            return {'colors': hex_colors}
        except ImportError:
            # Fallback sin sklearn
            return {'colors': ['#000000', '#FFFFFF', '#808080']}
        except Exception as e:
            print(f"Error in color extraction: {e}")
            return {'colors': []}
    
    def _generate_scene_description(self, result: VisualResult) -> str:
        """Generar descripción textual de la escena"""
        descriptions = []
        
        # Objetos detectados
        if result.objects_detected:
            obj_list = ", ".join([obj['class'] for obj in result.objects_detected[:5]])
            descriptions.append(f"Objetos detectados: {obj_list}")
        
        # Texto encontrado
        if result.text_extracted:
            text_preview = result.text_extracted[:100].replace('\n', ' ')
            descriptions.append(f"Texto encontrado: '{text_preview}'")
        
        # Colores dominantes
        if result.dominant_colors:
            descriptions.append(f"Colores: {', '.join(result.dominant_colors[:3])}")
        
        return " | ".join(descriptions) if descriptions else "Sin información visual relevante"
    
    def create_summary(self, visual_data: Dict[str, Any]) -> str:
        """
        Crear resumen textual compacto de datos visuales para enviar al LLM
        
        Args:
            visual_data: Datos procesados de process_image
            
        Returns:
            String compacto con la información esencial
        """
        if not visual_data:
            return ""
        
        lines = ["[ANÁLISIS VISUAL]"]
        
        # Dimensiones
        dims = visual_data.get('image_dimensions', (0, 0))
        lines.append(f"Imagen: {dims[0]}x{dims[1]}px")
        
        # Objetos
        objects = visual_data.get('objects_detected', [])
        if objects:
            obj_summary = ", ".join([
                f"{obj['class']} ({obj['confidence']:.0%})"
                for obj in objects[:5]
            ])
            lines.append(f"Objetos: {obj_summary}")
        
        # Texto
        text = visual_data.get('text_extracted', '')
        if text:
            preview = text[:200].replace('\n', ' ')
            lines.append(f"OCR: \"{preview}\"")
        
        # Escena
        scene = visual_data.get('scene_description', '')
        if scene:
            lines.append(f"Escena: {scene}")
        
        return "\n".join(lines)
    
    def encode_image_base64(self, image_path: str) -> str:
        """Codificar imagen en base64 para enviar a LLMs multi-modales"""
        path = Path(image_path)
        if not path.exists():
            return ""
        
        with open(path, 'rb') as f:
            image_bytes = f.read()
            return base64.b64encode(image_bytes).decode('utf-8')


# Función de conveniencia
def create_visual_primitives() -> VisualPrimitives:
    """Crear instancia de VisualPrimitives"""
    return VisualPrimitives()
