from aida.application.orchestrator import AidaOrchestrator
import os
from dotenv import load_dotenv

def test_soivre():
    load_dotenv()
    # Aseguramos que la ruta de la DB sea correcta
    db_path = os.getenv("DATABASE_PATH", "data/vector_db/aida_knowledge.db").replace('"', '')
    if not os.path.exists(db_path):
        print(f"Error: No existe {db_path}")
        return

    orchestrator = AidaOrchestrator(read_only=True)
    try:
        print("--- TEST SOIVRE ---")
        respuesta = orchestrator.explain_acronym("SOIVRE")
        print(f"\nRespuesta Final:\n{respuesta}")
    finally:
        orchestrator.close()

if __name__ == "__main__":
    test_soivre()
