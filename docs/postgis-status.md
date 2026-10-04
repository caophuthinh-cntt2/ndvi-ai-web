# PostgreSQL/PostGIS status

The project includes `database/schema.sql` and `scripts/setup_database.py` for the production persistence layer. The schema contains the required tables: `study_areas`, `raster_datasets`, `raster_statistics`, `ndvi_timeseries`, `model_runs`, and `forecast_results`, with PostGIS geometry columns and GiST indexes.

The local development database is `ndvi_ai` on PostgreSQL port `5432`, with the PostGIS extension enabled. The application uses a hybrid storage model:

- PostGIS stores raster metadata, spatial footprints, statistics, histograms, and annual time-series values.
- GeoTIFF files remain external and are read by Rasterio for XYZ tiles and pixel inspection.
- The API health endpoint reports both database and raster-storage status.

When PostgreSQL/PostGIS is installed:

```powershell
python scripts/setup_database.py
python scripts/ingest_rasters.py
```

Both setup and ingestion are idempotent and can be run again after replacing a GeoTIFF.
