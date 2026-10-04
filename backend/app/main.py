from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
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

@app.get("/")
async def root():
    return {"message": "NDVI AI Backend API", "version": "1.0.0"}

@app.get("/health")
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "ndvi-ai-backend", "database": "filesystem-mode"}
