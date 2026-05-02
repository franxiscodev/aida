from fastapi import FastAPI

app = FastAPI(
    title="AIDA - Asistente Inteligente de Despacho Aduanero",
    description="API para la validación de documentos DUA usando RAG y el Manual del Exportador.",
    version="0.1.0"
)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "AIDA API",
        "version": "0.1.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
