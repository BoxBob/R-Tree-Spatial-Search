"""
Centralized Database Connection Manager
File: database/connection.py
Purpose: Manage PostgreSQL connections with proper schema awareness
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from psycopg2.pool import ThreadedConnectionPool
from contextlib import contextmanager
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass
import threading
from pathlib import Path

@dataclass
class DatabaseConfig:
    """Database configuration dataclass"""
    host: str
    port: int
    database: str
    user: str
    password: str
    sslmode: str = 'prefer'
    pool_min: int = 5
    pool_max: int = 20
    schema_search_path: str = 'core,analytics,admin,public'

class DatabaseManager:
    """Centralized database connection manager with schema awareness"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.config = self._load_config()
            self.connection_pool = None
            self.logger = logging.getLogger(__name__)
            self._initialize_pool()
            self.initialized = True
    
    def _load_config(self) -> DatabaseConfig:
        """Load database configuration from environment"""
        return DatabaseConfig(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', '5432')),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            sslmode=os.getenv('DB_SSLMODE', 'prefer'),
            pool_min=int(os.getenv('DB_POOL_MIN', '5')),
            pool_max=int(os.getenv('DB_POOL_MAX', '20')),
            schema_search_path=os.getenv('DB_SCHEMA_PATH', 'core,analytics,admin,public')
        )
    
    def _initialize_pool(self):
        """Initialize connection pool with schema search path"""
        try:
            self.connection_pool = ThreadedConnectionPool(
                minconn=self.config.pool_min,
                maxconn=self.config.pool_max,
                host=self.config.host,
                port=self.config.port,
                database=self.config.database,
                user=self.config.user,
                password=self.config.password,
                sslmode=self.config.sslmode,
                cursor_factory=RealDictCursor,
                options=f"-c search_path={self.config.schema_search_path}"
            )
            self.logger.info("Database connection pool initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize database pool: {e}")
            raise
    
    @contextmanager
    def get_connection(self):
        """Get database connection from pool with proper schema context"""
        conn = None
        try:
            conn = self.connection_pool.getconn()
            # Ensure search path is set
            with conn.cursor() as cursor:
                cursor.execute(f"SET search_path TO {self.config.schema_search_path}")
            yield conn
        except Exception as e:
            if conn:
                conn.rollback()
            self.logger.error(f"Database operation failed: {e}")
            raise
        finally:
            if conn:
                self.connection_pool.putconn(conn)
    
    def initialize_database(self, sql_file_path):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            with open(sql_file_path, 'r') as f:
                sql_script = f.read()
                statements = [stmt.strip() for stmt in sql_script.split(';') if stmt.strip()]
                for stmt in statements:
                    try:
                        cursor.execute(stmt)
                    except Exception as e:
                        print(f"Error executing: {stmt}\n{e}")
                        raise
            conn.commit()

# Global database manager instance
db = DatabaseManager()
