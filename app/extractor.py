import re
import pytesseract
from PIL import Image
import io
import vobject
import json
import google.generativeai as genai
from bs4 import BeautifulSoup
from email.utils import parseaddr
from app.config import Config
from app.logger import logger

class SignatureExtractor:
    # Configurar el modelo solo si hay API Key
    if Config.GEMINI_API_KEY:
        genai.configure(api_key=Config.GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-1.5-flash") # Modelo rápido y potente
    else:
        model = None

    @staticmethod
    def _clean_field(text):
        if not text or not isinstance(text, str):
            return "N/A"
        return text.strip().replace('\n', ' ').replace('\r', '')

    @staticmethod
    def from_ai(text_block):
        """Usa Gemini para extraer datos de firmas desordenadas."""
        if not SignatureExtractor.model:
            return None
        
        prompt = f"""
        Extrae la siguiente información de contacto del bloque de texto (es una firma de correo).
        Devuelve el resultado ÚNICAMENTE en formato JSON plano, sin markdown, con estas claves:
        "nombre", "correo", "institucion", "puesto", "telefono", "web".
        Si no encuentras un dato, pon "N/A".
        
        Texto:
        \"\"\"{text_block}\"\"\"
        """
        
        try:
            response = SignatureExtractor.model.generate_content(prompt)
            # Limpiar posibles bloques markdown ```json ... ``` si la IA los pone
            clean_json = response.text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_json)
        except Exception as e:
            logger.error(f"Error en extracción por IA: {e}")
            return None

    @staticmethod
    def from_text(text):
        """Extrae info básica usando regex (Fallback)."""
        data = {"nombre": "N/A", "correo": "N/A", "institucion": "N/A", "puesto": "N/A", "telefono": "N/A", "web": "N/A"}
        
        email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        if email_match: data["correo"] = email_match.group(0)

        web_match = re.search(r'(https?://(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s]{2,})', text)
        if web_match: data["web"] = web_match.group(0)

        phone_match = re.search(r'(?:\+?(\d{1,3}))?[-. (]*(\d{3})[-. )]*(\d{3})[-. ]*(\d{4})', text)
        if phone_match: data["telefono"] = phone_match.group(0).strip()

        lines = [l.strip() for l in text.strip().split('\n') if l.strip()]
        for i, line in enumerate(lines):
            if data["correo"] in line and i > 0: data["nombre"] = lines[i-1]
            if re.search(r'\b(Universidad|Instituto|Hospital|Clinica|Corp|S\.?A\.?|S\.?L\.?|Inc\.?|Group|Org|Colegio)\b', line, re.I):
                data["institucion"] = line
            if re.search(r'\b(Director|Gerente|Jefe|Profesor|Ingeniero|Dr\.|Coordinador|Analista|CEO|Manager)\b', line, re.I):
                data["puesto"] = line
        return data

    @staticmethod
    def process_msg_object(msg):
        """
        Cadena de Procesamiento: VCard > Header > (IA o Regex/OCR)
        """
        final_data = {"nombre": "N/A", "correo": "N/A", "institucion": "N/A", "puesto": "N/A", "telefono": "N/A", "web": "N/A"}

        # 1. HEADER (Remitente básico)
        h_name, h_email = parseaddr(msg.from_)
        if h_email: final_data["correo"] = h_email
        if h_name: final_data["nombre"] = h_name

        # 2. VCARD
        for att in msg.attachments:
            if att.filename.lower().endswith('.vcf'):
                try:
                    vcard = vobject.readOne(att.payload)
                    if hasattr(vcard, 'fn'): final_data["nombre"] = str(vcard.fn.value)
                    if hasattr(vcard, 'email'): final_data["correo"] = str(vcard.email.value)
                    if hasattr(vcard, 'org'): final_data["institucion"] = str(vcard.org.value[0])
                    if hasattr(vcard, 'title'): final_data["puesto"] = str(vcard.title.value)
                    if hasattr(vcard, 'tel'): final_data["telefono"] = str(vcard.tel.value)
                    return final_data
                except: pass

        # 3. TEXTO (IA con fallback a Regex/OCR)
        body_text = msg.text or msg.html
        if body_text:
            soup = BeautifulSoup(body_text, "html.parser")
            clean_text = soup.get_text(separator='\n')
            
            # Cortar hilos de respuesta para no mezclar firmas ajenas
            lines = clean_text.split('\n')
            clean_lines = []
            for l in lines:
                if re.match(r'^On\s.*wrote:|^El\s.*escribió:|^\-\-$', l): break
                clean_lines.append(l)
            
            signature_block = "\n".join(clean_lines[-12:]) # Tomar bloque de firma probable
            
            # INTENTAR IA PRIMERO
            ai_data = SignatureExtractor.from_ai(signature_block)
            if ai_data:
                logger.info("Información extraída mediante IA exitosamente.")
                # Fusionar con los datos del header (email/nombre)
                for k, v in ai_data.items():
                    if v != "N/A": final_data[k] = v
            else:
                # FALLBACK A REGEX TRADICIONAL
                logger.warning("Fallo en IA o API Key faltante. Usando Regex tradicional.")
                text_data = SignatureExtractor.from_text(signature_block)
                for k, v in text_data.items():
                    if final_data[k] == "N/A" and v != "N/A": final_data[k] = v

        # 4. OCR (Para el logo de empresa o puestos en imagen)
        if (final_data["institucion"] == "N/A") and msg.attachments:
            for att in msg.attachments:
                if att.content_type.startswith('image/'):
                    try:
                        image = Image.open(io.BytesIO(att.payload))
                        ocr_text = pytesseract.image_to_string(image)
                        # Re-enviar texto OCR a la IA para mejor análisis si es posible
                        ocr_data = SignatureExtractor.from_ai(ocr_text) if Config.GEMINI_API_KEY else SignatureExtractor.from_text(ocr_text)
                        if ocr_data:
                            for k, v in ocr_data.items():
                                if final_data[k] == "N/A" and v != "N/A": final_data[k] = v
                    except: pass

        # Limpieza final
        for k, v in final_data.items():
            final_data[k] = SignatureExtractor._clean_field(v)

        return final_data
