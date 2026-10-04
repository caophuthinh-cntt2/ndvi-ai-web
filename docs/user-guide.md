# User Guide

Hướng dẫn sử dụng hệ thống NDVI AI WebGIS.

## Tổng quan

Hệ thống bao gồm 6 modules chính:
1. **Dashboard** - Tổng quan hệ thống
2. **Maps** - Xem và phân tích bản đồ NDVI
3. **Analytics** - Thống kê và biểu đồ
4. **Time Series** - Phân tích chuỗi thời gian
5. **AI Forecast** - Dự báo bằng Machine Learning
6. **Data Catalog** - Quản lý datasets

## 1. Dashboard

### Mục đích
Cung cấp cái nhìn tổng quan nhanh về hệ thống và dữ liệu.

### Các thành phần

#### Summary Cards
- **Total Years**: Số năm dữ liệu có sẵn (11 năm: 2015-2025)
- **Datasets**: Tổng số bộ dữ liệu
- **Area Coverage**: Diện tích khu vực nghiên cứu (km²)
- **Latest Update**: Ngày cập nhật gần nhất

#### Latest NDVI Map
- Hiển thị bản đồ NDVI năm mới nhất (2025)
- Color scheme: Đỏ (thấp) → Vàng → Xanh (cao)
- Interactive: Click vào pixel để xem giá trị

#### Quick Statistics
- NDVI Mean: Giá trị trung bình toàn khu vực
- NDVI Min/Max: Giá trị nhỏ nhất/lớn nhất
- Standard Deviation: Độ phân tán

#### Recent Changes
- Thay đổi NDVI so với năm trước
- % tăng/giảm
- Trend indicator

### Cách sử dụng

1. **Xem tổng quan**: Các cards ở đầu trang cho thông tin nhanh
2. **Xem bản đồ**: Bản đồ chính hiển thị NDVI mới nhất
3. **Quick insights**: Các số liệu thống kê ngắn gọn
4. **Navigate**: Click vào các cards để đi đến modules chi tiết

[TODO: Add screenshot - dashboard-overview.png]

## 2. Maps

### Mục đích
Xem, phân tích và so sánh bản đồ NDVI các năm khác nhau.

### 2.1. Single Map View

#### Chọn năm
1. Dùng dropdown "Select Year" ở góc trên phải
2. Chọn năm từ 2015-2026 (2026 là dự báo)
3. Bản đồ sẽ tự động cập nhật

#### Tương tác với bản đồ
- **Zoom**: Scroll chuột hoặc nút +/- trên bản đồ
- **Pan**: Click và kéo để di chuyển
- **Reset view**: Nút "Reset View" để về vị trí ban đầu

#### Click để xem giá trị pixel
1. Click vào bất kỳ pixel nào trên bản đồ
2. Popup hiển thị:
   - Tọa độ (lat, lon)
   - Giá trị NDVI chính xác
   - Phân loại (Very Low/Low/Moderate/High/Very High)
   - Màu indicator

**NDVI Classification:**
- **< 0.2**: Very Low (Red) - Đất trống, bê tông, nước
- **0.2 - 0.3**: Low (Orange) - Thực vật thưa thớt
- **0.3 - 0.4**: Moderate (Yellow) - Thực vật trung bình
- **0.4 - 0.6**: High (Light Green) - Thực vật tốt
- **> 0.6**: Very High (Dark Green) - Thực vật rất dày đặc

[TODO: Add screenshot - map-single-view.png]

### 2.2. Split Map View (Compare)

#### Mục đích
So sánh trực quan 2 năm bất kỳ cạnh nhau.

#### Cách sử dụng
1. Click nút "Compare" trên thanh toolbar
2. Chọn năm cho bản đồ bên trái
3. Chọn năm cho bản đồ bên phải
4. Kéo thanh chia ở giữa để điều chỉnh tỷ lệ hiển thị

#### Use cases
- So sánh 2015 vs 2025 để thấy thay đổi 11 năm
- So sánh 2025 (actual) vs 2026 (forecast)
- So sánh trước/sau các sự kiện đô thị hóa

**Ví dụ phân tích:**
```
2015 (Trái)         vs        2025 (Phải)
- Khu A: NDVI 0.65          - Khu A: NDVI 0.45 → Giảm 30%
  → Rừng nguyên sinh           → Đã xây dựng nhà ở

- Khu B: NDVI 0.25          - Khu B: NDVI 0.55 → Tăng 120%
  → Đất trống                  → Công viên mới
```

