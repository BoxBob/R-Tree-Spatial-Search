"""
Pytest configuration and fixtures for spatial search engine tests
"""

import pytest
import os
import tempfile
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.connection import DatabaseManager

@pytest.fixture(scope="session")
def test_db_config():
    """Test database configuration"""
    return {
        'host': os.getenv('POSTGRES_HOST', 'localhost'),
        'port': int(os.getenv('POSTGRES_PORT', '5432')),
        'database': os.getenv('POSTGRES_DB', 'postgres'),
        'user': os.getenv('POSTGRES_USER', 'test_user'),
        'password': os.getenv('POSTGRES_PASSWORD', 'test_password')
    }

@pytest.fixture(scope="session")
def test_database(test_db_config):
    """Create and setup test database"""
    # Create database if it doesn't exist
    conn = psycopg2.connect(
        host=test_db_config['host'],
        port=test_db_config['port'],
        user=test_db_config['user'],
        password=test_db_config['password'],
        database='postgres'
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    
    # Drop and recreate test database
    cursor.execute(f"DROP DATABASE IF EXISTS {test_db_config['database']}")
    cursor.execute(f"CREATE DATABASE {test_db_config['database']}")
    
    cursor.close()
    conn.close()
    
    # Setup environment variables for database connection
    os.environ['DB_HOST'] = test_db_config['host']
    os.environ['DB_PORT'] = str(test_db_config['port'])
    os.environ['DB_NAME'] = test_db_config['database']
    os.environ['DB_USER'] = test_db_config['user']
    os.environ['DB_PASSWORD'] = test_db_config['password']
    
    # Initialize database schema
    db_manager = DatabaseManager()
    
    # Run database initialization
    init_sql = """
        CREATE EXTENSION IF NOT EXISTS postgis;
        CREATE EXTENSION IF NOT EXISTS postgis_topology;
        
        CREATE SCHEMA IF NOT EXISTS core;
        CREATE SCHEMA IF NOT EXISTS analytics;
        CREATE SCHEMA IF NOT EXISTS admin;
        
        -- Create basic properties table for testing
        CREATE TABLE core.properties (
            id BIGSERIAL PRIMARY KEY,
            external_id VARCHAR(100) UNIQUE NOT NULL,
            address TEXT NOT NULL,
            city VARCHAR(100) NOT NULL,
            state VARCHAR(50) NOT NULL,
            price DECIMAL(15,2),
            bedrooms SMALLINT,
            bathrooms DECIMAL(3,1),
            square_feet INTEGER,
            property_type VARCHAR(50),
            geom GEOMETRY(POINT, 4326) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            is_active BOOLEAN DEFAULT TRUE
        );
        
        CREATE INDEX idx_properties_geom ON core.properties USING GIST (geom);
    """
    
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(init_sql)
        conn.commit()
    
    yield db_manager
    
    # Cleanup
    conn = psycopg2.connect(
        host=test_db_config['host'],
        port=test_db_config['port'],
        user=test_db_config['user'],
        password=test_db_config['password'],
        database='postgres'
    )
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = conn.cursor()
    cursor.execute(f"DROP DATABASE IF EXISTS {test_db_config['database']}")
    cursor.close()
    conn.close()

@pytest.fixture
def sample_properties():
    """Generate sample property data for testing"""
    data = {
        'external_id': ['PROP_001', 'PROP_002', 'PROP_003'],
        'address': ['123 Main St', '456 Oak Ave', '789 Pine Rd'],
        'city': ['New York', 'Los Angeles', 'Chicago'],
        'state': ['NY', 'CA', 'IL'],
        'price': [500000, 750000, 400000],
        'bedrooms': [2, 3, 2],
        'bathrooms': [1.5, 2.0, 1.0],
        'square_feet': [1200, 1800, 1000],
        'property_type': ['Condo', 'House', 'Condo'],
        'latitude': [40.7128, 34.0522, 41.8781],
        'longitude': [-74.0060, -118.2437, -87.6298]
    }
    
    df = pd.DataFrame(data)
    geometry = [Point(xy) for xy in zip(df['longitude'], df['latitude'])]
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:4326')
    
    return gdf

@pytest.fixture
def test_client():
    """FastAPI test client"""
    from fastapi.testclient import TestClient
    from api.main import app
    
    return TestClient(app)

@pytest.fixture(scope="module")
def test_database():
    db_manager = DatabaseManager(
        host="localhost",
        port=5432,
        user="postgres",
        password="test_password",
        database="test_db"
    )
    yield db_manager