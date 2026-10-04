# Data Dictionary

Mô tả chi tiết cấu trúc database cho hệ thống NDVI AI.

## Overview

Database: **PostgreSQL 15** với extension **PostGIS 3.3**

Schema: **public**

Total tables: 8

## Tables

### 1. `datasets`

Lưu thông tin metadata của các bộ dữ liệu NDVI.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | SERIAL | NO | AUTO | Primary key |
| `year` | INTEGER | NO | - | Năm dữ liệu (2015-2026) |
| `acquisition_date` | DATE | NO | - | Ngày chụp ảnh Landsat |
| `source` | VARCHAR(50) | NO | - | Nguồn (Landsat-8, Landsat-9) |
| `scene_id` | VARCHAR(100) | YES | NULL | Landsat scene identifier |
| `path` | INTEGER | YES | NULL | Landsat path (125) |
| `row` | INTEGER | YES | NULL | Landsat row (53) |
| `cloud_cover` | FLOAT | YES | NULL | % mây (0-100) |
| `processing_level` | VARCHAR(20) | YES | 'L2' | Processing level (L1, L2) |
| `file_path` | TEXT | NO | - | Đường dẫn file GeoTIFF |
| `file_size_mb` | FLOAT | YES | NULL | Kích thước file (MB) |
| `resolution` | FLOAT | YES | 30.0 | Spatial resolution (m) |
| `crs` | VARCHAR(20) | YES | 'EPSG:4326' | Coordinate reference system |
| `bounds` | GEOMETRY(POLYGON) | YES | NULL | Bounding box (WGS84) |
| `status` | VARCHAR(20) | YES | 'processed' | Status (raw, processing, processed, error) |
| `created_at` | TIMESTAMP | NO | NOW() | Timestamp tạo record |
| `updated_at` | TIMESTAMP | NO | NOW() | Timestamp cập nhật |

**Indexes:**
- PRIMARY KEY: `id`
- UNIQUE: `year`
- INDEX: `acquisition_date`
- SPATIAL INDEX: `bounds` (GIST)

**Example:**
```sql
INSERT INTO datasets (year, acquisition_date, source, scene_id, cloud_cover, file_path)
VALUES (2025, '2025-03-15', 'Landsat-9', 'LC09_L2SP_125053_20250315_20250317_02_T1', 8.5, 'D:/NDVI/data/ndvi_2025.tif');
```

---

### 2. `ndvi_statistics`

Lưu thống kê NDVI tổng thể cho mỗi năm.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | SERIAL | NO | AUTO | Primary key |
| `dataset_id` | INTEGER | NO | - | Foreign key → datasets.id |
| `year` | INTEGER | NO | - | Năm |
| `mean` | FLOAT | NO | - | NDVI trung bình |
| `median` | FLOAT | YES | NULL | NDVI trung vị |
| `std_dev` | FLOAT | YES | NULL | Độ lệch chuẩn |
| `min` | FLOAT | YES | NULL | Giá trị nhỏ nhất |
| `max` | FLOAT | YES | NULL | Giá trị lớn nhất |
| `percentile_25` | FLOAT | YES | NULL | Phân vị 25% |
| `percentile_75` | FLOAT | YES | NULL | Phân vị 75% |
| `total_pixels` | BIGINT | YES | NULL | Tổng số pixels |
| `valid_pixels` | BIGINT | YES | NULL | Số pixels hợp lệ (không phải NoData) |
| `nodata_pixels` | BIGINT | YES | NULL | Số pixels NoData |
| `area_km2` | FLOAT | YES | NULL | Diện tích phủ (km²) |
| `computed_at` | TIMESTAMP | NO | NOW() | Timestamp tính toán |

**Indexes:**
- PRIMARY KEY: `id`
- FOREIGN KEY: `dataset_id` → datasets(id) ON DELETE CASCADE
- UNIQUE: `(dataset_id, year)`
- INDEX: `year`

**Example:**
```sql
INSERT INTO ndvi_statistics (dataset_id, year, mean, median, std_dev, min, max)
VALUES (11, 2025, 0.4321, 0.4456, 0.1823, 0.0234, 0.8912);
```

---

### 3. `ndvi_timeseries`

Lưu time series NDVI mean theo năm (cho AI forecasting).

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | SERIAL | NO | AUTO | Primary key |
| `year` | INTEGER | NO | - | Năm |
| `ndvi_mean` | FLOAT | NO | - | NDVI trung bình |
| `district_id` | INTEGER | YES | NULL | ID quận/huyện (NULL = toàn TP) |
| `district_name` | VARCHAR(100) | YES | NULL | Tên quận/huyện |
| `is_forecast` | BOOLEAN | NO | FALSE | TRUE nếu là dự báo |
| `created_at` | TIMESTAMP | NO | NOW() | Timestamp |

