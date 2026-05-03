import duckdb
import os
from dotenv import load_dotenv

def find_soivre():
    load_dotenv()
    db_path = os.getenv("DATABASE_PATH", "data/vector_db/aida_knowledge.db").replace('"', '')
    conn = duckdb.connect(db_path, read_only=True)
    
    print("Buscando 'SOIVRE' por texto exacto...")
    # Buscamos en la columna 'text' (asumiendo que así se llama)
    try:
        res = conn.execute("SELECT content FROM knowledge WHERE content ILIKE '%SOIVRE%'").fetchall()
        print(f"Encontrados: {len(res)}")
        for i, r in enumerate(res):
            print(f"\n--- Match {i+1} ---\n{r[0]}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    find_soivre()
