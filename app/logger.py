import logging
import os
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv

load_dotenv()

# Configuración de variables de entorno para el logger
LOG_PATH = os.getenv("LOG_FILE", "logs/system.log")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
MAX_LOG_SIZE_MB = int(os.getenv("MAX_LOG_SIZE_MB", 5)) # Tamaño máximo en MB
BACKUP_COUNT = int(os.getenv("BACKUP_COUNT", 5)) # Número de archivos de backup

# Asegurar que el directorio de logs exista
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

def setup_logger():
    """
    Configura el motor de auditoría (logs) de la aplicación.
    Establece canales duales de salida: Consola y Archivo físico con rotación.
    Permite configurar el nivel de log.
    """
    # Crear un logger personalizado
    logger = logging.getLogger("email_automation")
    
    # Prevenir que los logs se propaguen al logger raíz duplicándose
    logger.propagate = False

    # Establecer el nivel de log
    try:
        logger.setLevel(LOG_LEVEL)
    except ValueError:
        logger.warning(f"Nivel de log '{LOG_LEVEL}' no válido. Usando INFO como predeterminado.")
        logger.setLevel(logging.INFO)

    # Formato del log
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Handler para la consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Handler para el archivo con rotación
    file_handler = RotatingFileHandler(
        LOG_PATH,
        maxBytes=MAX_LOG_SIZE_MB * 1024 * 1024, # Convertir MB a bytes
        backupCount=BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

logger = setup_logger()
