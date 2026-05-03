import duckdb
import os
from dotenv import load_dotenv

def check_db():
    load_dotenv()
    db_path = os.getenv("DATABASE_PATH", "data/vector_db/aida_knowledge.db")
    # Limpiar comillas si existen
    db_path = db_path.replace('"', '').replace("'", "")
    
    if not os.path.exists(db_path):
        print(f"Error: No existe el archivo de base de datos en {db_path}")
        return

    try:
        conn = duckdb.connect(db_path, read_only=True)
        # Suponiendo que la tabla se llama 'knowledge' (común en este proyecto)
        tables = conn.execute("SHOW TABLES").fetchall()
        print(f"Tablas encontradas: {tables}")
        
        for table in tables:
            table_name = table[0]
            count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
            print(f"Tabla '{table_name}': {count} filas.")
            
            if count > 0:
                print("Muestra de datos (primeras 2 filas):")
                sample = conn.execute(f"SELECT * FROM {table_name} LIMIT 2").fetchall()
                for row in sample:
                    print(row)
        
        conn.close()
    except Exception as e:
        print(f"Error al conectar a DuckDB: {e}")

if __name__ == "__main__":
    check_db()
