import sys
import os
# Add the absolute path to the rtree_engine module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../rtree_engine')))
import rtree_engine
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import psycopg2
from pydantic import BaseModel
from database.connection import db

app = FastAPI()

# Initialize the C++ R-tree engine
spatial_engine = rtree_engine.SpatialSearchEngine()
rtree_index = rtree_engine.RTree()
# Define RangeQuery and Bounds models
class Bounds(BaseModel):
    min_lng: float
    min_lat: float
    max_lng: float
    max_lat: float

class RangeQuery(BaseModel):
    bounds: Bounds

class Property(BaseModel):
    id: int
    property_type: str
    price: float
    bedrooms: int
    lng: float
    lat: float
    address: str
    bathrooms: float = 0.0

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

@app.on_event("startup")
async def startup_event():
    """Load existing spatial data into the R-tree engine"""
    await load_spatial_data()
    await load_spatial_data()

async def load_spatial_data():
    """Load property data from database into R-tree"""
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        database=os.getenv("DB_NAME", "postgres"),
        user=os.getenv("DB_USER", "spatial_user"),
        password=os.getenv("DB_PASSWORD", "spatial_password")
    )
    
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, ST_X(geom) as lng, ST_Y(geom) as lat 
        FROM core.properties
    """)
    
    count = 0
    for row in cursor.fetchall():
        property_id, lng, lat = row
        point = rtree_engine.create_point(lng, lat)
        rtree_index.insert(point, property_id)
        count += 1
    
    cursor.close()
    conn.close()
    print(f"✅ Loaded {count} properties into C++ R-tree engine")

@app.post("/search/range")
async def range_search(query: RangeQuery, token: str = Depends(oauth2_scheme)):
    """Range search using the C++ R-tree engine and new DB connection logic"""
    bounds = query.bounds
    search_rect = rtree_engine.create_rectangle(
        bounds.min_lng, bounds.min_lat,
        bounds.max_lng, bounds.max_lat
    )
    property_ids = rtree_index.search(search_rect)
    if not property_ids:
        return []
    with db.get_connection() as db_conn:
        cursor = db_conn.cursor()
        placeholders = ','.join(['%s'] * len(property_ids))
        cursor.execute(f"""
            SELECT id, property_type, price, bedrooms, 
                   ST_X(geom) as lng, ST_Y(geom) as lat, address
            FROM core.properties 
            WHERE id IN ({placeholders})
        """, property_ids)
        results = cursor.fetchall()
        cursor.close()
    properties = [
        Property(
            id=row[0], property_type=row[1], price=row[2], 
            bedrooms=row[3], lng=row[4], lat=row[5],
            address=row[6], bathrooms=0.0
        ) for row in results
    ]
    return properties

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "engine": "C++ R-tree",
        "indexed_properties": "Ready for queries"
    }
