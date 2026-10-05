#!/usr/bin/env python3
"""Register annual GeoTIFFs in PostGIS without storing raster pixels in PostgreSQL."""

import json
import os
from datetime import date
from pathlib import Path

import numpy as np
import psycopg2
import rasterio
from dotenv import load_dotenv
from psycopg2.extras import Json
from rasterio.warp import transform_bounds

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")
SOURCE_DATA_DIR = Path(os.getenv("SOURCE_DATA_DIR", "D:/NDVI"))


def connection():
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return psycopg2.connect(database_url)
    return psycopg2.connect(
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432"),
        database=os.getenv("POSTGRES_DB", "ndvi_ai"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "postgres"),
    )


def inspect_raster(path: Path):
    with rasterio.open(path) as src:
        masked = src.read(1, masked=True).astype("float64")
        values = masked.compressed()
        values = values[np.isfinite(values) & (values >= -1) & (values <= 1)]
        if not values.size:
            raise ValueError(f"Raster không có pixel hợp lệ: {path}")

        left, bottom, right, top = transform_bounds(
            src.crs, "EPSG:4326", *src.bounds, densify_pts=21
        )
        counts, edges = np.histogram(values, bins=50, range=(-1, 1))
        q1, median, q3 = np.percentile(values, [25, 50, 75])
        metadata = {
            "filename": path.name,
            "driver": src.driver,
            "count": src.count,
            "transform": list(src.transform),
            "bounds_native": list(src.bounds),
            "storage": "external_geotiff",
        }
        stats = {
            "min_value": float(values.min()),
            "max_value": float(values.max()),
            "mean_value": float(values.mean()),
            "median_value": float(median),
            "q1_value": float(q1),
            "q3_value": float(q3),
            "std_dev": float(values.std()),
            "valid_pixel_count": int(values.size),
            "total_pixel_count": int(masked.size),
            "ndvi_negative_count": int((values < 0).sum()),
            "ndvi_bare_soil_count": int(((values >= 0) & (values < 0.2)).sum()),
            "ndvi_low_vegetation_count": int(((values >= 0.2) & (values < 0.4)).sum()),
            "ndvi_moderate_vegetation_count": int(((values >= 0.4) & (values < 0.6)).sum()),
            "ndvi_high_vegetation_count": int((values >= 0.6).sum()),
            "histogram_json": {"counts": counts.tolist(), "bin_edges": edges.tolist()},
        }
        raster = {
            "crs": src.crs.to_string() if src.crs else "EPSG:4326",
            "width": src.width,
            "height": src.height,
            "resolution_x": float(abs(src.res[0])),
            "resolution_y": float(abs(src.res[1])),
            "bounds": (left, bottom, right, top),
            "nodata": src.nodata,
            "dtype": src.dtypes[0],
            "metadata": metadata,
        }
    return raster, stats


