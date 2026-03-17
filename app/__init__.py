# Email Contact Automation Service
# Copyright (c) 2026. All rights reserved.

"""
Módulo principal de la aplicación de automatización de contactos.
Expone los componentes clave para facilitar la importación.
"""

from .config import Config
from .email_reader import EmailReader
from .extractor import SignatureExtractor
from .excel_manager import ExcelManager
from .logger import logger

__version__ = "2.1.0"
__author__ = "Email Automation Team"
