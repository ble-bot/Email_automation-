import re
import vobject
import json
import requests
import pytesseract
import io
import time
import base64
from PIL import Image
from bs4 import BeautifulSoup
from email.utils import parseaddr
from typing import Optional, Dict, Any, List

from app.config import Config
from app.logger import logger
from app.utils import sanitize_text_field
import spacy

# Intentar importar librerías de visión por computadora de forma opcional
try:
    import cv2
    import numpy as np
    HAS_CV2 = True
except ImportError:
    HAS_CV2 = False
    logger.warning("OpenCV (cv2) o numpy no encontrados. La extracción de texto de imágenes (OCR) estará limitada.")

class SignatureExtractor:
    """
    Clase encargada de la lógica de extracción de información desde firmas de correo.
    Utiliza una arquitectura multi-capa: Reglas Heurísticas -> NLP (spaCy) -> IA (Gemini).
    """
    
    API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-flash-latest:generateContent"
    
    # Expresiones regulares pre-compiladas para optimización
    NAME_BLACKLIST = re.compile(r'\b(Hola|Saludos|Estimado|Buenos|Equipo|Querido|Atentamente|Cordialmente|Revisar|Confirmar|Adjunto|Gerente|Director|Jefe|Coordinador|Presidente|CEO|Manager|Socio)\b', re.I)
    ORG_KEYWORDS = re.compile(r'\b(Universidad|Instituto|Hospital|Clinica|Corp|S\.?A\.?|S\.?L\.?|Inc\.?|Group|Org|Colegio|Empresa|Ltda|Consulting|Services|Solutions|Bank|Agency|Studio|Lab|Foundation|Association|Global|Tech|Software|Industries)\b', re.I)
    ROLE_KEYWORDS = re.compile(r'\b(Director|Gerente|Jefe|Profesor|Ingeniero|Dr\.|Coordinador|Analista|CEO|Manager|Socio|Founder|Cofounder|Lead|Senior|Junior|Architect|Consultant|Developer|Specialist|Asistente|Presidente|Oficial|Accountant|Sales)\b', re.I)
    Narrative_Phrases = re.compile(r'\b(soy|trabajo|mi nombre es|cargo es|pertenezco a)\b', re.I)

    def __init__(self):
        """Inicializa los motores de procesamiento de texto (spaCy) con manejo robusto de excepciones."""
        try:
            self.nlp_en = spacy.load("en_core_web_sm")
            self.nlp_es = spacy.load("es_core_news_sm")
        except OSError:
            logger.warning("Modelos de spaCy no encontrados. Se usará modo degradado (solo RegEx).")
            self.nlp_en = None
            self.nlp_es = None
        except Exception as e:
            logger.error(f"Error crítico al cargar modelos de lenguaje: {type(e).__name__}")
            self.nlp_en = None
            self.nlp_es = None

    @staticmethod
    def _is_invalid_name(text: str) -> bool:
        """
        Valida si un texto extraído cumple con las características de un nombre propio válido.
        
        Args:
            text (str): Texto candidato a nombre.
            
        Returns:
            bool: True si el texto NO es un nombre válido.
        """
        if not text or text == "N/A": return True
        text = text.strip()
        
        # Filtros de seguridad
        if '@' in text or 'http' in text.lower() or 'www.' in text.lower(): return True
        if SignatureExtractor.NAME_BLACKLIST.search(text): return True
        if SignatureExtractor.ORG_KEYWORDS.search(text): return True
        
        # Heurística de composición
        digit_count = sum(c.isdigit() for c in text)
        if digit_count > 3: return True
        
        word_count = len(text.split())
        # Un nombre válido suele tener entre 2 y 5 componentes y al menos 4 caracteres totales
        return word_count < 2 or word_count > 5 or len(text) < 4

    @staticmethod
    def from_ai(text_block: str, subject: str = "", images: List[Dict[str, str]] = None) -> Optional[str]:
        """
        Consulta al modelo de IA (Gemini) para extraer datos estructurados.
        Soporta entrada multimodal (Texto + Imágenes).

        Args:
            text_block (str): Bloque de texto de la firma.
            subject (str): Asunto del correo para contexto adicional.
            images (List[Dict[str, str]]): Lista de diccionarios con 'mime_type' y 'data' (base64).

        Returns:
            Optional[str]: String JSON con los datos extraídos, o None si falla.
        """
        if not text_block.strip() and not images: return None

        for _ in range(len(Config.GEMINI_API_KEYS)):
            api_key = Config.get_next_api_key()
            if not api_key:
                logger.error("Configuración de API insuficiente: No hay llaves disponibles.")
                return None
            
            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": api_key
            }
            
            prompt = (
                "Actúa como un experto en extracción de datos de contacto corporativos. "
                "Analiza el texto y las imágenes adjuntas de una firma de correo. "
                "Extrae con precisión: nombre completo, correo electrónico, puesto/cargo e institución/empresa. "
                "Responde EXCLUSIVAMENTE en formato JSON válido con las claves: nombre, correo, puesto, institucion. "
                "Si un dato no es visible ni en texto ni en imagen, usa 'N/A'. "
                f"Asunto del correo: {subject}\n"
                f"Texto extraído: {text_block}"
            )

            parts = [{"text": prompt}]
            if images:
                for img in images:
                    parts.append({
                        "inlineData": {
                            "mimeType": img["mime_type"],
                            "data": img["data"]
                        }
                    })

            payload = {
                "contents": [{"parts": parts}],
                "generationConfig": {
                    "response_mime_type": "application/json",
                    "temperature": 0.1
                }
            }
            
            try:
                response = requests.post(SignatureExtractor.API_URL, json=payload, headers=headers, timeout=20)
                
                if response.status_code == 429:
                    logger.warning("Cuota de API alcanzada (429). Rotando llave...")
                    time.sleep(1)
                    continue
                
                response.raise_for_status()
                data = response.json()
                
                if "candidates" in data and len(data["candidates"]) > 0:
                    return data["candidates"][0]["content"]["parts"][0].get("text").strip()
                
            except requests.exceptions.RequestException as e:
                logger.error(f"Error de red al consultar IA: {type(e).__name__}")
                continue
            except Exception as e:
                logger.error(f"Error inesperado en módulo IA: {type(e).__name__}")
                continue
        
        return None

    def heuristic_extraction(self, text: str, email_hint: str = "") -> Dict[str, str]:
        """
        Aplica reglas heurísticas y modelos NER (spaCy) para extracción local rápida.

        Args:
            text (str): Texto completo a analizar.
            email_hint (str): Correo previamente detectado para ayudar en la desambiguación.

        Returns:
            Dict[str, str]: Diccionario con las claves nombre, correo, institucion, puesto.
        """
        data = {"nombre": "N/A", "correo": "N/A", "institucion": "N/A", "puesto": "N/A"}
        
        if SignatureExtractor.Narrative_Phrases.search(text):
            return data 

        # Extracción de correo (RegEx)
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        data["correo"] = email_match.group(0) if email_match else email_hint
        
        # Procesamiento NLP (NER)
        if self.nlp_en and self.nlp_es:
            try:
                # Procesamos solo los primeros 2000 caracteres para eficiencia
                text_slice = text[:2000]
                doc_en = self.nlp_en(text_slice)
                doc_es = self.nlp_es(text_slice)

                # Priorización de entidades
                for ent in doc_en.ents:
                    if ent.label_ == "PERSON" and not self._is_invalid_name(ent.text):
                        data["nombre"] = ent.text
                        break
                if data["nombre"] == "N/A":
                    for ent in doc_es.ents:
                        if ent.label_ == "PER" and not self._is_invalid_name(ent.text):
                            data["nombre"] = ent.text
                            break

                for ent in doc_en.ents:
                    if ent.label_ == "ORG" and data["institucion"] == "N/A":
                        data["institucion"] = ent.text
                for ent in doc_es.ents:
                    if ent.label_ == "ORG" and data["institucion"] == "N/A":
                        data["institucion"] = ent.text
            except Exception as e:
                logger.warning(f"Fallo parcial en análisis NLP: {type(e).__name__}")

        # Refinamiento RegEx (Línea por línea)
        lines = [l.strip() for l in text.split('\n') if l.strip() and len(l.strip()) > 2]
        email_prefix = data["correo"].split('@')[0].lower() if data["correo"] != "N/A" else ""

        if data["nombre"] == "N/A":
            for line in lines[:3]: # Analizamos solo las primeras 3 líneas para el nombre
                if self._is_invalid_name(line): continue
                name_parts = re.findall(r'\w+', line.lower())
                matches_email = any(p in email_prefix for p in name_parts if len(p) > 3)
                if (1 < len(line.split()) <= 4 and not any(c.isdigit() for c in line)) or matches_email:
                    data["nombre"] = line
                    break

        for line in lines:
            if len(line.split()) > 8: continue 
            parts = re.split(r'[|,\-/]', line)
            for part in parts:
                p = part.strip()
                if data["puesto"] == "N/A" and SignatureExtractor.ROLE_KEYWORDS.search(p):
                    data["puesto"] = p
                elif data["institucion"] == "N/A" and SignatureExtractor.ORG_KEYWORDS.search(p):
                    data["institucion"] = p
        
        return data

    @staticmethod
    def _extract_from_vcard(msg: Any, final_data: Dict[str, str]) -> bool:
        """Intenta extraer datos desde adjuntos VCF. Retorna True si tiene éxito."""
        for att in msg.attachments:
            if att.filename.lower().endswith('.vcf'):
                try:
                    v = vobject.readOne(att.payload)
                    v_name = str(v.fn.value) if hasattr(v, 'fn') else "N/A"
                    if not SignatureExtractor._is_invalid_name(v_name):
                        final_data["nombre"] = v_name
                    
                    final_data["institucion"] = str(v.org.value[0]) if hasattr(v, 'org') else "N/A"
                    final_data["puesto"] = str(v.title.value) if hasattr(v, 'title') else "N/A"
                    return True
                except Exception:
                    continue
        return False

    @staticmethod
    def _extract_from_ocr(msg: Any) -> str:
        """
        Procesa adjuntos de imagen mediante OCR (Tesseract) con preprocesamiento OpenCV.
        """
        if not HAS_CV2:
            return "" # Retornar vacío si no hay OpenCV para preprocesar

        ocr_text = ""
        for att in msg.attachments:
            if att.content_type.startswith('image/') and att.size < 3000000: # Límite aumentado a 3MB
                try:
                    nparr = np.frombuffer(att.payload, np.uint8)
                    img_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

                    if img_cv is not None:
                        # Preprocesamiento: Grises + Umbral Adaptativo
                        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
                        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
                        
                        img = Image.fromarray(thresh)

                        # Re-escalado para mejorar legibilidad de fuentes pequeñas
                        if img.width < 1000:
                            scale = 2
                            img = img.resize((img.width * scale, img.height * scale), Image.Resampling.LANCZOS)
                        
                        # OCR Bilingüe
                        text = pytesseract.image_to_string(img, config=r'--oem 3 --psm 6 -l eng+spa')
                        if text.strip():
                            ocr_text += "\n" + text
                except Exception as e:
                    logger.warning(f"Error en OCR para adjunto {att.filename}: {type(e).__name__} - {e}")
                    logger.debug(f"OCR text (on error): '{ocr_text}'")
        return ocr_text

    @staticmethod
    def process_msg_object(msg: Any) -> Dict[str, str]:
        """
        Orquestador principal del proceso de extracción.
        
        Args:
            msg (imap_tools.MailMessage): Objeto de mensaje de correo.
            
        Returns:
            Dict[str, str]: Datos normalizados del contacto.
        """
        extractor = SignatureExtractor()
        h_name, h_email = parseaddr(msg.from_)
        final_data = {
            "nombre": "N/A", 
            "correo": sanitize_text_field(h_email, 1), 
            "institucion": "N/A", 
            "puesto": "N/A"
        }
        
        if h_name and not SignatureExtractor._is_invalid_name(h_name):
            final_data["nombre"] = sanitize_text_field(h_name, 4)

        # Fase 1: VCard (Estándar de Oro)
        if SignatureExtractor._extract_from_vcard(msg, final_data):
            # Si se encuentra VCard, confiamos en ella y retornamos
            return final_data

        # Fase 2: Texto + OCR
        full_text = msg.text or ""
        if not full_text and msg.html:
            try:
                full_text = BeautifulSoup(msg.html, "html.parser").get_text(separator='\n')
            except Exception:
                full_text = ""

        # Recolección de imágenes para posible análisis multimodal
        image_attachments = []
        for att in msg.attachments:
            if att.content_type.startswith('image/') and att.size < 3000000:
                try:
                    image_attachments.append({
                        "mime_type": att.content_type,
                        "data": base64.b64encode(att.payload).decode('utf-8')
                    })
                except Exception as e:
                    logger.warning(f"Error al codificar imagen {att.filename} para IA: {e}")

        ocr_content = SignatureExtractor._extract_from_ocr(msg)
        full_text += "\n" + ocr_content

        if full_text.strip():
            signature_block = ""
            # Segmentación inteligente de la firma
            if extractor.nlp_en and extractor.nlp_es:
                doc_en = extractor.nlp_en(full_text[:3000]) # Limitamos input NLP
                doc_es = extractor.nlp_es(full_text[:3000])

                # Detección de despedidas en Inglés
                for i, token in enumerate(doc_en):
                    if token.text.lower() in ["sincerely", "regards", "best", "thank"] and i + 1 < len(doc_en):
                        if token.text.lower() == "best" and doc_en[i+1].text.lower() != "regards": continue
                        signature_block = doc_en[i:].text
                        break
                
                # Detección de despedidas en Español
                if not signature_block:
                    for i, token in enumerate(doc_es):
                        if token.text.lower() in ["saludos", "atentamente", "cordialmente", "gracias"] and i + 1 < len(doc_es):
                            signature_block = doc_es[i:].text
                            break

            if not signature_block:
                parts = re.split(r'\n--\n|\n__+\n|\nCordialmente,|\nAtentamente,', full_text, flags=re.I)
                signature_block = parts[-1] if len(parts) > 1 else "\n".join(full_text.split('\n')[-15:])
            
            # Aplicación de Heurística
            h_data = extractor.heuristic_extraction(signature_block, email_hint=final_data["correo"])
            for k in ["nombre", "institucion", "puesto"]:
                if final_data[k] == "N/A":
                    val = sanitize_text_field(h_data[k])
                    if val != "N/A": final_data[k] = val

        # Fase 3: Refinamiento por IA (Obligatorio si hay imágenes o datos incompletos)
        should_use_ai = (
            "N/A" in [final_data["nombre"], final_data["institucion"], final_data["puesto"]] or 
            SignatureExtractor._is_invalid_name(final_data["nombre"]) or
            len(image_attachments) > 0  # <--- Seguridad: Si hay imagen, la IA verifica SIEMPRE
        )

        if should_use_ai:
            logger.info(f"Iniciando verificación por IA {'Multimodal' if image_attachments else 'de Texto'} para máxima precisión...")
            
            context_text = full_text if len(full_text) < 3000 else signature_block
            ai_res = SignatureExtractor.from_ai(
                context_text, 
                subject=getattr(msg, 'subject', ''),
                images=image_attachments
            )
            
            if ai_res:
                try:
                    ai_data = json.loads(ai_res)
                    for k in ["nombre", "institucion", "puesto", "correo"]:
                        new_val = sanitize_text_field(ai_data.get(k))
                        if new_val != "N/A":
                            final_data[k] = new_val
                except json.JSONDecodeError:
                    logger.error("Error al decodificar respuesta JSON de la IA.")
        else:
            logger.info("Extracción local exitosa (Heurística/NLP).")

        return final_data
