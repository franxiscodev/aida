# AIDA - Asistente Inteligente de Despacho Aduanero 🤖📦

AIDA es un sistema avanzado de validación de documentos DUA (Documento Único Administrativo) diseñado para asistir en el comercio exterior español. Utiliza una arquitectura hexagonal, OCR con Azure Document Intelligence, y capacidades RAG (Retrieval-Augmented Generation) con DuckDB y Gemini 1.5 Flash.

## 🚀 Funcionalidades Principales

- **Validación Automática de DUA**: Extracción de casillas mediante Azure OCR y validación técnica contra el Manual del Exportador.
- **Consultas Técnicas (RAG)**: Resolución de dudas sobre siglas (CUD, REOCE, SOIVRE, etc.) y requisitos por país.
- **Respuesta por Voz**: Generación de audio natural mediante Azure Text-to-Speech.
- **Integración con Dialogflow**: Webhook listo para ser consumido por un Voicebot o Chatbot.

## 🛠️ Tecnologías

- **Lenguaje**: Python 3.12+
- **Framework API**: FastAPI
- **Base de Datos Vectorial**: DuckDB
- **LLM**: Gemini 1.5 Flash (Google AI Generative Language)
- **Servicios Cloud**: Azure AI (Document Intelligence & Speech Services)
- **Gestión de Entorno**: `uv`

## 📋 Configuración

1. **Dependencias**:
   ```powershell
   uv sync
   ```

2. **Variables de Entorno**: Crea un archivo `.env` basado en `.env.example` con tus llaves de Azure y Google.

3. **Ingesta de Conocimiento**:
   ```powershell
   uv run python src/aida/infrastructure/database/ingest_manual.py
   ```

## 🏃 Ejecución

### 1. Iniciar el servidor API
```powershell
uv run uvicorn aida.infrastructure.api.main:app --reload
```
La documentación interactiva estará disponible en `http://127.0.0.1:8000/docs`.

### 2. Exponer el servidor (ngrok)
Para conectar con Dialogflow, utiliza el script de túnel:
```powershell
uv run python run_tunnel.py
```
Copia la URL generada (ej. `https://xxx.ngrok-free.app`) y configúrala como URL del Webhook en la consola de Dialogflow añadiendo `/webhook`.

## 🧪 Pruebas

- **Test Integral**: `uv run python tests/test_orchestrator.py`
- **Test de Voz**: `uv run python tests/test_voice.py`
- **Test de Webhook**: `uv run python tests/test_webhook_voice.py`

## 📦 Exportación del Proyecto
Para preparar la entrega limpia:
```powershell
uv run python export_project.py
```