**Indexes:**
- PRIMARY KEY: `id`
- UNIQUE: `(year, district_id)`
- INDEX: `year`
- INDEX: `district_id`

**Example:**
```sql
-- Actual data
INSERT INTO ndvi_timeseries (year, ndvi_mean, district_id, district_name, is_forecast)
VALUES (2025, 0.4321, NULL, NULL, FALSE);

-- Forecast
INSERT INTO ndvi_timeseries (year, ndvi_mean, district_id, district_name, is_forecast)
VALUES (2026, 0.4283, NULL, NULL, TRUE);
```

---

### 4. `ml_models`

Lưu metadata các mô hình Machine Learning.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | SERIAL | NO | AUTO | Primary key |
| `name` | VARCHAR(100) | NO | - | Tên model (Linear Regression, Random Forest, ...) |
| `model_type` | VARCHAR(50) | NO | - | Loại (regression, classification) |
| `version` | VARCHAR(20) | YES | '1.0' | Version |
| `file_path` | TEXT | NO | - | Đường dẫn file model (.pkl) |
| `hyperparameters` | JSONB | YES | NULL | Hyperparameters (JSON) |
| `training_date` | TIMESTAMP | NO | NOW() | Ngày train |
| `training_samples` | INTEGER | YES | NULL | Số samples training |
| `features` | TEXT[] | YES | NULL | Danh sách features (array) |
| `target_variable` | VARCHAR(50) | YES | 'ndvi_mean' | Target variable |
| `is_active` | BOOLEAN | NO | TRUE | Model có đang sử dụng không |
| `created_at` | TIMESTAMP | NO | NOW() | Timestamp |

**Indexes:**
- PRIMARY KEY: `id`
- UNIQUE: `(name, version)`
- INDEX: `is_active`

**Example:**
```sql
INSERT INTO ml_models (name, model_type, file_path, hyperparameters, features)
VALUES (
  'Random Forest',
  'regression',
  'D:/NDVI/models/random_forest_v1.pkl',
  '{"n_estimators": 100, "max_depth": 10, "random_state": 42}',
  ARRAY['ndvi_lag_1', 'ndvi_lag_2', 'ndvi_lag_3', 'rolling_mean_3', 'rolling_std_3', 'year']
);
```

---

### 5. `ml_metrics`

Lưu metrics đánh giá models.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | SERIAL | NO | AUTO | Primary key |
| `model_id` | INTEGER | NO | - | Foreign key → ml_models.id |
| `metric_name` | VARCHAR(50) | NO | - | Tên metric (MAE, RMSE, R2) |
| `metric_value` | FLOAT | NO | - | Giá trị metric |
| `dataset_type` | VARCHAR(20) | YES | 'test' | Loại dataset (train, validation, test) |
| `evaluation_date` | TIMESTAMP | NO | NOW() | Ngày đánh giá |

**Indexes:**
- PRIMARY KEY: `id`
- FOREIGN KEY: `model_id` → ml_models(id) ON DELETE CASCADE
- INDEX: `(model_id, metric_name)`

**Example:**
```sql
INSERT INTO ml_metrics (model_id, metric_name, metric_value, dataset_type)
VALUES 
  (1, 'MAE', 0.0156, 'test'),
  (1, 'RMSE', 0.0201, 'test'),
  (1, 'R2', 0.2234, 'test');
```

---

### 6. `predictions`

Lưu kết quả dự báo.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | SERIAL | NO | AUTO | Primary key |
| `model_id` | INTEGER | NO | - | Foreign key → ml_models.id |
| `year` | INTEGER | NO | - | Năm dự báo |
| `predicted_value` | FLOAT | NO | - | Giá trị dự báo |
| `confidence_lower` | FLOAT | YES | NULL | Confidence interval lower bound |
| `confidence_upper` | FLOAT | YES | NULL | Confidence interval upper bound |
| `actual_value` | FLOAT | YES | NULL | Giá trị thực tế (nếu có) |
| `prediction_error` | FLOAT | YES | NULL | Sai số (actual - predicted) |
| `district_id` | INTEGER | YES | NULL | ID quận/huyện (NULL = toàn TP) |
| `created_at` | TIMESTAMP | NO | NOW() | Timestamp |

**Indexes:**
- PRIMARY KEY: `id`
- FOREIGN KEY: `model_id` → ml_models(id) ON DELETE CASCADE
- INDEX: `(model_id, year)`
- INDEX: `year`

