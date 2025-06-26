-- Analytics: query_performance
CREATE TABLE IF NOT EXISTS analytics.query_performance (
    id BIGSERIAL PRIMARY KEY,
    query_text TEXT NOT NULL,
    execution_time_ms DECIMAL(10,3) NOT NULL,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
