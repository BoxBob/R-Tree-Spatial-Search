import psycopg2
import os
import random
import json
from faker import Faker
from faker.providers import automotive, company, address
import numpy as np

fake = Faker()
fake.add_provider(automotive)
fake.add_provider(company)
fake.add_provider(address)

# Database connection
conn = psycopg2.connect(
    host=os.getenv("DB_HOST", "localhost"),
    port=os.getenv("DB_PORT", "5432"),
    database=os.getenv("DB_NAME", "postgres"),
    user=os.getenv("DB_USER", "spatial_user"),
    password=os.getenv("DB_PASSWORD", "spatial_password")
)

def generate_properties(count=10000):
    """Generate realistic property data"""
    cursor = conn.cursor()
    
    # Define realistic geographic bounds (San Francisco Bay Area)
    bounds = {
        'min_lat': 37.4419, 'max_lat': 37.9298,
        'min_lng': -122.5150, 'max_lng': -122.0700
    }
    
    property_types = ['house', 'condo', 'townhouse', 'apartment']
    
    batch_size = 1000
    for i in range(0, count, batch_size):
        batch_data = []
        
        for j in range(batch_size):
            if i + j >= count:
                break
                
            # Generate realistic property data
            lat = random.uniform(bounds['min_lat'], bounds['max_lat'])
            lng = random.uniform(bounds['min_lng'], bounds['max_lng'])
            
            prop_type = random.choice(property_types)
            bedrooms = random.randint(1, 5)
            bathrooms = round(random.uniform(1, 4), 1)
            
            # Price based on bedrooms and location
            base_price = {
                'apartment': 400000, 'condo': 600000,
                'townhouse': 800000, 'house': 1000000
            }[prop_type]
            
            price = base_price + (bedrooms * 100000) + random.randint(-200000, 500000)
            price = max(price, 200000)  # Minimum price
            
            square_feet = bedrooms * 400 + random.randint(200, 800)
            lot_size = random.uniform(0.1, 2.0) if prop_type == 'house' else 0
            year_built = random.randint(1950, 2023)
            
            batch_data.append((
                prop_type, fake.address().replace('\n', ', '),
                fake.city(), fake.state_abbr(), fake.zipcode(),
                price, bedrooms, bathrooms, square_feet, lot_size,
                year_built, lng, lat
            ))
        
        # Bulk insert batch
        cursor.executemany("""
            INSERT INTO spatial_engine.properties (
                property_type, address, city, state, zip_code,
                price, bedrooms, bathrooms, square_feet, lot_size,
                year_built, geom
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                ST_Point(%s, %s)
            )
        """, batch_data)
        
        conn.commit()
        print(f"Inserted {min(i + batch_size, count)} properties...")
    
    cursor.close()

def generate_poi(count=2000):
    """Generate Points of Interest"""
    cursor = conn.cursor()
    
    categories = {
        'restaurant': ['pizza', 'chinese', 'mexican', 'italian', 'american'],
        'retail': ['grocery', 'clothing', 'electronics', 'pharmacy'],
        'services': ['bank', 'gas_station', 'hospital', 'school'],
        'entertainment': ['movie_theater', 'park', 'gym', 'bar']
    }
    
    bounds = {
        'min_lat': 37.4419, 'max_lat': 37.9298,
        'min_lng': -122.5150, 'max_lng': -122.0700
    }
    
    for i in range(count):
        lat = random.uniform(bounds['min_lat'], bounds['max_lat'])
        lng = random.uniform(bounds['min_lng'], bounds['max_lng'])
        
        category = random.choice(list(categories.keys()))
        subcategory = random.choice(categories[category])
        
        cursor.execute("""
            INSERT INTO spatial_engine.poi (
                name, category, subcategory, description,
                rating, phone, geom
            ) VALUES (%s, %s, %s, %s, %s, %s, ST_Point(%s, %s))
        """, (
            fake.company(),
            category,
            subcategory,
            fake.text(max_nb_chars=200),
            round(random.uniform(2.0, 5.0), 1),
            fake.phone_number(),
            lng, lat
        ))
    
    conn.commit()
    cursor.close()
    print(f"Inserted {count} POI records")

if __name__ == "__main__":
    print("Generating sample spatial data...")
    generate_properties(10000)
    generate_poi(2000)
    print("Sample data generation complete!")
    conn.close()
