import sys
import os
from dotenv import load_dotenv

# Asegurar que el directorio src está en el PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))

from aida.application.orchestrator import AidaOrchestrator

def test_full_flow():
    """
    Test integral que valida el flujo completo:
    OCR (Azure) -> Identificación de Siglas -> Búsqueda RAG (DuckDB) -> Informe
    """
    load_dotenv()
    
    # Verificación de configuración
    endpoint = os.getenv("AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT")
    if not endpoint or "your-resource" in endpoint:
        print("\n[SKIP] Saltando test: Configura tus credenciales de Azure en .env")
        return

    print("\n" + "="*60)
    print("SISTEMA AIDA: TEST DE FLUJO COMPLETO (OCR + RAG)")
    print("="*60)

    orchestrator = AidaOrchestrator(read_only=True)
    pdf_path = "data/raw/ejemplo_dua_07.00.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"[ERROR] No se encuentra el archivo: {pdf_path}")
        return

    try:
        # Ejecutar orquestación
        report = orchestrator.validate_dua(pdf_path)
        
        print(f"\nINFORME GENERADO: {report.id_validacion}")
        print(f"Documento: {report.documento_id}")
        print(f"Fecha: {report.fecha.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Casillas extraídas: {report.metadatos.get('total_entries_ocr')}")
        print(f"Validaciones técnicas encontradas: {len(report.resultados)}")
        
        if report.resultados:
            print("\n" + "-"*60)
            print("DETALLE DE VALIDACIONES ENRIQUECIDAS CON EL MANUAL")
            print("-"*60)
            for res in report.resultados:
                print(f"\n>> {res.campo}")
                print(f"   Analisis: {res.mensaje}")
                print(f"   Accion: {res.sugerencia}")
        else:
            print("\n[!] No se detectaron siglas técnicas conocidas en este documento de prueba.")
            print("    Siglas buscadas: CUD, REOCE, SOIVRE, EUR.1, L.EXP, RCEP, DV1")
            
    except Exception as e:
        print(f"\n[ERROR] Fallo en la orquestación: {str(e)}")
    finally:
        orchestrator.close()
        print("\n" + "="*60)

if __name__ == "__main__":
    test_full_flow()
