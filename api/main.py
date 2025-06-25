# api/main.py
import psycopg2
import redis
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import json

# --- Connection Pooling ---
def get_db_connection():
    import os
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", 5432)
    conn = psycopg2.connect(
        host=host,
        port=port,
        database=os.getenv("POSTGRES_DB", "spatial_search_db"),
        user=os.getenv("POSTGRES_USER", "spatial_user"),
        password=os.getenv("POSTGRES_PASSWORD", "spatial_password")
    )
    try:
        yield conn
    finally:
        conn.close()

def get_redis_connection():
    import os
    r = redis.Redis(
        host=os.getenv("REDIS_HOST", "redis"),
        port=int(os.getenv("REDIS_PORT", 6379)),
        password=os.getenv("REDIS_PASSWORD", None),
        db=0, decode_responses=True
    )
    try:
        yield r
    finally:
        r.close()

# --- FastAPI Setup ---
app = FastAPI(
    title="R-tree Spatial Search API",
    description="High-performance spatial search engine with custom R-tree implementation",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models ---
class Point(BaseModel):
    lng: float
    lat: float

class BoundingBox(BaseModel):
    min_lng: float
    min_lat: float
    max_lng: float
    max_lat: float

class RangeQuery(BaseModel):
    bounds: BoundingBox
    filters: Optional[dict] = {}

class KNNQuery(BaseModel):
    center: Point
    k: int = 10
    radius_km: Optional[float] = None
    filters: Optional[dict] = {}

class Property(BaseModel):
    id: int
    property_type: str
    price: float
    bedrooms: int
    lng: float
    lat: float
    address: str = "N/A"
    bathrooms: float = 0.0

# --- API Endpoints ---
@app.post("/search/range", response_model=List[Property])
async def range_search(query: RangeQuery, db=Depends(get_db_connection)):
    """Range search using the PostGIS GIST R-tree index."""
    bounds = query.bounds
    cursor = db.cursor()
    cursor.execute(
        "SELECT * FROM spatial_engine.get_properties_in_bounds(%s, %s, %s, %s);",
        (bounds.min_lng, bounds.min_lat, bounds.max_lng, bounds.max_lat)
    )
    results = cursor.fetchall()
    cursor.close()
    properties = []
    for row in results:
        geom_data = json.loads(row[4]) # row[4] is geom_json
        properties.append(Property(
            id=row[0],
            property_type=row[1],
            price=row[2],
            bedrooms=row[3],
            lng=geom_data['coordinates'][0],
            lat=geom_data['coordinates'][1],
            address="N/A",
            bathrooms=0.0
        ))
    return properties

@app.post("/search/knn", response_model=List[Property])
async def knn_search(query: KNNQuery, db=Depends(get_db_connection)):
    """K-nearest neighbor search using the PostGIS distance operator."""
    center = query.center
    cursor = db.cursor()
    sql_query = """
    SELECT id, property_type, price, bedrooms, ST_AsGeoJSON(geom)::JSON
    FROM spatial_engine.properties
    ORDER BY geom <-> ST_SetSRID(ST_MakePoint(%s, %s), 4326)
    LIMIT %s;
    """
    cursor.execute(sql_query, (center.lng, center.lat, query.k))
    results = cursor.fetchall()
    cursor.close()
    properties = []
    for row in results:
        geom_data = json.loads(row[4])
        properties.append(Property(
            id=row[0], property_type=row[1], price=row[2], bedrooms=row[3],
            lng=geom_data['coordinates'][0], lat=geom_data['coordinates'][1],
            address="N/A", bathrooms=0.0
        ))
    return properties

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "rtree-spatial-search"}
