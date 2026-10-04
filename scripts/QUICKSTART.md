# NDVI Data Ingestion Pipeline - Quick Start Guide

## What Was Created

Complete data ingestion pipeline with 7 Python scripts + requirements + documentation.

### Scripts Created:

1. **setup_database.py** - Database setup and schema initialization
2. **convert_to_cog.py** - GeoTIFF to COG converter
3. **ingest_rasters.py** - Raster datasets ingestion
4. **ingest_model_metrics.py** - Model performance metrics
5. **ingest_forecast.py** - Forecast data and maps
6. **ingest_timeseries.py** - Time series data (2015-2025)
7. **ingest_all.py** - Master orchestration script

### Supporting Files:

- **requirements.txt** - Python dependencies
- **.env.example** - Environment configuration template
- **README.md** - Complete documentation
- **../database/schema.sql** - PostgreSQL database schema

## Prerequisites Check

Before running, ensure you have:

- [ ] Python 3.11+ installed
- [ ] PostgreSQL 14+ running
- [ ] PostGIS extension available
- [ ] GDAL installed and in PATH
- [ ] Source data files in D:\NDVI:
  - HCM_NDVI_2015.tif
  - HCM_NDVI_2025.tif
  - HCM_NDVI_Change_2015_2025.tif
  - HCM_NDVI_Forecast_Maps_2026.zip

## Installation Steps

### 1. Install Python Dependencies

\\\ash
cd D:\NDVI\ndvi-ai-web\scripts
pip install -r requirements.txt
\\\

### 2. Configure Environment

\\\ash
# Copy example to .env
copy .env.example .env

# Edit .env with your PostgreSQL password
notepad .env
\\\

Required settings in .env:
\\\env
POSTGRES_PASSWORD=your_actual_password
\\\

### 3. Verify PostgreSQL

\\\ash
# Test connection
psql -U postgres -c "SELECT version();"

# Check PostGIS availability
psql -U postgres -c "SELECT * FROM pg_available_extensions WHERE name = 'postgis';"
\\\

### 4. Run Complete Ingestion

\\\ash
python ingest_all.py
\\\

This will:
- Create database and schema
- Insert model metrics (4 models)
- Ingest 3 raster datasets with COG conversion
- Extract and load forecast data (12 months)
- Generate/load time series data (132 observations)

**Expected duration:** 3-4 minutes

## What Gets Ingested

### Raster Datasets (3 files)
- **HCM_NDVI_2015.tif** → NDVI_OBSERVED, year=2015
- **HCM_NDVI_2025.tif** → NDVI_OBSERVED, year=2025  
- **HCM_NDVI_Change_2015_2025.tif** → NDVI_CHANGE, year=2025

Each with:
- Metadata (CRS, bounds, resolution, dimensions)
- Statistics (min, max, mean, median, std, pixel counts, histogram)
- COG version in data/processed/

### Model Metrics (4 models)
- Random Forest (selected) - MAE: 0.021111, RMSE: 0.027339, R²: 0.221221
- Extra Trees - MAE: 0.020286, RMSE: 0.027439, R²: 0.193925
- HistGradientBoosting - MAE: 0.025380, RMSE: 0.032245, R²: -0.293690
- Seasonal Naive - MAE: 0.026834, RMSE: 0.036315, R²: -0.760498

### Forecast Data
- 12 monthly predictions for 2026 (Jan-Dec)
- Linked to Random Forest model
- PNG visualization maps (13 files)
- Study area boundary (GeoJSON → PostGIS)

### Time Series
- 132 monthly NDVI observations (2015-2025)
- Source: Observed data
- If CSV not found, generates placeholder based on audit statistics

## Verification

After successful ingestion, verify data:

\\\sql
psql -U postgres -d ndvi_ai

-- Check raster datasets
SELECT id, name, dataset_type, year FROM raster_datasets;

-- Check statistics
SELECT d.name, s.mean_value, s.std_dev, s.valid_pixel_count 
FROM raster_statistics s
JOIN raster_datasets d ON s.dataset_id = d.id;

-- Check time series
SELECT COUNT(*), MIN(observation_date), MAX(observation_date) 
FROM ndvi_timeseries WHERE source_type = 'OBSERVED';

