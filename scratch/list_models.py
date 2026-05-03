import google.generativeai as genai
import os
from dotenv import load_dotenv

def list_available_models():
    load_dotenv()
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY no encontrada.")
        return

    genai.configure(api_key=api_key)
    
    print("--- Modelos Disponibles ---")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"ID: {m.name} | Display Name: {m.display_name}")
    except Exception as e:
        print(f"Error al listar modelos: {e}")

if __name__ == "__main__":
    list_available_models()
