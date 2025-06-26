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
GRANT INSERT ON analytics.query_performance TO spatial_api_user;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA core TO spatial_api_user;

-- Readonly permissions
GRANT SELECT ON ALL TABLES IN SCHEMA core TO spatial_readonly;
GRANT SELECT ON ALL TABLES IN SCHEMA analytics TO spatial_readonly;

-- Grant permissions on views
GRANT SELECT ON core.v_active_properties TO spatial_api_user, spatial_readonly;
GRANT SELECT ON core.v_properties_with_rtree TO spatial_api_user, spatial_readonly;
GRANT SELECT ON core.v_property_stats_by_city TO spatial_api_user, spatial_readonly;
