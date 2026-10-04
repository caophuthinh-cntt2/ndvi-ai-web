from pathlib import Path
import io
import math
import threading
import numpy as np
import rasterio
from PIL import Image
from rasterio.enums import Resampling
from rasterio.warp import transform_bounds
from rasterio.windows import from_bounds
from fastapi import APIRouter, HTTPException, Response
from app.config import settings

router = APIRouter(tags=["tiles"])
DATA_ROOT = Path(settings.SOURCE_DATA_DIR)
FILES = {f"ndvi_{year}": f"HCM_NDVI_{year}.tif" for year in range(2015, 2026)}
FILES["ndvi_change"] = "HCM_NDVI_Change_2015_2025.tif"
TILE_SEMAPHORE = threading.BoundedSemaphore(2)

def _tile_bounds(x: int, y: int, z: int):
    n = 2 ** z
    west, east = x / n * 360 - 180, (x + 1) / n * 360 - 180
    north = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n))))
    south = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * (y + 1) / n))))
    return west, south, east, north


def _read_tile(path: Path, bounds):
    west, south, east, north = bounds
    with rasterio.open(path) as src:
        if src.crs and src.crs.to_epsg() != 4326:
            west, south, east, north = transform_bounds(
                "EPSG:4326", src.crs, west, south, east, north
            )
        window = from_bounds(west, south, east, north, src.transform)
        return src.read(
            1,
            window=window,
            out_shape=(256, 256),
            boundless=True,
            masked=True,
            resampling=Resampling.bilinear,
        ).filled(np.nan).astype("float32")

def _render_tile(dataset_id: str, z: int, x: int, y: int):
    filename = FILES.get(dataset_id)
    if filename is None:
        raise HTTPException(status_code=404, detail="Dataset không tồn tại")
    bounds = _tile_bounds(x, y, z)
    if dataset_id == "ndvi_change":
        old = _read_tile(DATA_ROOT / FILES["ndvi_2015"], bounds)
        new = _read_tile(DATA_ROOT / FILES["ndvi_2025"], bounds)
        source_valid = np.isfinite(old) & np.isfinite(new) & (old >= -1) & (old <= 1) & (new >= -1) & (new <= 1)
        destination = np.where(source_valid, new - old, np.nan)
    else:
        destination = _read_tile(DATA_ROOT / filename, bounds)
    valid = np.isfinite(destination)
    if dataset_id != "ndvi_change":
        valid &= (destination >= -1) & (destination <= 1)
    rgba = np.zeros((256, 256, 4), dtype=np.uint8)
    if valid.any():
        low, high = (-0.5, 0.5) if dataset_id == "ndvi_change" else (-1.0, 1.0)
        scaled = np.where(valid, np.clip((destination - low) / (high - low), 0, 1), 0)
        rgba[..., 0] = (255 * scaled).astype(np.uint8)
        rgba[..., 1] = (255 * (1 - np.abs(scaled - 0.5) * 2)).astype(np.uint8)
        rgba[..., 2] = (255 * (1 - scaled)).astype(np.uint8)
        rgba[..., 3] = (valid * 210).astype(np.uint8)
    buffer = io.BytesIO()
    Image.fromarray(rgba, "RGBA").save(buffer, format="PNG", optimize=True)
    return Response(content=buffer.getvalue(), media_type="image/png", headers={"Cache-Control": "public, max-age=3600"})


@router.get("/tiles/{dataset_id}/{z}/{x}/{y}.png")
def tile(dataset_id: str, z: int, x: int, y: int):
    with TILE_SEMAPHORE, rasterio.Env(GDAL_CACHEMAX=16, GDAL_NUM_THREADS="1"):
        return _render_tile(dataset_id, z, x, y)
