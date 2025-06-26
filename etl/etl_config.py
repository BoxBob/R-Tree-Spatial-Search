"""
ETL Configuration Management
File: etl/etl_config.py
"""

from typing import Dict, Any
import os
from pathlib import Path
import yaml
import json

class ETLConfig:
    """Configuration management for ETL processes"""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or "configs/etl_config.yaml"
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        config_file = Path(self.config_path)
        
        if not config_file.exists():
            return self._get_default_config()
        
        try:
            with open(config_file, 'r') as f:
                if config_file.suffix.lower() == '.yaml':
                    return yaml.safe_load(f)
                elif config_file.suffix.lower() == '.json':
                    return json.load(f)
                else:
                    raise ValueError(f"Unsupported config format: {config_file.suffix}")
        except Exception as e:
            print(f"Failed to load config from {config_file}: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default ETL configuration"""
        return {
            'property_etl': {
                'source_type': 'csv',
                'source_path': 'data/raw/properties.csv',
                'batch_size': 1000,
                'latitude_column': 'latitude',
                'longitude_column': 'longitude',
                'coordinate_bounds': {
                    'min_lat': 25.0, 'max_lat': 50.0,
                    'min_lng': -125.0, 'max_lng': -65.0
                },
                'column_mapping': {
                    'lat': 'latitude',
                    'lng': 'longitude',
                    'addr': 'address'
                }
            },
            'amenity_etl': {
                'source_type': 'shapefile',
                'source_path': 'data/raw/amenities.shp',
                'batch_size': 500,
                'amenity_types': ['school', 'hospital', 'park', 'shopping']
            },
            'boundary_etl': {
                'source_type': 'geojson',
                'source_path': 'data/raw/boundaries.geojson',
                'batch_size': 100
            }
        }
    
    def get_config(self, etl_type: str) -> Dict[str, Any]:
        """Get configuration for specific ETL type"""
        return self.config.get(etl_type, {})
