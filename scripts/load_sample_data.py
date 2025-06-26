#!/usr/bin/env python3
"""
Sample Data Loading Script
File: scripts/load_sample_data.py
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
from shapely.geometry import Point
import geopandas as gpd

# Add src to path
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path.resolve()))

from etl.property_etl import PropertyETL
from etl.etl_config import ETLConfig
import argparse

def generate_sample_properties(count: int = 1000) -> gpd.GeoDataFrame:
    """Generate sample property data for testing"""
    np.random.seed(42)
    
    # Generate random coordinates (US bounds)
    latitudes = np.random.uniform(25.0, 49.0, count)
    longitudes = np.random.uniform(-125.0, -66.0, count)
    
    # Generate property data
    data = {
        'external_id': [f"PROP_{i:06d}" for i in range(count)],
        'address': [f"{np.random.randint(1, 9999)} {np.random.choice(['Main', 'Oak', 'Pine', 'Elm'])} St" 
                   for _ in range(count)],
        'city': np.random.choice(['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix'], count),
        'state': np.random.choice(['NY', 'CA', 'IL', 'TX', 'AZ'], count),
        'zip_code': [f"{np.random.randint(10000, 99999)}" for _ in range(count)],
        'price': np.random.uniform(100000, 2000000, count),
        'bedrooms': np.random.randint(1, 6, count),
        'bathrooms': np.random.uniform(1, 4, count).round(1),
        'square_feet': np.random.randint(500, 5000, count),
        'property_type': np.random.choice(['Single Family', 'Condo', 'Townhouse', 'Apartment'], count),
        'year_built': np.random.randint(1950, 2024, count),
        'latitude': latitudes,
        'longitude': longitudes
    }
    
    df = pd.DataFrame(data)
    
    # Create GeoDataFrame
    geometry = [Point(xy) for xy in zip(df['longitude'], df['latitude'])]
    gdf = gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:4326')
    
    return gdf

def main():
    parser = argparse.ArgumentParser(description='Load sample data into database')
    parser.add_argument('--count', type=int, default=1000,
                       help='Number of sample properties to generate')
    parser.add_argument('--config', help='ETL configuration file path')
    
    args = parser.parse_args()
    
    print(f"Generating {args.count} sample properties...")
    
    # Generate sample data
    gdf = generate_sample_properties(args.count)
    
    # Save to CSV for reference
    sample_file = Path('data/sample/sample_properties.csv')
    sample_file.parent.mkdir(parents=True, exist_ok=True)
    
    df_for_csv = gdf.drop(columns=['geometry'])
    df_for_csv.to_csv(sample_file, index=False)
    print(f"Sample data saved to: {sample_file}")
    
    # Load using ETL
    config_manager = ETLConfig(args.config)
    etl_config = config_manager.get_config('property_etl')
    etl_config['source_type'] = 'dataframe'  # Special mode for in-memory data
    
    etl = PropertyETL(etl_config)
    
    # Override extract method to use our generated data
    etl.extract = lambda: gdf
    
    print("Loading sample data into database...")
    result = etl.run()
    
    if result.get('errors'):
        print(f"ETL completed with errors: {result['errors']}")
    else:
        print(f"Successfully loaded {result['records_loaded']} properties")
        print(f"Processing time: {result['duration']:.2f} seconds")

if __name__ == "__main__":
    main()
