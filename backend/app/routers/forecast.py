from pathlib import Path
import csv
import zipfile

from fastapi import APIRouter, HTTPException, Response

router = APIRouter(tags=["forecast"])
ZIP_PATH = Path("D:/NDVI/HCM_NDVI_Forecast_Maps_2026.zip")

def _forecast_rows():
    if not ZIP_PATH.exists():
        raise HTTPException(status_code=503, detail="Không tìm thấy file dự báo nguồn")
    with zipfile.ZipFile(ZIP_PATH) as archive:
        with archive.open("HCM_NDVI_Forecast_2026.csv") as stream:
            return list(csv.DictReader(line.decode("utf-8-sig") for line in stream))

@router.get("/forecast/2026")
def forecast_2026():
    rows = _forecast_rows()
    months = [f"{int(row['year']):04d}-{int(row['month']):02d}" for row in rows]
    values = [float(row["NDVI_forecast"]) for row in rows]
    return {"model": "Random Forest", "forecast_period": "2026", "values": values, "months": months,
            "statistics": {"min": min(values), "max": max(values), "mean": sum(values) / len(values)},
            "status": "reference_results",
            "source_note": "Kết quả tham chiếu từ bộ dữ liệu và mô hình do giảng viên cung cấp"}

@router.get("/models")
def models():
    return ["Random Forest", "Extra Trees", "HistGradientBoosting", "Seasonal Naive"]

@router.get("/models/metrics")
def model_metrics():
    return [
        {"model_name": "Random Forest", "mae": 0.021111, "rmse": 0.027339, "r2": 0.221221},
        {"model_name": "Extra Trees", "mae": 0.020286, "rmse": 0.027439, "r2": 0.193925},
        {"model_name": "HistGradientBoosting", "mae": 0.025380, "rmse": 0.032245, "r2": -0.293690},
        {"model_name": "Seasonal Naive", "mae": 0.026834, "rmse": 0.036315, "r2": -0.760498},
    ]

@router.get("/forecast/2026/maps/{month}.png")
def forecast_map(month: int):
    if month < 1 or month > 12:
        raise HTTPException(status_code=400, detail="Month phải nằm trong khoảng 1-12")
    filename = f"HCM_NDVI_Forecast_2026_M{month:02d}.png"
    with zipfile.ZipFile(ZIP_PATH) as archive:
        try:
            content = archive.read(filename)
        except KeyError:
            raise HTTPException(status_code=404, detail="Không tìm thấy bản đồ dự báo tháng")
    return Response(content=content, media_type="image/png", headers={"Cache-Control": "public, max-age=86400"})

@router.get("/forecast/2026/maps")
def forecast_maps():
    return [{"month": month, "label": f"Tháng {month:02d}", "url": f"/api/forecast/2026/maps/{month}.png"} for month in range(1, 13)]
