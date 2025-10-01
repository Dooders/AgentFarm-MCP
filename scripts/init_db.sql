-- PostgreSQL Database Initialization Script
-- This script is automatically run when PostgreSQL container starts

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create schema if needed
CREATE SCHEMA IF NOT EXISTS public;

-- Grant permissions
GRANT ALL PRIVILEGES ON SCHEMA public TO agentfarm;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO agentfarm;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO agentfarm;

-- Set default privileges for future tables
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON TABLES TO agentfarm;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL PRIVILEGES ON SEQUENCES TO agentfarm;

-- Create a sample configuration table (optional)
CREATE TABLE IF NOT EXISTS db_metadata (
    key VARCHAR(255) PRIMARY KEY,
    value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO db_metadata (key, value) VALUES 
    ('version', '1.0.0'),
    ('initialized_at', CURRENT_TIMESTAMP::TEXT)
ON CONFLICT (key) DO NOTHING;

-- Index optimization for common queries
-- These will be created by SQLAlchemy models, but we can add custom ones here

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'AgentFarm database initialized successfully';
END $$;
