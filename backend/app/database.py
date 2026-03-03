import duckdb
import os

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../censo2024.duckdb'))

class DuckDBConnection:
    _instance = None
    
    @classmethod
    def get_connection(cls):
        if cls._instance is None:
            # Conexión read-only para mayor rendimiento y seguridad en concurrencia
            cls._instance = duckdb.connect(DB_PATH, read_only=True)
        return cls._instance

def get_db():
    return DuckDBConnection.get_connection()
