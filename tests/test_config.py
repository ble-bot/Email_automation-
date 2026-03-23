import os
import pytest
from unittest.mock import patch
from app.config import Config

@pytest.fixture(autouse=True)
def mock_load_dotenv():
    """
    Mockea load_dotenv para que los tests no lean el archivo .env real.
    """
    with patch('app.config.load_dotenv'):
        yield

@pytest.fixture(autouse=True)
def clean_environment():
    """
    Asegura un entorno limpio para cada test.
    """
    # Guardar original
    original_env = os.environ.copy()
    
    # Lista de variables proactivamente eliminadas
    vars_to_clear = [
        "EMAIL_USER", "EMAIL_PASS", "IMAP_SERVER", 
        "GEMINI_API_KEY", "API_RATE_LIMIT_SECONDS"
    ]
    for i in range(1, 6):
        vars_to_clear.append(f"GEMINI_API_KEY_{i}")
    
    for v in vars_to_clear:
        os.environ.pop(v, None)
    
    # Recargar Config con entorno limpio
    Config.load()
    
    yield
    
    # Restaurar original
    os.environ.clear()
    os.environ.update(original_env)
    Config.load()

def test_email_config_loading(monkeypatch):
    """Verifica la carga de credenciales de email."""
    monkeypatch.setenv("EMAIL_USER", "user@example.com")
    monkeypatch.setenv("EMAIL_PASS", "secret")
    Config.load()
    
    assert Config.EMAIL_USER == "user@example.com"
    assert Config.EMAIL_PASS == "secret"

def test_gemini_multiple_keys(monkeypatch):
    """Verifica la carga de múltiples llaves API."""
    monkeypatch.setenv("GEMINI_API_KEY_1", "key1")
    monkeypatch.setenv("GEMINI_API_KEY_2", "key2")
    monkeypatch.setenv("GEMINI_API_KEY_5", "key5")
    Config.load()
    
    assert Config.GEMINI_API_KEYS == ["key1", "key2", "key5"]

def test_gemini_fallback_key(monkeypatch):
    """Verifica el fallback a la llave única."""
    monkeypatch.setenv("GEMINI_API_KEY", "single_key")
    Config.load()
    
    assert Config.GEMINI_API_KEYS == ["single_key"]

def test_get_next_api_key_logic(monkeypatch):
    """Verifica el algoritmo round-robin."""
    monkeypatch.setenv("GEMINI_API_KEY_1", "A")
    monkeypatch.setenv("GEMINI_API_KEY_2", "B")
    Config.load()
    
    assert Config.get_next_api_key() == "A"
    assert Config.get_next_api_key() == "B"
    assert Config.get_next_api_key() == "A"

def test_empty_config_behavior():
    """Verifica comportamiento cuando no hay llaves."""
    Config.load()
    assert Config.GEMINI_API_KEYS == []
    assert Config.get_next_api_key() is None
