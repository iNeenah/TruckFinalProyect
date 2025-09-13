-- Initialize PostgreSQL database with PostGIS extension
-- This script runs automatically when the container starts for the first time

-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- Create initial database user if needed
-- (The main user is already created by the container)

-- Set timezone
SET timezone = 'America/Argentina/Buenos_Aires';

-- Create initial schema if needed
-- (Tables will be created by Alembic migrations)

-- Insert some initial data for development
-- This will be replaced by proper seed data later

COMMENT ON DATABASE optimizador_rutas IS 'Database for Optimizador de Rutas con IA - Route optimization system for transport companies in Misiones';

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'PostgreSQL with PostGIS initialized successfully for Optimizador de Rutas';
END $$;