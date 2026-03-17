import time
import sys
from imap_tools import AND, MailBox, MailMessage
from typing import Any

from app.config import Config
from app.email_reader import EmailReader
from app.extractor import SignatureExtractor
from app.excel_manager import ExcelManager
from app.logger import logger

def process_single_email(msg: MailMessage, manager: ExcelManager) -> None:
    """
    Coordina el procesamiento de un correo electrónico individual:
    extracción, validación y almacenamiento.

    Args:
        msg (MailMessage): Objeto de mensaje recuperado vía IMAP.
        manager (ExcelManager): Instancia del gestor de persistencia.
    """
    try:
        # Por privacidad de datos: No se registra información sensible de remitentes en los logs.
        logger.info("Analizando nueva entrada de correo detectada...")
        
        # Extracción de metadatos de la firma
        contact_info = SignatureExtractor.process_msg_object(msg)
        
        # Validación de integridad: Solo guardamos si tenemos la información completa
        required_fields = ["nombre", "correo", "puesto", "institucion"]
        is_complete = all(contact_info.get(f) != "N/A" for f in required_fields)

        if is_complete:
            # Persistencia de datos en el gestor de Excel
            manager.save_contacts([contact_info])
            logger.info(f"Contacto de '{contact_info['correo']}' guardado correctamente.")
        else:
            missing = [f for f in required_fields if contact_info.get(f) == "N/A"]
            logger.warning(f"Contacto descartado por información incompleta ({', '.join(missing)}).")
        
        # Gestión de Rate Limit: Pausa prudencial para la API de IA
        time.sleep(5)
        
    except Exception as e:
        logger.error(f"Error durante el procesamiento del mensaje: {type(e).__name__}")

def main() -> None:
    """
    Punto de entrada principal del servicio de automatización.
    Inicializa los subsistemas y mantiene el ciclo de vida de conexión (Polling/IDLE).
    """
    logger.info("=== Iniciando Servicio de Automatización de Contactos (v2.1) ===")
    
    # Verificación de pre-requisitos de configuración
    if not Config.EMAIL_USER or not Config.EMAIL_PASS:
        logger.critical("Error de configuración: Faltan credenciales de acceso en el entorno (.env)")
        sys.exit(1)

    reader = EmailReader()
    manager = ExcelManager()

    while True:
        try:
            logger.info("Estableciendo conexión con el servidor de correo...")
            mailbox = reader.connect()
            
            # Procesamiento de la bandeja de entrada (correos no leídos)
            logger.info("Sincronizando mensajes pendientes...")
            try:
                for msg in mailbox.fetch(AND(seen=False), mark_seen=True):
                    process_single_email(msg, manager)
            except Exception as e:
                logger.error(f"Fallo en la sincronización inicial: {type(e).__name__}")

            # Modo de espera activa (IDLE) para procesamiento en tiempo real
            logger.info("Entrando en modo de escucha activa (IDLE)...")
            while True:
                try:
                    # Notificación del servidor sobre nuevos eventos
                    responses = mailbox.idle.wait(timeout=600)
                    
                    if responses:
                        logger.info("Evento de nuevo correo recibido.")
                        for msg in mailbox.fetch(AND(seen=False), mark_seen=True):
                            process_single_email(msg, manager)
                    
                except KeyboardInterrupt:
                    raise
                except Exception:
                    logger.warning("Conexión IDLE interrumpida. Reiniciando protocolo de escucha...")
                    break 

        except KeyboardInterrupt:
            logger.info("Cierre de servicio solicitado por el usuario.")
            try:
                reader.disconnect()
            except Exception: pass
            sys.exit(0)
            
        except Exception as e:
            logger.error(f"Error crítico en el servicio: {type(e).__name__}. Reintentando en 60s...")
            time.sleep(60)

if __name__ == "__main__":
    main()
