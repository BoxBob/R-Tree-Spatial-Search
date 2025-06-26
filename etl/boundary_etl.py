"""
Administrative Boundary ETL Pipeline
File: src/spatial_search_engine/etl/boundary_etl.py
"""

import geopandas as gpd
from typing import Dict, Any
from .base_etl import BaseETL
from ..database.connection import db
import psycopg2.extras

class BoundaryETL(BaseETL):
    """ETL pipeline for administrative boundaries"""
    
    def extract(self) -> gpd.GeoDataFrame:
        """Extract boundary data"""
        source_path = self.config.get('source_path')
        gdf = gpd.read_file(source_path)
        self.logger.info(f"Extracted {len(gdf)} boundary records")
        return gdf
    
    def transform(self, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """Transform boundary data"""
        # Ensure WGS84
        if gdf.crs != 'EPSG:4326':
            gdf = gdf.to_crs('EPSG:4326')
        
        # Standardize columns
        column_mapping = self.config.get('column_mapping', {})
        if column_mapping:
            gdf = gdf.rename(columns=column_mapping)
        
        # Ensure required columns
        if 'boundary_name' not in gdf.columns:
            gdf['boundary_name'] = 'Unknown'
        
        if 'boundary_type' not in gdf.columns:
            gdf['boundary_type'] = 'district'
        
        return gdf
    
    def load(self, gdf: gpd.GeoDataFrame) -> bool:
        """Load boundaries into database"""
        try:
            self._create_boundaries_table()
            
            with db.get_transaction() as conn:
                cursor = conn.cursor()
                
                for _, row in gdf.iterrows():
                    insert_query = """
                        INSERT INTO core.administrative_boundaries 
                        (boundary_name, boundary_type, geom)
                        VALUES (%s, %s, ST_GeomFromText(%s, 4326))
                        ON CONFLICT (boundary_name, boundary_type) DO NOTHING
                    """
                    
                    cursor.execute(insert_query, [
                        row.get('boundary_name'),
                        row.get('boundary_type'),
                        row.geometry.wkt
                    ])
                
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to load boundaries: {e}")
            return False
    
    def _create_boundaries_table(self):
        """Create boundaries table"""
        create_table_sql = """
            CREATE TABLE IF NOT EXISTS core.administrative_boundaries (
                id BIGSERIAL PRIMARY KEY,
                boundary_name VARCHAR(255) NOT NULL,
                boundary_type VARCHAR(100) NOT NULL,
                geom GEOMETRY(MULTIPOLYGON, 4326) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(boundary_name, boundary_type)
            );
            
            CREATE INDEX IF NOT EXISTS idx_boundaries_geom 
            ON core.administrative_boundaries USING GIST (geom);
        """
        
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(create_table_sql)
            conn.commit()
