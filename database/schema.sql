-- NDVI AI WebGIS Database Schema
-- PostgreSQL 14+ with PostGIS 3.3+

-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;

-- Create ENUM types
DO $$ BEGIN
    CREATE TYPE dataset_type_enum AS ENUM ('NDVI_OBSERVED', 'NDVI_CHANGE', 'NDVI_FORECAST');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE source_type_enum AS ENUM ('OBSERVED', 'FORECAST');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$ BEGIN
    CREATE TYPE model_type_enum AS ENUM ('RANDOM_FOREST', 'EXTRA_TREES', 'HIST_GRADIENT_BOOSTING', 'SEASONAL_NAIVE', 'LSTM', 'OTHER');
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- Table: study_areas
CREATE TABLE IF NOT EXISTS study_areas (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    geom GEOMETRY(POLYGON, 4326),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_study_areas_geom ON study_areas USING GIST(geom);

-- Table: raster_datasets
CREATE TABLE IF NOT EXISTS raster_datasets (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    dataset_type dataset_type_enum NOT NULL,
    observation_date DATE,
    year INTEGER,
    file_path TEXT NOT NULL,
    cog_path TEXT,
    crs VARCHAR(50) DEFAULT 'EPSG:4326',
    width INTEGER,
    height INTEGER,
    resolution_x DOUBLE PRECISION,
    resolution_y DOUBLE PRECISION,
    bounds GEOMETRY(POLYGON, 4326),
    nodata_value DOUBLE PRECISION,
    dtype VARCHAR(20),
    metadata_json JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_raster_datasets_type ON raster_datasets(dataset_type);
CREATE INDEX IF NOT EXISTS idx_raster_datasets_year ON raster_datasets(year);
CREATE INDEX IF NOT EXISTS idx_raster_datasets_date ON raster_datasets(observation_date);
CREATE INDEX IF NOT EXISTS idx_raster_datasets_bounds ON raster_datasets USING GIST(bounds);

-- Table: raster_statistics
CREATE TABLE IF NOT EXISTS raster_statistics (
    id SERIAL PRIMARY KEY,
    dataset_id INTEGER NOT NULL REFERENCES raster_datasets(id) ON DELETE CASCADE,
    min_value DOUBLE PRECISION,
    max_value DOUBLE PRECISION,
    mean_value DOUBLE PRECISION,
    median_value DOUBLE PRECISION,
    q1_value DOUBLE PRECISION,
    q3_value DOUBLE PRECISION,
    std_dev DOUBLE PRECISION,
    valid_pixel_count BIGINT,
    total_pixel_count BIGINT,
    ndvi_negative_count BIGINT,
    ndvi_bare_soil_count BIGINT,
    ndvi_low_vegetation_count BIGINT,
    ndvi_moderate_vegetation_count BIGINT,
    ndvi_high_vegetation_count BIGINT,
    histogram_json JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_raster_statistics_dataset ON raster_statistics(dataset_id);

-- Table: ndvi_timeseries
CREATE TABLE IF NOT EXISTS ndvi_timeseries (
    id SERIAL PRIMARY KEY,
    observation_date DATE NOT NULL,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    ndvi_mean DOUBLE PRECISION NOT NULL,
    ndvi_median DOUBLE PRECISION,
    ndvi_std DOUBLE PRECISION,
    ndvi_min DOUBLE PRECISION,
    ndvi_max DOUBLE PRECISION,
    source_type source_type_enum NOT NULL DEFAULT 'OBSERVED',
    dataset_id INTEGER REFERENCES raster_datasets(id) ON DELETE SET NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_ndvi_timeseries_date ON ndvi_timeseries(observation_date);
CREATE INDEX IF NOT EXISTS idx_ndvi_timeseries_year_month ON ndvi_timeseries(year, month);
CREATE INDEX IF NOT EXISTS idx_ndvi_timeseries_source ON ndvi_timeseries(source_type);
CREATE UNIQUE INDEX IF NOT EXISTS idx_ndvi_timeseries_unique ON ndvi_timeseries(observation_date, source_type);

-- Table: model_runs
CREATE TABLE IF NOT EXISTS model_runs (
    id SERIAL PRIMARY KEY,
    model_type model_type_enum NOT NULL,
    model_name VARCHAR(255) NOT NULL,
    run_name VARCHAR(255) UNIQUE,
    training_start_date DATE,
    training_end_date DATE,
    validation_method VARCHAR(100),
    mae DOUBLE PRECISION,
    rmse DOUBLE PRECISION,
    r2_score DOUBLE PRECISION,
    parameters_json JSONB,
    feature_importance_json JSONB,
    is_selected BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_model_runs_type ON model_runs(model_type);
CREATE INDEX IF NOT EXISTS idx_model_runs_selected ON model_runs(is_selected);

-- Table: forecast_results
CREATE TABLE IF NOT EXISTS forecast_results (
    id SERIAL PRIMARY KEY,
    model_run_id INTEGER NOT NULL REFERENCES model_runs(id) ON DELETE CASCADE,
    forecast_date DATE NOT NULL,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    predicted_ndvi DOUBLE PRECISION NOT NULL,
    confidence_lower DOUBLE PRECISION,
    confidence_upper DOUBLE PRECISION,
    is_extrapolation BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_forecast_results_model ON forecast_results(model_run_id);
CREATE INDEX IF NOT EXISTS idx_forecast_results_date ON forecast_results(forecast_date);
CREATE INDEX IF NOT EXISTS idx_forecast_results_year_month ON forecast_results(year, month);
CREATE UNIQUE INDEX IF NOT EXISTS idx_forecast_results_unique ON forecast_results(model_run_id, forecast_date);

-- Create updated_at trigger function
ALTER TABLE raster_statistics ADD COLUMN IF NOT EXISTS q1_value DOUBLE PRECISION;
ALTER TABLE raster_statistics ADD COLUMN IF NOT EXISTS q3_value DOUBLE PRECISION;

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers
DROP TRIGGER IF EXISTS update_study_areas_updated_at ON study_areas;
CREATE TRIGGER update_study_areas_updated_at BEFORE UPDATE ON study_areas
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_raster_datasets_updated_at ON raster_datasets;
CREATE TRIGGER update_raster_datasets_updated_at BEFORE UPDATE ON raster_datasets
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_model_runs_updated_at ON model_runs;
CREATE TRIGGER update_model_runs_updated_at BEFORE UPDATE ON model_runs
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Insert initial study area (Ho Chi Minh City bounds from audit report)
INSERT INTO study_areas (name, description, geom) VALUES (
    'Ho Chi Minh City',
    'Ho Chi Minh City boundary for NDVI analysis',
    ST_MakeEnvelope(106.33097506690382, 10.320295141607122, 107.57145864274446, 11.50095091952541, 4326)
) ON CONFLICT (name) DO NOTHING;


