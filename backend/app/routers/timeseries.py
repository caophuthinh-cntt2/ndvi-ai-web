import numpy as np
from fastapi import APIRouter, HTTPException
from sqlalchemy import text

from app.database import SessionLocal

router = APIRouter(tags=["timeseries"])


@router.get("/timeseries")
def timeseries():
    with SessionLocal() as db:
        rows = db.execute(text("""
            SELECT year, ndvi_mean
            FROM ndvi_timeseries
            WHERE source_type = 'OBSERVED'
            ORDER BY year, month
        """)).mappings().all()
    if not rows:
        raise HTTPException(status_code=503, detail="PostGIS chưa có chuỗi thời gian")
    data = [{"date": str(row["year"]), "value": float(row["ndvi_mean"])} for row in rows]
    values = np.array([point["value"] for point in data], dtype="float64")
    return {
        "data": data,
        "statistics": {
            "min": float(values.min()), "max": float(values.max()),
            "mean": float(values.mean()), "median": float(np.median(values)),
            "std": float(values.std()),
        },
        "status": "observed_postgis_annual",
        "source_note": "Chuỗi năm lấy từ bảng ndvi_timeseries trong PostGIS; giá trị được tính từ 11 GeoTIFF ngoài database.",
    }
