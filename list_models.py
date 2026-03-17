import requests
import os
import json
from dotenv import load_dotenv

def list_available_models():
    """
    Utility script to list available Gemini models for the current API Key.
    Uses headers for secure API key transmission.
    """
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY_1") or os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("❌ CONFIGURATION ERROR: GEMINI_API_KEY not found in .env")
        return

    print("📡 Querying available models (v1beta API)...")
    url = "https://generativelanguage.googleapis.com/v1beta/models"
    headers = {"x-goog-api-key": api_key}

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        models = response.json().get('models', [])
        
        print(f"\n✅ Found {len(models)} models:")
        for model in models:
            name = model.get('name', 'Unknown')
            version = model.get('version', 'N/A')
            print(f" - {name} (Version: {version})")
            
        # Highlight Flash models
        flash_models = [m['name'] for m in models if 'flash' in m['name'].lower()]
        if flash_models:
            print(f"\n💡 Recommended model for this project: {flash_models[0]}")

    except Exception as e:
        print(f"\n❌ Error listing models: {type(e).__name__}")
        if 'response' in locals():
            print(f"Server response: {response.status_code}")

if __name__ == "__main__":
    list_available_models()