[TODO: Add screenshot - map-compare.png]

### 2.3. Change Map

#### Mục đích
Hiển thị bản đồ thay đổi (difference map) giữa 2 năm.

#### Cách sử dụng
1. Chọn "Base Year" (năm gốc)
2. Chọn "Compare Year" (năm so sánh)
3. Click "Generate Change Map"
4. Bản đồ hiển thị:
   - **Blue**: Tăng NDVI (tăng thực vật)
   - **White/Gray**: Không đổi
   - **Red**: Giảm NDVI (mất thực vật)

#### Statistics Panel
Bên phải hiển thị:
- **Total pixels changed**: Số pixel có thay đổi đáng kể (|Δ| > 0.05)
- **Increased**: Số pixel tăng NDVI
- **Decreased**: Số pixel giảm NDVI
- **No significant change**: Không đổi
- **Mean change**: Thay đổi trung bình
- **Max increase/decrease**: Thay đổi lớn nhất

#### Histogram
Biểu đồ phân bố giá trị thay đổi:
- X-axis: NDVI change (-1 to +1)
- Y-axis: Số lượng pixels
- Normal distribution nếu thay đổi ngẫu nhiên
- Skewed nếu có xu hướng rõ ràng

[TODO: Add screenshot - map-change.png]

### Tips
- Dùng basemap selector để đổi nền (Streets/Satellite/Topo)
- Dùng layer control để bật/tắt các layers
- Export screenshot bằng nút "Export"
- Dùng measurement tool để đo khoảng cách/diện tích

## 3. Analytics

### Mục đích
Phân tích thống kê chi tiết về phân bố và xu hướng NDVI.

### 3.1. Statistics Table

Bảng thống kê cho từng năm:
- **Year**: Năm dữ liệu
- **Mean NDVI**: Giá trị trung bình
- **Std Dev**: Độ lệch chuẩn
- **Min**: Giá trị nhỏ nhất
- **25th Percentile**: Phân vị 25%
- **Median**: Trung vị
- **75th Percentile**: Phân vị 75%
- **Max**: Giá trị lớn nhất

**Đọc bảng:**
- Mean cao = nhiều thực vật
- Std Dev cao = phân bố không đồng đều
- Median vs Mean: Nếu khác nhiều → phân bố skewed

### 3.2. Histogram

Biểu đồ phân bố tần suất giá trị NDVI.

#### Cách sử dụng
1. Chọn năm từ dropdown
2. Histogram hiển thị số lượng pixels cho mỗi khoảng NDVI

#### Phân tích
- **Single peak**: Khu vực đồng nhất
- **Multiple peaks**: Khu vực có nhiều loại địa hình
- **Right skewed**: Nhiều thực vật
- **Left skewed**: Ít thực vật

**Ví dụ:**
```
NDVI 0.0-0.2: 15% pixels → Khu đô thị
NDVI 0.2-0.4: 35% pixels → Khu dân cư có cây
NDVI 0.4-0.6: 40% pixels → Công viên, cây xanh
NDVI 0.6-0.8: 10% pixels → Rừng
```

[TODO: Add screenshot - analytics-histogram.png]

### 3.3. Box Plot

Biểu đồ hộp so sánh phân bố NDVI qua các năm.

#### Các thành phần
- **Box**: Từ Q1 (25%) đến Q3 (75%) - chứa 50% dữ liệu giữa
- **Line trong box**: Median (Q2, 50%)
- **Whiskers**: Extend to min/max (trong 1.5×IQR)
- **Dots**: Outliers

#### Phân tích xu hướng
- Box di chuyển lên → NDVI tăng qua thời gian
- Box di chuyển xuống → NDVI giảm
- Box cao → phân bố rộng (heterogeneous)
- Box thấp → phân bố hẹp (homogeneous)

**Nhận xét xu hướng:**
- 2015-2018: Box cao, nhiều biến động
- 2019-2022: Box ổn định
- 2023-2025: Box giảm dần → Đô thị hóa
- 2026: Dự báo tiếp tục giảm nhẹ

[TODO: Add screenshot - analytics-boxplot.png]

### 3.4. Year-over-Year Comparison

Biểu đồ cột so sánh Mean NDVI từng năm.

