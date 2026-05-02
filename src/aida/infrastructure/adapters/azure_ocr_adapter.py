import os
from typing import List
from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv
from aida.domain.models import DuaEntry

load_dotenv()

class AzureOCRAdapter:
    """
    Adaptador para extraer información de documentos DUA usando Azure Document Intelligence.
    """
    def __init__(self):
        self.endpoint = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
        self.key = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_KEY")
        
        if not self.endpoint or not self.key or "your-key" in self.key:
            # No lanzamos excepción aquí para permitir que la app cargue, 
            # pero el método analyze_dua fallará si no están configuradas.
            self.client = None
        else:
            self.client = DocumentAnalysisClient(
                endpoint=self.endpoint, 
                credential=AzureKeyCredential(self.key)
            )

    def analyze_dua(self, file_path: str) -> List[DuaEntry]:
        """
        Analiza un archivo PDF/Imagen de un DUA y devuelve una lista de DuaEntry.
        """
        if self.client is None:
            raise ValueError("Azure Document Intelligence no está configurado. Revisa el archivo .env")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Archivo no encontrado: {file_path}")

        with open(file_path, "rb") as f:
            # Usamos el modelo 'prebuilt-layout' que es excelente para documentos con tablas y formularios
            poller = self.client.begin_analyze_document("prebuilt-layout", document=f)
            result = poller.result()

        entries = []
        
        # Procesamos las líneas de texto extraídas
        # Nota: En una implementación real, buscaríamos coordenadas o etiquetas específicas
        # Para este esqueleto, extraemos el contenido por líneas como aproximación
        for page in result.pages:
            for line in page.lines:
                text = line.content.strip()
                if not text:
                    continue
                
                # Intentamos identificar si la línea empieza con un número de casilla (ej: "1 ESTATUTO")
                parts = text.split(maxsplit=1)
                casilla = parts[0] if parts[0].isdigit() else "Text"
                valor = parts[1] if len(parts) > 1 else text
                
                entries.append(DuaEntry(
                    casilla=casilla,
                    valor=valor,
                    descripcion=f"Extraído de la página {page.page_number}"
                ))

        return entries
