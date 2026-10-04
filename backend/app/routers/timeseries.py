from pathlib import Path
import numpy as np
import rasterio
from fastapi import APIRouter

router = APIRouter(tags=["timeseries"])
DATA_ROOT = Path("D:/NDVI")

@router.get("/timeseries")
def timeseries():
    data = []
    for year in range(2015, 2026):
        filename = f"HCM_NDVI_{year}.tif"
        with rasterio.open(DATA_ROOT / filename) as src:
            values = src.read(1, masked=True).compressed().astype("float64")
        values = values[np.isfinite(values)]
        data.append({"date": str(year), "value": float(values.mean())})
    values = [point["value"] for point in data]
    return {"data": data, "statistics": {"min": min(values), "max": max(values),
            "mean": sum(values) / len(values), "median": float(np.median(values)), "std": float(np.std(values))},
            "status": "observed_raster_annual", "source_note": "Giá trị trung bình theo năm được tính trực tiếp từ 11 raster GeoTIFF quan sát 2015–2025; chưa phải chuỗi 132 tháng."}
