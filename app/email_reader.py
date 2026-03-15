from imap_tools import MailBox, AND
from app.config import Config
from app.logger import logger
import time

class EmailReader:
    def __init__(self):
        self.mailbox = None

    def connect(self):
        """Conecta y retorna el objeto mailbox."""
        try:
            self.mailbox = MailBox(Config.IMAP_SERVER).login(
                Config.EMAIL_USER, Config.EMAIL_PASS, initial_folder='INBOX'
            )
            logger.info("Conectado a Gmail exitosamente.")
            return self.mailbox
        except Exception as e:
            logger.error(f"Error al conectar a Gmail: {e}")
            raise

    def get_unread_emails(self):
        """Retorna una lista de objetos de correo (solo no leídos)."""
        try:
            # AND(seen=False) busca correos no leídos
            return list(self.mailbox.fetch(AND(seen=False)))
        except Exception as e:
            logger.error(f"Error al buscar correos: {e}")
            return []

    def disconnect(self):
        if self.mailbox:
            self.mailbox.logout()
            logger.info("Conexión cerrada.")
