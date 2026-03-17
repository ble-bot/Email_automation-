import os
import threading
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

class Config:
    """
    Gestor centralizado de configuración de la aplicación.
    Carga variables de entorno y define parámetros operativos predeterminados.
    """
    # Credenciales de acceso al correo
    EMAIL_USER: Optional[str] = os.getenv("EMAIL_USER")
    EMAIL_PASS: Optional[str] = os.getenv("EMAIL_PASS")
    
    # Parámetros del servidor IMAP
    IMAP_SERVER: str = os.getenv("IMAP_SERVER", "imap.gmail.com")
    
    # Frecuencia de sincronización y rutas de archivos
    CHECK_INTERVAL: int = int(os.getenv("CHECK_INTERVAL", 300))
    DATA_FILE: str = os.getenv("DATA_FILE", "data/contactos.xlsx")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/system.log")
    
    # Configuración de Inteligencia Artificial (Gemini)
    # Permite múltiples llaves para balanceo de carga y rebasamiento de límites
    GEMINI_API_KEYS: List[str] = [
        key for key in (os.getenv(f"GEMINI_API_KEY_{i}") for i in range(1, 6)) if key
    ]
    
    if not GEMINI_API_KEYS:
        # Compatibilidad con llave única (retrocompatibilidad)
        single_key = os.getenv("GEMINI_API_KEY")
        if single_key:
            GEMINI_API_KEYS = [single_key]

    _current_key_index: int = 0
    _key_lock: threading.Lock = threading.Lock()

    @classmethod
    def get_next_api_key(cls) -> Optional[str]:
        """
        Implementa un algoritmo Round Robin para distribuir las peticiones
        entre todas las llaves de API configuradas. Hilo seguro.
        
        Returns:
            Optional[str]: La siguiente API Key disponible, o None si no hay.
        """
        with cls._key_lock:
            if not cls.GEMINI_API_KEYS:
                return None
            key = cls.GEMINI_API_KEYS[cls._current_key_index]
            cls._current_key_index = (cls._current_key_index + 1) % len(cls.GEMINI_API_KEYS)
            return key

