-- =====================================================
-- Audit Triggers for Data Tracking
-- File: database/triggers/audit_triggers.sql
-- =====================================================

-- Trigger for property spatial metadata updates
DROP TRIGGER IF EXISTS trg_property_spatial_update ON core.properties;
CREATE TRIGGER trg_property_spatial_update
    BEFORE INSERT OR UPDATE ON core.properties
    FOR EACH ROW
    EXECUTE FUNCTION core.update_property_spatial_metadata();

-- Audit table for property changes
CREATE TABLE IF NOT EXISTS core.property_audit (
    audit_id BIGSERIAL PRIMARY KEY,
    property_id BIGINT NOT NULL,
    operation VARCHAR(10) NOT NULL, -- INSERT, UPDATE, DELETE
    old_values JSONB,
    new_values JSONB,
    changed_by VARCHAR(100),
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Audit trigger function
CREATE OR REPLACE FUNCTION core.property_audit_trigger()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'DELETE' THEN
        INSERT INTO core.property_audit (property_id, operation, old_values, changed_by)
        VALUES (OLD.id, 'DELETE', row_to_json(OLD), USER);
        RETURN OLD;
    ELSIF TG_OP = 'UPDATE' THEN
        INSERT INTO core.property_audit (property_id, operation, old_values, new_values, changed_by)
        VALUES (NEW.id, 'UPDATE', row_to_json(OLD), row_to_json(NEW), USER);
        RETURN NEW;
    ELSIF TG_OP = 'INSERT' THEN
        INSERT INTO core.property_audit (property_id, operation, new_values, changed_by)
        VALUES (NEW.id, 'INSERT', row_to_json(NEW), USER);
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Create audit trigger
DROP TRIGGER IF EXISTS trg_property_audit ON core.properties;
CREATE TRIGGER trg_property_audit
    AFTER INSERT OR UPDATE OR DELETE ON core.properties
    FOR EACH ROW
    EXECUTE FUNCTION core.property_audit_trigger();
