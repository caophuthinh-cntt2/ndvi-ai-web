from pathlib import Path
import numpy as np
import rasterio
from fastapi import APIRouter, HTTPException, Query
from .datasets import _get_dataset

router = APIRouter(tags=["statistics"])
DATA_ROOT = Path("D:/NDVI")

def _values(dataset_id: str):
    dataset = _get_dataset(dataset_id)
    if dataset_id == "ndvi_change":
        with rasterio.open(DATA_ROOT / "HCM_NDVI_2015.tif") as old_src, rasterio.open(DATA_ROOT / "HCM_NDVI_2025.tif") as new_src:
            old = old_src.read(1, masked=True).astype("float64")
            new = new_src.read(1, masked=True).astype("float64")
            values = (new - old).compressed()
    else:
        with rasterio.open(DATA_ROOT / dataset["file"]) as src:
            values = src.read(1, masked=True).compressed().astype("float64")
    values = values[np.isfinite(values)]
    if not len(values):
        raise HTTPException(status_code=404, detail="Raster không có pixel hợp lệ")
    return values

@router.get("/datasets/{dataset_id}/statistics")
def statistics(dataset_id: str):
    values = _values(dataset_id)
    return {"min": float(values.min()), "max": float(values.max()), "mean": float(values.mean()),
            "median": float(np.median(values)), "std": float(values.std()),
            "valid_pixels": int(values.size), "total_pixels": int(values.size)}

@router.get("/datasets/{dataset_id}/histogram")
def histogram(dataset_id: str, bins: int = Query(50, ge=5, le=200)):
    values = _values(dataset_id)
    counts, edges = np.histogram(values, bins=bins)
    return {"bins": [float(x) for x in edges[:-1]], "counts": [int(x) for x in counts]}

@router.get("/datasets/{dataset_id}/boxplot")
def boxplot(dataset_id: str):
    values = _values(dataset_id)
    q1, median, q3 = np.percentile(values, [25, 50, 75])
    iqr = q3 - q1
    return {"dataset_id": dataset_id, "min": float(values.min()), "q1": float(q1),
            "median": float(median), "q3": float(q3), "max": float(values.max()),
            "lower_whisker": float(max(values.min(), q1 - 1.5 * iqr)),
            "upper_whisker": float(min(values.max(), q3 + 1.5 * iqr))}

@router.get("/datasets/{dataset_id}/change-summary")
def change_summary(dataset_id: str, threshold: float = 0.05):
    values = _values(dataset_id)
    decreasing = int((values < -threshold).sum())
    stable = int((np.abs(values) <= threshold).sum())
    increasing = int((values > threshold).sum())
    total = decreasing + stable + increasing
    return {"dataset_id": dataset_id, "threshold": threshold, "decreasing_pixels": decreasing,
            "stable_pixels": stable, "increasing_pixels": increasing, "valid_pixels": total,
            "decreasing_percent": decreasing / total * 100, "stable_percent": stable / total * 100,
            "increasing_percent": increasing / total * 100}