**Example:**
```sql
INSERT INTO predictions (model_id, year, predicted_value, confidence_lower, confidence_upper)
VALUES (1, 2026, 0.4283, 0.4083, 0.4483);
```

---

### 7. `districts`

Lưu thông tin các quận/huyện TP.HCM.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | SERIAL | NO | AUTO | Primary key |
| `name` | VARCHAR(100) | NO | - | Tên quận/huyện |
| `name_en` | VARCHAR(100) | YES | NULL | Tên tiếng Anh |
| `type` | VARCHAR(20) | YES | 'district' | Loại (district, rural_district) |
| `area_km2` | FLOAT | YES | NULL | Diện tích (km²) |
| `population` | INTEGER | YES | NULL | Dân số |
| `geometry` | GEOMETRY(MULTIPOLYGON) | YES | NULL | Ranh giới hành chính |
| `centroid` | GEOMETRY(POINT) | YES | NULL | Tâm quận |
| `created_at` | TIMESTAMP | NO | NOW() | Timestamp |

**Indexes:**
- PRIMARY KEY: `id`
- UNIQUE: `name`
- SPATIAL INDEX: `geometry` (GIST)
- SPATIAL INDEX: `centroid` (GIST)

**Example:**
```sql
INSERT INTO districts (name, name_en, type, area_km2, population)
VALUES ('Quận 1', 'District 1', 'district', 7.73, 204899);
```

**List of Districts:**
1. Quận 1 - 12
2. Gò Vấp
3. Bình Thạnh
4. Tân Bình
5. Tân Phú
6. Phú Nhuận
7. Bình Tân
8. Thủ Đức
9. Hóc Môn
10. Củ Chi
11. Bình Chánh
12. Nhà Bè
13. Cần Giờ

---

### 8. `change_analysis`

Lưu kết quả phân tích thay đổi giữa các năm.

| Column | Type | Nullable | Default | Description |
|--------|------|----------|---------|-------------|
| `id` | SERIAL | NO | AUTO | Primary key |
| `base_year` | INTEGER | NO | - | Năm gốc |
| `compare_year` | INTEGER | NO | - | Năm so sánh |
| `mean_change` | FLOAT | NO | - | Thay đổi trung bình |
| `percent_change` | FLOAT | NO | - | % thay đổi |
| `pixels_increased` | BIGINT | YES | NULL | Số pixels tăng NDVI |
| `pixels_decreased` | BIGINT | YES | NULL | Số pixels giảm NDVI |
| `pixels_no_change` | BIGINT | YES | NULL | Số pixels không đổi |
| `max_increase` | FLOAT | YES | NULL | Tăng tối đa |
| `max_decrease` | FLOAT | YES | NULL | Giảm tối đa |
| `area_increased_km2` | FLOAT | YES | NULL | Diện tích tăng (km²) |
| `area_decreased_km2` | FLOAT | YES | NULL | Diện tích giảm (km²) |
| `district_id` | INTEGER | YES | NULL | ID quận (NULL = toàn TP) |
| `created_at` | TIMESTAMP | NO | NOW() | Timestamp |

**Indexes:**
- PRIMARY KEY: `id`
- UNIQUE: `(base_year, compare_year, district_id)`
- INDEX: `base_year`
- INDEX: `compare_year`

**Example:**
```sql
INSERT INTO change_analysis (base_year, compare_year, mean_change, percent_change, pixels_decreased)
VALUES (2015, 2025, -0.018, -4.3, 1456789);
```

---

## Enums & Constants

### Dataset Status
```sql
CREATE TYPE dataset_status AS ENUM ('raw', 'processing', 'processed', 'error');
```

### Model Types
```sql
CREATE TYPE model_type AS ENUM ('regression', 'classification', 'clustering');
```

### Dataset Types (for metrics)
```sql
CREATE TYPE dataset_type AS ENUM ('train', 'validation', 'test', 'cross_validation');
```

### District Types
```sql
CREATE TYPE district_type AS ENUM ('district', 'rural_district');
```

---

## Relationships

```
datasets (1) ──────── (1) ndvi_statistics
    │
    └──────── (M) change_analysis

ml_models (1) ──────── (M) ml_metrics
    │
    └──────── (M) predictions

districts (1) ──────── (M) ndvi_timeseries
    │
    └──────── (M) change_analysis
    │
    └──────── (M) predictions
```

---

## Views

### `v_latest_ndvi`
View hiển thị NDVI mới nhất.

```sql
CREATE VIEW v_latest_ndvi AS
SELECT 
    d.year,
    d.acquisition_date,
    d.source,
    s.mean,
    s.median,
    s.std_dev,
    s.min,
    s.max
FROM datasets d
JOIN ndvi_statistics s ON d.id = s.dataset_id
ORDER BY d.year DESC
LIMIT 1;
```

