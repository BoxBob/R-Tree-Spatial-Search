-- Spatial indexes for fast queries
CREATE INDEX idx_properties_geom ON spatial_engine.properties USING GIST (geom);
CREATE INDEX idx_properties_bounds ON spatial_engine.properties USING GIST (bounds);
CREATE INDEX idx_poi_geom ON spatial_engine.poi USING GIST (geom);
CREATE INDEX idx_boundaries_geom ON spatial_engine.boundaries USING GIST (geom);
CREATE INDEX idx_query_logs_bounds ON spatial_engine.query_logs USING GIST (bounds_geom);
CREATE INDEX idx_query_logs_center ON spatial_engine.query_logs USING GIST (center_point);

-- Non-spatial indexes for filtering
CREATE INDEX idx_properties_type ON spatial_engine.properties (property_type);
CREATE INDEX idx_properties_price ON spatial_engine.properties (price);
CREATE INDEX idx_properties_bedrooms ON spatial_engine.properties (bedrooms);
CREATE INDEX idx_properties_city ON spatial_engine.properties (city);
CREATE INDEX idx_poi_category ON spatial_engine.poi (category);
CREATE INDEX idx_query_logs_type ON spatial_engine.query_logs (query_type);
CREATE INDEX idx_query_logs_created ON spatial_engine.query_logs (created_at);

-- Composite indexes for common queries
CREATE INDEX idx_properties_type_price ON spatial_engine.properties (property_type, price);
CREATE INDEX idx_properties_bed_bath ON spatial_engine.properties (bedrooms, bathrooms);
