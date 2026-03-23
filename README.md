# 📧 Servicio de Automatización de Extracción de Contactos por Correo Electrónico

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)
![IMAP](https://img.shields.io/badge/Protocol-IMAP-lightgrey?style=for-the-badge)
![NLP](https://img.shields.io/badge/Tech-NLP-green?style=for-the-badge)
![OCR](https://img.shields.io/badge/Tech-OCR-orange?style=for-the-badge)
![AI](https://img.shields.io/badge/AI-Gemini%20Flash-purple?style=for-the-badge)
![Excel](https://img.shields.io/badge/Data-Excel-darkgreen?style=for-the-badge&logo=microsoft-excel)

---

## 🎯 Propósito del Proyecto

El **"Servicio de Extracción de Contactos por Correo Electrónico"** es una solución automatizada diseñada para **extraer, procesar y almacenar datos de contacto (nombres, cargos, empresas, emails, etc.) directamente desde las firmas de correo electrónico**.

En muchas organizaciones, la información de contacto llega a través de emails y a menudo se pierde o requiere entrada manual. Este servicio resuelve ese problema automatizando la captura de datos críticos, mejorando la eficiencia y la calidad de la información de contacto disponible.

## ✨ Características Principales

*   **Monitoreo en Tiempo Real:** Conexión y monitoreo continuo de bandejas de entrada IMAP para correos nuevos o no leídos.
*   **Extracción Multi-Capa:**
    *   **Heurística:** Identificación rápida de patrones de contacto comunes (regex).
    *   **Procesamiento del Lenguaje Natural (NLP):** Análisis semántico con `spaCy` para entidades como nombres, organizaciones y cargos.
    *   **Visión por Computadora (OCR):** Extracción de texto de firmas en imágenes (`OpenCV` + `Tesseract`).
    *   **Refinamiento con IA:** Validación semántica y mejora de la calidad de los datos con `Gemini Flash`.
*   **Persistencia de Datos:** Almacenamiento organizado de contactos extraídos en un archivo `Excel` (`data/contactos.xlsx`).
*   **Gestión de Logs:** Registro detallado de eventos y operaciones del sistema (`logs/system.log`) con anonimización de datos sensibles.

## 🚀 ¿Cómo Funciona? (Arquitectura y Flujo de Trabajo)

El sistema opera como un **pipeline de procesamiento asíncrono** con una arquitectura de tres capas principales (más una de refinamiento) que trabajan en conjunto:

1.  **Monitoreo IMAP en Tiempo Real:** El servicio se conecta a una bandeja de entrada de correo electrónico y monitorea en tiempo real los correos nuevos o no leídos.
2.  **Procesamiento Multi-Capa para la Extracción de Datos:**
    *   **Capa Heurística:** Identifica rápidamente información de contacto común utilizando expresiones regulares.
    *   **Capa NLP:** Analiza el texto para entender su significado y contexto, identificando entidades (Nombres, Organizaciones, etc.) con `spaCy`.
    *   **Capa Visión por Computadora (OCR):** Si la firma es una imagen, "lee" el texto dentro de ella utilizando `OpenCV` y `Tesseract`.
    *   **Capa de Refinamiento con IA:** Utiliza el modelo `Gemini Flash` para validar semánticamente y asegurar la calidad de los datos finales.
3.  **Salida y Almacenamiento:** Los contactos validados se guardan en un archivo **Excel (`data/contactos.xlsx`)**, organizado alfabéticamente por institución.

## 🛠️ Tecnologías Clave Utilizadas

*   **Python 3.9+**: Lenguaje de programación principal.
*   **IMAP**: Protocolo para lectura y monitoreo de correos.
*   **spaCy**: Librería de NLP para análisis semántico.
*   **OpenCV**: Librería de visión por computadora para procesamiento de imágenes.
*   **Tesseract OCR**: Motor de reconocimiento óptico de caracteres.
*   **API de Gemini Flash**: Modelo de IA para validación y refinamiento de datos.
*   **Pandas**: Librería para manejo eficiente de datos (Excel).
*   **Requests**: Para peticiones HTTP a APIs.
*   **BeautifulSoup4/lxml**: Para parsing HTML/XML (contenido de correo).
*   **python-dotenv**: Gestión de variables de entorno.
*   **vobject**: Para parsing de datos tipo vCard.

## 📦 Componentes del Proyecto (Estructura de Archivos)

```
email_automation/
├── .env.example              # Plantilla para variables de entorno
├── .gitignore                # Archivos y directorios a ignorar por Git
├── list_models.py            # Script para listar modelos de IA/NLP
├── main.py                   # Punto de entrada principal del servicio
├── project_documentation.txt # Documentación detallada del proyecto (referencia)
├── README.md                 # Este archivo
├── requirements.txt          # Dependencias de Python
├── test_api.py               # Pruebas para la integración con APIs
├── app/
│   ├── __init__.py           # Marca el directorio como un paquete Python
│   ├── config.py             # Configuración de la aplicación (lee .env)
│   ├── email_reader.py       # Lógica para leer y monitorear correos IMAP
│   ├── excel_manager.py      # Gestión del archivo de contactos Excel
│   ├── extractor.py          # Lógica multi-capa de extracción de datos
│   ├── logger.py             # Configuración y manejo de logs
│   ├── utils.py              # Funciones de utilidad varias
│   └── __pycache__/          # Archivos compilados de Python
├── data/                     # Directorio para archivos de datos (e.g., contactos.xlsx)
└── logs/                     # Directorio para archivos de log (e.g., system.log)
```

## ⚙️ Instalación y Configuración

Sigue estos pasos para poner en marcha el servicio en tu sistema operativo:

### 📥 Prerrequisitos

Asegúrate de tener instalado:
*   **Python 3.9+**
*   **Git** (opcional, para clonar el repositorio)

### 💻 Pasos de Instalación

1.  **Clonar el Repositorio (si aún no lo has hecho):**
    ```bash
    git clone git@github.com:ble-bot/Email_automation-.git
    cd Email_automation-
    ```

2.  **Instalación de Dependencias del Sistema Operativo:**

    #### 🐧 Linux (Debian/Ubuntu-like)
    ```bash
    sudo apt update
    sudo apt install python3-pip tesseract-ocr libtesseract-dev libleptonica-dev libjpeg-dev libpng-dev libtiff-dev -y
    # Para OpenCV, a veces es necesario instalar cabeceras adicionales si se compila
    # sudo apt install libopencv-dev python3-opencv
    ```
    *Nota: `python3-opencv` puede instalar su propia versión de OpenCV. Si encuentras problemas, puedes optar por instalar `opencv-python` vía `pip` y asegurarte de tener las librerías del sistema necesarias.*

    #### 윈도우 🪟 Windows
    *   **Python:** Instala Python desde [python.org](https://www.python.org/downloads/windows/). Asegúrate de añadir Python al PATH durante la instalación.
    *   **Tesseract OCR:** Descarga e instala Tesseract OCR desde [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki). Asegúrate de añadir el directorio de instalación de Tesseract al PATH de tu sistema.
    *   **OpenCV:** Las dependencias de `opencv-python` generalmente se manejan a través de `pip`.

    #### 🍎 macOS
    ```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    brew install python tesseract
    # OpenCV suele instalarse bien con pip, pero si hay problemas, puedes intentar:
    # brew install opencv
    ```

3.  **Configurar Entorno Virtual (Recomendado):**
    ```bash
    python3 -m venv venv
    source venv/bin/activate   # En Linux/macOS
    # .\venv\Scripts\activate   # En Windows (PowerShell)
    # venv\Scripts\activate.bat # En Windows (CMD)
    ```

4.  **Instalar Dependencias de Python:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Descargar Modelos de `spaCy`:**
    ```bash
    python -m spacy download en_core_web_sm
    python -m spacy download es_core_news_sm
    ```

6.  **Configurar Credenciales y APIs:**
    *   Crea una copia del archivo `.env.example` y nómbrala `.env` en la raíz del proyecto.
    *   Edita el archivo `.env` y rellena tus credenciales. **Es CRÍTICO usar una contraseña de aplicación para el email, no tu contraseña principal.**
    ```env
    EMAIL_USER="tu_usuario@ejemplo.com"
    EMAIL_PASS="tu_contraseña_de_aplicación" # ¡IMPORTANTE! Genera una contraseña de app.
    GEMINI_API_KEY_1="tu_llave_api_principal_de_gemini"
    ```
    *   Para `GEMINI_API_KEY_1`, puedes obtener una clave API de Google AI Studio o Google Cloud Platform.

### ▶️ Ejecución del Servicio

Una vez configurado, inicia el servicio:
```bash
python main.py
```
El servicio se conectará a tu servidor de correo y comenzará a monitorear y procesar emails en tiempo real. Presiona `Ctrl+C` para detener el servicio.

## 📊 Valor y Beneficios del Proyecto

*   **Automatización Completa:** Elimina la necesidad de entrada manual de datos de contacto de correos, ahorrando tiempo y reduciendo errores.
*   **Alta Eficiencia:** Procesa grandes volúmenes de correos de forma rápida y continua, ideal para campañas o flujos de trabajo con alto volumen.
*   **Precisión Mejorada:** Utiliza una combinación de heurística, NLP, OCR y IA avanzada (Gemini Flash) para asegurar la alta calidad y coherencia de los datos extraídos.
*   **Datos Estructurados al Instante:** Transforma información desorganizada y semi-estructurada (firmas de correo) en un formato útil y estandarizado (Excel).
*   **Base de Datos Dinámica:** Mantiene una base de datos de contactos actualizada y centralizada, accesible y fácil de integrar con otras herramientas.
*   **Auditabilidad y Depuración:** Los logs detallados permiten rastrear la actividad del sistema, solucionar problemas y garantizar la privacidad de la información.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Si deseas mejorar este proyecto:
1.  Haz un "fork" del repositorio.
2.  Crea una nueva rama (`git checkout -b feature/AmazingFeature`).
3.  Realiza tus cambios y asegúrate de que el código pasa las pruebas.
4.  Haz "commit" de tus cambios (`git commit -m 'Add some AmazingFeature'`).
5.  Haz "push" a la rama (`git push origin feature/AmazingFeature`).
6.  Abre un "Pull Request".

## 📄 Licencia

Distribuido bajo la Licencia MIT. Consulta `LICENSE` para más información.

---

_Desarrollado con ❤️ y 🤖 por Beley Gomez U._
