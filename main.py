import time
import sys
from imap_tools import AND, MailBox
from app.config import Config
from app.email_reader import EmailReader
from app.extractor import SignatureExtractor
from app.excel_manager import ExcelManager
from app.logger import logger

def process_single_email(msg, manager):
    """Procesa un solo correo y lo guarda."""
    try:
        logger.info(f"Procesando correo de: {msg.from_} | Asunto: {msg.subject}")
        
        # Extraer info de la firma usando el método robusto
        contact_info = SignatureExtractor.process_msg_object(msg)
        
        if contact_info and contact_info["correo"] != "N/A":
            # Guardar en Excel
            manager.save_contacts([contact_info])
            logger.info(f"Guardado: {contact_info['nombre']} <{contact_info['correo']}>")
        else:
            logger.warning(f"No se pudo extraer información válida de {msg.from_}")
        
    except Exception as e:
        logger.error(f"Error procesando correo individual: {e}")

def main():
    logger.info("Iniciando Email Automation V2.0 (Detección Robusta)...")
    
    if not Config.EMAIL_USER or not Config.EMAIL_PASS:
        logger.error("Error: EMAIL_USER o EMAIL_PASS no configurados en .env")
        sys.exit(1)

    reader = EmailReader()
    manager = ExcelManager()

    while True:
        try:
            logger.info("Conectando a Gmail...")
            mailbox = reader.connect()
            
            # 1. Procesar pendientes
            logger.info("Revisando correos pendientes...")
            try:
                # Usar un generador para no cargar todo en memoria si hay miles
                for msg in mailbox.fetch(AND(seen=False), mark_seen=True):
                    process_single_email(msg, manager)
            except Exception as e:
                logger.error(f"Error al leer pendientes: {e}")

            # 2. Modo IDLE
            logger.info("Esperando nuevos correos (IDLE activo)...")
            while True:
                try:
                    # Esperar hasta 10 min (heartbeat)
                    responses = mailbox.idle.wait(timeout=600)
                    
                    if responses:
                        logger.info("¡Nuevo correo detectado!")
                        # Obtener solo los nuevos
                        for msg in mailbox.fetch(AND(seen=False), mark_seen=True):
                            process_single_email(msg, manager)
                    
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    logger.error(f"Error en ciclo IDLE: {e}. Reiniciando conexión...")
                    break # Romper loop interno para reconectar

        except KeyboardInterrupt:
            logger.info("Deteniendo servicio...")
            try:
                reader.disconnect()
            except: pass
            sys.exit(0)
            
        except Exception as e:
            logger.error(f"Error crítico de conexión: {e}. Reintentando en 60s...")
            time.sleep(60)

if __name__ == "__main__":
    main()