#### Cách đọc
- Cột cao → NDVI cao → nhiều thực vật
- Xu hướng giảm dần → mất thực vật
- Spikes → năm bất thường (mưa nhiều, ít mây)

### Export Data
Click nút "Export CSV" để download dữ liệu thống kê.

## 4. Time Series

### Mục đích
Phân tích xu hướng NDVI qua thời gian (2015-2025).

### 4.1. Main Chart

Line chart hiển thị NDVI mean qua các năm.

#### Các thành phần
- **X-axis**: Năm (2015-2025)
- **Y-axis**: NDVI Mean (0-1)
- **Line**: Xu hướng NDVI
- **Markers**: Data points cho mỗi năm
- **Tooltip**: Hover để xem giá trị chính xác

#### Phân tích xu hướng
1. **Trend line**: Thêm trend line để thấy xu hướng tổng thể
2. **Slope**: 
   - Positive slope → NDVI tăng
   - Negative slope → NDVI giảm
   - Zero slope → ổn định

**Ví dụ phân tích:**
```
2015: 0.450 → Baseline
2016-2018: 0.460-0.470 → Tăng nhẹ (mưa tốt)
2019: 0.445 → Giảm (hạn)
2020-2022: 0.450-0.455 → Ổn định
2023-2025: 0.440-0.430 → Giảm (đô thị hóa)
```

[TODO: Add screenshot - timeseries-full.png]

### 4.2. Filter by District

Dropdown cho phép filter theo quận/huyện cụ thể.

#### Cách sử dụng
1. Click dropdown "Filter by District"
2. Chọn quận/huyện muốn xem
3. Chart cập nhật hiển thị chỉ khu vực đó

#### So sánh các quận
- **Quận 1, 3, 5**: NDVI thấp, giảm ít (đã đô thị hóa)
- **Quận 12, Hóc Môn**: NDVI trung bình, giảm nhanh (đang đô thị hóa)
- **Củ Chi, Cần Giờ**: NDVI cao, giảm chậm (còn nhiều cây xanh)

### 4.3. Change Detection

Panel bên phải hiển thị:
- **Total Change**: Thay đổi từ 2015 → 2025
- **% Change**: Phần trăm thay đổi
- **Average Annual Change**: Thay đổi trung bình mỗi năm
- **Trend**: Up/Down/Stable

### Export
Click "Export Data" để download time series CSV.

Format CSV:
```csv
Year,NDVI_Mean,District
2015,0.450,All
2016,0.465,All
...
```

## 5. AI Forecast

### Mục đích
Dự báo NDVI năm 2026 bằng Machine Learning.

### 5.1. Model Comparison

Bảng so sánh 5 models:

| Model | MAE | RMSE | R² | Training Time |
|-------|-----|------|----|--------------
| Linear Regression | 0.0189 | 0.0245 | 0.12 | <1s |
| Ridge Regression | 0.0187 | 0.0242 | 0.14 | <1s |
| Lasso Regression | 0.0188 | 0.0244 | 0.13 | <1s |
| SVR | 0.0165 | 0.0215 | 0.19 | 3s |
| **Random Forest** | **0.0156** | **0.0201** | **0.22** | 5s |

**Best Model: Random Forest** (lowest MAE, RMSE; highest R²)

#### Metrics giải thích
- **MAE** (Mean Absolute Error): Sai số trung bình tuyệt đối
  - Giá trị nhỏ = tốt
  - 0.0156 nghĩa là sai số trung bình ±0.0156 NDVI units
- **RMSE** (Root Mean Squared Error): Căn bậc hai sai số bình phương trung bình
  - Penalty cao hơn cho sai số lớn
  - 0.0201 là khá tốt
- **R²** (R-squared): Hệ số xác định
  - 0 = model không giải thích được gì
  - 1 = model giải thích hoàn hảo
  - 0.22 = model giải thích 22% biến động → hạn chế

[TODO: Add screenshot - forecast-models.png]

### 5.2. Forecast Result

#### NDVI 2026 Prediction
Hiển thị:
- **Predicted Mean NDVI**: Giá trị dự báo
- **Confidence Interval**: Khoảng tin cậy 95%
- **Comparison with 2025**: So với năm trước
- **Trend**: Xu hướng

**Ví dụ:**
```
Predicted NDVI 2026: 0.428 ± 0.020
2025 Actual: 0.432
Change: -0.004 (-0.9%)
Trend: Slight decrease
```

