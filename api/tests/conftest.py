import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from pathlib import Path
import pytest
import pandas as pd
from database.connection import DatabaseManager

# Add project root to sys.path for imports
project_root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(project_root))

@pytest.fixture(scope="session")
def test_database():
    """Fixture to initialize the test database schema using a flat SQL file."""
    db_manager = DatabaseManager()

    # Ensure the core schema exists and drop the properties table if it exists
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("CREATE SCHEMA IF NOT EXISTS core;")
        cursor.execute("DROP TABLE IF EXISTS core.properties CASCADE;")
        conn.commit()

    schema_path = os.getenv("TEST_DB_SCHEMA_PATH", "database/setup/init_database_flat.sql")
    try:
        print("Running:", schema_path)
        db_manager.initialize_database(sql_file_path=schema_path)
    except Exception as e:
        print(f"Schema initialization failed: {e}")
        raise

    # Create the spatial index on the geometry column if it exists
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_properties_geom_gist ON core.properties USING GIST (geom);")
        conn.commit()

    return db_manager

@pytest.fixture(scope="session")
def sample_properties():
    """Fixture to provide a sample DataFrame for API tests."""
    data = {
        'external_id': ['A1', 'A2', 'A3'],
        'address': ['1 Main St', '2 Main St', '3 Main St'],
        'city': ['CityA', 'CityB', 'CityC'],
        'state': ['ST', 'ST', 'ST'],
        'zip_code': ['12345', '23456', '34567'],
        'county': ['County1', 'County2', 'County3'],
        'price': [100000, 200000, 300000],
        'bedrooms': [2, 3, 4],
        'bathrooms': [1.0, 2.0, 3.0],
        'square_feet': [1000, 1500, 2000],
        'lot_size': [0.2, 0.3, 0.4],
        'property_type': ['residential', 'residential', 'residential'],
        'year_built': [2000, 2005, 2010],
        'latitude': [40.7128, 40.7138, 40.7148],
        'longitude': [-74.0060, -74.0070, -74.0080],
        'data_source': ['test', 'test', 'test'],
        'geometry': [None, None, None]
    }
    df = pd.DataFrame(data)
    return df