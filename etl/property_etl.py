"""
Property Data ETL Pipeline
File: etl/property_etl.py
"""

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from etl.base_etl import BaseETL
from database.connection import db
import psycopg2.extras

class PropertyETL(BaseETL):
    """ETL pipeline for property data"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.source_type = config.get('source_type', 'csv')
        self.source_path = config.get('source_path')
        self.batch_size = config.get('batch_size', 1000)
        
    def extract(self) -> pd.DataFrame:
        """Extract property data from various sources"""
        self.logger.info(f"Extracting data from {self.source_type}: {self.source_path}")
        
        if self.source_type == 'csv':
            return self._extract_from_csv()
        elif self.source_type == 'api':
            return self._extract_from_api()
        elif self.source_type == 'shapefile':
            return self._extract_from_shapefile()
        else:
            raise ValueError(f"Unsupported source type: {self.source_type}")
    
    def _extract_from_csv(self) -> pd.DataFrame:
        """Extract data from CSV file"""
        try:
            df = pd.read_csv(self.source_path)
            self.logger.info(f"Extracted {len(df)} records from CSV")
            return df
        except Exception as e:
            self.logger.error(f"Failed to extract from CSV: {e}")
            raise
    
    def transform(self, data: pd.DataFrame) -> gpd.GeoDataFrame:
        """Transform property data"""
        self.logger.info("Starting data transformation")
        
        # Convert to GeoDataFrame if not already
        if not isinstance(data, gpd.GeoDataFrame):
            data = self._create_geodataframe(data)
        
        # Data cleaning and validation
        data = self._clean_data(data)
        data = self._validate_coordinates(data)
        data = self._standardize_columns(data)
        data = self._enrich_data(data)
        
        self.logger.info(f"Transformation complete: {len(data)} valid records")
        return data
    
    def _create_geodataframe(self, df: pd.DataFrame) -> gpd.GeoDataFrame:
        """Create GeoDataFrame from regular DataFrame"""
        lat_col = self.config.get('latitude_column', 'latitude')
        lng_col = self.config.get('longitude_column', 'longitude')
        
        if lat_col not in df.columns or lng_col not in df.columns:
            raise ValueError(f"Required coordinate columns not found: {lat_col}, {lng_col}")
        
        # Remove rows with invalid coordinates
        df = df.dropna(subset=[lat_col, lng_col])
        
        # Create geometry column
        geometry = [Point(xy) for xy in zip(df[lng_col], df[lat_col])]
        gdf = gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:4326')
        
        return gdf
    
    def _clean_data(self, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """Clean and standardize data"""
        # Remove duplicates
        initial_count = len(gdf)
        gdf = gdf.drop_duplicates(subset=['address'], keep='first')
        self.logger.info(f"Removed {initial_count - len(gdf)} duplicate records")
        
        # Clean price data
        if 'price' in gdf.columns:
            gdf['price'] = pd.to_numeric(gdf['price'], errors='coerce')
            gdf = gdf[gdf['price'] > 0]  # Remove invalid prices
        
        return gdf
    
    def _validate_coordinates(self, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """Validate geographic coordinates"""
        # Remove invalid geometries
        gdf = gdf[gdf.geometry.is_valid]
        
        # Check coordinate bounds
        bounds = self.config.get('coordinate_bounds', {
            'min_lat': -90, 'max_lat': 90,
            'min_lng': -180, 'max_lng': 180
        })
        
        gdf = gdf[
            (gdf.geometry.x >= bounds['min_lng']) & 
            (gdf.geometry.x <= bounds['max_lng']) &
            (gdf.geometry.y >= bounds['min_lat']) & 
            (gdf.geometry.y <= bounds['max_lat'])
        ]
        
        return gdf
    
    def _standardize_columns(self, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """Standardize column names and formats"""
        column_mapping = self.config.get('column_mapping', {})
        
        if column_mapping:
            gdf = gdf.rename(columns=column_mapping)
        
        # Ensure required columns exist
        required_columns = [
            'address', 'city', 'state', 'price', 
            'bedrooms', 'bathrooms', 'square_feet', 'property_type'
        ]
        
        for col in required_columns:
            if col not in gdf.columns:
                if col in ['bedrooms', 'bathrooms', 'square_feet']:
                    gdf[col] = 0
                elif col == 'property_type':
                    gdf[col] = 'Unknown'
                else:
                    gdf[col] = ''
        
        return gdf
    
    def _enrich_data(self, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """Enrich data with additional information"""
        # Add processing timestamp
        gdf['created_at'] = datetime.now()
        gdf['updated_at'] = datetime.now()
        
        return gdf
    
    def load(self, gdf: gpd.GeoDataFrame) -> bool:
        """Load data into PostgreSQL database"""
        try:
            self.logger.info(f"Loading {len(gdf)} records to database")
            
            with db.get_connection() as conn:
                cursor = conn.cursor()
                
                # Prepare insert query
                insert_query = """
                    INSERT INTO core.properties (
                        external_id, address, city, state, zip_code, price, bedrooms, 
                        bathrooms, square_feet, property_type, geom,
                        created_at, updated_at, data_source
                    ) VALUES %s
                    ON CONFLICT (external_id) DO UPDATE SET
                        price = EXCLUDED.price,
                        updated_at = EXCLUDED.updated_at,
                        data_source = EXCLUDED.data_source
                """
                
                # Process in batches
                for i in range(0, len(gdf), self.batch_size):
                    batch = gdf.iloc[i:i + self.batch_size]
                    
                    # Prepare batch data
                    batch_data = []
                    for idx, row in batch.iterrows():
                        external_id = f"PROP_{idx}_{int(datetime.now().timestamp())}"
                        batch_data.append((
                            external_id,
                            row.get('address', ''),
                            row.get('city', ''),
                            row.get('state', ''),
                            row.get('zip_code', ''),
                            row.get('price', 0),
                            int(row.get('bedrooms', 0)),
                            float(row.get('bathrooms', 0)),
                            int(row.get('square_feet', 0)),
                            row.get('property_type', 'Unknown'),
                            f"POINT({row.geometry.x} {row.geometry.y})",
                            row.get('created_at'),
                            row.get('updated_at'),
                            'test'  # Always set data_source to 'test' for ETL/test runs
                        ))
                    
                    # Execute batch insert
                    psycopg2.extras.execute_values(
                        cursor, insert_query, batch_data, 
                        template=None, page_size=100
                    )
                    
                    conn.commit()
                    self.logger.info(f"Loaded batch {i//self.batch_size + 1}")
                
                self.logger.info("Data loading completed successfully")
                return True
                
        except Exception as e:
            self.logger.error(f"Failed to load data: {e}")
            return False
