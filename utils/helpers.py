"""
Utility Helper Functions
File: src/spatial_search_engine/utils/helpers.py
"""

import hashlib
import json
from typing import Any, Dict, List, Tuple
import geohash
from shapely.geometry import Point, Polygon
import logging

def calculate_geohash(latitude: float, longitude: float, precision: int = 8) -> str:
    """Calculate geohash for spatial indexing"""
    return geohash.encode(latitude, longitude, precision)

def validate_coordinates(latitude: float, longitude: float) -> bool:
    """Validate geographic coordinates"""
    return -90 <= latitude <= 90 and -180 <= longitude <= 180

def calculate_bounding_box(points: List[Tuple[float, float]]) -> Tuple[float, float, float, float]:
    """Calculate minimum bounding box for a list of points"""
    if not points:
        return 0, 0, 0, 0
    
    lats = [p[0] for p in points]
    lngs = [p[1] for p in points]
    
    return min(lngs), min(lats), max(lngs), max(lats)

def generate_query_hash(query_params: Dict[str, Any]) -> str:
    """Generate hash for query caching"""
    query_string = json.dumps(query_params, sort_keys=True)
    return hashlib.md5(query_string.encode()).hexdigest()

def setup_logging(name: str, level: str = 'INFO') -> logging.Logger:
    """Setup standardized logging"""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))
    
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger

def validate_polygon_coordinates(coordinates: List[List[float]]) -> bool:
    """Validate polygon coordinates"""
    try:
        if len(coordinates) < 3:
            return False
        
        # Check if polygon is closed
        if coordinates[0] != coordinates[-1]:
            coordinates.append(coordinates[0])
        
        # Validate each coordinate pair
        for coord in coordinates:
            if len(coord) != 2 or not validate_coordinates(coord[1], coord[0]):
                return False
        
        # Try to create shapely polygon
        polygon = Polygon(coordinates)
        return polygon.is_valid
        
    except Exception:
        return False
