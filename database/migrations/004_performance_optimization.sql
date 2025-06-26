-- Migration: Performance optimization
-- This migration adds indexes and materialized views for query performance.

-- Add a BRIN index for time-based queries
CREATE INDEX IF NOT EXISTS idx_properties_created_brin
ON core.properties USING BRIN (created_at);

-- Materialized view for fast property counts by city
CREATE MATERIALIZED VIEW IF NOT EXISTS analytics.city_property_counts AS
SELECT city, COUNT(*) as property_count
FROM core.properties
WHERE is_active = TRUE
GROUP BY city;

-- (Add more indexes, views, or performance-related SQL as needed)
