from pathlib import Path
import math

import rasterio
from rasterio.windows import Window
from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import text

from app.config import settings
from app.database import SessionLocal

router = APIRouter(tags=["datasets"])
DATA_ROOT = Path(settings.SOURCE_DATA_DIR)

DATASET_SQL = text("""
    SELECT year, file_path, crs, width, height, resolution_x, resolution_y,
           nodata_value, dtype, metadata_json,
           ST_XMin(Box3D(bounds)) AS min_lng,
           ST_YMin(Box3D(bounds)) AS min_lat,
           ST_XMax(Box3D(bounds)) AS max_lng,
           ST_YMax(Box3D(bounds)) AS max_lat
    FROM raster_datasets
    WHERE dataset_type = 'NDVI_OBSERVED'
      AND (:year IS NULL OR year = :year)
    ORDER BY year
""")


def _rows(year=None):
    with SessionLocal() as db:
        return db.execute(DATASET_SQL, {"year": year}).mappings().all()


def _annual_metadata(row):
    year = int(row["year"])
    return {
        "id": f"ndvi_{year}",
        "name": f"NDVI năm {year}",
        "type": f"ndvi_{year}",
        "year": year,
        "resolution": f"{round(float(row['resolution_x']) * 111_320)}m",
        "dimensions": {"width": row["width"], "height": row["height"]},
        "crs": row["crs"],
        "source": "GeoTIFF ngoài database; metadata và thống kê trong PostGIS",
        "nodata": row["nodata_value"],
        "file_type": "GeoTIFF",
        "data_status": "observed",
        "bounds": {
            "minLat": row["min_lat"], "maxLat": row["max_lat"],
            "minLng": row["min_lng"], "maxLng": row["max_lng"],
        },
    }


def _change_metadata(rows):
    base = rows[-1]
    return {
        **_annual_metadata(base),
        "id": "ndvi_change",
        "name": "Biến động NDVI 2015–2025",
        "type": "ndvi_change",
        "year": None,
        "source": "Tính động từ GeoTIFF 2025 trừ GeoTIFF 2015",
    }


def _get_dataset(dataset_id: str):
    if dataset_id == "ndvi_change":
        rows = _rows()
        if not rows:
            raise HTTPException(status_code=503, detail="PostGIS chưa có dữ liệu raster")
        return {**_change_metadata(rows), "file_path": str(DATA_ROOT / "HCM_NDVI_Change_2015_2025.tif")}
    if not dataset_id.startswith("ndvi_"):
        raise HTTPException(status_code=404, detail="Dataset không tồn tại")
    try:
        year = int(dataset_id.removeprefix("ndvi_"))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail="Dataset không tồn tại") from exc
    rows = _rows(year)
    if not rows:
        raise HTTPException(status_code=404, detail="Dataset không tồn tại trong PostGIS")
    row = rows[0]
    return {**_annual_metadata(row), "file_path": str(DATA_ROOT / Path(row["file_path"]).name)}


@router.get("/datasets")
def list_datasets():
    rows = _rows()
    if not rows:
        raise HTTPException(status_code=503, detail="PostGIS chưa có metadata raster")
    return [_annual_metadata(row) for row in rows] + [_change_metadata(rows)]


@router.get("/datasets/{dataset_id}")
def get_dataset(dataset_id: str):
    dataset = _get_dataset(dataset_id)
    dataset.pop("file_path", None)
    return dataset


def _read_pixel(path: Path, lat: float, lng: float):
    with rasterio.open(path) as src:
        row, col = src.index(lng, lat)
        if row < 0 or col < 0 or row >= src.height or col >= src.width:
            raise IndexError
        value = float(src.read(1, window=Window(col, row, 1, 1))[0, 0])
        return value if math.isfinite(value) and -1 <= value <= 1 else None


@router.get("/datasets/{dataset_id}/pixel")
def get_pixel(dataset_id: str, lat: float = Query(...), lng: float = Query(...)):
    try:
        if dataset_id == "ndvi_change":
            old = _read_pixel(DATA_ROOT / "HCM_NDVI_2015.tif", lat, lng)
            new = _read_pixel(DATA_ROOT / "HCM_NDVI_2025.tif", lat, lng)
            value = None if old is None or new is None else new - old
        else:
            dataset = _get_dataset(dataset_id)
            value = _read_pixel(Path(dataset["file_path"]), lat, lng)
        return {"value": value, "lat": lat, "lng": lng}
    except (IndexError, rasterio.errors.RasterioIOError):
        raise HTTPException(status_code=404, detail="Điểm nằm ngoài raster hoặc không đọc được dữ liệu")


@router.get("/raster/value")
def get_raster_value(dataset_id: str = Query(...), lat: float = Query(...), lng: float = Query(...)):
    return get_pixel(dataset_id, lat, lng)