### 5.3. Feature Importance

Biểu đồ bar chart hiển thị tầm quan trọng của từng feature.

**Features được sử dụng:**
- **NDVI_lag_1**: NDVI năm trước (t-1)
- **NDVI_lag_2**: NDVI 2 năm trước (t-2)
- **NDVI_lag_3**: NDVI 3 năm trước (t-3)
- **NDVI_rolling_mean_3**: Trung bình 3 năm
- **NDVI_rolling_std_3**: Độ lệch chuẩn 3 năm
- **Year**: Năm (trend tuyến tính)

**Interpretation:**
- NDVI_lag_1 thường có importance cao nhất (>40%)
- Rolling mean quan trọng thứ 2 (~20%)
- Year có importance thấp (~5%) → weak temporal trend

[TODO: Add screenshot - forecast-importance.png]

### 5.4. Validation Plot

Scatter plot: Predicted vs Actual NDVI.

- **X-axis**: Actual NDVI
- **Y-axis**: Predicted NDVI
- **Diagonal line**: Perfect prediction
- **Points**: Predictions từ walk-forward validation

**Đọc plot:**
- Points gần diagonal = prediction tốt
- Points phân tán = prediction kém
- Pattern → model có thể cải thiện

### Limitations

⚠️ **Quan trọng:**
- Dự báo chỉ cho NDVI **trung bình toàn khu vực**, không theo pixel
- R² = 0.22 → model chỉ giải thích 22% biến động
- Không sử dụng biến ngoại sinh (nhiệt độ, mưa, LST, policy)
- Recursive forecasting tích lũy sai số
- Kết quả chỉ mang tính tham khảo

## 6. Data Catalog

### Mục đích
Browse và quản lý toàn bộ datasets.

### 6.1. Dataset List

Bảng danh sách datasets:
- **ID**: Dataset ID
- **Year**: Năm dữ liệu
- **Date**: Ngày chụp ảnh Landsat
- **Source**: Landsat 8/9
- **Scene ID**: Landsat scene identifier
- **Cloud Cover**: % mây
- **Status**: Processed/Raw
- **Actions**: Download, View metadata

### 6.2. Filtering & Sorting

- **Filter by year**: Dropdown chọn năm
- **Filter by source**: Landsat 8 hoặc 9
- **Sort**: Click column header để sort

### 6.3. Dataset Details

Click vào row để xem chi tiết:
- Metadata đầy đủ
- Processing parameters
- Quality metrics
- Preview thumbnail
- Download links

### 6.4. Download

Click "Download" để tải GeoTIFF:
- **Original**: Raw Landsat bands
- **NDVI**: Processed NDVI raster
- **Metadata**: JSON file

## Tips & Tricks

### Performance
- Bản đồ có thể load chậm với zoom level cao
- Dùng "Low Quality" mode khi explore nhanh
- Clear cache nếu bản đồ không hiển thị

### Keyboard Shortcuts
- **Ctrl + M**: Toggle Maps view
- **Ctrl + A**: Toggle Analytics
- **Ctrl + T**: Toggle Time Series
- **Ctrl + F**: Toggle Forecast
- **ESC**: Close modals/popups

### Data Export
Tất cả modules đều support export:
- **CSV**: Statistics, time series
- **PNG**: Charts, screenshots
- **GeoTIFF**: Raster data
- **GeoJSON**: Vector boundaries

### Comparison Workflow
1. Dashboard → Xem overview
2. Maps → Xem bản đồ 2015 và 2025
3. Maps Compare → So sánh trực quan
4. Analytics → Xem thống kê chi tiết
5. Time Series → Xem xu hướng
6. AI Forecast → Xem dự báo 2026

### Best Practices
- Luôn check cloud cover trước khi phân tích
- So sánh nhiều năm để tránh outliers
- Kết hợp nhiều visualizations để có insight đầy đủ
- Export data để phân tích sâu hơn trong Python/R
- Document findings trong reports

## Troubleshooting

### Bản đồ không hiển thị
1. Check console logs (F12)
2. Verify data files tồn tại trong `data/`
3. Restart backend

### Charts không load
1. Check API connection
2. Verify database có dữ liệu
3. Clear browser cache

### Slow performance
1. Reduce zoom level
2. Close unused tabs
3. Increase backend resources

---

Để biết thêm chi tiết kỹ thuật, xem [Development Guide](development.md).
