import os
from pypdf import PdfReader
from aida.infrastructure.database.duckdb_repository import KnowledgeRepository
from tqdm import tqdm

def chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200):
    """
    Divide el texto en chunks de tamaño fijo con solapamiento.
    """
    chunks = []
    if not text:
        return chunks
        
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        if end >= len(text):
            break
        start += chunk_size - overlap
    return chunks

def ingest_manual():
    """
    Lee el PDF del manual, lo procesa y guarda los embeddings en DuckDB.
    """
    pdf_path = "data/raw/MANUAL DEL EXPORTADOR IMPORTADOR.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"Error: No se encuentra el archivo en {pdf_path}")
        return

    print(f"Leyendo manual desde: {pdf_path}")
    reader = PdfReader(pdf_path)
    full_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"

    print(f"Procesando texto ({len(full_text)} caracteres)...")
    chunks = chunk_text(full_text)
    print(f"Generados {len(chunks)} chunks.")

    print("Inicializando base de datos y modelo de embeddings...")
    repo = KnowledgeRepository()
    
    # Limpiamos la tabla para una ingesta limpia en este ejercicio
    repo.conn.execute("DELETE FROM knowledge")
    
    print("Generando embeddings e insertando en DuckDB...")
    for i, chunk in enumerate(tqdm(chunks)):
        # El repositorio ya tiene el modelo cargado
        embedding = repo.model.encode(chunk).tolist()
        repo.insert_knowledge(chunk, embedding, id=i)
    
    print(f"Exito: Se han indexado {len(chunks)} fragmentos del manual.")
    repo.close()

if __name__ == "__main__":
    ingest_manual()