### `v_timeseries_full`
View kết hợp actual + forecast.

```sql
CREATE VIEW v_timeseries_full AS
SELECT 
    year,
    ndvi_mean,
    is_forecast,
    CASE WHEN is_forecast THEN 'Forecast' ELSE 'Actual' END as data_type
FROM ndvi_timeseries
ORDER BY year;
```

### `v_model_performance`
View tổng hợp performance các models.

```sql
CREATE VIEW v_model_performance AS
SELECT 
    m.name,
    m.version,
    MAX(CASE WHEN me.metric_name = 'MAE' THEN me.metric_value END) as mae,
    MAX(CASE WHEN me.metric_name = 'RMSE' THEN me.metric_value END) as rmse,
    MAX(CASE WHEN me.metric_name = 'R2' THEN me.metric_value END) as r2
FROM ml_models m
JOIN ml_metrics me ON m.id = me.model_id
WHERE me.dataset_type = 'test'
GROUP BY m.id, m.name, m.version
ORDER BY mae ASC;
```

---

## Stored Procedures

### `calculate_change(base_year INT, compare_year INT)`
Tính toán change analysis giữa 2 năm.

```sql
CREATE OR REPLACE FUNCTION calculate_change(base_year INT, compare_year INT)
RETURNS TABLE (
    mean_change FLOAT,
    percent_change FLOAT,
    pixels_increased BIGINT,
    pixels_decreased BIGINT
) AS $$
BEGIN
    -- Logic to calculate change from raster files
    -- Return aggregated statistics
END;
$$ LANGUAGE plpgsql;
```

### `forecast_next_year(model_name VARCHAR)`
Dự báo năm tiếp theo bằng model đã train.

```sql
CREATE OR REPLACE FUNCTION forecast_next_year(model_name VARCHAR)
RETURNS FLOAT AS $$
DECLARE
    predicted FLOAT;
BEGIN
    -- Load model and make prediction
    -- Return predicted value
    RETURN predicted;
END;
$$ LANGUAGE plpgsql;
```

---

## Sample Queries

### Get NDVI statistics for all years
```sql
SELECT 
    d.year,
    s.mean,
    s.std_dev,
    s.min,
    s.max
FROM datasets d
JOIN ndvi_statistics s ON d.id = s.dataset_id
ORDER BY d.year;
```

### Get time series with forecast
```sql
SELECT 
    year,
    ndvi_mean,
    is_forecast
FROM ndvi_timeseries
WHERE district_id IS NULL
ORDER BY year;
```

### Get best performing model
```sql
SELECT 
    m.name,
    m.version,
    me.metric_value as mae
FROM ml_models m
JOIN ml_metrics me ON m.id = me.model_id
WHERE me.metric_name = 'MAE' AND me.dataset_type = 'test'
ORDER BY me.metric_value ASC
LIMIT 1;
```

### Get change analysis 2015 vs 2025
```sql
SELECT 
    mean_change,
    percent_change,
    pixels_increased,
    pixels_decreased,
    (pixels_increased::FLOAT / (pixels_increased + pixels_decreased)) * 100 as pct_increased
FROM change_analysis
WHERE base_year = 2015 AND compare_year = 2025 AND district_id IS NULL;
```

### Get NDVI by district for a year
```sql
SELECT 
    d.name,
    ts.ndvi_mean
FROM districts d
JOIN ndvi_timeseries ts ON d.id = ts.district_id
WHERE ts.year = 2025
ORDER BY ts.ndvi_mean DESC;
```

---

## Database Maintenance

### Backup
```bash
pg_dump -U ndvi_user -d ndvi_db -F c -f backup_$(date +%Y%m%d).dump
```

### Restore
```bash
pg_restore -U ndvi_user -d ndvi_db backup_20261003.dump
```

### Vacuum
```sql
VACUUM ANALYZE;
```

### Reindex
```sql
REINDEX DATABASE ndvi_db;
```

---

## Performance Optimization

### Key Indexes
- All foreign keys have indexes
- Spatial columns use GIST indexes
- Query columns (year, date) have B-tree indexes

### Partitioning (Future)
Có thể partition `ndvi_timeseries` by year:
```sql
CREATE TABLE ndvi_timeseries_2025 PARTITION OF ndvi_timeseries
FOR VALUES FROM (2025) TO (2026);
```

### Materialized Views (Future)
Có thể cache expensive queries:
```sql
CREATE MATERIALIZED VIEW mv_annual_stats AS
SELECT year, mean, std_dev FROM ndvi_statistics;
```

---

For schema initialization, see `database/init.sql`.
For data seeding, see `database/seed_data.py`.
