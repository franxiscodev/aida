from fastapi import FastAPI, HTTPException, Request
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import os

from aida.application.orchestrator import AidaOrchestrator
from aida.infrastructure.adapters.azure_voice_adapter import AzureVoiceAdapter

# Cargar variables de entorno al inicio
load_dotenv()

# Modelos Pydantic para Dialogflow ES
class IntentModel(BaseModel):
    displayName: str

class QueryResultModel(BaseModel):
    intent: IntentModel
    parameters: Dict[str, Any] = Field(default_factory=dict)

class DialogflowRequest(BaseModel):
    """
    Modelo estructurado para las peticiones de Dialogflow ES.
    Esto permite que Swagger UI muestre un JSON editable.
    """
    queryResult: QueryResultModel
    session: Optional[str] = None

app = FastAPI(
    title="AIDA - Asistente Inteligente de Despacho Aduanero",
    description="API para la validación de documentos DUA usando RAG y el Manual del Exportador.",
    version="0.1.0",
    # El root_path es útil cuando se despliega detrás de proxies como ngrok
    root_path=os.getenv("ROOT_PATH", "")
)

# Inicializamos el orquestador y el adaptador de voz
orchestrator = AidaOrchestrator(read_only=True)
voice_adapter = AzureVoiceAdapter()

@app.middleware("http")
async def add_ngrok_skip_header(request: Request, call_next):
    """
    Añade un encabezado a todas las respuestas para saltar la advertencia de ngrok.
    Esto permite que Dialogflow consuma el webhook sin bloqueos.
    """
    response = await call_next(request)
    response.headers["ngrok-skip-browser-warning"] = "true"
    return response

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "AIDA API",
        "version": "0.1.0"
    }

@app.post("/webhook")
async def dialogflow_webhook(payload: DialogflowRequest):
    """
    Webhook para Dialogflow ES. Procesa intenciones de validación de documentos.
    """
    try:
        # Extraemos datos del modelo validado por Pydantic
        intent_name = payload.queryResult.intent.displayName
        parameters = payload.queryResult.parameters
        session_full = payload.session or "projects/aida/agent/sessions/session-id-local"
        
        # Log básico para depuración
        session_id = session_full.split("/")[-1]
        print(f"Procesando intención: {intent_name}")
        print(f"Sesión: {session_id}")

        respuesta_voz = ""

        if intent_name == "Validar DUA":
            # Si el usuario no proporciona una ruta, usamos el archivo de ejemplo por defecto
            file_path = parameters.get("file_path", "data/raw/ejemplo_dua_07.00.pdf")
            
            if not os.path.exists(file_path):
                respuesta_voz = "Lo siento, no he podido encontrar el archivo en la ruta especificada."
            else:
                # Ejecutamos la validación RAG
                report = orchestrator.validate_dua(file_path)
                
                if report.resultados:
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

        else:
            respuesta_voz = f"He recibido la intención {intent_name}, pero aún estoy aprendiendo a gestionarla."

        # Generar audio de la respuesta si el servicio de voz está configurado
        if respuesta_voz:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_filename = f"response_{session_id}_{timestamp}.wav"
            try:
                voice_adapter.speak(respuesta_voz, output_filename=audio_filename)
            except Exception as e:
                print(f"Error generando audio: {str(e)}")

        return {
            "fulfillmentText": respuesta_voz
        }

    except Exception as e:
        print(f"Error en el Webhook: {str(e)}")
        return {
            "fulfillmentText": "Lo siento, he tenido un problema técnico al procesar su solicitud. Por favor, inténtelo de nuevo más tarde."
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
