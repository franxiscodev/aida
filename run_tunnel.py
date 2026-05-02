import sys
from pyngrok import ngrok
from dotenv import load_dotenv
import os

def run_tunnel(port=8000):
    """
    Inicia un túnel de ngrok para exponer el servidor local a Internet.
    Útil para pruebas con el Webhook de Dialogflow.
    """
    load_dotenv()
    
    # Si el usuario tiene un authtoken en el .env, lo configuramos
    auth_token = os.getenv("NGROK_AUTHTOKEN")
    if auth_token:
        ngrok.set_auth_token(auth_token)

    try:
        # Abrimos el túnel HTTP en el puerto especificado
        print(f"Intentando abrir túnel en el puerto {port}...")
        public_url = ngrok.connect(port).public_url
        
        print("\n" + "="*60)
        print("🚀 TÚNEL NGROK ACTIVO")
        print(f"🔗 URL Pública: {public_url}")
        print(f"🤖 Webhook para Dialogflow: {public_url}/webhook")
        print("="*60)
        print("\nManten esta ventana abierta para mantener el túnel activo.")
        print("Presiona Ctrl+C para terminar.\n")
        
        # Mantener el proceso activo
        ngrok_process = ngrok.get_ngrok_process()
        ngrok_process.proc.wait()
        
    except KeyboardInterrupt:
        print("\nCerrando túnel ngrok...")
        ngrok.kill()
    except Exception as e:
        print(f"\n[ERROR] No se pudo iniciar ngrok: {str(e)}")
        print("Asegúrate de tener ngrok configurado o un authtoken válido.")

if __name__ == "__main__":
    # Permitir cambiar el puerto vía argumentos si es necesario
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    run_tunnel(port)
