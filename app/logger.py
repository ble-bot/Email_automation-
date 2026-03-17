import logging
import os
from dotenv import load_dotenv

load_dotenv()

LOG_PATH = os.getenv("LOG_FILE", "logs/system.log")

# Asegurar que el directorio de logs exista
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

def setup_logger():
    """
    Configura el motor de auditoría (logs) de la aplicación.
    Establece canales duales de salida: Consola y Archivo físico.
    Incluye niveles de severidad y sellos de tiempo precisos.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_PATH, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("email_automation")

logger = setup_logger()
