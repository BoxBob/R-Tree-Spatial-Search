-- Enable PostGIS extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;
CREATE EXTENSION IF NOT EXISTS fuzzystrmatch;
CREATE EXTENSION IF NOT EXISTS postgis_tiger_geocoder;

-- Create spatial reference system if needed
-- EPSG:4326 (WGS84) is default, but you can add custom ones

-- Verify installation
SELECT PostGIS_Version();
SELECT ST_AsText(ST_Point(-71.060316, 42.358431));
