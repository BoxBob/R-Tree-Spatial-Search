# database/tests/conftest.py

import os
import pytest
from database.connection import DatabaseManager

@pytest.fixture(scope="session")
def test_database():
    """Fixture to provide the global DatabaseManager instance and initialize schema"""
    db_manager = DatabaseManager()
    # Initialize the database schema before running tests
    schema_path = os.getenv("TEST_DB_SCHEMA_PATH", "database/setup/init_database.sql")
    print("Running:", schema_path)
    db_manager.initialize_database(sql_file_path=schema_path)
    return db_manager