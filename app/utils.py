from typing import Optional, Union, Any

def sanitize_text_field(text: Union[str, Any], max_words: int = 6) -> str:
    """
    Limpia, normaliza y valida campos de texto extraídos para garantizar la integridad de los datos.
    
    Args:
        text (Union[str, Any]): El texto crudo a limpiar.
        max_words (int): Número máximo de palabras permitidas antes de considerar el dato inválido (ruido).

    Returns:
        str: El texto limpio y normalizado, o "N/A" si no es válido.
    """
    if not text or not isinstance(text, str):
        return "N/A"
    
    # Normalización básica: eliminar espacios extra y saltos de línea
    clean = text.strip().replace('\n', ' ').replace('\r', '')
    
    # Validación de contenido vacío o nulo explícito
    if not clean or clean.upper() in ["N/A", "NONE", "NULL", ""]:
        return "N/A"
        
    # Heurística de longitud: Si es demasiado largo, probablemente sea una oración y no un campo de datos
    if len(clean.split()) > max_words:
        return "N/A"
        
    return clean

def is_safe_filename(filename: str) -> bool:
    """
    Verifica si un nombre de archivo es seguro para procesar, evitando Path Traversal.
    
    Args:
        filename (str): Nombre del archivo.
        
    Returns:
        bool: True si es seguro, False si contiene caracteres sospechosos.
    """
    if not filename:
        return False
    return not (".." in filename or "/" in filename or "\\" in filename)
