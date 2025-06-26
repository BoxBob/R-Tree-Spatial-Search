"""
Database connection tests
"""

import pytest
from database.connection import DatabaseManager

def test_database_connection(test_database):
    """Test database connection"""
    db_manager = test_database
    
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        assert list(result.values())[0] == 1


def test_spatial_query(test_database):
    """Test basic spatial query functionality"""
    db_manager = test_database
    
    with db_manager.get_connection() as conn:
        cursor = conn.cursor()
        # Insert test data
        cursor.execute(
            "INSERT INTO core.properties (external_id, address, city, state, price, geom, property_type, data_source) "
            "VALUES ('TEST_001', '123 Test St', 'Test City', 'TS', 100000, "
            "ST_Point(-74.0060, 40.7128), 'residential', 'test')"
        )
        # Test spatial query
        cursor.execute(
            "SELECT COUNT(*) FROM core.properties "
            "WHERE ST_DWithin(geom::geography, ST_Point(-74.0060, 40.7128)::geography, 1000)"
        )
        result = cursor.fetchone()
        assert list(result.values())[0] >= 1
        conn.commit()
