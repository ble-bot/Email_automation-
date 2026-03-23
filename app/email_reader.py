from imap_tools import MailBox, AND
from app.config import Config
from app.logger import logger
from typing import Optional, List, Any

class EmailReader:
    """
    Controlador de acceso al servidor de correo electrónico mediante protocolo IMAP.
    Gestiona la conexión, autenticación y recuperación de mensajes no leídos.
    """
    def __init__(self):
        """Inicializa la instancia del lector de correo."""
        self.mailbox: Optional[MailBox] = None

    def connect(self) -> MailBox:
        """
        Establece una sesión segura con el servidor de correo.
        
        Returns:
            MailBox: Objeto de conexión autenticado para su uso en el bucle principal.
            
        Raises:
            Exception: Si falla la autenticación o conexión.
        """
        try:
            self.mailbox = MailBox(Config.IMAP_SERVER).login(
                Config.EMAIL_USER, Config.EMAIL_PASS, initial_folder='INBOX'
            )
            logger.info("Sesión IMAP iniciada correctamente.")
            return self.mailbox
        except Exception as e:
            logger.error(f"Fallo en la autenticación IMAP: {type(e).__name__}")
            raise

    def disconnect(self) -> None:
        """Finaliza la sesión de forma segura y libera los recursos del servidor."""
        if self.mailbox:
            try:
                self.mailbox.logout()
                logger.info("Sesión finalizada y recursos liberados.")
            except Exception as e:
                logger.warning(f"Error al desconectar del servidor IMAP: {type(e).__name__}")
