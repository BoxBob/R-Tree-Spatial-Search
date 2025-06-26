-- Core properties table with optimized spatial design
CREATE SCHEMA IF NOT EXISTS core;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS admin;

-- Main properties table
CREATE TABLE core.properties (
    id BIGSERIAL PRIMARY KEY,
    -- Property identification
    external_id VARCHAR(100) UNIQUE,
    mls_id VARCHAR(50),
    
    -- Location data
    address TEXT NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(50) NOT NULL,
    zip_code VARCHAR(10),
    county VARCHAR(100),
    
    -- Property details
    price DECIMAL(15,2) CHECK (price >= 0),
    bedrooms SMALLINT CHECK (bedrooms >= 0),
    bathrooms DECIMAL(3,1) CHECK (bathrooms >= 0),
    square_feet INTEGER CHECK (square_feet >= 0),
    lot_size DECIMAL(10,2),
    property_type VARCHAR(50) NOT NULL,
    year_built SMALLINT,
    
    -- Spatial data (optimized for R-tree integration)
    geom GEOMETRY(POINT, 4326) NOT NULL,
    geom_mercator GEOMETRY(POINT, 3857), -- For distance calculations
    
    -- R-tree integration fields
    rtree_node_id BIGINT,
    spatial_hash VARCHAR(20), -- Geohash for quick spatial grouping
    
    -- Data quality and metadata
    data_source VARCHAR(50) NOT NULL,
    data_quality_score DECIMAL(3,2) DEFAULT 1.0,
    last_verified TIMESTAMP,
    
    -- Audit fields
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(100),
    updated_by VARCHAR(100),
    
    -- Soft delete
    is_active BOOLEAN DEFAULT TRUE,
    deleted_at TIMESTAMP
);
