# 📄 Informe de Entrega: Proyecto AIDA

**Asistente Inteligente de Despacho Aduanero**

Este documento detalla la estructura de intenciones configurada en Dialogflow ES y las instrucciones necesarias para la ejecución y evaluación del proyecto.

## 🎯 Tabla de Intenciones (10 Intents)

| # | Intención (Intent) | Funcionalidad | Capacidad Técnica |
| :--- | :--- | :--- | :--- |
| 1 | **Default Welcome Intent** | Saludo inicial y presentación de AIDA. | Conversacional |
| 2 | **Default Fallback Intent** | Captura consultas no entendidas y delega en Gemini. | LLM (Gemini) |
| 3 | **Validar DUA** | Procesa el PDF del DUA, extrae datos y valida contra el manual. | OCR + RAG + Audio |
| 4 | **Consulta Sigla** | Resuelve dudas sobre términos técnicos (CUD, REOCE, etc.). | RAG Directo + Audio |
| 5 | **Requisitos Pais** | Informa sobre requisitos de exportación a países específicos. | LLM (Gemini) + Audio |
| 6 | **Contacto Agente** | Explica cómo contactar con soporte técnico oficial. | LLM (Gemini) |
| 7 | **Funciones AIDA** | Explica qué tareas puede realizar el asistente. | LLM (Gemini) |
| 8 | **Documentacion General** | Lista los documentos básicos para exportar. | LLM (Gemini) |
| 9 | **Ayuda** | Ofrece guía sobre cómo usar el sistema de validación. | Conversacional |
| 10 | **Despedida** | Cierre de la sesión y finalización de la conversación. | Conversacional |

---

## 🚀 Instrucciones de Ejecución

Para poner en marcha el sistema AIDA y conectar el Webhook con Dialogflow, siga estos pasos:

### 1. Requisitos Previos
- Tener instalado el gestor de paquetes **`uv`**.
- Configurar el archivo **`.env`** con las credenciales de Azure (Speech y OCR) y Google AI (Gemini).

### 2. Iniciar el Servidor de Backend
Abra una terminal en la raíz del proyecto y ejecute:
```powershell
uv run uvicorn aida.infrastructure.api.main:app --reload
```
- La API estará escuchando en el puerto **8000**.
- Puede verificar el estado en: `http://127.0.0.1:8000/health`.

### 3. Exponer el Webhook (ngrok)
Abra una **segunda terminal** y ejecute el script de túnel:
```powershell
uv run python run_tunnel.py
```
- El script le proporcionará una **URL Pública** (ej: `https://abcd-123.ngrok-free.app`).
- Copie esa URL y añada `/webhook` al final.

### 4. Configurar Dialogflow
- En la consola de Dialogflow ES, vaya a la sección **Fulfillment**.
- Active el Webhook y pegue la URL completa (ej: `https://abcd-123.ngrok-free.app/webhook`).
- Asegúrese de que las intenciones tengan activada la opción *"Enable webhook call for this intent"*.

---

## 🛠️ Notas de Implementación
- El sistema utiliza **Arquitectura Hexagonal** para asegurar la mantenibilidad.
- Las respuestas de voz se generan dinámicamente y se almacenan en `data/output/`.
- El cerebro de AIDA utiliza el modelo **Gemini 1.5 Flash** para garantizar respuestas naturales y sin frases cortadas.
