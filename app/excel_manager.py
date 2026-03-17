import pandas as pd
import os
from datetime import datetime
from typing import List, Dict, Any

from app.config import Config
from app.logger import logger

class ExcelManager:
    """
    Gestor de persistencia de datos en formato Microsoft Excel.
    Se encarga de la lectura, escritura y sincronización de contactos,
    garantizando la integridad de la información y evitando duplicados.
    """
    def __init__(self):
        """Inicializa la ruta del archivo y asegura la existencia del directorio base."""
        self.file_path: str = Config.DATA_FILE
        try:
            os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        except OSError as e:
            logger.error(f"Error al crear directorio de datos: {e}")

    def save_contacts(self, new_data_list: List[Dict[str, Any]]) -> None:
        """
        Registra una lista de nuevos contactos en el archivo maestro.
        
        Si el contacto ya existe (basado en el correo), actualiza los campos modificados.
        Mantiene un sello de tiempo de la última actualización.
        
        Args:
            new_data_list (List[Dict[str, Any]]): Lista de diccionarios con datos de contacto.
        """
        if not new_data_list:
            return

        try:
            # Estructura de columnas definida para el reporte final
            allowed_columns = ["institucion", "nombre", "puesto", "correo", "ultima_actualizacion"]
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Carga de base de datos existente o creación de una nueva
            if os.path.exists(self.file_path):
                df_existing = pd.read_excel(self.file_path)
                # Normalización de esquema
                for col in allowed_columns:
                    if col not in df_existing.columns:
                        df_existing[col] = "N/A"
                df_existing = df_existing[allowed_columns]
            else:
                df_existing = pd.DataFrame(columns=allowed_columns)

            for new_contact in new_data_list:
                email = str(new_contact.get("correo", "N/A"))
                if email == "N/A": continue

                # Verificación de existencia previa (Búsqueda por ID único: Correo)
                existing_idx = df_existing.index[df_existing['correo'] == email].tolist()

                if existing_idx:
                    idx = existing_idx[0]
                    # Lógica de actualización selectiva para no sobreescribir con datos vacíos
                    changed = False
                    for field in ["nombre", "puesto", "institucion"]:
                        new_val = str(new_contact.get(field, "N/A")).strip()
                        old_val = str(df_existing.at[idx, field]).strip()
                        if new_val != "N/A" and new_val != old_val:
                            df_existing.at[idx, field] = new_val
                            changed = True
                    
                    if changed:
                        df_existing.at[idx, "ultima_actualizacion"] = current_time
                        logger.info("Registro de contacto actualizado correctamente.")
                else:
                    # Inserción de nuevo registro
                    new_row = {
                        "nombre": str(new_contact.get("nombre", "N/A")),
                        "correo": email,
                        "institucion": str(new_contact.get("institucion", "N/A")),
                        "puesto": str(new_contact.get("puesto", "N/A")),
                        "ultima_actualizacion": current_time
                    }
                    df_existing = pd.concat([df_existing, pd.DataFrame([new_row])], ignore_index=True)
                    logger.info("Nuevo registro de contacto añadido a la base de datos.")

            # Organización alfabética por institución para facilitar la revisión manual
            df_existing = df_existing.sort_values(by='institucion', ascending=True)

            # Persistencia física en el sistema de archivos
            df_existing.to_excel(self.file_path, index=False)
            logger.info("Sincronización con archivo Excel finalizada con éxito.")
            
        except Exception as e:
            logger.error(f"Error en la gestión de persistencia Excel: {type(e).__name__}")
