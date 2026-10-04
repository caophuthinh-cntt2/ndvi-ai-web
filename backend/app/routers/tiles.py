from pathlib import Path
import io
import math
import numpy as np
import rasterio
from PIL import Image
from rasterio.enums import Resampling
from rasterio.warp import reproject
from fastapi import APIRouter, HTTPException, Response
from app.config import settings

router = APIRouter(tags=["tiles"])
DATA_ROOT = Path(settings.SOURCE_DATA_DIR)
FILES = {f"ndvi_{year}": f"HCM_NDVI_{year}.tif" for year in range(2015, 2026)}
FILES["ndvi_change"] = "HCM_NDVI_Change_2015_2025.tif"

def _tile_bounds(x: int, y: int, z: int):
    n = 2 ** z
    west, east = x / n * 360 - 180, (x + 1) / n * 360 - 180
    north = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * y / n))))
    south = math.degrees(math.atan(math.sinh(math.pi * (1 - 2 * (y + 1) / n))))
    return west, south, east, north

@router.get("/tiles/{dataset_id}/{z}/{x}/{y}.png")
def tile(dataset_id: str, z: int, x: int, y: int):
    filename = FILES.get(dataset_id)
    if filename is None:
        raise HTTPException(status_code=404, detail="Dataset không tồn tại")
    west, south, east, north = _tile_bounds(x, y, z)
    dst_transform = rasterio.transform.from_bounds(west, south, east, north, 256, 256)
    destination = np.full((256, 256), np.nan, dtype="float32")
    if dataset_id == "ndvi_change":
        old = np.full((256, 256), np.nan, dtype="float32")
        new = np.full((256, 256), np.nan, dtype="float32")
        for year, target in ((2015, old), (2025, new)):
            with rasterio.open(DATA_ROOT / FILES[f"ndvi_{year}"]) as src:
                reproject(rasterio.band(src, 1), target, src_transform=src.transform, src_crs=src.crs,
                          dst_transform=dst_transform, dst_crs="EPSG:4326", resampling=Resampling.bilinear,
                          dst_nodata=np.nan)
        source_valid = np.isfinite(old) & np.isfinite(new) & (old >= -1) & (old <= 1) & (new >= -1) & (new <= 1)
        destination = np.where(source_valid, new - old, np.nan)
    else:
        with rasterio.open(DATA_ROOT / filename) as src:
            reproject(rasterio.band(src, 1), destination, src_transform=src.transform, src_crs=src.crs,
                      dst_transform=dst_transform, dst_crs="EPSG:4326", resampling=Resampling.bilinear,
                      dst_nodata=np.nan)
    valid = np.isfinite(destination)
    if dataset_id != "ndvi_change":
        valid &= (destination >= -1) & (destination <= 1)
    rgba = np.zeros((256, 256, 4), dtype=np.uint8)
    if valid.any():
        low, high = (-0.5, 0.5) if dataset_id == "ndvi_change" else (-1.0, 1.0)
        scaled = np.clip((destination - low) / (high - low), 0, 1)
        rgba[..., 0] = (255 * scaled).astype(np.uint8)
        rgba[..., 1] = (255 * (1 - np.abs(scaled - 0.5) * 2)).astype(np.uint8)
        rgba[..., 2] = (255 * (1 - scaled)).astype(np.uint8)
        rgba[..., 3] = (valid * 210).astype(np.uint8)
    buffer = io.BytesIO()
    Image.fromarray(rgba, "RGBA").save(buffer, format="PNG", optimize=True)
    return Response(content=buffer.getvalue(), media_type="image/png", headers={"Cache-Control": "public, max-age=3600"})
