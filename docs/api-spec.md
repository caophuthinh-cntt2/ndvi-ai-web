# API Specification

## Base URL
http://localhost:8000

## Endpoints

### Health Check
- GET /health - Check API health status

### Datasets
- GET /api/datasets - List all datasets
- GET /api/datasets/{id} - Get dataset details
- POST /api/datasets - Upload new dataset

### Tiles
- GET /api/tiles/{dataset_id}/{z}/{x}/{y}.png - Get map tile

### Statistics
- GET /api/statistics/{dataset_id} - Get dataset statistics
- GET /api/statistics/compare - Compare multiple datasets

### Time Series
- GET /api/timeseries - Get NDVI time series data
- GET /api/timeseries/range - Get time series for date range

### Forecast
- POST /api/forecast/train - Train forecasting model
- GET /api/forecast/predict - Get NDVI predictions
- GET /api/forecast/metrics - Get model performance metrics
