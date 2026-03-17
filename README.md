# Email Contact Extraction Service v2.1

Solución automatizada para la extracción, procesamiento y almacenamiento de datos de contacto derivados de firmas de correos electrónicos. Diseñado para ejecutarse en entornos de servidor o dispositivos móviles mediante Termux.

## 📋 Descripción Técnica
El sistema implementa un pipeline de procesamiento asíncrono que monitorea una bandeja de entrada IMAP en tiempo real. Utiliza una arquitectura de tres capas para la extracción de datos:
1. **Capa Heurística:** Procesamiento rápido mediante expresiones regulares y validación de patrones.
2. **Capa NLP (Natural Language Processing):** Análisis semántico utilizando modelos de `spaCy` para identificar entidades (Personas y Organizaciones).
3. **Capa de Visión (OCR):** Extracción de texto en firmas incrustadas en imágenes mediante `OpenCV` y `Tesseract`.
4. **Capa de Refinamiento (IA):** Validación semántica mediante el modelo Gemini Flash para garantizar la integridad de los datos estructurados.

## 🛠️ Requisitos del Sistema
- **Python:** 3.9 o superior.
- **Tesseract OCR:** Instalado en el sistema para el procesamiento de imágenes.
- **Acceso IMAP:** Cuenta de correo con permisos de "Contraseñas de Aplicación" activos.

## 🚀 Guía de Instalación Rápida

### 1. Preparación del Entorno (Termux)
Si utiliza Termux, ejecute el siguiente comando para instalar las dependencias base:
```bash
pkg update && pkg upgrade
pkg install python tesseract libjpeg-turbo libpng pandas opencv-python
```

### 2. Instalación de Dependencias Python
Instale los módulos necesarios y los modelos de lenguaje:
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
python -m spacy download es_core_news_sm
```

### 3. Configuración de Variables (.env)
Cree un archivo llamado `.env` en la raíz del proyecto con la siguiente estructura:
```env
EMAIL_USER="tu_usuario@gmail.com"
EMAIL_PASS="tu_contraseña_de_aplicación"
GEMINI_API_KEY_1="tu_llave_api_principal"
# Opcional: llaves adicionales para balanceo de carga
# GEMINI_API_KEY_2="..."
```

## ⚙️ Uso
Para iniciar el servicio en modo de escucha activa (IDLE):
```bash
python main.py
```
El sistema procesará automáticamente los correos no leídos y se mantendrá a la espera de nuevas entradas en tiempo real. Los resultados se sincronizarán en `data/contactos.xlsx`.

## 📁 Estructura de Salida
- **Excel:** Ubicado en `data/contactos.xlsx`. Organizado alfabéticamente por institución.
- **Logs:** Historial técnico disponible en `logs/system.log` (anonimizado para privacidad).
