# R-Tree Spatial Search API Documentation

## Authentication
Most endpoints require a Bearer token (OAuth2). Obtain a token via `/auth/token` (see implementation).

## Endpoints

### POST `/search/range`
Range search for properties within a bounding box.
- **Request Body:**
  ```json
  {
    "bounds": {
      "min_lng": -122.5,
      "min_lat": 37.7,
      "max_lng": -122.3,
      "max_lat": 37.8
    }
  }
  ```
- **Response:** List of properties.

### GET `/health`
Health check for API and R-tree engine.
- **Response:**
  ```json
  {
    "status": "healthy",
    "engine": "C++ R-tree",
    "indexed_properties": "Ready for queries"
  }
  ```

### POST `/api/v1/advanced/search/polygon`
Search properties within a custom polygon.
- **Request Body:**
  ```json
  {
    "polygon_coordinates": [[-122.5,37.7],[-122.4,37.7],[-122.4,37.8],[-122.5,37.8]],
    "max_price": 1000000,
    "min_bedrooms": 2
  }
  ```
- **Response:** List of properties.

### POST `/api/v1/advanced/search/proximity`
Find properties near specific amenities.
- **Request Body:**
  ```json
  {
    "amenity_type": "school",
    "distance_km": 1.0,
    "max_price": 800000
  }
  ```
- **Response:** List of properties.

### GET `/api/v1/advanced/search/districts`
Get property distribution by districts.
- **Response:**
  ```json
  {
    "DistrictA": {
      "count": 10,
      "avg_price": 750000,
      "properties": [ ... ]
    },
    "DistrictB": { ... }
  }
  ```

## Models
- `Property`: id, property_type, price, bedrooms, lng, lat, address, bathrooms
- `Bounds`: min_lng, min_lat, max_lng, max_lat
- `RangeQuery`: bounds
- `PolygonQueryRequest`: polygon_coordinates, max_price, min_bedrooms
- `ProximityQueryRequest`: amenity_type, distance_km, max_price

## Error Handling
- 401 Unauthorized: Invalid/missing token
- 500 Internal Server Error: Query failures

## Example Usage
See README for curl and Python examples.

## Contact
See `docs/README.md` for support and contributing.
