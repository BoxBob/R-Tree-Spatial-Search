-- =====================================================
-- Flat Database Initialization Script (psycopg2 compatible)
-- File: database/setup/init_database_flat.sql
-- Purpose: Contains only valid SQL for programmatic execution (no psql meta-commands)
-- Verified: All DO/function blocks and statements are properly closed and terminated with semicolons. No unterminated dollar-quoted strings. [2025-06-27]
-- =====================================================

-- ===== MIGRATION: 001_initial_schema.sql =====
-- =====================================================
-- Initial Schema Migration
-- File: database/migrations/001_initial_schema.sql
-- Purpose: Create initial database structure
-- =====================================================

-- Enable required extensions (run as superuser only, not in this script)
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS core;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS admin;

-- Core properties table with optimized spatial design
-- ...existing code...

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

-- =====================================================
-- Spatial Metadata Schema including R-tree Integration
-- File: database/schemas/core/spatial_metadata.sql
-- Purpose: Define spatial metadata and R-tree node structure
-- =====================================================

-- Ensure core schema exists
CREATE SCHEMA IF NOT EXISTS core;

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

-- Add foreign key constraints after all tables are created
ALTER TABLE core.rtree_entries 
ADD CONSTRAINT fk_rtree_entries_property 
FOREIGN KEY (property_id) REFERENCES core.properties(id) ON DELETE CASCADE;

ALTER TABLE core.properties 
ADD CONSTRAINT fk_properties_rtree_node 
FOREIGN KEY (rtree_node_id) REFERENCES core.rtree_nodes(node_id) ON DELETE SET NULL;

-- ===== MIGRATION: 002_spatial_indexes.sql =====
-- =====================================================
-- Spatial Indexes Migration
-- File: database/migrations/002_spatial_indexes.sql
-- Purpose: Create optimized spatial indexes
-- =====================================================

-- Primary spatial indexes for properties
CREATE INDEX IF NOT EXISTS idx_properties_geom_gist 
ON core.properties USING GIST (geom);

CREATE INDEX IF NOT EXISTS idx_properties_geom_mercator_gist 
ON core.properties USING GIST (geom_mercator) 
WHERE geom_mercator IS NOT NULL;

-- R-tree specific indexes
CREATE INDEX IF NOT EXISTS idx_rtree_nodes_mbr_gist 
ON core.rtree_nodes USING GIST (mbr_geom);

CREATE INDEX IF NOT EXISTS idx_rtree_nodes_parent 
ON core.rtree_nodes (parent_id) 
WHERE parent_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_rtree_nodes_level 
ON core.rtree_nodes (level, is_leaf);

-- Property optimization indexes
CREATE INDEX IF NOT EXISTS idx_properties_active_price 
ON core.properties (price, bedrooms) 
WHERE is_active = TRUE;

CREATE INDEX IF NOT EXISTS idx_properties_city_type 
ON core.properties (city, property_type) 
WHERE is_active = TRUE;

CREATE INDEX IF NOT EXISTS idx_properties_spatial_hash 
ON core.properties (spatial_hash) 
WHERE spatial_hash IS NOT NULL;

-- R-tree entries indexes
CREATE INDEX IF NOT EXISTS idx_rtree_entries_node 
ON core.rtree_entries (node_id);

CREATE INDEX IF NOT EXISTS idx_rtree_entries_property 
ON core.rtree_entries (property_id);

-- Time-based indexes for large datasets
CREATE INDEX IF NOT EXISTS idx_properties_created_brin 
ON core.properties USING BRIN (created_at);

-- ===== MIGRATION: 003_rtree_metadata.sql =====
-- Migration: R-tree metadata
-- Add your R-tree metadata SQL here

-- ===== FUNCTIONS: spatial_functions.sql =====
-- =====================================================
-- Spatial Functions for R-tree Integration
-- File: database/functions/spatial_functions.sql
-- =====================================================

-- Function to calculate geohash for spatial grouping
CREATE OR REPLACE FUNCTION core.calculate_geohash(lat DOUBLE PRECISION, lng DOUBLE PRECISION, geohash_precision INTEGER DEFAULT 8)
RETURNS VARCHAR(20) AS $$
DECLARE
    geohash VARCHAR(20);
BEGIN
    -- Simple geohash implementation (you can use PostGIS ST_GeoHash for production)
    SELECT ST_GeoHash(ST_Point(lng, lat), geohash_precision) INTO geohash;
    RETURN geohash;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Function to update spatial metadata after property insert/update
CREATE OR REPLACE FUNCTION core.update_property_spatial_metadata()
RETURNS TRIGGER AS $$
BEGIN
    -- Update geohash
    NEW.spatial_hash := core.calculate_geohash(ST_Y(NEW.geom), ST_X(NEW.geom));
    
    -- Update mercator projection for distance calculations
    NEW.geom_mercator := ST_Transform(NEW.geom, 3857);
    
    -- Update timestamp
    NEW.updated_at := CURRENT_TIMESTAMP;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function to estimate query result count
CREATE OR REPLACE FUNCTION core.estimate_spatial_query_count(
    min_lng DOUBLE PRECISION,
    min_lat DOUBLE PRECISION,
    max_lng DOUBLE PRECISION,
    max_lat DOUBLE PRECISION
) RETURNS INTEGER AS $$
DECLARE
    estimated_count INTEGER;
BEGIN
    SELECT COUNT(*)::INTEGER INTO estimated_count
    FROM core.properties
    WHERE ST_Intersects(
        geom,
        ST_MakeEnvelope(min_lng, min_lat, max_lng, max_lat, 4326)
    ) AND is_active = TRUE;
    
    RETURN estimated_count;
END;
$$ LANGUAGE plpgsql STABLE;

