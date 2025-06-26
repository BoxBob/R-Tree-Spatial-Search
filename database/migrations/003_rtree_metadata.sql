-- Migration: R-tree metadata
-- This migration adds metadata tables and views for R-tree structure monitoring and maintenance.

-- Table to track R-tree maintenance and statistics
CREATE TABLE IF NOT EXISTS core.rtree_metadata (
    id SERIAL PRIMARY KEY,
    last_rebuild TIMESTAMP,
    node_count INTEGER,
    leaf_count INTEGER,
    max_depth INTEGER,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- View to summarize R-tree node distribution by level
CREATE OR REPLACE VIEW core.v_rtree_node_levels AS
SELECT level, COUNT(*) AS node_count
FROM core.rtree_nodes
GROUP BY level
ORDER BY level;

-- (Add more metadata tables or views as needed)
