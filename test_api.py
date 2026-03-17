import requests
import os
import json
from dotenv import load_dotenv

def test_gemini_api():
    """
    Test script to verify connectivity and API Key validity with Gemini.
    Follows security best practices by sending key in headers.
    """
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY_1") or os.getenv("GEMINI_API_KEY")

    if not api_key:
        print("❌ CONFIGURATION ERROR: GEMINI_API_KEY_1 or GEMINI_API_KEY not found in .env")
        return

    # Recommended model for content generation
    model_to_try = "gemini-1.5-flash" 
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_to_try}:generateContent"
    
    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
    }
    
    payload = {
        "contents": [{
            "parts": [{"text": "Hello, respond with 'OK' if you can read this."}]
        }]
    }

    try:
        print(f"📡 Testing connection with model: {model_to_try}...")
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        # Fallback if specific model is not available
        if response.status_code in [404, 429]:
            print(f"⚠️ {model_to_try} failed (Code {response.status_code}), trying 'gemini-flash-latest'...")
            model_to_try = "gemini-flash-latest"
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_to_try}:generateContent"
            response = requests.post(url, json=payload, headers=headers, timeout=10)

        response.raise_for_status()
        data = response.json()
        
        if "candidates" in data and len(data["candidates"]) > 0:
            content_text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
            print(f"\n✅ CONNECTION SUCCESSFUL with {model_to_try}!")
            print(f"🤖 Response: {content_text}")
        else:
            print("\n⚠️ Unexpected API response format.")

    except Exception as e:
        print(f"\n❌ CRITICAL ERROR: {type(e).__name__}")
        if 'response' in locals():
            print(f"Server detail: {response.status_code}")

if __name__ == "__main__":
    test_gemini_api()