-- ===== TRIGGERS: audit_triggers.sql =====
-- =====================================================
-- Audit Triggers for Data Tracking
-- File: database/triggers/audit_triggers.sql
-- =====================================================

-- Trigger for property spatial metadata updates
DROP TRIGGER IF EXISTS trg_property_spatial_update ON core.properties;
CREATE TRIGGER trg_property_spatial_update
    BEFORE INSERT OR UPDATE ON core.properties
    FOR EACH ROW
    EXECUTE FUNCTION core.update_property_spatial_metadata();

-- Audit table for property changes
CREATE TABLE IF NOT EXISTS core.property_audit (
    audit_id BIGSERIAL PRIMARY KEY,
    property_id BIGINT NOT NULL,
    operation VARCHAR(10) NOT NULL, -- INSERT, UPDATE, DELETE
    old_values JSONB,
    new_values JSONB,
    changed_by VARCHAR(100),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit trigger function
CREATE OR REPLACE FUNCTION core.property_audit_trigger()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        INSERT INTO core.property_audit (property_id, operation, old_values, changed_by)
        VALUES (OLD.id, 'DELETE', row_to_json(OLD), USER);
        RETURN OLD;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO core.property_audit (property_id, operation, old_values, new_values, changed_by)
        VALUES (NEW.id, 'UPDATE', row_to_json(OLD), row_to_json(NEW), USER);
        RETURN NEW;
    ELSIF TG_OP = 'INSERT' THEN
        INSERT INTO core.property_audit (property_id, operation, new_values, changed_by)
        VALUES (NEW.id, 'INSERT', row_to_json(NEW), USER);
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Create audit trigger
DROP TRIGGER IF EXISTS trg_property_audit ON core.properties;
CREATE TRIGGER trg_property_audit
    AFTER INSERT OR UPDATE OR DELETE ON core.properties
    FOR EACH ROW
    EXECUTE FUNCTION core.property_audit_trigger();

-- ===== VIEWS: property_views.sql =====
-- =====================================================
-- Property Views for Common Queries
-- File: database/views/property_views.sql
-- =====================================================

-- Active properties view with computed fields
CREATE OR REPLACE VIEW core.v_active_properties AS
SELECT 
    p.id,
    p.external_id,
    p.address,
    p.city,
    p.state,
    p.zip_code,
    p.price,
    p.bedrooms,
    p.bathrooms,
    p.square_feet,
    p.property_type,
    p.year_built,
    ST_X(p.geom) as longitude,
    ST_Y(p.geom) as latitude,
    p.spatial_hash,
    p.data_quality_score,
    -- Computed fields
    CASE 
        WHEN p.square_feet > 0 THEN p.price / p.square_feet 
        ELSE NULL 
    END as price_per_sqft,
    EXTRACT(YEAR FROM CURRENT_DATE) - p.year_built as property_age,
    p.created_at,
    p.updated_at,
    p.rtree_node_id
FROM core.properties p
WHERE p.is_active = TRUE AND p.deleted_at IS NULL;

-- Properties with R-tree node information
CREATE OR REPLACE VIEW core.v_properties_with_rtree AS
SELECT 
    p.*,
    rn.node_id,
    rn.level as rtree_level,
    rn.is_leaf as is_leaf_node
FROM core.v_active_properties p
LEFT JOIN core.rtree_nodes rn ON p.rtree_node_id = rn.node_id;

-- Property statistics by city
CREATE OR REPLACE VIEW core.v_property_stats_by_city AS
SELECT 
    city,
    state,
    COUNT(*) as property_count,
    AVG(price) as avg_price,
    MIN(price) as min_price,
    MAX(price) as max_price,
    AVG(bedrooms) as avg_bedrooms,
    AVG(square_feet) as avg_square_feet,
    AVG(data_quality_score) as avg_quality_score
FROM core.v_active_properties
GROUP BY city, state
ORDER BY property_count DESC;

-- ===== PERMISSIONS: grant_permissions.sql =====
-- =====================================================
-- Database Permissions Setup
-- File: database/setup/grant_permissions.sql
-- =====================================================

-- Create roles
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'spatial_admin') THEN
        CREATE ROLE spatial_admin;
    END IF;
END$$;
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'spatial_api_user') THEN
        CREATE ROLE spatial_api_user;
    END IF;
END$$;
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'spatial_readonly') THEN
        CREATE ROLE spatial_readonly;
    END IF;
END$$;

-- Grant schema usage
GRANT USAGE ON SCHEMA core TO spatial_admin, spatial_api_user, spatial_readonly;
GRANT USAGE ON SCHEMA analytics TO spatial_admin, spatial_api_user, spatial_readonly;
GRANT USAGE ON SCHEMA admin TO spatial_admin;

-- Admin permissions (full access)
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA core TO spatial_admin;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA core TO spatial_admin;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA core TO spatial_admin;

-- API user permissions (read/write for properties, read for others)
GRANT SELECT, INSERT, UPDATE ON core.properties TO spatial_api_user;
GRANT SELECT ON core.rtree_nodes, core.rtree_entries TO spatial_api_user;
-- GRANT INSERT ON analytics.query_performance TO spatial_api_user;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA core TO spatial_api_user;

-- Readonly permissions
GRANT SELECT ON ALL TABLES IN SCHEMA core TO spatial_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA analytics TO spatial_readonly;

-- Grant permissions on views
GRANT SELECT ON core.v_active_properties TO spatial_api_user, spatial_readonly;
GRANT SELECT ON core.v_properties_with_rtree TO spatial_api_user, spatial_readonly;
GRANT SELECT ON core.v_property_stats_by_city TO spatial_api_user, spatial_readonly;
