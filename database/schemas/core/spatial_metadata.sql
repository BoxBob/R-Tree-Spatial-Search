-- =====================================================
-- Spatial Metadata Schema including R-tree Integration
-- File: database/schemas/core/spatial_metadata.sql
-- Purpose: Define spatial metadata and R-tree node structure
-- =====================================================

-- Ensure core schema exists
CREATE SCHEMA IF NOT EXISTS core;

-- =====================================================
-- R-TREE METADATA TABLES
-- =====================================================

-- R-tree nodes table for hybrid PostGIS/R-tree approach
CREATE TABLE IF NOT EXISTS core.rtree_nodes (
    node_id BIGSERIAL PRIMARY KEY,
    parent_id BIGINT REFERENCES core.rtree_nodes(node_id) ON DELETE CASCADE,
    level INTEGER NOT NULL DEFAULT 0 CHECK (level >= 0),
    is_leaf BOOLEAN DEFAULT FALSE,
    
    -- Minimum Bounding Rectangle coordinates
    mbr_min_x DOUBLE PRECISION NOT NULL,
    mbr_min_y DOUBLE PRECISION NOT NULL,
    mbr_max_x DOUBLE PRECISION NOT NULL,
    mbr_max_y DOUBLE PRECISION NOT NULL,
    
    -- Performance optimization fields
    child_count INTEGER DEFAULT 0 CHECK (child_count >= 0),
    property_count INTEGER DEFAULT 0 CHECK (property_count >= 0),
    
    -- Metadata
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Computed spatial geometry for PostGIS integration
    mbr_geom GEOMETRY(POLYGON, 4326) GENERATED ALWAYS AS (
        ST_MakeEnvelope(mbr_min_x, mbr_min_y, mbr_max_x, mbr_max_y, 4326)
    ) STORED,
    
    -- Constraints
    CONSTRAINT valid_mbr CHECK (
        mbr_min_x <= mbr_max_x AND mbr_min_y <= mbr_max_y
    ),
    CONSTRAINT valid_coordinates CHECK (
        mbr_min_x >= -180 AND mbr_max_x <= 180 AND
        mbr_min_y >= -90 AND mbr_max_y <= 90
    )
);

-- Property-node mapping for R-tree leaf entries
CREATE TABLE IF NOT EXISTS core.rtree_entries (
    entry_id BIGSERIAL PRIMARY KEY,
    property_id BIGINT NOT NULL,
    node_id BIGINT NOT NULL REFERENCES core.rtree_nodes(node_id) ON DELETE CASCADE,
    
    -- Entry-specific MBR (for leaf nodes)
    mbr_min_x DOUBLE PRECISION,
    mbr_min_y DOUBLE PRECISION,
    mbr_max_x DOUBLE PRECISION,
    mbr_max_y DOUBLE PRECISION,
    
    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    UNIQUE(property_id, node_id),
    CONSTRAINT valid_entry_mbr CHECK (
        (mbr_min_x IS NULL AND mbr_min_y IS NULL AND mbr_max_x IS NULL AND mbr_max_y IS NULL) OR
        (mbr_min_x <= mbr_max_x AND mbr_min_y <= mbr_max_y)
    )
);

-- =====================================================
-- GENERAL SPATIAL METADATA TABLES
-- =====================================================

-- Spatial reference systems metadata (if you need custom SRS)
CREATE TABLE IF NOT EXISTS core.spatial_reference_systems (
    srid INTEGER PRIMARY KEY,
    auth_name VARCHAR(256),
    auth_srid INTEGER,
    srtext VARCHAR(2048),
    proj4text VARCHAR(2048),
    description TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Spatial data quality tracking
CREATE TABLE IF NOT EXISTS core.spatial_data_quality (
    id BIGSERIAL PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    geometry_column VARCHAR(100) NOT NULL,
    total_records INTEGER,
    valid_geometries INTEGER,
    invalid_geometries INTEGER,
    null_geometries INTEGER,
    quality_score DECIMAL(5,4),
    last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT valid_quality_score CHECK (quality_score >= 0 AND quality_score <= 1)
);

-- Spatial index performance tracking
CREATE TABLE IF NOT EXISTS core.spatial_index_stats (
    id BIGSERIAL PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    index_name VARCHAR(100) NOT NULL,
    index_type VARCHAR(50), -- GIST, BRIN, etc.
    size_bytes BIGINT,
    last_analyzed TIMESTAMP,
    avg_query_time_ms DECIMAL(10,3),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
