# NDVI AI WebGIS - Data Ingestion Scripts

Complete data ingestion pipeline for processing and loading NDVI raster datasets, time series, and forecast data into PostgreSQL/PostGIS database.

## Overview

This directory contains scripts to:
1. Setup PostgreSQL database with PostGIS extension
2. Convert GeoTIFF files to Cloud Optimized GeoTIFF (COG)
3. Ingest raster datasets with metadata and statistics
4. Load forecast data and visualizations
5. Import model metrics and time series data

## Prerequisites

### Software Requirements

- **Python 3.11+**
- **PostgreSQL 14+** with **PostGIS 3.3+**
- **GDAL 3.x** (for COG conversion)

### Python Packages

Install dependencies:

\\\ash
pip install -r requirements.txt
\\\

### GDAL Installation (Windows)

Download and install GDAL from:
- https://www.gisinternals.com/release.php
- Or use OSGeo4W: https://trac.osgeo.org/osgeo4w/

Add GDAL binaries to PATH.

## Configuration

1. Copy \.env.example\ to \.env\:

\\\ash
cp .env.example .env
\\\

2. Edit \.env\ with your database credentials:

\\\env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=ndvi_ai
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password

SOURCE_DATA_DIR=D:/NDVI
PROCESSED_DATA_DIR=D:/NDVI/ndvi-ai-web/data/processed
CACHE_DIR=D:/NDVI/ndvi-ai-web/data/cache
\\\

## Source Data Location

Place source data files in \D:\NDVI\:

\\\
D:\NDVI\
  ├── HCM_NDVI_2015.tif
  ├── HCM_NDVI_2025.tif
  ├── HCM_NDVI_Change_2015_2025.tif
  └── HCM_NDVI_Forecast_Maps_2026.zip
\\\

## Scripts

### 1. setup_database.py

Creates PostgreSQL database, enables PostGIS, and runs schema.sql to create all tables.

**Usage:**
\\\ash
python setup_database.py
\\\

**What it does:**
- Connects to PostgreSQL
- Creates database if not exists
- Enables PostGIS extension
- Creates tables: raster_datasets, raster_statistics, ndvi_timeseries, model_runs, forecast_results, study_areas
- Sets up indexes and triggers

### 2. convert_to_cog.py

Converts a GeoTIFF file to Cloud Optimized GeoTIFF format for fast tile serving.

**Usage:**
\\\ash
python convert_to_cog.py <input.tif> <output_cog.tif>

# Options:
python convert_to_cog.py input.tif output.tif --compression DEFLATE --blocksize 512 --no-overviews
\\\

**Options:**
- \--compression TYPE\: Compression method (LZW, DEFLATE, JPEG). Default: LZW
- \--blocksize SIZE\: Internal tile size. Default: 256
- \--no-overviews\: Skip overview generation

### 3. ingest_rasters.py

Scans source directory for GeoTIFF files, converts to COG, computes statistics, and registers in database.

**Usage:**
\\\ash
python ingest_rasters.py
\\\

**What it does:**
- Processes HCM_NDVI_2015.tif → dataset_type='NDVI_OBSERVED', year=2015
- Processes HCM_NDVI_2025.tif → dataset_type='NDVI_OBSERVED', year=2025
- Processes HCM_NDVI_Change_2015_2025.tif → dataset_type='NDVI_CHANGE', year=2025
- For each raster:
  - Reads metadata (CRS, bounds, resolution, dimensions)
  - Converts to COG format
  - Computes statistics (min, max, mean, median, std, pixel counts, histogram)
  - Inserts metadata into \aster_datasets\ table
  - Inserts statistics into \aster_statistics\ table

**Idempotent:** Safe to run multiple times; skips existing datasets.

### 4. ingest_model_metrics.py

Inserts model comparison results from audit report into database.

**Usage:**
\\\ash
python ingest_model_metrics.py
\\\

**What it does:**
- Inserts 4 model runs:
  - Random Forest (selected, best performance)
  - Extra Trees
  - HistGradientBoosting
  - Seasonal Naive (baseline)
- Metrics: MAE, RMSE, R²
- Training period: 2015-2025
- Validation method: expanding_walk_forward

### 5. ingest_forecast.py

Extracts forecast ZIP file and loads forecast data, GeoJSON boundary, and PNG maps.

**Usage:**
\\\ash
python ingest_forecast.py
\\\

**What it does:**
- Extracts \HCM_NDVI_Forecast_Maps_2026.zip\
- Reads \HCM_NDVI_Forecast_2026.csv\ (12 monthly forecasts)
- Inserts forecast values into \orecast_results\ table
- Reads \HCM_NDVI_Forecast_2026.geojson\ (study area boundary)
- Inserts boundary into \study_areas\ table
- Copies PNG maps to \data/processed/forecast_maps/\

**Requires:** \ingest_model_metrics.py\ must run first to create model_run record.

### 6. ingest_timeseries.py

Imports observed NDVI time series data (2015-2025).

