import sys
import os
from dotenv import load_dotenv

# Añadir src al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from aida.infrastructure.adapters.azure_voice_adapter import AzureVoiceAdapter

def test_voice_synthesis():
    """
    Prueba básica de generación de audio a partir de texto.
    """
    load_dotenv()
    
    key = os.getenv("AZURE_SPEECH_KEY")
    if not key or "your-speech" in key:
        print("\n[SKIP] Saltando test de voz: Configura AZURE_SPEECH_KEY en .env")
        return

    print("\n--- Probando Azure Text-to-Speech ---")
    adapter = AzureVoiceAdapter()
    
    texto_prueba = (
        "Hola, soy AIDA, tu Asistente Inteligente de Despacho Aduanero. "
        "He revisado tu documento y todo parece estar en orden según el manual."
    )
    
    try:
        path = adapter.speak(texto_prueba)
        print(f"Prueba completada. Archivo generado en: {path}")
    except Exception as e:
        print(f"Error en el test de voz: {e}")

if __name__ == "__main__":
    test_voice_synthesis()
