# NDVI AI WebGIS - Architecture Design Document

## Document Information

- **Project**: NDVI Forecasting WebGIS for Ho Chi Minh City
- **Version**: 1.0.0
- **Date**: 2026-10-03
- **Target Environment**: Windows Localhost Demo

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Technology Stack](#technology-stack)
3. [Architecture Diagram](#architecture-diagram)
4. [Database Design](#database-design)
5. [Backend Architecture](#backend-architecture)
6. [Frontend Architecture](#frontend-architecture)
7. [Data Processing Pipeline](#data-processing-pipeline)
8. [Project Structure](#project-structure)
9. [Configuration Management](#configuration-management)
10. [Deployment Strategy](#deployment-strategy)
11. [Performance Optimization](#performance-optimization)
12. [Security Considerations](#security-considerations)

---

## 1. System Overview

### 1.1 Purpose

Web-based GIS application for visualizing and forecasting NDVI (Normalized Difference Vegetation Index) changes in Ho Chi Minh City using time series satellite imagery and AI/ML models.

### 1.2 Key Features

- **Interactive Map Visualization**: Display NDVI rasters (2015, 2025, Change Detection, 2026 Forecast)
- **Tile Server**: Fast XYZ tile serving using Cloud-Optimized GeoTIFFs (COG)
- **Point Query**: Extract NDVI values at clicked locations
- **Time Series Analysis**: Visualize historical NDVI trends (2015-2025)
- **AI Forecasting**: Display ML model predictions for 2026
- **Statistics Dashboard**: Pre-computed statistics and comparative analysis
- **Model Management**: Track and compare multiple AI model performances

### 1.3 User Workflow


```
User ? Frontend (React + Leaflet)
    ?
    ? Map displays NDVI layers via tiles
    ? User clicks map ? Point query ? Shows NDVI value
    ? Selects time range ? Chart displays time series + forecast
    ? Compares datasets ? Statistics dashboard
```

---

## 2. Technology Stack

### 2.1 Frontend

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Framework | React | 18+ | UI framework |
| Language | TypeScript | 5+ | Type safety |
| Build Tool | Vite | 5+ | Fast dev server & bundling |
| Styling | Tailwind CSS | 3+ | Utility-first CSS |
| Mapping | Leaflet | 1.9+ | Interactive maps |
| Charts | Apache ECharts | 5+ | Time series visualization |
| State | Zustand | 4+ | Lightweight state management |
| HTTP Client | Axios | 1.6+ | API communication |

### 2.2 Backend

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Framework | FastAPI | 0.104+ | REST API framework |
| Language | Python | 3.11+ | Backend logic |
| Database | PostgreSQL | 14+ | Relational database |
| Spatial Extension | PostGIS | 3.3+ | Spatial queries |
| Raster Library | rasterio | 1.3+ | GeoTIFF processing |
| Tile Server | rio-tiler | 6+ | COG tile generation |
| ORM | SQLAlchemy | 2+ | Database ORM |
| Validation | Pydantic | 2+ | Data validation |
| ASGI Server | Uvicorn | 0.24+ | Production server |

### 2.3 Data Processing

| Tool | Purpose |
|------|---------|
| GDAL | Raster manipulation, COG conversion |
| NumPy | Numerical operations |
| Pandas | Time series data handling |
| Scikit-learn | Model evaluation metrics |
| TensorFlow/PyTorch | AI model inference (optional) |

### 2.4 Development Tools

- **Version Control**: Git
- **Package Manager (Python)**: pip + venv
- **Package Manager (Node)**: npm/pnpm
- **Database Client**: pgAdmin 4 / DBeaver
- **API Testing**: Thunder Client / Postman
- **Code Quality**: ESLint, Prettier, Ruff

---

## 3. Architecture Diagram

### 3.1 System Architecture (High Level)

```
+-------------------------------------------------------------+
¦                        CLIENT BROWSER                        ¦
¦                     (http://localhost:5173)                  ¦
+-------------------------------------------------------------+
                         ¦
                         ¦ HTTP/REST API
                         ?
+-------------------------------------------------------------+
¦                    FRONTEND (React + Vite)                   ¦
¦  +----------+  +----------+  +----------+  +----------+   ¦
¦  ¦Dashboard ¦  ¦   Maps   ¦  ¦Analytics ¦  ¦ Forecast ¦   ¦
¦  +----------+  +----------+  +----------+  +----------+   ¦
¦                                                               ¦
¦  +-----------------------------------------------------+   ¦
¦  ¦  Leaflet (Map) + ECharts (Graphs) + API Client      ¦   ¦
¦  +-----------------------------------------------------+   ¦
+-------------------------------------------------------------+
                         ¦
                         ¦ Axios HTTP Requests
                         ?
+-------------------------------------------------------------+
¦                 BACKEND API (FastAPI)                        ¦
¦              (http://localhost:8000/api/v1)                  ¦
¦                                                               ¦
¦  +------------------------------------------------------+  ¦
¦  ¦                    API Routers                        ¦  ¦
¦  ¦  /datasets  /tiles  /raster  /statistics             ¦  ¦
¦  ¦  /timeseries  /models  /forecast                     ¦  ¦
¦  +------------------------------------------------------+  ¦
¦                          ¦                                   ¦
¦  +---------------------------------------------------+    ¦
¦  ¦              ¦                  ¦                   ¦    ¦
¦  ?              ?                  ?                   ?    ¦
¦ +--------+  +--------+  +--------------+  +----------+   ¦
¦ ¦Database¦  ¦  COG   ¦  ¦   Rasterio   ¦  ¦ Business ¦   ¦
¦ ¦ Layer  ¦  ¦  Tile  ¦  ¦   (Point     ¦  ¦  Logic   ¦   ¦
¦ ¦(SQLAlch¦  ¦ Server ¦  ¦   Query)     ¦  ¦          ¦   ¦
¦ ¦emy)    ¦  ¦(rio-   ¦  +--------------+  +----------+   ¦
¦ +--------+  ¦tiler)  ¦                                     ¦
¦      ¦      +--------+                                     ¦
+------+-----------+-----------------------------------------+
       ¦           ¦
       ¦           ¦ Read COG Files
       ?           ?
+--------------------------------------+  +------------------+
¦   PostgreSQL + PostGIS Database      ¦  ¦  File System     ¦
¦   - raster_datasets                  ¦  ¦  D:\NDVI\data\   ¦
¦   - raster_statistics                ¦  ¦    +- raw\       ¦
¦   - ndvi_timeseries                  ¦  ¦    +- processed\ ¦
¦   - model_runs                       ¦  ¦    +- cog\       ¦
¦   - forecast_results                 ¦  ¦                  ¦
+--------------------------------------+  +------------------+
```

### 3.2 Data Flow

#### 3.2.1 Map Tile Request Flow

```
User pans map
    ? Leaflet requests tile: /api/v1/tiles/1/12/3245/2156.png
    ? FastAPI router receives request
    ? rio-tiler reads COG file at zoom/x/y
    ? Applies colormap (greens, rdylgn)
    ? Returns PNG image (256x256)
    ? Leaflet displays tile on map
```

#### 3.2.2 Point Query Flow

```
User clicks map (lat, lng)
    ? Frontend sends: GET /api/v1/raster/point?dataset_id=1&lat=10.7756&lng=106.7019
    ? Backend opens raster with rasterio
    ? Converts lat/lng to pixel row/col
    ? Reads pixel value
    ? Returns JSON: { value: 0.6523 }
    ? Frontend displays in popup/sidebar
```

#### 3.2.3 Time Series Chart Flow

```
User selects date range
    ? GET /api/v1/timeseries/complete?start_date=2015-01-01&end_date=2026-12-31
    ? Backend queries:
        - ndvi_timeseries table (observed data)
        - forecast_results table (predictions)
    ? Returns combined JSON
    ? Frontend renders ECharts line chart with confidence intervals
```

---

## 4. Database Design

### 4.1 Entity Relationship Diagram

```
+-----------------+
¦  study_areas    ¦
¦-----------------¦
¦ id (PK)         ¦
¦ name            ¦
¦ geom (POLYGON)  ¦
+-----------------+

+----------------------+
¦  raster_datasets     ¦
¦----------------------¦
¦ id (PK)              ¦
¦ name                 ¦
¦ dataset_type (ENUM)  ¦
¦ observation_date     ¦
¦ file_path            ¦
¦ cog_path             ¦?--------+
¦ crs, width, height   ¦         ¦
¦ metadata_json        ¦         ¦
+----------------------+         ¦
           ¦                      ¦
           ¦ 1:1                  ¦ FK
           ?                      ¦
+----------------------+         ¦
¦ raster_statistics    ¦         ¦
¦----------------------¦         ¦
¦ id (PK)              ¦         ¦
¦ dataset_id (FK)      ¦---------¦
¦ min, max, mean       ¦         ¦
¦ median, std_dev      ¦         ¦
¦ valid_pixel_count    ¦         ¦
¦ ndvi_*_count         ¦         ¦
+----------------------+         ¦
                                 ¦
+----------------------+         ¦
¦  ndvi_timeseries     ¦         ¦
¦----------------------¦         ¦
¦ id (PK)              ¦         ¦
¦ observation_date     ¦         ¦
¦ ndvi_mean            ¦         ¦
¦ source_type (ENUM)   ¦         ¦
¦ dataset_id (FK)      ¦---------+
+----------------------+

+----------------------+
¦   model_runs         ¦
¦----------------------¦
¦ id (PK)              ¦
¦ model_type (ENUM)    ¦
¦ model_name           ¦
¦ mae, rmse, r2_score  ¦
¦ parameters_json      ¦
¦ is_production        ¦
+----------------------+
           ¦
           ¦ 1:N
           ?
+----------------------+
¦  forecast_results    ¦
¦----------------------¦
¦ id (PK)              ¦
¦ model_run_id (FK)    ¦
¦ forecast_date        ¦
¦ predicted_ndvi       ¦
¦ confidence_lower     ¦
¦ confidence_upper     ¦
+----------------------+
```

### 4.2 Key Design Decisions

**4.2.1 Separation of Metadata and Raster Data**
- Database stores metadata, file paths, and statistics
- Actual raster data (.tif files) stored on filesystem
- Enables efficient queries without loading large rasters

**4.2.2 Pre-computed Statistics**
- `raster_statistics` table stores pre-calculated values
- Avoids expensive on-the-fly computations
- Trade-off: storage vs query speed

**4.2.3 Time Series Storage**
- Monthly aggregated values in `ndvi_timeseries`
- Separate from raw raster datasets
- Optimized for chart rendering

**4.2.4 Model Tracking**
- `model_runs` stores hyperparameters as JSONB
- Flexible schema for different model types
- `is_production` flag for active model selection

**4.2.5 Forecast Confidence Intervals**
- Store lower/upper bounds for uncertainty visualization
- `is_extrapolation` flag for dates beyond training range

### 4.3 Indexing Strategy

See `database-schema.sql` for complete index definitions. Key indexes:

- **Spatial**: GIST indexes on geometry columns
- **Temporal**: B-tree indexes on date columns
- **Composite**: Multi-column indexes for common query patterns
- **JSONB**: GIN indexes for metadata searches

---

## 5. Backend Architecture

### 5.1 Directory Structure

```
backend/
+-- app/
¦   +-- __init__.py
¦   +-- main.py                    # FastAPI app entry point
¦   +-- config.py                  # Configuration (env vars)
¦   +-- database.py                # SQLAlchemy setup
¦   ¦
¦   +-- models/                    # SQLAlchemy ORM models
¦   ¦   +-- __init__.py
¦   ¦   +-- dataset.py
¦   ¦   +-- statistics.py
¦   ¦   +-- timeseries.py
¦   ¦   +-- model.py
¦   ¦   +-- forecast.py
¦   ¦
¦   +-- schemas/                   # Pydantic schemas
¦   ¦   +-- __init__.py
¦   ¦   +-- dataset.py
¦   ¦   +-- statistics.py
¦   ¦   +-- timeseries.py
¦   ¦   +-- model.py
¦   ¦   +-- forecast.py
¦   ¦
¦   +-- routers/                   # API route handlers
¦   ¦   +-- __init__.py
¦   ¦   +-- health.py
¦   ¦   +-- datasets.py
¦   ¦   +-- tiles.py
¦   ¦   +-- raster.py
¦   ¦   +-- statistics.py
¦   ¦   +-- timeseries.py
¦   ¦   +-- models.py
¦   ¦   +-- forecast.py
¦   ¦
¦   +-- services/                  # Business logic
¦   ¦   +-- __init__.py
¦   ¦   +-- dataset_service.py
¦   ¦   +-- tile_service.py        # COG tile generation
¦   ¦   +-- raster_service.py      # Rasterio operations
¦   ¦   +-- statistics_service.py
¦   ¦   +-- timeseries_service.py
¦   ¦
¦   +-- utils/                     # Utilities
¦   ¦   +-- __init__.py
¦   ¦   +-- colormaps.py          # NDVI colormaps
¦   ¦   +-- validators.py         # Input validation
¦   ¦   +-- exceptions.py         # Custom exceptions
¦   ¦
¦   +-- dependencies.py            # FastAPI dependencies
¦
+-- tests/
¦   +-- test_routers/
¦   +-- test_services/
¦   +-- conftest.py
¦
+-- requirements.txt
+-- .env.example
+-- README.md
```


### 5.2 Core Components

#### 5.2.1 Main Application (`main.py`)

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import (
    health, datasets, tiles, raster, 
    statistics, timeseries, models, forecast
)

app = FastAPI(
    title="NDVI AI WebGIS API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# Register routers
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(datasets.router, prefix="/api/v1/datasets", tags=["datasets"])
app.include_router(tiles.router, prefix="/api/v1/tiles", tags=["tiles"])
app.include_router(raster.router, prefix="/api/v1/raster", tags=["raster"])
app.include_router(statistics.router, prefix="/api/v1/statistics", tags=["statistics"])
app.include_router(timeseries.router, prefix="/api/v1/timeseries", tags=["timeseries"])
app.include_router(models.router, prefix="/api/v1/models", tags=["models"])
app.include_router(forecast.router, prefix="/api/v1/forecast", tags=["forecast"])
```

#### 5.2.2 Configuration (`config.py`)

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/ndvi_db"
    
    # File paths (Windows)
    DATA_DIR: str = "D:\\NDVI\\data"
    RAW_DIR: str = "D:\\NDVI\\data\\raw"
    PROCESSED_DIR: str = "D:\\NDVI\\data\\processed"
    COG_DIR: str = "D:\\NDVI\\data\\cog"
    
    # Tile server
    TILE_SIZE: int = 256
    MAX_ZOOM: int = 18
    DEFAULT_COLORMAP: str = "greens"
    
    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "NDVI AI WebGIS"
    
    class Config:
        env_file = ".env"

settings = Settings()
```

#### 5.2.3 Tile Service (`tile_service.py`)

```python
from rio_tiler.io import COGReader
from rio_tiler.colormap import cmap

def generate_tile(
    cog_path: str,
    z: int,
    x: int,
    y: int,
    colormap: str = "greens",
    rescale: tuple = None
) -> bytes:
    """Generate PNG tile from COG"""
    
    with COGReader(cog_path) as cog:
        img = cog.tile(x, y, z)
        
        if rescale:
            img = img.post_process(in_range=rescale)
        
        img = img.render(colormap=cmap.get(colormap))
        
        return img
```

#### 5.2.4 Raster Query Service (`raster_service.py`)

```python
import rasterio
from rasterio.transform import rowcol

def extract_value_at_point(
    raster_path: str,
    lat: float,
    lng: float
) -> dict:
    """Extract raster value at geographic coordinates"""
    
    with rasterio.open(raster_path) as src:
        if not (src.bounds.left <= lng <= src.bounds.right and
                src.bounds.bottom <= lat <= src.bounds.top):
            raise ValueError("Point outside raster bounds")
        
        row, col = rowcol(src.transform, lng, lat)
        value = src.read(1)[row, col]
        is_nodata = (value == src.nodata) if src.nodata else False
        
        return {
            "value": None if is_nodata else float(value),
            "is_nodata": is_nodata,
            "pixel_coords": {"row": int(row), "col": int(col)}
        }
```

### 5.3 API Router Pattern

Each router follows this structure:

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.dataset import DatasetResponse, DatasetList
from app.services import dataset_service

router = APIRouter()

@router.get("/", response_model=DatasetList)
async def list_datasets(
    dataset_type: str | None = None,
    year: int | None = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """List all datasets with optional filters"""
    datasets = dataset_service.get_datasets(
        db, dataset_type=dataset_type, year=year, limit=limit, offset=offset
    )
    total = dataset_service.count_datasets(db, dataset_type=dataset_type, year=year)
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "items": datasets
    }
```

### 5.4 Error Handling

```python
from fastapi import HTTPException

class DatasetNotFoundException(HTTPException):
    def __init__(self, dataset_id: int):
        super().__init__(
            status_code=404,
            detail=f"Dataset {dataset_id} not found"
        )

class PointOutOfBoundsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=400,
            detail="Point is outside raster bounds"
        )
```

---

## 6. Frontend Architecture

### 6.1 Directory Structure

```
frontend/
+-- src/
¦   +-- main.tsx                   # App entry point
¦   +-- App.tsx                    # Root component
¦   ¦
¦   +-- pages/                     # Page components
¦   ¦   +-- Dashboard.tsx          # Home/overview
¦   ¦   +-- Maps.tsx               # Interactive map viewer
¦   ¦   +-- Analytics.tsx          # Statistics & comparisons
¦   ¦   +-- TimeSeries.tsx         # Time series charts
¦   ¦   +-- AIForecast.tsx         # AI predictions
¦   ¦   +-- DataManagement.tsx     # Dataset info
¦   ¦
¦   +-- components/                # Reusable components
¦   ¦   +-- layout/
¦   ¦   ¦   +-- Sidebar.tsx
¦   ¦   ¦   +-- Header.tsx
¦   ¦   ¦   +-- Layout.tsx
¦   ¦   ¦
¦   ¦   +-- map/
¦   ¦   ¦   +-- MapViewer.tsx      # Leaflet map wrapper
¦   ¦   ¦   +-- LayerControl.tsx   # Layer switcher
¦   ¦   ¦   +-- Legend.tsx         # NDVI legend
¦   ¦   ¦   +-- PointQuery.tsx     # Click query popup
¦   ¦   ¦
¦   ¦   +-- charts/
¦   ¦   ¦   +-- TimeSeriesChart.tsx
¦   ¦   ¦   +-- ForecastChart.tsx
¦   ¦   ¦   +-- ComparisonChart.tsx
¦   ¦   ¦   +-- StatisticsCard.tsx
¦   ¦   ¦
¦   ¦   +-- common/
¦   ¦       +-- DatasetSelector.tsx
¦   ¦       +-- DateRangePicker.tsx
¦   ¦       +-- LoadingSpinner.tsx
¦   ¦       +-- ErrorBoundary.tsx
¦   ¦
¦   +-- stores/                    # Zustand stores
¦   ¦   +-- datasetStore.ts
¦   ¦   +-- mapStore.ts
¦   ¦   +-- timeseriesStore.ts
¦   ¦   +-- uiStore.ts
¦   ¦
¦   +-- services/                  # API clients
¦   ¦   +-- api.ts
¦   ¦   +-- datasetService.ts
¦   ¦   +-- rasterService.ts
¦   ¦   +-- timeseriesService.ts
¦   ¦   +-- modelService.ts
¦   ¦
¦   +-- types/                     # TypeScript types
¦   ¦   +-- dataset.ts
¦   ¦   +-- timeseries.ts
¦   ¦   +-- model.ts
¦   ¦
¦   +-- utils/
¦   ¦   +-- colormap.ts
¦   ¦   +-- formatters.ts
¦   ¦   +-- constants.ts
¦   ¦
¦   +-- styles/
¦       +-- index.css
¦
+-- package.json
+-- tsconfig.json
+-- vite.config.ts
+-- tailwind.config.js
```

### 6.2 State Management (Zustand)

```typescript
import { create } from 'zustand';
import { Dataset } from '@/types/dataset';

interface DatasetState {
  datasets: Dataset[];
  selectedDatasetId: number | null;
  loading: boolean;
  error: string | null;
  
  setDatasets: (datasets: Dataset[]) => void;
  selectDataset: (id: number) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useDatasetStore = create<DatasetState>((set) => ({
  datasets: [],
  selectedDatasetId: null,
  loading: false,
  error: null,
  
  setDatasets: (datasets) => set({ datasets }),
  selectDataset: (id) => set({ selectedDatasetId: id }),
  setLoading: (loading) => set({ loading }),
  setError: (error) => set({ error }),
}));
```

### 6.3 API Service Layer

```typescript
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// services/datasetService.ts
import { api } from './api';
import { Dataset, DatasetList } from '@/types/dataset';

export const datasetService = {
  async getAll(params?: {
    dataset_type?: string;
    year?: number;
  }): Promise<DatasetList> {
    const { data } = await api.get<DatasetList>('/datasets', { params });
    return data;
  },
  
  async getById(id: number): Promise<Dataset> {
    const { data } = await api.get<Dataset>(`/datasets/${id}`);
    return data;
  },
};
```

### 6.4 Map Component

```typescript
import { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { useDatasetStore } from '@/stores/datasetStore';

export const MapViewer = () => {
  const mapRef = useRef<L.Map | null>(null);
  const { selectedDatasetId } = useDatasetStore();
  
  useEffect(() => {
    if (!mapRef.current) {
      mapRef.current = L.map('map', {
        center: [10.775, 106.69],
        zoom: 11,
      });
      
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(mapRef.current);
    }
  }, []);
  
  useEffect(() => {
    if (!mapRef.current || !selectedDatasetId) return;
    
    const tileUrl = `http://localhost:8000/api/v1/tiles/${selectedDatasetId}/{z}/{x}/{y}.png`;
    const ndviLayer = L.tileLayer(tileUrl, { opacity: 0.7 });
    ndviLayer.addTo(mapRef.current);
    
    return () => {
      if (mapRef.current) {
        ndviLayer.remove();
      }
    };
  }, [selectedDatasetId]);
  
  return <div id="map" className="h-full w-full" />;
};
```

### 6.5 Chart Component

```typescript
import { useEffect, useRef } from 'react';
import * as echarts from 'echarts';

export const TimeSeriesChart = ({ data, forecastData }) => {
  const chartRef = useRef<HTMLDivElement>(null);
  
  useEffect(() => {
    if (!chartRef.current) return;
    
    const chart = echarts.init(chartRef.current);
    
    const option = {
      title: { text: 'NDVI Time Series & Forecast' },
      tooltip: { trigger: 'axis' },
      xAxis: { type: 'time' },
      yAxis: { type: 'value', name: 'NDVI', min: -0.2, max: 1.0 },
      series: [
        {
          name: 'Observed',
          type: 'line',
          data: data.map(d => [d.date, d.ndvi_mean]),
          lineStyle: { color: '#10b981' },
        },
        {
          name: 'Forecast',
          type: 'line',
          data: forecastData?.map(d => [d.date, d.predicted_ndvi]),
          lineStyle: { color: '#3b82f6', type: 'dashed' },
        },
      ],
    };
    
    chart.setOption(option);
    
    return () => chart.dispose();
  }, [data, forecastData]);
  
  return <div ref={chartRef} className="w-full h-96" />;
};
```

---

## 7. Data Processing Pipeline

### 7.1 Ingestion Workflow

```
Raw GeoTIFF Files (D:\NDVI\data\raw)
    ?
STEP 1: Validate & Standardize
    - Check CRS (reproject to EPSG:4326)
    - Validate extent (HCMC bounds)
    - Check nodata values
    ?
STEP 2: Convert to COG
    - Use GDAL: gdal_translate
    - Add overviews (2, 4, 8, 16)
    - Internal tiling (256x256)
    - Output: D:\NDVI\data\cog\*.tif
    ?
STEP 3: Compute Statistics
    - Calculate: min, max, mean, median, std_dev
    - Count pixels by NDVI class
    - Store in raster_statistics table
    ?
STEP 4: Register in Database
    - Insert into raster_datasets
    - Link statistics
```


### 7.2 Ingestion Script Design

**Key Script: `scripts/ingest_raster.py`**

```python
import rasterio
from subprocess import run
import numpy as np
from pathlib import Path

def ingest_raster(input_path: str, name: str, dataset_type: str, observation_date: str, db):
    """Idempotent raster ingestion pipeline"""
    
    # Check if already exists
    existing = db.query(RasterDataset).filter_by(name=name).first()
    if existing:
        print(f"Dataset {name} already exists. Skipping.")
        return existing.id
    
    # STEP 1: Validate and reproject if needed
    with rasterio.open(input_path) as src:
        if src.crs != 'EPSG:4326':
            print(f"Reprojecting from {src.crs} to EPSG:4326...")
            # Reproject logic here
    
    # STEP 2: Convert to COG
    cog_path = Path("D:/NDVI/data/cog") / f"{name}_cog.tif"
    run([
        "gdal_translate",
        "-of", "COG",
        "-co", "COMPRESS=LZW",
        "-co", "BLOCKSIZE=256",
        "-co", "OVERVIEWS=AUTO",
        input_path,
        str(cog_path)
    ])
    
    # STEP 3: Compute statistics
    with rasterio.open(cog_path) as src:
        data = src.read(1)
        mask = (data != src.nodata) if src.nodata else np.ones_like(data, dtype=bool)
        valid_data = data[mask]
        
        stats = {
            'min_value': float(valid_data.min()),
            'max_value': float(valid_data.max()),
            'mean_value': float(valid_data.mean()),
            'median_value': float(np.median(valid_data)),
            'std_dev': float(valid_data.std()),
            'valid_pixel_count': int(mask.sum()),
        }
    
    # STEP 4: Register in database
    dataset = RasterDataset(name=name, dataset_type=dataset_type, 
                           observation_date=observation_date, cog_path=str(cog_path), ...)
    db.add(dataset)
    db.flush()
    
    statistics = RasterStatistics(dataset_id=dataset.id, **stats)
    db.add(statistics)
    db.commit()
    
    return dataset.id
```

### 7.3 Master Ingestion Script

**`scripts/ingest_all.py`**

```python
def main():
    db = SessionLocal()
    
    try:
        # 1. Ingest raster datasets
        datasets = [
            ("D:/NDVI/data/raw/ndvi_2015.tif", "ndvi_2015_hcmc", "ndvi_2015", "2015-12-31"),
            ("D:/NDVI/data/raw/ndvi_2025.tif", "ndvi_2025_hcmc", "ndvi_2025", "2025-12-31"),
            ("D:/NDVI/data/raw/ndvi_change.tif", "ndvi_change_2015_2025", "ndvi_change", "2025-12-31"),
            ("D:/NDVI/data/raw/ndvi_forecast_2026.tif", "ndvi_forecast_2026", "ndvi_forecast_2026", "2026-12-31"),
        ]
        
        for path, name, dtype, date in datasets:
            print(f"Ingesting {name}...")
            ingest_raster(path, name, dtype, date, db)
        
        # 2. Import time series from CSV
        print("Importing time series...")
        import_timeseries_csv("D:/NDVI/data/timeseries.csv", db)
        
        # 3. Register AI model
        print("Registering AI model...")
        model_id = register_model(
            run_name="lstm_best",
            model_type="lstm",
            model_name="LSTM with 128-64 units",
            training_start_date="2015-01-01",
            training_end_date="2024-12-31",
            mae=0.0234,
            rmse=0.0312,
            r2_score=0.9245,
            parameters={"layers": [128, 64], "dropout": 0.2},
            db=db
        )
        
        # 4. Import forecast results
        print("Importing forecast data...")
        import_forecast_csv("D:/NDVI/data/forecast_2026.csv", model_id, db)
        
        print("\n? All data ingested successfully!")
    
    finally:
        db.close()
```

---

## 8. Project Structure

### 8.1 Complete Directory Layout

```
D:\NDVI\ndvi-ai-web\
+-- frontend/                      # React application
¦   +-- src/
¦   ¦   +-- pages/
¦   ¦   +-- components/
¦   ¦   +-- stores/
¦   ¦   +-- services/
¦   ¦   +-- types/
¦   ¦   +-- utils/
¦   +-- public/
¦   +-- package.json
¦   +-- vite.config.ts
¦   +-- tsconfig.json
¦   +-- tailwind.config.js
¦
+-- backend/                       # FastAPI application
¦   +-- app/
¦   ¦   +-- routers/
¦   ¦   +-- services/
¦   ¦   +-- models/
¦   ¦   +-- schemas/
¦   ¦   +-- utils/
¦   +-- tests/
¦   +-- requirements.txt
¦   +-- .env
¦
+-- scripts/                       # Data processing scripts
¦   +-- ingest_all.py
¦   +-- ingest_raster.py
¦   +-- import_timeseries.py
¦   +-- import_forecast.py
¦   +-- utils.py
¦
+-- database/                      # Database setup
¦   +-- schema.sql
¦   +-- init_db.py
¦
+-- data/                          # Data files
¦   +-- raw/                       # Original GeoTIFFs
¦   +-- processed/                 # Cleaned data
¦   +-- cog/                       # Cloud-Optimized GeoTIFFs
¦   +-- timeseries.csv
¦   +-- forecast_2026.csv
¦
+-- docs/                          # Documentation
¦   +-- architecture.md            # This file
¦   +-- database-schema.sql
¦   +-- api-spec.md
¦   +-- README.md
¦
+-- .gitignore
+-- README.md
+-- setup.ps1                      # Setup script
+-- start.ps1                      # Start services
+-- stop.ps1                       # Stop services
```

---

## 9. Configuration Management

### 9.1 Backend Environment Variables (`.env`)

```env
# Database
DATABASE_URL=postgresql://ndvi_user:secure_password@localhost:5432/ndvi_db

# Data Directories (Windows paths)
DATA_DIR=D:\NDVI\data
RAW_DIR=D:\NDVI\data\raw
PROCESSED_DIR=D:\NDVI\data\processed
COG_DIR=D:\NDVI\data\cog

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=True

# Tile Server
TILE_SIZE=256
MAX_ZOOM=18
MIN_ZOOM=8
DEFAULT_COLORMAP=greens

# CORS
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

### 9.2 Frontend Environment Variables (`.env`)

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_MAP_CENTER_LAT=10.775
VITE_MAP_CENTER_LNG=106.69
VITE_MAP_DEFAULT_ZOOM=11
```

---

## 10. Deployment Strategy

### 10.1 Setup Script (`setup.ps1`)

```powershell
# Windows PowerShell setup script
Write-Host "=== NDVI AI WebGIS Setup ===" -ForegroundColor Green

# Check prerequisites
Write-Host "`nChecking prerequisites..."
$required = @("python", "node", "psql", "gdal_translate")
foreach ($cmd in $required) {
    if (!(Get-Command $cmd -ErrorAction SilentlyContinue)) {
        Write-Host "ERROR: $cmd not found" -ForegroundColor Red
        exit 1
    }
}

# Setup Python virtual environment
Write-Host "`nSetting up Python environment..."
Set-Location backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

# Setup database
Write-Host "`nSetting up database..."
$env:PGPASSWORD = "secure_password"
psql -U postgres -c "CREATE DATABASE ndvi_db;"
psql -U postgres -d ndvi_db -c "CREATE EXTENSION postgis;"
psql -U postgres -d ndvi_db -f ..\database\schema.sql

# Initialize database with data
Write-Host "`nIngesting data..."
python ..\scripts\ingest_all.py

# Setup frontend
Write-Host "`nSetting up frontend..."
Set-Location ..\frontend
npm install

Write-Host "`n? Setup complete!" -ForegroundColor Green
Write-Host "Run './start.ps1' to start the application"
```

### 10.2 Start Script (`start.ps1`)

```powershell
Write-Host "=== Starting NDVI AI WebGIS ===" -ForegroundColor Green

# Start backend
Write-Host "`nStarting backend..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", `
    "cd backend; .\venv\Scripts\Activate.ps1; uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

Start-Sleep -Seconds 3

# Start frontend
Write-Host "Starting frontend..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", `
    "cd frontend; npm run dev"

Write-Host "`n? Services started!" -ForegroundColor Green
Write-Host "Backend:  http://localhost:8000" -ForegroundColor Cyan
Write-Host "Frontend: http://localhost:5173" -ForegroundColor Cyan
Write-Host "API Docs: http://localhost:8000/api/docs" -ForegroundColor Cyan
```

### 10.3 Stop Script (`stop.ps1`)

```powershell
Write-Host "=== Stopping NDVI AI WebGIS ===" -ForegroundColor Yellow

Get-Process | Where-Object {$_.ProcessName -like "*node*"} | Stop-Process -Force
Get-Process | Where-Object {$_.ProcessName -like "*python*"} | Stop-Process -Force

Write-Host "? Services stopped" -ForegroundColor Green
```

---

## 11. Performance Optimization

### 11.1 Backend Optimizations

**Database Connection Pooling**
```python
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True
)
```

**Tile Caching**
```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_tile_cached(dataset_id: int, z: int, x: int, y: int) -> bytes:
    return generate_tile(dataset_id, z, x, y)
```

**Async Endpoints**
```python
@router.get("/datasets")
async def list_datasets(db: AsyncSession = Depends(get_async_db)):
    result = await db.execute(select(RasterDataset))
    return result.scalars().all()
```

### 11.2 Frontend Optimizations

- **Code Splitting**: Lazy load pages with `React.lazy()`
- **Memoization**: Use `useMemo` and `React.memo` for expensive renders
- **Debounced Queries**: Debounce map click queries (300ms)
- **Virtual Scrolling**: For large dataset lists

### 11.3 COG Optimization

```bash
gdal_translate \
  -of COG \
  -co COMPRESS=LZW \
  -co BLOCKSIZE=256 \
  -co OVERVIEW_RESAMPLING=AVERAGE \
  -co OVERVIEWS=AUTO \
  input.tif output_cog.tif
```

---

## 12. Security Considerations

### 12.1 Localhost Demo Security

Since this is a **localhost demo**, minimal security:

1. **SQL Injection Protection**: SQLAlchemy ORM
2. **Input Validation**: Pydantic schemas
3. **Path Traversal**: Restrict file access to DATA_DIR
4. **CORS**: Limited to `localhost:5173`
5. **No Authentication**: Not required for demo

### 12.2 Production Recommendations

For public deployment:

- JWT authentication
- HTTPS/TLS certificates
- Rate limiting (slowapi)
- Input sanitization
- Secrets management
- Database user with restricted permissions
- WAF (Web Application Firewall)

---

## 13. Testing Strategy

### 13.1 Backend Tests

```python
import pytest
from fastapi.testclient import TestClient

def test_list_datasets(client: TestClient):
    response = client.get("/api/v1/datasets")
    assert response.status_code == 200
    assert "items" in response.json()

def test_query_point(client: TestClient):
    response = client.get("/api/v1/raster/point?dataset_id=1&lat=10.7756&lng=106.7019")
    assert response.status_code == 200
    assert "value" in response.json()
```

### 13.2 Frontend Tests

```typescript
import { render, screen } from '@testing-library/react';
import { DatasetSelector } from '@/components/common/DatasetSelector';

test('renders dataset selector', () => {
  render(<DatasetSelector />);
  expect(screen.getByText(/select dataset/i)).toBeInTheDocument();
});
```

---

## 14. Monitoring & Logging

### 14.1 Backend Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

### 14.2 Error Tracking

- Console logging for development
- Structured logging for production
- Error boundaries in React

---

## 15. Key Design Decisions Summary

| Decision | Rationale |
|----------|-----------|
| **COG for rasters** | Fast tile serving without loading full raster |
| **PostgreSQL + PostGIS** | Mature, reliable, excellent spatial support |
| **FastAPI** | Modern, async, automatic API docs |
| **React + TypeScript** | Type safety, component reusability |
| **Zustand** | Lightweight, simpler than Redux |
| **Leaflet** | Mature, extensive plugin ecosystem |
| **ECharts** | Rich features, good performance |
| **Separate metadata/files** | Database for queries, filesystem for rasters |
| **Pre-computed stats** | Trade storage for query speed |
| **JSONB for parameters** | Flexibility for different model types |

---

## 16. Dependencies

### 16.1 Backend (`requirements.txt`)

```txt
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
pydantic==2.5.0
pydantic-settings==2.1.0
rasterio==1.3.9
rio-tiler==6.0.0
numpy==1.26.2
pandas==2.1.4
python-multipart==0.0.6
```

### 16.2 Frontend (`package.json` dependencies)

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0",
    "leaflet": "^1.9.4",
    "echarts": "^5.4.3",
    "axios": "^1.6.2",
    "zustand": "^4.4.7",
    "date-fns": "^2.30.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.43",
    "@types/leaflet": "^1.9.8",
    "@vitejs/plugin-react": "^4.2.1",
    "typescript": "^5.3.3",
    "vite": "^5.0.7",
    "tailwindcss": "^3.3.6"
  }
}
```

---

## 17. Future Enhancements

### 17.1 Short-term
- Redis caching for tiles
- User preferences (colormap, opacity)
- Export functionality (PNG, GeoTIFF, CSV)
- Mobile-responsive design

### 17.2 Long-term
- Real-time NDVI updates from satellite APIs
- Multi-region support (beyond HCMC)
- 3D visualization (Cesium.js)
- Advanced analytics (anomaly detection)
- Collaborative annotations

---

## 18. References

- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **PostgreSQL/PostGIS**: https://postgis.net/
- **Leaflet**: https://leafletjs.com/
- **ECharts**: https://echarts.apache.org/
- **Rasterio**: https://rasterio.readthedocs.io/
- **rio-tiler**: https://cogeotiff.github.io/rio-tiler/
- **Cloud-Optimized GeoTIFF**: https://www.cogeo.org/

---

**End of Architecture Document**

**Next Steps:**
1. Review this architecture document
2. Set up development environment (Python, Node.js, PostgreSQL, GDAL)
3. Create project directory structure
4. Initialize databases with `database-schema.sql`
5. Begin backend implementation (FastAPI)
6. Begin frontend implementation (React)
7. Implement data ingestion pipeline
8. Test and iterate

For detailed API specifications, see `api-spec.md`.
For database schema details, see `database-schema.sql`.
