from pathlib import Path

import numpy as np
import rasterio
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import text

from app.config import settings
from app.database import SessionLocal
from .datasets import _get_dataset

router = APIRouter(tags=["statistics"])
DATA_ROOT = Path(settings.SOURCE_DATA_DIR)

STATS_SQL = text("""
    SELECT rs.*
    FROM raster_statistics rs
    JOIN raster_datasets rd ON rd.id = rs.dataset_id
    WHERE rd.year = :year AND rd.dataset_type = 'NDVI_OBSERVED'
""")


def _annual_stats(dataset_id: str):
    _get_dataset(dataset_id)
    try:
        year = int(dataset_id.removeprefix("ndvi_"))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Dataset không tồn tại") from exc
    with SessionLocal() as db:
        row = db.execute(STATS_SQL, {"year": year}).mappings().first()
    if row is None:
        raise HTTPException(status_code=404, detail="PostGIS chưa có thống kê dataset")
    return row


def _change_values():
    with rasterio.open(DATA_ROOT / "HCM_NDVI_2015.tif") as old_src, rasterio.open(DATA_ROOT / "HCM_NDVI_2025.tif") as new_src:
        old = old_src.read(1, masked=True).astype("float64")
        new = new_src.read(1, masked=True).astype("float64")
    invalid = (old < -1) | (old > 1) | (new < -1) | (new > 1)
    values = np.ma.masked_where(invalid, new - old).compressed()
    values = values[np.isfinite(values)]
    if not values.size:
        raise HTTPException(status_code=404, detail="Raster biến động không có pixel hợp lệ")
    return values


def _summary(values):
    return {
        "min": float(values.min()), "max": float(values.max()),
        "mean": float(values.mean()), "median": float(np.median(values)),
        "std": float(values.std()), "valid_pixels": int(values.size),
        "total_pixels": int(values.size),
    }


@router.get("/datasets/{dataset_id}/statistics")
def statistics(dataset_id: str):
    if dataset_id == "ndvi_change":
        return _summary(_change_values())
    row = _annual_stats(dataset_id)
    return {
        "min": row["min_value"], "max": row["max_value"],
        "mean": row["mean_value"], "median": row["median_value"],
        "std": row["std_dev"], "valid_pixels": row["valid_pixel_count"],
        "total_pixels": row["total_pixel_count"],
    }


@router.get("/datasets/{dataset_id}/histogram")
def histogram(dataset_id: str, bins: int = Query(50, ge=5, le=200)):
    if dataset_id == "ndvi_change" or bins != 50:
        values = _change_values() if dataset_id == "ndvi_change" else None
        if values is None:
            dataset = _get_dataset(dataset_id)
            with rasterio.open(Path(dataset["file_path"])) as src:
                values = src.read(1, masked=True).compressed().astype("float64")
            values = values[np.isfinite(values) & (values >= -1) & (values <= 1)]
        counts, edges = np.histogram(values, bins=bins)
        return {"bins": edges[:-1].tolist(), "counts": counts.tolist()}
    row = _annual_stats(dataset_id)
    payload = row["histogram_json"]
    return {"bins": payload["bin_edges"][:-1], "counts": payload["counts"]}


@router.get("/datasets/{dataset_id}/boxplot")
def boxplot(dataset_id: str):
    if dataset_id == "ndvi_change":
        values = _change_values()
        minimum, q1, median, q3, maximum = np.percentile(values, [0, 25, 50, 75, 100])
    else:
        row = _annual_stats(dataset_id)
        minimum, q1, median, q3, maximum = (
            row["min_value"], row["q1_value"], row["median_value"],
            row["q3_value"], row["max_value"],
        )
    iqr = q3 - q1
    return {
        "dataset_id": dataset_id, "min": float(minimum), "q1": float(q1),
        "median": float(median), "q3": float(q3), "max": float(maximum),
        "lower_whisker": float(max(minimum, q1 - 1.5 * iqr)),
        "upper_whisker": float(min(maximum, q3 + 1.5 * iqr)),
    }


@router.get("/datasets/{dataset_id}/change-summary")
def change_summary(dataset_id: str, threshold: float = 0.05):
    values = _change_values() if dataset_id == "ndvi_change" else None
    if values is None:
        raise HTTPException(status_code=400, detail="Change summary chỉ áp dụng cho ndvi_change")
    decreasing = int((values < -threshold).sum())
    stable = int((np.abs(values) <= threshold).sum())
    increasing = int((values > threshold).sum())
    total = decreasing + stable + increasing
    return {
        "dataset_id": dataset_id, "threshold": threshold,
        "decreasing_pixels": decreasing, "stable_pixels": stable,
        "increasing_pixels": increasing, "valid_pixels": total,
        "decreasing_percent": decreasing / total * 100,
        "stable_percent": stable / total * 100,
        "increasing_percent": increasing / total * 100,
    }
