import pandas as pd
import os

file_path = "data/contactos.xlsx"

if os.path.exists(file_path):
    df = pd.read_excel(file_path)
    if not df.empty:
        print("Contenido del archivo Excel (columnas clave):")
        # Asegurarse de que las columnas existen antes de intentar acceder a ellas
        display_columns = ["institucion", "nombre", "puesto", "correo", "ultima_actualizacion"]
        actual_columns = [col for col in display_columns if col in df.columns]
        print(df[actual_columns].to_string(index=False))
    else:
        print(f"El archivo '{file_path}' está vacío.")
else:
    print(f"El archivo '{file_path}' no existe.")
