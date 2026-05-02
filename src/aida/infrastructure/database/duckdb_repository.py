import duckdb
import numpy as np
from sentence_transformers import SentenceTransformer
import os
from typing import List, Tuple

class KnowledgeRepository:
    """
    Adaptador de persistencia para el conocimiento técnico usando DuckDB como base de datos vectorial.
    """
    def __init__(self, db_path: str = "data/vector_db/aida_knowledge.db"):
        self.db_path = db_path
        # Asegurar que el directorio de la base de datos existe
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        self.conn = duckdb.connect(self.db_path)
        # Cargamos un modelo ligero para embeddings locales
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self._init_db()

    def _init_db(self):
        """
        Inicializa la tabla de conocimiento con soporte para vectores de tamaño fijo (384).
        """
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS knowledge (
                id INTEGER PRIMARY KEY,
                content TEXT,
                embedding FLOAT[384]
            )
        """)

    def insert_knowledge(self, content: str, embedding: List[float], id: int = None):
        """
        Inserta un nuevo chunk de conocimiento con su embedding.
        """
        if id is None:
            # Obtener el siguiente ID
            res = self.conn.execute("SELECT COALESCE(MAX(id), 0) + 1 FROM knowledge").fetchone()
            id = res[0]
            
        self.conn.execute(
            "INSERT INTO knowledge (id, content, embedding) VALUES (?, ?, ?)",
            [id, content, embedding]
        )

    def search_context(self, query: str, limit: int = 3) -> List[str]:
        """
        Realiza una búsqueda por similitud de coseno sobre los textos.
        """
        query_embedding = self.model.encode(query).tolist()
        
        # Usamos array_cosine_similarity de DuckDB para la búsqueda vectorial
        result = self.conn.execute("""
            SELECT content, array_cosine_similarity(embedding, ?::FLOAT[384]) as similarity
            FROM knowledge
            ORDER BY similarity DESC
            LIMIT ?
        """, [query_embedding, limit]).fetchall()
        
        return [r[0] for r in result]

    def close(self):
        self.conn.close()
