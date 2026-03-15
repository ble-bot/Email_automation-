import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    EMAIL_USER = os.getenv("EMAIL_USER")
    EMAIL_PASS = os.getenv("EMAIL_PASS")
    IMAP_SERVER = os.getenv("IMAP_SERVER", "imap.gmail.com")
    CHECK_INTERVAL = int(os.getenv("CHECK_INTERVAL", 300))
    DATA_FILE = os.getenv("DATA_FILE", "data/contactos.xlsx")
    LOG_FILE = os.getenv("LOG_FILE", "logs/system.log")
    
    # AI Config
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
