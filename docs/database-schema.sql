-- ============================================================================
-- NDVI AI WebGIS - PostgreSQL Database Schema
-- ============================================================================
-- Purpose: Store raster datasets, timeseries, AI model results, and forecasts
-- DBMS: PostgreSQL 14+ with PostGIS 3.3+
-- Date: 2026-10-03
-- ============================================================================

-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_raster;

-- ============================================================================
-- ENUMS
-- ============================================================================

CREATE TYPE dataset_type_enum AS ENUM (
    'ndvi_2015',
    'ndvi_2025',
    'ndvi_change',
    'ndvi_forecast_2026',
    'landsat_raw',
    'sentinel_raw',
    'other'
);

CREATE TYPE source_type_enum AS ENUM (
    'landsat_8',
    'landsat_9',
    'sentinel_2',
    'modis',
    'combined',
    'interpolated'
);

CREATE TYPE model_type_enum AS ENUM (
    'lstm',
    'gru',
    'sarima',
    'prophet',
    'xgboost',
    'ensemble'
);

-- ============================================================================
-- TABLE: study_areas
-- Purpose: Define geographic boundaries for HCMC study regions
-- ============================================================================

CREATE TABLE study_areas (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    geom GEOMETRY(POLYGON, 4326) NOT NULL,
    area_km2 DECIMAL(10, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

CREATE INDEX idx_study_areas_geom ON study_areas USING GIST(geom);
CREATE INDEX idx_study_areas_name ON study_areas(name);

COMMENT ON TABLE study_areas IS 'Geographic boundaries for study regions in HCMC';
COMMENT ON COLUMN study_areas.geom IS 'Polygon geometry in WGS84 (EPSG:4326)';

-- ============================================================================
-- TABLE: raster_datasets
-- Purpose: Metadata for NDVI raster datasets (GeoTIFF and COG)
-- ============================================================================

CREATE TABLE raster_datasets (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    display_name VARCHAR(255),
    dataset_type dataset_type_enum NOT NULL,
    observation_date DATE,
    year INTEGER,
    month INTEGER,
    
    -- File paths (Windows-compatible)
    file_path TEXT NOT NULL,
    cog_path TEXT,
    
    -- Raster metadata
    crs VARCHAR(50) DEFAULT 'EPSG:4326',
    resolution_x DECIMAL(12, 8),
    resolution_y DECIMAL(12, 8),
    width INTEGER,
    height INTEGER,
    bounds_xmin DECIMAL(12, 8),
    bounds_ymin DECIMAL(12, 8),
    bounds_xmax DECIMAL(12, 8),
    bounds_ymax DECIMAL(12, 8),
    nodata_value DECIMAL(10, 4),
    
    -- Additional metadata
    metadata_json JSONB,
    file_size_mb DECIMAL(10, 2),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE,
    
    CONSTRAINT unique_dataset_name UNIQUE(name),
    CONSTRAINT check_year_range CHECK (year IS NULL OR (year >= 2000 AND year <= 2100)),
    CONSTRAINT check_month_range CHECK (month IS NULL OR (month >= 1 AND month <= 12))
);

CREATE INDEX idx_raster_datasets_type ON raster_datasets(dataset_type);
CREATE INDEX idx_raster_datasets_date ON raster_datasets(observation_date);
CREATE INDEX idx_raster_datasets_year_month ON raster_datasets(year, month);
CREATE INDEX idx_raster_datasets_metadata ON raster_datasets USING GIN(metadata_json);

COMMENT ON TABLE raster_datasets IS 'Metadata for NDVI raster files including GeoTIFF and COG';
COMMENT ON COLUMN raster_datasets.cog_path IS 'Path to Cloud-Optimized GeoTIFF for tile serving';
COMMENT ON COLUMN raster_datasets.metadata_json IS 'Additional metadata: satellite, processing info, quality flags';

-- ============================================================================
-- TABLE: raster_statistics
-- Purpose: Pre-computed statistics for each raster dataset
-- ============================================================================

CREATE TABLE raster_statistics (
    id SERIAL PRIMARY KEY,
    dataset_id INTEGER NOT NULL REFERENCES raster_datasets(id) ON DELETE CASCADE,
    
    -- Statistical measures
    min_value DECIMAL(10, 6),
    max_value DECIMAL(10, 6),
    mean_value DECIMAL(10, 6),
    median_value DECIMAL(10, 6),
    std_dev DECIMAL(10, 6),
    
    -- Pixel counts
    valid_pixel_count BIGINT,
    total_pixel_count BIGINT,
    nodata_pixel_count BIGINT,
    
    -- NDVI-specific statistics
    ndvi_negative_count BIGINT,
    ndvi_water_count BIGINT,        -- NDVI < 0.1
    ndvi_barren_count BIGINT,       -- 0.1 - 0.2
    ndvi_sparse_veg_count BIGINT,   -- 0.2 - 0.4
    ndvi_moderate_veg_count BIGINT, -- 0.4 - 0.6
    ndvi_dense_veg_count BIGINT,    -- > 0.6
    
    -- Percentiles
    percentile_10 DECIMAL(10, 6),
    percentile_25 DECIMAL(10, 6),
    percentile_50 DECIMAL(10, 6),
    percentile_75 DECIMAL(10, 6),
    percentile_90 DECIMAL(10, 6),
    
    computed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_dataset_stats UNIQUE(dataset_id)
);

CREATE INDEX idx_raster_stats_dataset ON raster_statistics(dataset_id);

COMMENT ON TABLE raster_statistics IS 'Pre-computed statistical summaries for raster datasets';
COMMENT ON COLUMN raster_statistics.ndvi_water_count IS 'Water/non-vegetation pixels (NDVI < 0.1)';

-- ============================================================================
-- TABLE: ndvi_timeseries
-- Purpose: Monthly NDVI aggregated values for time series analysis
-- ============================================================================

CREATE TABLE ndvi_timeseries (
    id SERIAL PRIMARY KEY,
    observation_date DATE NOT NULL,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    
    -- NDVI statistics
    ndvi_mean DECIMAL(10, 6),
    ndvi_median DECIMAL(10, 6),
    ndvi_std_dev DECIMAL(10, 6),
    ndvi_min DECIMAL(10, 6),
    ndvi_max DECIMAL(10, 6),
    
    -- Pixel count
    valid_pixel_count BIGINT,
    
    -- Data source
    source_type source_type_enum NOT NULL,
    dataset_id INTEGER REFERENCES raster_datasets(id) ON DELETE SET NULL,
    
    -- Quality flags
    cloud_cover_percent DECIMAL(5, 2),
    quality_score DECIMAL(3, 2), -- 0-1 scale
    is_interpolated BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    metadata_json JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_observation_date UNIQUE(observation_date, source_type),
    CONSTRAINT check_ts_year_range CHECK (year >= 2000 AND year <= 2100),
    CONSTRAINT check_ts_month_range CHECK (month >= 1 AND month <= 12),
    CONSTRAINT check_quality_score CHECK (quality_score IS NULL OR (quality_score >= 0 AND quality_score <= 1))
);

CREATE INDEX idx_ndvi_ts_date ON ndvi_timeseries(observation_date);
CREATE INDEX idx_ndvi_ts_year_month ON ndvi_timeseries(year, month);
CREATE INDEX idx_ndvi_ts_source ON ndvi_timeseries(source_type);
CREATE INDEX idx_ndvi_ts_dataset ON ndvi_timeseries(dataset_id);

COMMENT ON TABLE ndvi_timeseries IS 'Monthly aggregated NDVI values for training and visualization';
COMMENT ON COLUMN ndvi_timeseries.is_interpolated IS 'TRUE if gaps were filled by interpolation';

-- ============================================================================
-- TABLE: model_runs
-- Purpose: Track AI model training runs and hyperparameters
-- ============================================================================

CREATE TABLE model_runs (
    id SERIAL PRIMARY KEY,
    run_name VARCHAR(255),
    model_type model_type_enum NOT NULL,
    model_name VARCHAR(255) NOT NULL,
    
    -- Training period
    training_start_date DATE NOT NULL,
    training_end_date DATE NOT NULL,
    
    -- Performance metrics
    mae DECIMAL(10, 6),
    rmse DECIMAL(10, 6),
    r2_score DECIMAL(10, 6),
    mape DECIMAL(10, 4), -- Mean Absolute Percentage Error
    
    -- Cross-validation metrics
    cv_mae_mean DECIMAL(10, 6),
    cv_rmse_mean DECIMAL(10, 6),
    cv_r2_mean DECIMAL(10, 6),
    
    -- Model configuration
    parameters_json JSONB NOT NULL,
    feature_importance_json JSONB,
    
    -- Tracking
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    trained_by VARCHAR(100),
    notes TEXT,
    is_production BOOLEAN DEFAULT FALSE,
    
    CONSTRAINT check_training_dates CHECK (training_end_date >= training_start_date),
    CONSTRAINT check_r2_score CHECK (r2_score IS NULL OR r2_score <= 1)
);

CREATE INDEX idx_model_runs_type ON model_runs(model_type);
CREATE INDEX idx_model_runs_created ON model_runs(created_at DESC);
CREATE INDEX idx_model_runs_production ON model_runs(is_production) WHERE is_production = TRUE;
CREATE INDEX idx_model_runs_params ON model_runs USING GIN(parameters_json);

COMMENT ON TABLE model_runs IS 'AI model training runs with hyperparameters and performance metrics';
COMMENT ON COLUMN model_runs.parameters_json IS 'Full hyperparameters: layers, units, learning_rate, etc.';
COMMENT ON COLUMN model_runs.is_production IS 'Mark the active production model';

-- ============================================================================
-- TABLE: forecast_results
-- Purpose: Store AI model prediction results
-- ============================================================================

CREATE TABLE forecast_results (
    id SERIAL PRIMARY KEY,
    model_run_id INTEGER NOT NULL REFERENCES model_runs(id) ON DELETE CASCADE,
    
    forecast_date DATE NOT NULL,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL,
    
    -- Predicted values
    predicted_ndvi DECIMAL(10, 6) NOT NULL,
    
    -- Confidence intervals
    confidence_lower DECIMAL(10, 6),
    confidence_upper DECIMAL(10, 6),
    confidence_level DECIMAL(3, 2) DEFAULT 0.95, -- e.g., 0.95 for 95%
    
    -- Prediction metadata
    prediction_std_dev DECIMAL(10, 6),
    is_extrapolation BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_forecast_per_model UNIQUE(model_run_id, forecast_date),
    CONSTRAINT check_fc_year_range CHECK (year >= 2000 AND year <= 2100),
    CONSTRAINT check_fc_month_range CHECK (month >= 1 AND month <= 12),
    CONSTRAINT check_confidence_level CHECK (confidence_level >= 0 AND confidence_level <= 1),
    CONSTRAINT check_confidence_interval CHECK (
        (confidence_lower IS NULL AND confidence_upper IS NULL) OR
        (confidence_lower IS NOT NULL AND confidence_upper IS NOT NULL AND confidence_lower <= predicted_ndvi AND predicted_ndvi <= confidence_upper)
    )
);

CREATE INDEX idx_forecast_model_run ON forecast_results(model_run_id);
CREATE INDEX idx_forecast_date ON forecast_results(forecast_date);
CREATE INDEX idx_forecast_year_month ON forecast_results(year, month);

COMMENT ON TABLE forecast_results IS 'NDVI predictions from trained AI models';
COMMENT ON COLUMN forecast_results.is_extrapolation IS 'TRUE if forecasting beyond training date range';

-- ============================================================================
-- TABLE: spatial_queries_log (Optional - for analytics)
-- Purpose: Log user queries for spatial point extraction
-- ============================================================================

CREATE TABLE spatial_queries_log (
    id SERIAL PRIMARY KEY,
    query_time TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    latitude DECIMAL(10, 7) NOT NULL,
    longitude DECIMAL(10, 7) NOT NULL,
    location GEOMETRY(POINT, 4326),
    dataset_id INTEGER REFERENCES raster_datasets(id) ON DELETE SET NULL,
    extracted_value DECIMAL(10, 6),
    response_time_ms INTEGER,
    client_ip INET,
    
    CONSTRAINT check_lat_range CHECK (latitude >= -90 AND latitude <= 90),
    CONSTRAINT check_lng_range CHECK (longitude >= -180 AND longitude <= 180)
);

CREATE INDEX idx_spatial_queries_time ON spatial_queries_log(query_time DESC);
CREATE INDEX idx_spatial_queries_location ON spatial_queries_log USING GIST(location);

COMMENT ON TABLE spatial_queries_log IS 'Optional logging for user spatial queries and analytics';

-- ============================================================================
-- VIEWS
-- ============================================================================

-- View: Latest NDVI statistics by dataset type
CREATE VIEW v_latest_dataset_stats AS
SELECT 
    rd.id,
    rd.name,
    rd.display_name,
    rd.dataset_type,
    rd.observation_date,
    rd.year,
    rd.month,
    rs.mean_value,
    rs.median_value,
    rs.std_dev,
    rs.min_value,
    rs.max_value,
    rs.valid_pixel_count,
    rs.ndvi_dense_veg_count,
    rs.ndvi_moderate_veg_count,
    rs.ndvi_sparse_veg_count
FROM raster_datasets rd
LEFT JOIN raster_statistics rs ON rd.id = rs.dataset_id
WHERE rd.is_active = TRUE
ORDER BY rd.observation_date DESC;

COMMENT ON VIEW v_latest_dataset_stats IS 'Combined view of active datasets with their statistics';

-- View: Best performing models by type
CREATE VIEW v_best_models AS
SELECT DISTINCT ON (model_type)
    id,
    model_type,
    model_name,
    mae,
    rmse,
    r2_score,
    training_start_date,
    training_end_date,
    created_at
FROM model_runs
WHERE is_production = TRUE OR id IN (
    SELECT id FROM model_runs WHERE r2_score IS NOT NULL ORDER BY r2_score DESC LIMIT 10
)
ORDER BY model_type, r2_score DESC NULLS LAST;

COMMENT ON VIEW v_best_models IS 'Best performing model for each model type';

-- View: Complete timeseries with forecasts
CREATE VIEW v_complete_timeseries AS
SELECT 
    observation_date AS date,
    year,
    month,
    ndvi_mean AS value,
    'observed' AS data_type,
    source_type::TEXT AS source,
    NULL::INTEGER AS model_run_id,
    NULL::DECIMAL AS confidence_lower,
    NULL::DECIMAL AS confidence_upper
FROM ndvi_timeseries
WHERE is_interpolated = FALSE

UNION ALL

SELECT 
    forecast_date AS date,
    year,
    month,
    predicted_ndvi AS value,
    'forecast' AS data_type,
    mr.model_name AS source,
    fr.model_run_id,
    fr.confidence_lower,
    fr.confidence_upper
FROM forecast_results fr
JOIN model_runs mr ON fr.model_run_id = mr.id
WHERE mr.is_production = TRUE

ORDER BY date;

COMMENT ON VIEW v_complete_timeseries IS 'Combined observed and forecasted NDVI timeseries';

-- ============================================================================
-- FUNCTIONS
-- ============================================================================

-- Function: Update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for updated_at
CREATE TRIGGER trigger_study_areas_updated_at
    BEFORE UPDATE ON study_areas
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_raster_datasets_updated_at
    BEFORE UPDATE ON raster_datasets
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Function: Calculate area in km² for study areas
CREATE OR REPLACE FUNCTION calculate_area_km2()
RETURNS TRIGGER AS $$
BEGIN
    NEW.area_km2 = ST_Area(ST_Transform(NEW.geom, 3857)) / 1000000;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_calculate_area
    BEFORE INSERT OR UPDATE OF geom ON study_areas
    FOR EACH ROW
    EXECUTE FUNCTION calculate_area_km2();

-- Function: Auto-populate location point from lat/lng
CREATE OR REPLACE FUNCTION populate_location_point()
RETURNS TRIGGER AS $$
BEGIN
    NEW.location = ST_SetSRID(ST_MakePoint(NEW.longitude, NEW.latitude), 4326);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_populate_location
    BEFORE INSERT ON spatial_queries_log
    FOR EACH ROW
    EXECUTE FUNCTION populate_location_point();

-- ============================================================================
-- SEED DATA
-- ============================================================================

-- Insert default HCMC study area (approximate bounds)
INSERT INTO study_areas (name, description, geom) VALUES
(
    'Ho Chi Minh City',
    'Full extent of HCMC administrative boundary',
    ST_GeomFromText('POLYGON((
        106.36 10.35,
        107.02 10.35,
        107.02 11.20,
        106.36 11.20,
        106.36 10.35
    ))', 4326)
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Additional composite indexes for common queries
CREATE INDEX idx_forecast_results_model_date ON forecast_results(model_run_id, forecast_date);
CREATE INDEX idx_ndvi_ts_date_source ON ndvi_timeseries(observation_date, source_type);

-- ============================================================================
-- GRANTS (Adjust for your database user)
-- ============================================================================

-- Example: Grant permissions to application user
-- CREATE USER ndvi_app_user WITH PASSWORD 'your_secure_password';
-- GRANT CONNECT ON DATABASE ndvi_db TO ndvi_app_user;
-- GRANT USAGE ON SCHEMA public TO ndvi_app_user;
-- GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO ndvi_app_user;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO ndvi_app_user;

-- ============================================================================
-- MAINTENANCE
-- ============================================================================

-- Analyze tables for query optimization
ANALYZE study_areas;
ANALYZE raster_datasets;
ANALYZE raster_statistics;
ANALYZE ndvi_timeseries;
ANALYZE model_runs;
ANALYZE forecast_results;

-- ============================================================================
-- SCHEMA VERSION
-- ============================================================================

CREATE TABLE schema_version (
    version VARCHAR(20) PRIMARY KEY,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    description TEXT
);

INSERT INTO schema_version (version, description) VALUES
('1.0.0', 'Initial schema: datasets, timeseries, models, forecasts with PostGIS support');

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
