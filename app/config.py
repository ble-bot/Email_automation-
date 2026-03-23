import os
import threading
from typing import List, Optional
from dotenv import load_dotenv

class Config:
    """
    Gestor centralizado de configuración de la aplicación.
    Carga variables de entorno y define parámetros operativos.
    """
    EMAIL_USER: Optional[str] = None
    EMAIL_PASS: Optional[str] = None
    IMAP_SERVER: str = "imap.gmail.com"
    CHECK_INTERVAL: int = 300
    DATA_FILE: str = "data/contactos.xlsx"
    LOG_FILE: str = "logs/system.log"
    API_RATE_LIMIT_SECONDS: int = 5
    GEMINI_API_KEYS: List[str] = []
    
    _current_key_index: int = 0
    _key_lock: threading.Lock = threading.Lock()

    @classmethod
    def load(cls):
        """
        Lee las variables de entorno y las asigna a los atributos de clase.
        Permite recargar la configuración dinámicamente.
        """
        # Intentamos cargar .env si existe, pero no bloqueamos si no.
        load_dotenv(override=True)
        
        cls.EMAIL_USER = os.getenv("EMAIL_USER")
        cls.EMAIL_PASS = os.getenv("EMAIL_PASS")
        cls.IMAP_SERVER = os.getenv("IMAP_SERVER", "imap.gmail.com")
        cls.CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 300))
        cls.DATA_FILE = os.getenv("DATA_FILE", "data/contactos.xlsx")
        cls.LOG_FILE = os.getenv("LOG_FILE", "logs/system.log")
        cls.API_RATE_LIMIT_SECONDS = int(os.getenv("API_RATE_LIMIT_SECONDS", 5))
        
        # Carga de llaves Gemini
        keys = []
        for i in range(1, 6):
            val = os.getenv(f"GEMINI_API_KEY_{i}")
            if val:
                keys.append(val.strip())
        
        if not keys:
            val = os.getenv("GEMINI_API_KEY")
            if val:
                keys = [val.strip()]
        
        cls.GEMINI_API_KEYS = keys
        cls._current_key_index = 0

    @classmethod
    def get_next_api_key(cls) -> Optional[str]:
        """
        Retorna la siguiente llave disponible (Round Robin).
        """
        with cls._key_lock:
            if not cls.GEMINI_API_KEYS:
                return None
            key = cls.GEMINI_API_KEYS[cls._current_key_index]
            cls._current_key_index = (cls._current_key_index + 1) % len(cls.GEMINI_API_KEYS)
            return key

# Carga inicial al importar el módulo
Config.load()
