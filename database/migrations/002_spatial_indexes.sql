-- =====================================================
-- Spatial Indexes Migration
-- File: database/migrations/002_spatial_indexes.sql
-- Purpose: Create optimized spatial indexes
-- =====================================================

-- Primary spatial indexes for properties
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_geom_gist 
ON core.properties USING GIST (geom);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_geom_mercator_gist 
ON core.properties USING GIST (geom_mercator) 
WHERE geom_mercator IS NOT NULL;

-- R-tree specific indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_rtree_nodes_mbr_gist 
ON core.rtree_nodes USING GIST (mbr_geom);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_rtree_nodes_parent 
ON core.rtree_nodes (parent_id) 
WHERE parent_id IS NOT NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_rtree_nodes_level 
ON core.rtree_nodes (level, is_leaf);

-- Property optimization indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_active_price 
ON core.properties (price, bedrooms) 
WHERE is_active = TRUE;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_city_type 
ON core.properties (city, property_type) 
WHERE is_active = TRUE;

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_spatial_hash 
ON core.properties (spatial_hash) 
WHERE spatial_hash IS NOT NULL;

-- R-tree entries indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_rtree_entries_node 
ON core.rtree_entries (node_id);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_rtree_entries_property 
ON core.rtree_entries (property_id);

-- Time-based indexes for large datasets
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_properties_created_brin 
ON core.properties USING BRIN (created_at);
