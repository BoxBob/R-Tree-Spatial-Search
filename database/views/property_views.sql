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
    p.updated_at
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
