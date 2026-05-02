import sys
import os
from dotenv import load_dotenv

# Asegurar que el directorio src está en el PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from aida.infrastructure.adapters.azure_ocr_adapter import AzureOCRAdapter

def test_ocr_extraction():
    """
    Script de prueba para validar la conexión con Azure y la extracción de datos.
    """
    load_dotenv()
    
    endpoint = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
    key = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")
    
    if not endpoint or "your-resource" in endpoint or not key or "your-key" in key:
        print("\n[SKIP] Saltando test de OCR: Debes configurar las credenciales reales en el archivo .env")
        return

    adapter = AzureOCRAdapter()
    # Usamos el archivo de ejemplo proporcionado en la estructura
    file_path = "data/raw/ejemplo_dua_07.00.pdf"
    
    if not os.path.exists(file_path):
        print(f"\n[ERROR] No se encuentra el archivo de prueba en: {file_path}")
        return

    print(f"\n--- Iniciando análisis OCR de: {file_path} ---")
    try:
        entries = adapter.analyze_dua(file_path)
        print(f"✅ Éxito: Se han extraído {len(entries)} elementos del DUA.")
        
        print("\nPrimeros 5 elementos extraídos:")
        for entry in entries[:5]:
            print(f" - Casilla {entry.casilla}: {entry.valor}")
            
    except Exception as e:
        print(f"\n❌ Error durante el proceso de OCR: {str(e)}")

if __name__ == "__main__":
    test_ocr_extraction()
