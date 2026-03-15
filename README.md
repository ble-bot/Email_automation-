# Email Automation for Gmail (Termux)

Este proyecto automatiza la extracción de contactos desde las firmas de correos de Gmail (no leídos). Detecta texto y también imágenes (mediante OCR).

## Estructura
- `main.py`: Bucle principal de ejecución.
- `app/`: Lógica de extracción, IMAP y manejo de Excel.
- `data/`: Almacena `contactos.xlsx`.
- `logs/`: Historial de operaciones y errores.

## Configuración en Termux

1. **Instalar dependencias del sistema:**
   ```bash
   pkg update && pkg upgrade
   pkg install python tesseract libjpeg-turbo libpng pandas
   ```

2. **Instalar librerías de Python:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar Gmail:**
   - Activa la **Verificación en 2 pasos** en tu cuenta de Google.
   - Crea una **Contraseña de Aplicación** (App Password).
   - Edita el archivo `.env` con tus credenciales.

4. **Ejecutar:**
   ```bash
   python main.py
   ```

## Características
- **Detección Automática:** Revisa cada X segundos definidos en `.env`.
- **Extractor Inteligente:** Usa Regex para texto y Pytesseract para imágenes de firma.
- **Limpieza de Datos:** Elimina duplicados por email y ordena por institución.
- **Logs:** Registro detallado en `logs/system.log`.