-- Check forecasts
SELECT COUNT(*), MIN(forecast_date), MAX(forecast_date) 
FROM forecast_results;

-- Check models
SELECT model_name, mae, rmse, r2_score, is_selected 
FROM model_runs ORDER BY mae;
\\\

Expected results:
- 3 raster datasets
- 3 raster statistics records
- 132 time series observations
- 12 forecast results
- 4 model runs (1 selected)
- 1 study area

## Output Files

### Processed Data: D:\NDVI\ndvi-ai-web\data\processed\
\\\
HCM_NDVI_2015_cog.tif (COG format, ~30-50 MB)
HCM_NDVI_2025_cog.tif (COG format, ~30-50 MB)
HCM_NDVI_Change_2015_2025_cog.tif (COG format, ~30-50 MB)
forecast_maps/
  HCM_NDVI_Forecast_2026_M01.png
  HCM_NDVI_Forecast_2026_M02.png
  ... (M03-M12)
  HCM_NDVI_Forecast_2026_12Months.png
\\\

### Logs: D:\NDVI\ndvi-ai-web\data\logs\
\\\
ingest_all_20261003_HHMMSS.log
ingest_rasters_20261003_HHMMSS.log
ingest_forecast_20261003_HHMMSS.log
ingest_timeseries_20261003_HHMMSS.log
ingest_models_20261003_HHMMSS.log
\\\

## Troubleshooting

### Issue: GDAL not found
\\\
Error: gdal_translate: command not found
Solution: Install GDAL from https://www.gisinternals.com/release.php
         Add to PATH: C:\Program Files\GDAL\
\\\

### Issue: Database connection failed
\\\
Error: could not connect to server
Solution: 1. Check PostgreSQL is running (services.msc)
         2. Verify credentials in .env file
         3. Test: psql -U postgres
\\\

### Issue: PostGIS not available
\\\
Error: extension "postgis" is not available
Solution: Install PostGIS bundle with PostgreSQL
         Or download from https://postgis.net/install/
\\\

### Issue: Permission denied
\\\
Error: PermissionError on data directory
Solution: Run PowerShell as Administrator
         Or adjust directory permissions
\\\

## Individual Scripts

Run scripts individually if needed:

\\\ash
# Setup database only
python setup_database.py

# Ingest rasters only
python ingest_rasters.py

# Convert single file to COG
python convert_to_cog.py input.tif output_cog.tif
\\\

All scripts are idempotent - safe to run multiple times.

## Next Steps

After successful ingestion:

1. **Start Backend API:**
   \\\ash
   cd D:\NDVI\ndvi-ai-web\backend
   uvicorn app.main:app --reload
   \\\

2. **Start Frontend:**
   \\\ash
   cd D:\NDVI\ndvi-ai-web\frontend
   npm run dev
   \\\

3. **Access Application:**
   - Frontend: http://localhost:5173
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/api/docs

## Architecture

The pipeline follows this data flow:

\\\
Raw GeoTIFF Files (D:\NDVI\*.tif)
  ↓
[Convert to COG] → processed/*.cog.tif
  ↓
[Compute Statistics] → min, max, mean, histogram
  ↓
[Insert to Database] → raster_datasets + raster_statistics
  
Forecast ZIP (HCM_NDVI_Forecast_Maps_2026.zip)
  ↓
[Extract] → CSV, GeoJSON, PNGs
  ↓
[Parse & Insert] → forecast_results + study_areas
  
Model Metrics (from audit report)
  ↓
[Insert] → model_runs (4 models with MAE/RMSE/R²)
  
Time Series (observed/generated)
  ↓
[Insert] → ndvi_timeseries (132 monthly records)
\\\

## Database Schema Overview

Tables created:
- **raster_datasets** - Raster file metadata
- **raster_statistics** - Pre-computed statistics
- **ndvi_timeseries** - Monthly NDVI observations
- **model_runs** - ML model configurations
- **forecast_results** - Future predictions
- **study_areas** - Geographic boundaries

All with proper indexes, foreign keys, and PostGIS geometries.

---

**Created:** 2026-10-03  
**Location:** D:\NDVI\ndvi-ai-web\scripts\  
**Documentation:** README.md (full details)
