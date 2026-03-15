import logging
import os
from dotenv import load_dotenv

load_dotenv()

LOG_PATH = os.getenv("LOG_FILE", "logs/system.log")

# Asegurar que el directorio de logs exista
os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)

def setup_logger():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_PATH),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger("email_automation")

logger = setup_logger()
