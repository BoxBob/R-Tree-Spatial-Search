"""
Amenity Data ETL Pipeline
File: src/spatial_search_engine/etl/amenity_etl.py
"""

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point
from typing import Dict, Any, List
from .base_etl import BaseETL
from ..database.connection import db
import psycopg2.extras

class AmenityETL(BaseETL):
    """ETL pipeline for amenity data (schools, hospitals, parks, etc.)"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.amenity_types = config.get('amenity_types', ['school', 'hospital', 'park'])
    
    def extract(self) -> gpd.GeoDataFrame:
        """Extract amenity data from shapefile or other sources"""
        source_path = self.config.get('source_path')
        
        if source_path.endswith('.shp'):
            gdf = gpd.read_file(source_path)
        elif source_path.endswith('.geojson'):
            gdf = gpd.read_file(source_path)
        else:
            raise ValueError(f"Unsupported file format: {source_path}")
        
        self.logger.info(f"Extracted {len(gdf)} amenity records")
        return gdf
    
    def transform(self, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """Transform amenity data"""
        # Ensure CRS is WGS84
        if gdf.crs != 'EPSG:4326':
            gdf = gdf.to_crs('EPSG:4326')
        
        # Clean and standardize amenity types
        if 'amenity_type' in gdf.columns:
            gdf['amenity_type'] = gdf['amenity_type'].str.lower().str.strip()
            gdf = gdf[gdf['amenity_type'].isin(self.amenity_types)]
        
        # Ensure required columns
        required_columns = ['name', 'amenity_type']
        for col in required_columns:
            if col not in gdf.columns:
                if col == 'name':
                    gdf[col] = 'Unknown'
                elif col == 'amenity_type':
                    gdf[col] = 'unknown'
        
        # Add metadata
        gdf['created_at'] = pd.Timestamp.now()
        
        return gdf
    
    def load(self, gdf: gpd.GeoDataFrame) -> bool:
        """Load amenities into database"""
        try:
            # Create amenities table if not exists
            self._create_amenities_table()
            
            with db.get_transaction() as conn:
                cursor = conn.cursor()
                
                insert_query = """
                    INSERT INTO core.amenities (
                        name, amenity_type, geom, created_at
                    ) VALUES %s
                    ON CONFLICT (name, amenity_type, geom) DO NOTHING
                """
                
                batch_data = []
                for _, row in gdf.iterrows():
                    batch_data.append((
                        row.get('name', 'Unknown'),
                        row.get('amenity_type', 'unknown'),
                        f"POINT({row.geometry.x} {row.geometry.y})",
                        row.get('created_at')
                    ))
                
                psycopg2.extras.execute_values(
                    cursor, insert_query, batch_data, page_size=100
                )
                
                self.logger.info(f"Loaded {len(batch_data)} amenity records")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to load amenities: {e}")
            return False
    
    def _create_amenities_table(self):
        """Create amenities table if it doesn't exist"""
        create_table_sql = """
            CREATE TABLE IF NOT EXISTS core.amenities (
                id BIGSERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                amenity_type VARCHAR(100) NOT NULL,
                geom GEOMETRY(POINT, 4326) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(name, amenity_type, geom)
            );
            
            CREATE INDEX IF NOT EXISTS idx_amenities_geom 
            ON core.amenities USING GIST (geom);
            
            CREATE INDEX IF NOT EXISTS idx_amenities_type 
            ON core.amenities (amenity_type);
        """
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(create_table_sql)
            conn.commit()
