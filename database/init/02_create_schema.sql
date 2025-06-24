-- Create schema for spatial search engine
CREATE SCHEMA IF NOT EXISTS spatial_engine;

-- Properties table (main spatial data)
CREATE TABLE spatial_engine.properties (
    id SERIAL PRIMARY KEY,
    property_type VARCHAR(50) NOT NULL,
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(20),
    price DECIMAL(12,2),
    bedrooms INTEGER,
    bathrooms DECIMAL(3,1),
    square_feet INTEGER,
    lot_size DECIMAL(10,2),
    year_built INTEGER,
    geom GEOMETRY(POINT, 4326) NOT NULL,
    bounds GEOMETRY(POLYGON, 4326),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Points of Interest table
CREATE TABLE spatial_engine.poi (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    category VARCHAR(100),
    subcategory VARCHAR(100),
    description TEXT,
    rating DECIMAL(3,2),
    phone VARCHAR(20),
    website VARCHAR(500),
    geom GEOMETRY(POINT, 4326) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Administrative boundaries
CREATE TABLE spatial_engine.boundaries (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    boundary_type VARCHAR(50), -- city, county, state, zip
    code VARCHAR(20),
    population INTEGER,
    area_sq_km DECIMAL(12,4),
    geom GEOMETRY(MULTIPOLYGON, 4326) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Search query logs (for your R-tree optimization)
CREATE TABLE spatial_engine.query_logs (
    id SERIAL PRIMARY KEY,
    query_type VARCHAR(50), -- range, knn, polygon
    bounds_geom GEOMETRY(POLYGON, 4326),
    center_point GEOMETRY(POINT, 4326),
    radius_meters INTEGER,
    k_value INTEGER, -- for k-NN queries
    execution_time_ms INTEGER,
    results_count INTEGER,
    user_session VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Performance metrics table
CREATE TABLE spatial_engine.performance_metrics (
    id SERIAL PRIMARY KEY,
    metric_name VARCHAR(100),
    metric_value DECIMAL(15,6),
    query_id INTEGER REFERENCES spatial_engine.query_logs(id),
    rtree_depth INTEGER,
    rtree_nodes_accessed INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
