import google.generativeai as genai
import os
from dotenv import load_dotenv

# Cargar .env
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("❌ ERROR: No se encontró GEMINI_API_KEY en el archivo .env")
    exit()

print(f"🔍 Probando API Key: {api_key[:6]}...{api_key[-4:]}")

genai.configure(api_key=api_key)

try:
    # Intentamos listar los modelos disponibles para ver si la clave tiene permisos
    print("📡 Verificando conexión con Google...")
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Responde 'OK' si recibes esto.")
    
    print("\n✅ ¡TODO FUNCIONA CORRECTAMENTE!")
    print(f"🤖 Respuesta de la IA: {response.text}")

except Exception as e:
    print("\n❌ SE DETECTÓ UN ERROR:")
    error_str = str(e)
    print(f"Detalle: {error_str}")
    
    if "400" in error_str:
        print("\n💡 POSIBLES SOLUCIONES PARA ERROR 400:")
        if "API_KEY_INVALID" in error_str:
            print("- La clave es incorrecta. Asegúrate de que no falte ninguna letra al final.")
        elif "USER_LOCATION_INSUFFICIENT" in error_str:
            print("- RESTRICCIÓN REGIONAL: Tu país/IP actual no tiene acceso a Gemini API. Prueba usando una VPN (EE.UU. o Europa).")
        else:
            print("- Verifica que hayas aceptado los términos de servicio en Google AI Studio (aistudio.google.com).")
            print("- Asegúrate de que el modelo 'gemini-1.5-flash' esté habilitado para tu clave.")