**Usage:**
\\\ash
python ingest_timeseries.py
\\\

**What it does:**
- Searches for training time series CSV in multiple locations
- If found: parses and inserts 132 monthly observations (2015-2025)
- If not found: generates placeholder data based on audit report statistics
- Fields: observation_date, year, month, ndvi_mean, ndvi_median, ndvi_std, source_type='OBSERVED'

### 7. ingest_all.py

**Master script** that runs all ingestion steps in correct order.

**Usage:**
\\\ash
python ingest_all.py
\\\

**Execution order:**
1. setup_database.py
2. ingest_model_metrics.py
3. ingest_rasters.py
4. ingest_forecast.py
5. ingest_timeseries.py

**Features:**
- Detailed logging to \data/logs/ingest_all_TIMESTAMP.log\
- Error handling with summary report
- Continues on non-critical errors
- Final success/failure report

## Quick Start

Run the complete ingestion pipeline:

\\\ash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure environment
cp .env.example .env
# Edit .env with your database credentials

# 3. Ensure PostgreSQL is running
# Verify with: psql -U postgres -c "SELECT version();"

# 4. Ensure source data files exist in D:\NDVI

# 5. Run complete ingestion
python ingest_all.py
\\\

## Logs

All scripts write logs to \D:\NDVI\ndvi-ai-web\data\logs\:

- \ingest_all_TIMESTAMP.log\ - Master script log
- \ingest_rasters_TIMESTAMP.log\ - Raster ingestion log
- \ingest_forecast_TIMESTAMP.log\ - Forecast ingestion log
- \ingest_timeseries_TIMESTAMP.log\ - Time series ingestion log
- \ingest_models_TIMESTAMP.log\ - Model metrics ingestion log

## Output Data

Processed data is saved to \D:\NDVI\ndvi-ai-web\data\processed\:

\\\
processed/
  ├── HCM_NDVI_2015_cog.tif
  ├── HCM_NDVI_2025_cog.tif
  ├── HCM_NDVI_Change_2015_2025_cog.tif
  └── forecast_maps/
      ├── HCM_NDVI_Forecast_2026_M01.png
      ├── HCM_NDVI_Forecast_2026_M02.png
      └── ... (12 monthly maps + 1 combined)
\\\

## Database Schema

See \../database/schema.sql\ for complete schema.

**Key tables:**
- \aster_datasets\ - Raster metadata and file paths
- \aster_statistics\ - Pre-computed statistics per dataset
- \
dvi_timeseries\ - Monthly NDVI observations and forecasts
- \model_runs\ - ML model configurations and metrics
- \orecast_results\ - Monthly forecast predictions
- \study_areas\ - Geographic boundaries

## Troubleshooting

### GDAL not found

**Error:** \gdal_translate: command not found\

**Solution:**
- Install GDAL: https://www.gisinternals.com/release.php
- Add to PATH: \C:\Program Files\GDAL\
- Verify: \gdal_translate --version\

### Database connection failed

**Error:** \psycopg2.OperationalError: could not connect to server\

**Solution:**
- Ensure PostgreSQL is running
- Verify credentials in \.env\
- Check PostgreSQL is listening: \
etstat -an | findstr 5432\

### PostGIS extension not available

**Error:** \extension "postgis" is not available\

**Solution:**
- Install PostGIS: https://postgis.net/install/
- Or use PostgreSQL installer with PostGIS bundle

### Permission denied on data directory

**Error:** \PermissionError: [Errno 13] Permission denied\

**Solution:**
- Run as administrator
- Or change directory permissions
- Or modify paths in \.env\

## Idempotency

All scripts are **idempotent** - safe to run multiple times:
- Checks if records exist before inserting
- Uses \ON CONFLICT DO NOTHING\ or explicit checks
- Skips existing files and database records

## Performance

Typical ingestion times (Windows 10, i7-9700K, 16GB RAM, SSD):
- Database setup: ~5 seconds
- Raster ingestion (3 files): ~2-3 minutes
- Model metrics: ~1 second
- Forecast data: ~10 seconds
- Time series: ~5 seconds

**Total: ~3-4 minutes**

## Next Steps

After successful ingestion:

1. **Verify data in PostgreSQL:**
   \\\sql
   psql -U postgres -d ndvi_ai
   
   SELECT COUNT(*) FROM raster_datasets;
   SELECT COUNT(*) FROM ndvi_timeseries;
   SELECT COUNT(*) FROM forecast_results;
   \\\

2. **Start backend API:**
   \\\ash
   cd ../backend
   uvicorn app.main:app --reload
   \\\

3. **Start frontend:**
   \\\ash
   cd ../frontend
   npm run dev
   \\\

4. **Access application:**
   - Frontend: http://localhost:5173
   - API Docs: http://localhost:8000/api/docs

## Support

For issues or questions:
- Check logs in \data/logs/\
- Review \../docs/architecture.md\
- Verify source data files exist and are valid GeoTIFFs

---

**Last Updated:** 2026-10-03  
**Version:** 1.0.0
