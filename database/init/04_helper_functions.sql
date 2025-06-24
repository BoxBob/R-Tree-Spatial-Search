-- Function to calculate MBR for your R-tree engine
CREATE OR REPLACE FUNCTION spatial_engine.get_mbr(geom GEOMETRY)
RETURNS JSON AS $$
BEGIN
    RETURN json_build_object(
        'min_x', ST_XMin(geom),
        'min_y', ST_YMin(geom),
        'max_x', ST_XMax(geom),
        'max_y', ST_YMax(geom)
    );
END;
$$ LANGUAGE plpgsql;

-- Function to log queries for R-tree optimization
CREATE OR REPLACE FUNCTION spatial_engine.log_spatial_query(
    p_query_type VARCHAR,
    p_bounds_geom GEOMETRY DEFAULT NULL,
    p_center_point GEOMETRY DEFAULT NULL,
    p_radius_meters INTEGER DEFAULT NULL,
    p_k_value INTEGER DEFAULT NULL,
    p_execution_time_ms INTEGER DEFAULT NULL,
    p_results_count INTEGER DEFAULT NULL,
    p_user_session VARCHAR DEFAULT NULL
) RETURNS INTEGER AS $$
DECLARE
    query_id INTEGER;
BEGIN
    INSERT INTO spatial_engine.query_logs (
        query_type, bounds_geom, center_point, radius_meters,
        k_value, execution_time_ms, results_count, user_session
    )
    VALUES (
        p_query_type, p_bounds_geom, p_center_point, p_radius_meters,
        p_k_value, p_execution_time_ms, p_results_count, p_user_session
    )
    RETURNING id INTO query_id;
    
    RETURN query_id;
END;
$$ LANGUAGE plpgsql;

-- Function to get properties in bounding box (for R-tree comparison)
CREATE OR REPLACE FUNCTION spatial_engine.get_properties_in_bounds(
    min_x DECIMAL, min_y DECIMAL, max_x DECIMAL, max_y DECIMAL
) RETURNS TABLE (
    id INTEGER,
    property_type VARCHAR,
    price DECIMAL,
    bedrooms INTEGER,
    geom_json JSON
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        p.id,
        p.property_type,
        p.price,
        p.bedrooms,
        ST_AsGeoJSON(p.geom)::JSON as geom_json
    FROM spatial_engine.properties p
    WHERE ST_Intersects(
        p.geom,
        ST_MakeEnvelope(min_x, min_y, max_x, max_y, 4326)
    );
END;
$$ LANGUAGE plpgsql;
