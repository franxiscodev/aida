from pypdf import PdfReader
import os

def check_pdf():
    pdf_path = "data/raw/MANUAL DEL EXPORTADOR IMPORTADOR.pdf"
    if not os.path.exists(pdf_path):
        print(f"Error: No existe {pdf_path}")
        return

    print(f"Analizando {pdf_path}...")
    reader = PdfReader(pdf_path)
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text()
    
    count = full_text.upper().count("SOIVRE")
    print(f"Total de menciones de 'SOIVRE': {count}")
    
    if count > 0:
        # Mostrar el primer contexto donde aparece
        idx = full_text.upper().find("SOIVRE")
        start = max(0, idx - 100)
        end = min(len(full_text), idx + 300)
        print("\n--- Ejemplo de contexto en el PDF ---\n")
        print(full_text[start:end])

if __name__ == "__main__":
    check_pdf()