def upsert_year(conn, year: int):
    path = SOURCE_DATA_DIR / f"HCM_NDVI_{year}.tif"
    if not path.exists():
        raise FileNotFoundError(path)
    raster, stats = inspect_raster(path)
    left, bottom, right, top = raster["bounds"]
    with conn.cursor() as cursor:
        cursor.execute(
            """
            INSERT INTO raster_datasets (
                name, dataset_type, indicator_type, observation_date, year, file_path, cog_path,
                crs, width, height, resolution_x, resolution_y, bounds,
                nodata_value, dtype, metadata_json
            ) VALUES (
                %s, 'NDVI_OBSERVED', 'NDVI', %s, %s, %s, NULL, %s, %s, %s, %s, %s,
                ST_MakeEnvelope(%s, %s, %s, %s, 4326), %s, %s, %s
            )
            ON CONFLICT (name) DO UPDATE SET
                observation_date = EXCLUDED.observation_date,
                year = EXCLUDED.year,
                file_path = EXCLUDED.file_path,
                crs = EXCLUDED.crs,
                width = EXCLUDED.width,
                height = EXCLUDED.height,
                resolution_x = EXCLUDED.resolution_x,
                resolution_y = EXCLUDED.resolution_y,
                bounds = EXCLUDED.bounds,
                nodata_value = EXCLUDED.nodata_value,
                dtype = EXCLUDED.dtype,
                metadata_json = EXCLUDED.metadata_json,
                updated_at = CURRENT_TIMESTAMP
            RETURNING id
            """,
            (
                f"HCM_NDVI_{year}", date(year, 12, 31), year, str(path),
                raster["crs"], raster["width"], raster["height"],
                raster["resolution_x"], raster["resolution_y"],
                left, bottom, right, top, raster["nodata"], raster["dtype"],
                Json(raster["metadata"]),
            ),
        )
        dataset_id = cursor.fetchone()[0]
        cursor.execute(
            """
            INSERT INTO raster_statistics (
                dataset_id, min_value, max_value, mean_value, median_value,
                q1_value, q3_value, std_dev, valid_pixel_count, total_pixel_count,
                ndvi_negative_count, ndvi_bare_soil_count, ndvi_low_vegetation_count,
                ndvi_moderate_vegetation_count, ndvi_high_vegetation_count, histogram_json
            ) VALUES (
                %(dataset_id)s, %(min_value)s, %(max_value)s, %(mean_value)s,
                %(median_value)s, %(q1_value)s, %(q3_value)s, %(std_dev)s,
                %(valid_pixel_count)s, %(total_pixel_count)s, %(ndvi_negative_count)s,
                %(ndvi_bare_soil_count)s, %(ndvi_low_vegetation_count)s,
                %(ndvi_moderate_vegetation_count)s, %(ndvi_high_vegetation_count)s,
                %(histogram_json)s
            )
            ON CONFLICT (dataset_id) DO UPDATE SET
                min_value = EXCLUDED.min_value, max_value = EXCLUDED.max_value,
                mean_value = EXCLUDED.mean_value, median_value = EXCLUDED.median_value,
                q1_value = EXCLUDED.q1_value, q3_value = EXCLUDED.q3_value,
                std_dev = EXCLUDED.std_dev,
                valid_pixel_count = EXCLUDED.valid_pixel_count,
                total_pixel_count = EXCLUDED.total_pixel_count,
                ndvi_negative_count = EXCLUDED.ndvi_negative_count,
                ndvi_bare_soil_count = EXCLUDED.ndvi_bare_soil_count,
                ndvi_low_vegetation_count = EXCLUDED.ndvi_low_vegetation_count,
                ndvi_moderate_vegetation_count = EXCLUDED.ndvi_moderate_vegetation_count,
                ndvi_high_vegetation_count = EXCLUDED.ndvi_high_vegetation_count,
                histogram_json = EXCLUDED.histogram_json,
                created_at = CURRENT_TIMESTAMP
            """,
            {"dataset_id": dataset_id, **stats, "histogram_json": Json(stats["histogram_json"])},
        )
        cursor.execute(
            """
            INSERT INTO ndvi_timeseries (
                observation_date, year, month, ndvi_mean, ndvi_median, ndvi_std,
                ndvi_min, ndvi_max, source_type, dataset_id, notes
            ) VALUES (%s, %s, 12, %s, %s, %s, %s, %s, 'OBSERVED', %s, %s)
            ON CONFLICT (observation_date, source_type) DO UPDATE SET
                ndvi_mean = EXCLUDED.ndvi_mean,
                ndvi_median = EXCLUDED.ndvi_median,
                ndvi_std = EXCLUDED.ndvi_std,
                ndvi_min = EXCLUDED.ndvi_min,
                ndvi_max = EXCLUDED.ndvi_max,
                dataset_id = EXCLUDED.dataset_id,
                notes = EXCLUDED.notes
            """,
            (
                date(year, 12, 31), year, stats["mean_value"], stats["median_value"],
                stats["std_dev"], stats["min_value"], stats["max_value"], dataset_id,
                "Giá trị năm tính từ GeoTIFF; pixel raster lưu ngoài PostGIS.",
            ),
        )
        cursor.execute(
            """
            INSERT INTO indicator_timeseries (
                indicator_type, observation_date, year, month, mean_value,
                median_value, std_value, min_value, max_value, source_type,
                dataset_id, unit, notes
            ) VALUES (
                'NDVI', %s, %s, 12, %s, %s, %s, %s, %s,
                'OBSERVED', %s, 'dimensionless', %s
            )
            ON CONFLICT (indicator_type, observation_date, source_type) DO UPDATE SET
                year = EXCLUDED.year,
                month = EXCLUDED.month,
                mean_value = EXCLUDED.mean_value,
                median_value = EXCLUDED.median_value,
                std_value = EXCLUDED.std_value,
                min_value = EXCLUDED.min_value,
                max_value = EXCLUDED.max_value,
                dataset_id = EXCLUDED.dataset_id,
                unit = EXCLUDED.unit,
                notes = EXCLUDED.notes,
                updated_at = CURRENT_TIMESTAMP
            """,
            (
                date(year, 12, 31), year, stats["mean_value"], stats["median_value"],
                stats["std_dev"], stats["min_value"], stats["max_value"], dataset_id,
                "Annual value calculated from the source GeoTIFF.",
            ),
        )
    conn.commit()
    print(f"OK {year}: dataset_id={dataset_id}, mean={stats['mean_value']:.6f}")


def main():
    with connection() as conn:
        for year in range(2015, 2026):
            upsert_year(conn, year)
    print("Registered 11 rasters and statistics in PostGIS.")


if __name__ == "__main__":
    main()
