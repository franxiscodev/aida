from fastapi import FastAPI, HTTPException, Request
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import os
import re

from aida.application.orchestrator import AidaOrchestrator
from aida.infrastructure.adapters.azure_voice_adapter import AzureVoiceAdapter

# Cargar variables de entorno al inicio
load_dotenv()

# Modelos Pydantic para Dialogflow ES
class IntentModel(BaseModel):
    displayName: str

class QueryResultModel(BaseModel):
    queryText: str = ""
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
async def dialogflow_webhook(request: Request, payload: DialogflowRequest):
    """
    Webhook para Dialogflow ES. Procesa intenciones de validación de documentos.
    """
    try:
        # Log del JSON crudo para depuración profunda
        raw_data = await request.json()
        print("DEBUG RAW DATA:", raw_data)

        # Extraemos datos del modelo validado por Pydantic
        intent_name = payload.queryResult.intent.displayName
        parameters = payload.queryResult.parameters
        session_full = payload.session or "projects/aida/agent/sessions/session-id-local"
        
        # Log básico para depuración (Demo en vivo)
        session_id = session_full.split("/")[-1]
        print(f"Intent detectado: {intent_name}")
        print(f"Sesión: {session_id}")
        print(f"Body recibido: {payload}")

        respuesta_voz = ""

        if intent_name == "Validar DUA":
            # Si el usuario no proporciona una ruta, usamos el archivo de ejemplo por defecto
            file_path = parameters.get("file_path", "data/raw/ejemplo_dua_07.00.pdf")
            
            if not os.path.exists(file_path):
                respuesta_voz = "Lo siento, no he podido encontrar el archivo en la ruta especificada."
            else:
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

        elif intent_name in ["Consulta Sigla", "Requisitos Pais"]:
            query_text = payload.queryResult.queryText or "Consulta técnica"
            respuesta_voz = orchestrator.answer_general_question(query_text)

        elif intent_name == "Informar Código REOCE":
            codigo = str(parameters.get("CodigoAduanero", "")).strip()
            print(f"[DEBUG] Código Aduanero extraído: '{codigo}'")
            
            if not codigo:
                respuesta_voz = "Por favor, indícame el código REOCE que deseas consultar."
            # Validación de formato: 2 letras + 8 números
            elif not re.match(r"^[A-Z]{2}\d{8}$", codigo.upper()):
                respuesta_voz = "El código proporcionado no tiene un formato válido. Recuerda que debe empezar por dos letras seguidas de ocho dígitos. Por favor, compruébalo e inténtalo de nuevo."
                print(f"[DEBUG] Formato REOCE inválido: {codigo}")
            else:
                # Respuesta fija (Hardcoded) para asegurar 0 cortes y máxima velocidad
                respuesta_voz = f"He recibido tu código REOCE {codigo}. El formato es correcto para operar en aduanas. ¿Deseas consultar algo más del manual?"
                print(f"[DEBUG] Usando respuesta fija para REOCE: {codigo}")

        else:
            query_text = payload.queryResult.queryText or "Hola"
            respuesta_voz = orchestrator.answer_general_question(query_text)

        # Generar audio y persistencia si hay respuesta
        if respuesta_voz:
            print("-" * 30)
            print(f"RESPUESTA AIDA: {respuesta_voz}")
            print("-" * 30)

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_filename = f"response_{session_id}_{timestamp}.wav"
            text_filename = f"response_{session_id}_{timestamp}.txt"
            
            output_dir = "data/output"
            os.makedirs(output_dir, exist_ok=True)

            try:
                with open(os.path.join(output_dir, text_filename), "w", encoding="utf-8") as f:
                    f.write(respuesta_voz)
            except Exception as e:
                print(f"Error en persistencia de texto: {str(e)}")

            try:
                voice_adapter.speak(respuesta_voz, output_filename=audio_filename)
            except Exception as e:
                print(f"Error generando audio: {str(e)}")

        return {"fulfillmentText": respuesta_voz}

    except Exception as e:
        print(f"Error en el Webhook: {str(e)}")
        return {"fulfillmentText": "Lo siento, he tenido un problema técnico."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
