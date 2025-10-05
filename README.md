
# R-Tree Spatial Search

Spatial property search platform using a C++ R-tree engine, FastAPI, and PostgreSQL/PostGIS.

## Features
- High-performance spatial queries (range, polygon, proximity)
- Advanced analytics (district distribution, amenity proximity)
- ETL pipeline for property/amenity data
- Dockerized deployment

## Architecture
- **Backend:** FastAPI, C++ R-tree engine (Python bindings), PostgreSQL/PostGIS
- **Frontend:** React (see `frontend/`)
- **ETL:** Python scripts for ingesting property/amenity/boundary data

## Setup
### Prerequisites
- Docker & Docker Compose (recommended)
- Python 3.11+
- PostgreSQL with PostGIS extension

### Quick Start (Docker)
```sh
docker-compose up --build
```

### Manual Setup
1. Install Python dependencies:
	 ```sh
	 pip install -r requirements.txt
	 pip install -r api/requirements.txt
	 ```
2. Build C++ R-tree engine (see `rtree_engine/README.md`)
3. Initialize database:
	 ```sh
	 python scripts/setup_database.py
	 ```
4. Run API:
	 ```sh
	 uvicorn api.main:app --reload
	 ```

## Usage
### API Endpoints
See [API Documentation](#api-documentation) below.

### ETL
Run ETL scripts to ingest data:
```sh
python etl/etl_runner.py
```

### Testing
```sh
pytest api/tests/
pytest etl/tests/
```

## Database
- Initialization scripts: `database/setup/`
- Schemas: `database/schemas/`
- Functions, indexes, triggers: `database/functions/`, `database/indexes/`, `database/triggers/`

## API Documentation

### Authentication
Most endpoints require a Bearer token (OAuth2).

### Endpoints

#### `POST /search/range`
Range search for properties within bounding box.
**Request:**
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
**Response:** List of properties.

#### `GET /health`
Health check for API and R-tree engine.

#### `POST /api/v1/advanced/search/polygon`
Search properties within a custom polygon.
**Request:**
```json
{
	"polygon_coordinates": [[-122.5,37.7],[-122.4,37.7],[-122.4,37.8],[-122.5,37.8]],
	"max_price": 1000000,
	"min_bedrooms": 2
}
```
**Response:** List of properties.

#### `POST /api/v1/advanced/search/proximity`
Find properties near specific amenities.
**Request:**
```json
{
	"amenity_type": "school",
	"distance_km": 1.0,
	"max_price": 800000
}
```
**Response:** List of properties.

#### `GET /api/v1/advanced/search/districts`
Get property distribution by districts.
**Response:** District stats (count, avg_price, properties).

## Contributing
See `docs/README.md` for guidelines.

## License
MIT
