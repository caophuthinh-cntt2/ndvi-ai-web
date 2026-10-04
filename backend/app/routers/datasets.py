from pathlib import Path
import math

import rasterio
from fastapi import APIRouter, HTTPException, Query

router = APIRouter(tags=["datasets"])
DATA_ROOT = Path("D:/NDVI")
DATASETS = [
    {"id": f"ndvi_{year}", "name": f"NDVI năm {year}", "type": f"ndvi_{year}", "year": year, "file": f"HCM_NDVI_{year}.tif"}
    for year in range(2015, 2026)
]
DATASETS.append({"id": "ndvi_change", "name": "Biến động NDVI 2015–2025", "type": "ndvi_change", "file": "HCM_NDVI_Change_2015_2025.tif"})

def _get_dataset(dataset_id: str):
    dataset = next((item for item in DATASETS if item["id"] == dataset_id), None)
    if dataset is None:
        raise HTTPException(status_code=404, detail="Dataset không tồn tại")
    return dataset

def _metadata(dataset):
    result = {k: v for k, v in dataset.items() if k != "file"}
    with rasterio.open(DATA_ROOT / dataset["file"]) as src:
        left, bottom, right, top = src.bounds
        result.update({"resolution": "30m", "dimensions": {"width": src.width, "height": src.height},
                       "crs": str(src.crs), "source": "Raster NDVI nguồn cung cấp",
                       "nodata": src.nodata, "file_type": "GeoTIFF", "data_status": "observed",
                       "bounds": {"minLat": bottom, "maxLat": top, "minLng": left, "maxLng": right}})
    return result

@router.get("/datasets")
def list_datasets():
    return [_metadata(item) for item in DATASETS]

@router.get("/datasets/{dataset_id}")
def get_dataset(dataset_id: str):
    return _metadata(_get_dataset(dataset_id))

@router.get("/datasets/{dataset_id}/pixel")
def get_pixel(dataset_id: str, lat: float = Query(...), lng: float = Query(...)):
    dataset = _get_dataset(dataset_id)
    try:
        with rasterio.open(DATA_ROOT / dataset["file"]) as src:
            row, col = src.index(lng, lat)
            if row < 0 or col < 0 or row >= src.height or col >= src.width:
                raise IndexError
            value = float(src.read(1)[row, col])
            return {"value": value if math.isfinite(value) else None, "lat": lat, "lng": lng}
    except (IndexError, rasterio.errors.RasterioIOError):
        raise HTTPException(status_code=404, detail="Điểm nằm ngoài raster hoặc không đọc được dữ liệu")

@router.get("/raster/value")
def get_raster_value(dataset_id: str = Query(...), lat: float = Query(...), lng: float = Query(...)):
    """Canonical pixel-value endpoint; kept separate from the dataset convenience route."""
    return get_pixel(dataset_id, lat, lng)
