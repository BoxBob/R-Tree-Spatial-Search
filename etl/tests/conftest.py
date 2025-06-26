import os
import pytest
import pandas as pd
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

@pytest.fixture(scope="session")
def sample_properties():
    """Fixture to provide a sample DataFrame for ETL tests."""
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
