import os
import psycopg2
from contextlib import contextmanager

@contextmanager
def get_connection():
    """Context manager for PostgreSQL connection using environment variables."""
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        database=os.getenv("DB_NAME", "postgres"),
        user=os.getenv("DB_USER", "spatial_user"),
        password=os.getenv("DB_PASSWORD", "spatial_password")
    )
    try:
        yield conn
    finally:
        conn.close()
