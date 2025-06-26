-- =====================================================
-- Spatial Functions for R-tree Integration
-- File: database/functions/spatial_functions.sql
-- =====================================================

-- ========================================
-- Function: calculate_geohash
-- Purpose:  Calculate geohash from lat/lng using PostGIS
-- ========================================


-- ========================================
-- Function: update_property_spatial_metadata
-- Purpose:  Trigger function to update spatial metadata fields
-- ========================================
CREATE OR REPLACE FUNCTION core.update_property_spatial_metadata()
RETURNS TRIGGER AS $$
BEGIN
    -- Automatically update geohash
    NEW.spatial_hash := core.calculate_geohash(ST_Y(NEW.geom), ST_X(NEW.geom));
    
    -- Store the geometry in Web Mercator for spatial distance calculations
    NEW.geom_mercator := ST_Transform(NEW.geom, 3857);
    
    -- Update modification timestamp
    NEW.updated_at := CURRENT_TIMESTAMP;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- ========================================
-- Function: estimate_spatial_query_count
-- Purpose:  Estimate number of results in a bounding box query
-- ========================================
CREATE OR REPLACE FUNCTION core.estimate_spatial_query_count(
    min_lng DOUBLE PRECISION,
    min_lat DOUBLE PRECISION,
    max_lng DOUBLE PRECISION,
    max_lat DOUBLE PRECISION
)
RETURNS INTEGER AS $$
DECLARE
    estimated_count INTEGER;
BEGIN
    -- Count how many properties fall inside the bounding box and are active
    SELECT COUNT(*)::INTEGER INTO estimated_count
    FROM core.properties
    WHERE ST_Intersects(
        geom,
        ST_MakeEnvelope(min_lng, min_lat, max_lng, max_lat, 4326)
    ) AND is_active = TRUE;

    RETURN estimated_count;
END;
$$ LANGUAGE plpgsql STABLE;
