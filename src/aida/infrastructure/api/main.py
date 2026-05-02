from fastapi import FastAPI, Request
from dotenv import load_dotenv
import os

from aida.application.orchestrator import AidaOrchestrator

# Cargar variables de entorno al inicio
load_dotenv()

app = FastAPI(
    title="AIDA - Asistente Inteligente de Despacho Aduanero",
    description="API para la validación de documentos DUA usando RAG y el Manual del Exportador.",
    version="0.1.0"
)

# Inicializamos el orquestador en modo lectura para el Webhook
orchestrator = AidaOrchestrator(read_only=True)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "AIDA API",
        "version": "0.1.0"
    }

@app.post("/webhook")
async def dialogflow_webhook(request: Request):
    """
    Webhook para Dialogflow ES. Procesa intenciones de validación de documentos.
    """
    try:
        data = await request.json()
        query_result = data.get("queryResult", {})
        intent_name = query_result.get("intent", {}).get("displayName")
        parameters = query_result.get("parameters", {})
        
        # Log básico para depuración
        session = data.get("session", "unknown")
        print(f"Recibida intención '{intent_name}' para la sesión {session}")

        if intent_name == "validar_documento":
            # Si el usuario no proporciona una ruta, usamos el archivo de ejemplo por defecto
            file_path = parameters.get("file_path", "data/raw/ejemplo_dua_07.00.pdf")
            
            if not os.path.exists(file_path):
                return {
                    "fulfillmentText": f"Lo siento, no he podido encontrar el archivo en la ruta especificada."
                }

            # Ejecutamos la validación RAG
            report = orchestrator.validate_dua(file_path)
            
            if report.resultados:
                # Generamos una respuesta natural para voz
                num_hallazgos = len(report.resultados)
                first_result = report.resultados[0]
                
                respuesta_voz = (
                    f"He analizado el documento con éxito. He detectado {num_hallazgos} puntos "
                    f"técnicos que requieren su atención según el Manual del Exportador. "
                    f"Por ejemplo, en la {first_result.campo}, se ha identificado {first_result.mensaje[:150]}. "
                    f"¿Desea que le detalle algún otro punto o que genere el informe final?"
                )
            else:
                respuesta_voz = (
                    "He revisado el documento por completo y no he detectado ninguna sigla "
                    "técnica que requiera una validación especial según los criterios del Manual. "
                    "El documento parece estar en orden para su despacho."
                )

            return {
                "fulfillmentText": respuesta_voz
            }

        return {
            "fulfillmentText": f"He recibido la intención {intent_name}, pero aún estoy aprendiendo a gestionarla."
        }

    except Exception as e:
        print(f"Error en el Webhook: {str(e)}")
        return {
            "fulfillmentText": "Lo siento, he tenido un problema técnico al procesar su solicitud. Por favor, inténtelo de nuevo más tarde."
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
