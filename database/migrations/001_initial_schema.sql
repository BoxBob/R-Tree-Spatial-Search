-- =====================================================
-- Initial Schema Migration
-- File: database/migrations/001_initial_schema.sql
-- Purpose: Create initial database structure
-- =====================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS core;
CREATE SCHEMA IF NOT EXISTS analytics;
CREATE SCHEMA IF NOT EXISTS admin;

-- Execute core schema files in correct order
\i database/schemas/core/properties.sql
\i database/schemas/core/spatial_metadata.sql

-- Add foreign key constraints after all tables are created
ALTER TABLE core.rtree_entries 
ADD CONSTRAINT fk_rtree_entries_property 
FOREIGN KEY (property_id) REFERENCES core.properties(id) ON DELETE CASCADE;

ALTER TABLE core.properties 
ADD CONSTRAINT fk_properties_rtree_node 
FOREIGN KEY (rtree_node_id) REFERENCES core.rtree_nodes(node_id) ON DELETE SET NULL;
