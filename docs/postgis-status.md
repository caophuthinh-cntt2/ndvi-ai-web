# PostgreSQL/PostGIS status

The project includes `database/schema.sql` and `scripts/setup_database.py` for the production persistence layer. The schema contains the required tables: `study_areas`, `raster_datasets`, `raster_statistics`, `ndvi_timeseries`, `model_runs`, and `forecast_results`, with PostGIS geometry columns and GiST indexes.

Use `scripts/check_postgis.py` before running the setup script. On the current machine, Docker, `docker-compose`, and `psql` are not installed, so PostGIS has not been started or verified. The filesystem-mode API remains available and reads the source GeoTIFF/ZIP files directly; this does not claim that PostgreSQL is active.

When PostgreSQL/PostGIS is installed:

```powershell
python scripts/check_postgis.py
python scripts/setup_database.py
python scripts/ingest_all.py
```
