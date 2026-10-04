from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import check_db_connection
from app.routers import datasets, forecast, statistics, tiles, timeseries

app = FastAPI(title="NDVI AI Backend", description="API phan tich va du bao NDVI TP.HCM", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.CORS_ORIGINS.split(",")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(datasets.router, prefix="/api")
app.include_router(forecast.router, prefix="/api")
app.include_router(statistics.router, prefix="/api")
app.include_router(tiles.router, prefix="/api")
app.include_router(timeseries.router, prefix="/api")

@app.get("/api")
async def api_root():
    return {"message": "NDVI AI Backend API", "version": "1.0.0"}

@app.get("/health")
@app.get("/api/health")
async def health_check():
    database_ok = check_db_connection()
    return {
        "status": "healthy" if database_ok else "degraded",
        "service": "ndvi-ai-backend",
        "database": "postgis-connected" if database_ok else "postgis-unavailable",
        "raster_storage": "external-geotiff",
    }


FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"

@app.get("/{full_path:path}", include_in_schema=False)
async def serve_frontend(full_path: str):
    if not FRONTEND_DIST.exists():
        raise HTTPException(status_code=404, detail="Frontend build chưa tồn tại")
    requested = (FRONTEND_DIST / full_path).resolve()
    if requested.is_file() and FRONTEND_DIST.resolve() in requested.parents:
        return FileResponse(requested)
    return FileResponse(FRONTEND_DIST / "index.html")
