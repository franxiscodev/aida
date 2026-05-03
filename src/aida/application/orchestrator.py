import os
import uuid
from datetime import datetime
from typing import List

from aida.domain.models import DuaEntry, ValidationReport, ValidationResult
from aida.infrastructure.adapters.azure_ocr_adapter import AzureOCRAdapter
from aida.infrastructure.database.duckdb_repository import KnowledgeRepository
from aida.infrastructure.adapters.gemini_adapter import GeminiAdapter

class AidaOrchestrator:
    """
    Orquestador principal de AIDA. Coordina el OCR, la búsqueda de conocimiento (RAG)
    y la generación de informes de validación.
    """
    def __init__(self, read_only: bool = False):
        self.ocr_adapter = AzureOCRAdapter()
        self.knowledge_repo = KnowledgeRepository(read_only=read_only)
        self.brain = GeminiAdapter()
        
        # Lista de siglas técnicas a buscar en el Manual del Exportador
        self.technical_acronyms = ["CUD", "REOCE", "SOIVRE", "EUR.1", "L.EXP", "RCEP", "DV1", "EUROPEA", "EXPEDIDOR"]

    def validate_dua(self, file_path: str) -> ValidationReport:
        """
        Orquesta el flujo completo de validación para un archivo DUA.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"No se encuentra el archivo: {file_path}")

        # 1. Extracción de datos vía Azure OCR
        print(f"Buscando información en el DUA: {os.path.basename(file_path)}...")
        entries = self.ocr_adapter.analyze_dua(file_path)
        
        validation_results = []
        
        # 2. Análisis y Enriquecimiento con Conocimiento Técnico (RAG)
        print("Validando siglas técnicas encontradas contra el Manual del Exportador...")
        
        for entry in entries:
            # Comprobar si el valor de la casilla contiene alguna de nuestras siglas de interés
            # O si la casilla en sí es una de las siglas (ej: casilla 44 suele contener certificados)
            text_to_analyze = f"{entry.casilla} {entry.valor}".upper()
            
            for acronym in self.technical_acronyms:
                if acronym in text_to_analyze:
                    # Búsqueda semántica en DuckDB
                    query = f"¿Qué es el {acronym} y cuáles son sus requisitos de validación?"
                    # Aumentamos el límite a 2 contextos para que Gemini tenga más información
                    contexts = self.knowledge_repo.search_context(query, limit=2)
                    
                    if contexts:
                        full_context = "\n".join(contexts)
                        # Usamos el Cerebro (Gemini) para sintetizar la respuesta
                        definition = self.brain.summarize_definition(acronym, full_context)
                        
                        # Generamos un resultado de validación enriquecido
                        validation_results.append(ValidationResult(
                            campo=f"Casilla {entry.casilla} ({acronym})",
                            es_valido=True,
                            mensaje=definition,
                            sugerencia=f"Asegúrese de que el código {acronym} cumple con la normativa descrita."
                        ))

        # 3. Generación del Informe Final
        report = ValidationReport(
            id_validacion=str(uuid.uuid4()),
            fecha=datetime.now(),
            documento_id=os.path.basename(file_path),
            resultados=validation_results,
            resumen_validez=all(r.es_valido for r in validation_results) if validation_results else True,
            metadatos={
                "total_entries_ocr": len(entries),
                "acronyms_detected": len(validation_results)
            }
        )
        
        return report

    def explain_acronym(self, acronym: str) -> str:
        """
        Busca la definición de una sigla directamente en el manual sin usar OCR.
        """
        # Limpiamos la sigla de posibles interrogaciones (Dialogflow a veces las envía)
        acronym = acronym.replace('?', '').strip()
        
        print(f"Consultando sigla directamente: {acronym}...")
        query = f"¿Qué es el {acronym} y cuáles son sus requisitos de validación?"
        contexts = self.knowledge_repo.search_context(query, limit=2)
        
        if contexts:
            full_context = "\n".join(contexts)
            # Usamos el Cerebro (Gemini) para sintetizar la respuesta
            return self.brain.summarize_definition(acronym, full_context)
        
        return f"Lo siento, no he encontrado información sobre la sigla {acronym} en el Manual del Exportador."

    def answer_general_question(self, question: str) -> str:
        """
        Delega una pregunta abierta al Cerebro (Gemini).
        """
        return self.brain.ask_general_question(question)

    def close(self):
        """Libera recursos."""
        self.knowledge_repo.close()
