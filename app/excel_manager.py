import pandas as pd
import os
from app.config import Config
from app.logger import logger

class ExcelManager:
    def __init__(self):
        self.file_path = Config.DATA_FILE
        # Asegurar directorio
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)

    def save_contacts(self, new_data_list):
        """
        Guarda una lista de diccionarios en Excel, evitando duplicados y ordenando.
        """
        if not new_data_list:
            return

        try:
            # Crear DataFrame con nuevos datos y columnas aseguradas
            df_new = pd.DataFrame(new_data_list)
            
            # Asegurar que existan todas las columnas clave aunque vengan vacías
            expected_columns = ["nombre", "correo", "institucion", "puesto", "telefono", "web"]
            for col in expected_columns:
                if col not in df_new.columns:
                    df_new[col] = "N/A"

            # Cargar datos existentes si el archivo ya existe
            if os.path.exists(self.file_path):
                try:
                    df_existing = pd.read_excel(self.file_path)
                    # Normalizar columnas del excel existente (por si es versión vieja)
                    for col in expected_columns:
                        if col not in df_existing.columns:
                            df_existing[col] = "N/A"
                            
                    df_combined = pd.concat([df_existing, df_new], ignore_index=True)
                except Exception:
                    # Si el archivo está corrupto o ilegible, empezar de cero (haciendo backup)
                    logger.warning("Archivo Excel corrupto o incompatible. Creando uno nuevo y respaldando el anterior.")
                    os.rename(self.file_path, self.file_path + ".bak")
                    df_combined = df_new
            else:
                df_combined = df_new

            # Limpiar duplicados manteniendo el último
            df_combined = df_combined.drop_duplicates(subset=['correo'], keep='last')
            
            # Ordenar
            if 'institucion' in df_combined.columns:
                df_combined = df_combined.sort_values(by='institucion', ascending=True)

            # Reordenar columnas para que queden bonitas
            final_columns = [c for c in expected_columns if c in df_combined.columns] + \
                            [c for c in df_combined.columns if c not in expected_columns]
            df_combined = df_combined[final_columns]

            # Guardar
            df_combined.to_excel(self.file_path, index=False)
            logger.info(f"Datos guardados exitosamente en {self.file_path}")
            
        except Exception as e:
            logger.error(f"Error al guardar en Excel: {e}")
