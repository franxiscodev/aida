import httpx
import json

def test_webhook_voice():
    url = "http://127.0.0.1:8000/webhook"
    
    payload = {
        "queryResult": {
            "intent": {
                "displayName": "validar_documento"
            },
            "parameters": {
                "file_path": "data/raw/ejemplo_dua_07.00.pdf"
            }
        },
        "session": "projects/test/agent/sessions/session123"
    }
    
    print("\n--- Enviando peticion simulada de Dialogflow al Webhook ---")
    try:
        response = httpx.post(url, json=payload, timeout=60.0)
        print(f"Status: {response.status_code}")
        print(f"Respuesta JSON: {response.json()}")
        
        # Verificar si el archivo de audio se creó
        audio_path = "data/output/response_session123.wav"
        import os
        if os.path.exists(audio_path):
            print(f"✅ EXITO: El archivo de audio se ha generado en {audio_path}")
        else:
            print(f"❌ ERROR: El archivo de audio NO se encuentra en {audio_path}")
            
    except Exception as e:
        print(f"Error en el test manual: {e}")

if __name__ == "__main__":
    test_webhook_voice()
