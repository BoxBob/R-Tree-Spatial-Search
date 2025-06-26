"""
Property ETL tests
"""

import pytest
import pandas as pd
import tempfile
import os
from etl.property_etl import PropertyETL
from etl.etl_config import ETLConfig

def test_property_etl_csv_extraction(sample_properties):
    """Test CSV extraction"""
    # Create temporary CSV file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        sample_properties.drop(columns=['geometry']).to_csv(f.name, index=False)
        csv_path = f.name
    
    try:
        config = {
            'source_type': 'csv',
            'source_path': csv_path,
            'latitude_column': 'latitude',
            'longitude_column': 'longitude'
        }
        
        etl = PropertyETL(config)
        result = etl.extract()
        
        assert len(result) == 3
        assert 'latitude' in result.columns
        assert 'longitude' in result.columns
        
    finally:
        os.unlink(csv_path)

def test_property_etl_transformation(sample_properties):
    """Test data transformation"""
    config = {
        'coordinate_bounds': {
            'min_lat': 25.0, 'max_lat': 50.0,
            'min_lng': -125.0, 'max_lng': -65.0
        }
    }
    
    etl = PropertyETL(config)
    
    # Convert to regular DataFrame for testing
    df = sample_properties.drop(columns=['geometry'])
    
    result = etl.transform(df)
    
    assert len(result) == 3
    assert hasattr(result, 'geometry')
    assert result.crs.to_string() == 'EPSG:4326'

def test_property_etl_full_pipeline(test_database, sample_properties):
    """Test complete ETL pipeline"""
    # Create temporary CSV
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        sample_properties.drop(columns=['geometry']).to_csv(f.name, index=False)
        csv_path = f.name
    
    try:
        config = {
            'source_type': 'csv',
            'source_path': csv_path,
            'batch_size': 10,
            'latitude_column': 'latitude',
            'longitude_column': 'longitude'
        }
        
        etl = PropertyETL(config)
        result = etl.run()
        
        assert result['success'] == True
        assert result['records_processed'] == 3
        assert result['records_loaded'] == 3
        
        # Verify data was loaded
        with test_database.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM core.properties")
            count = cursor.fetchone()['count']
            assert count >= 3
            
    finally:
        os.unlink(csv_path)
