# BÁO CÁO TIẾN ĐỘ - DỰ ÁN XÂY DỰNG PHẦN MỀM DỰ BÁO NDVI

Cập nhật: 03/10/2026 | Dự án: D:\NDVI\ndvi-ai-web

## 1. TỔNG QUAN ĐỀ TÀI

Tên đề tài: Xây dựng phần mềm trí tuệ nhân tạo dự báo biến động NDVI từ chuỗi thời gian dữ liệu viễn thám tại TP.HCM (2015-2026).

Phạm vi công việc:
- Kiểm tra và audit toàn bộ dữ liệu nguồn trong D:\NDVI (8 file).
- Xây dựng backend FastAPI với database PostGIS lưu trữ raster, chuỗi thời gian và kết quả dự báo.
- Xây dựng frontend React hiển thị bản đồ lớp NDVI và biểu đồ dự báo 12 tháng năm 2026.
- Xây dựng pipeline học máy (Random Forest và các mô hình so sánh) để dự báo NDVI theo tháng.

## 2. NGUYÊN TẮC TUÂN THỦ

- Chỉ NDVI: không có chức năng LST, không có chỉ số TVDI trong menu, trong database hay trong bất kỳ chức năng nào.
- Không bịa dữ liệu: mọi con số trong báo cáo này đều lấy từ raster thật, từ CSV/GeoJSON thật, hoặc từ tài liệu giảng viên cung cấp.
- Không sửa file gốc trong D:\NDVI. Mọi sản phẩm sinh ra đều nằm trong D:\NDVI\ndvi-ai-web.

## 3. KẾT QUẢ AUDIT DỮ LIỆU (HOÀN THÀNH 100%)

Đã đọc 8 file trong D:\NDVI: 3 file DOCX, 1 file PDF, 3 file GeoTIFF, 1 file ZIP.

### 3.1 GeoTIFF

Cả 3 file cùng một grid: 4603 x 4381 pixel, EPSG:4326, độ phân giải ~30m, kiểu float64, không khai báo nodata.

| File | Min | Max | Mean | Std |
|---|---|---|---|---|
| HCM_NDVI_2015.tif | -0.9957 | 0.9165 | 0.5558 | 0.3042 |
| HCM_NDVI_2025.tif | -0.9263 | 0.9326 | 0.5585 | 0.2832 |
| HCM_NDVI_Change_2015_2025.tif | -1.3106 | 1.3124 | 0.0027 | 0.1600 |

Bounds chung của 3 file: 106.3310E đến 107.5715E, 10.3203N đến 11.5010N.

### 3.2 File ZIP dự báo

HCM_NDVI_Forecast_Maps_2026.zip chứa 16 file: 1 file CSV duy nhất (HCM_NDVI_Forecast_2026.csv) ghi 12 dong du bao thang 01 den thang 12 nam 2026, 1 file GeoJSON ranh gioi TP.HCM, 13 file PNG ban do (12 ban do tung thang + 1 ban do tong hop, 300 dpi), 1 file README.txt.

### 3.3 Training dataset 132 tháng (2015-2025)

CHƯA có file CSV hay dữ liệu thô trong D:\NDVI. Chỉ có mô tả trong tài liệu phương pháp. Đây là TRƯỜNG HỢP B theo đặc tả của đề tài.

### 3.4 Lưu ý về giá trị méo (outlier)

Có 2 pixel có giá trị không hợp lệ trong GeoTIFF: HCM_NDVI_2015.tif có 1 pixel bằng -0.9957, HCM_NDVI_2025.tif có 1 pixel bằng 0.9326. Cần ghi chú khi tính thống kê để không làm lệch kết quả.

### 3.5 File audit đã sinh ra

File audit: D:\NDVI\data_audit_report.json và D:\NDVI\data_audit_report.md

## 4. TRẠNG THÁI TỪNG THÀNH PHẦN

| Thành phần | Trạng thái | Ghi chú |
|---|---|---|
| Audit dữ liệu D:\NDVI | HOÀN THÀNH | 8/8 file đã đọc, có báo cáo JSON và MD |
| Kiến trúc hệ thống (docs/architecture.md, api-spec.md) | HOÀN THÀNH | 37.8 KB + 20.2 KB |
| Database schema PostGIS (database/schema.sql) | HOÀN THÀNH | 6 bảng, 3 enum, 2 view, GiST index, trigger |
| Cấu trúc project và config | HOÀN THÀNH | backend/, frontend/, scripts/, docs/, data/, database/ |
| Backend FastAPI (backend/app/) | ĐÃ VIẾT CODE | config, database, models, schemas, services, 5 routers - CHƯA chạy |
| Frontend React (frontend/src/) | ĐÃ VIẾT CODE | 6 trang, components, api client - CHƯA build |
| Data ingestion scripts (scripts/) | ĐÃ VIẾT CODE | ingest_rasters, ingest_forecast, ingest_model_metrics, ingest_timeseries, ingest_all - CHƯA chạy |
| ML pipeline (scripts/ml/) | ĐÃ VIẾT CODE | feature_engineering, train_model, forecast, evaluate_model - CHƯA chạy |
| Windows PowerShell scripts | HOÀN THÀNH | setup.ps1, start.ps1, stop.ps1, check_requirements.ps1, reset_database.ps1 + SCRIPTS_GUIDE.md |
| Tailwind / Vite / TypeScript config | HOÀN THÀNH | tailwind.config.js, vite.config.ts, tsconfig.json |
| Cài đặt node_modules (npm install) | ĐÃ CHẠY | Đã cài đặt node_modules |
| Tài liệu: installation-guide, user-guide, demo-script, data-dictionary | HOÀN THÀNH | Đã viết đầy đủ |
| Tài liệu: docs/ai-methodology.md | THIẾU | Chưa viết |
| Setup môi trường (venv + pip install) | CHƯA CHẠY | |
| Cài PostgreSQL/PostGIS và tạo database | CHƯA CHẠY | |
| COG conversion | CHƯA CHẠY | |
| Chạy backend và frontend | CHƯA CHẠY | |
| Build frontend production | CHƯA CHẠY | |
| Test API / test tile / test map | CHƯA CHẠY | |
| Training model trên 132 tháng thật | CHƯA CHẠY | Trường hợp B - thiếu training data |

## 5. TRẠNG THÁI AI VÀ DỰ BÁO

### 5.1 Metrics hiện tại (KẾT QUẢ THAM CHIẾU)

Các giá trị dưới đây là kết quả tham chiếu lấy từ tài liệu giảng viên, CHƯA được hệ thống tính lại.

| Mô hình | MAE | RMSE | R2 | Trạng thái |
|---|---|---|---|---|
| Random Forest | 0.021111 | 0.027339 | 0.221221 | ĐÃ CHỌN |
| Extra Trees | 0.020286 | 0.027439 | 0.193925 | So sánh |
| HistGradientBoosting | 0.025380 | 0.032245 | -0.293690 | So sánh |
| Seasonal Naive | 0.026834 | 0.036315 | -0.760498 | Baseline |

### 5.2 Dự báo 12 tháng năm 2026

Lấy trực tiếp từ file CSV trong ZIP:

| Tháng | NDVI dự báo | Tháng | NDVI dự báo |
|---|---|---|---|
| 01 | 0.5347 | 07 | 0.5736 |
| 02 | 0.5247 | 08 | 0.5762 |
| 03 | 0.5250 | 09 | 0.5705 |
| 04 | 0.5333 | 10 | 0.5772 |
| 05 | 0.5488 | 11 | 0.5713 |
| 06 | 0.5679 | 12 | 0.5618 |

Trung bình cả năm: 0.5554 | Tháng thấp nhất: tháng 02 (0.5247) | Tháng cao nhất: tháng 10 (0.5772)

### 5.3 Ghi chú quan trọng về ý nghĩa dự báo

Đây là dự báo NDVI TRUNG BÌNH THEO THÁNG cho toàn TP.HCM, KHÔNG phải dự báo theo từng pixel 30m.
Website bắt buộc phải hiển thị rõ nhãn: "Kết quả tham chiếu từ bộ dữ liệu và mô hình do giảng viên cung cấp".

## 6. CÁC BƯỚC CÒN PHẢI LÀM (KẾ TIẾP)

1. Cài Python venv và pip install requirements.
2. Cài PostgreSQL/PostGIS (Docker hoặc local), tạo database ndvi_ai.
3. Chạy setup_database.py và ingest_all.py để nạp dữ liệu.
4. Chuyển đổi 3 file TIF sang COG phục vụ tile endpoint.
5. Chạy backend bằng uvicorn, kiểm tra /api/health.
6. Build/chạy frontend Vite, kiểm tra map và tile endpoint.
7. Tạo dữ liệu training 132 tháng (cần GEE script hoặc CSV từ nguồn).
8. Chạy train_model.py để tính lại MAE, RMSE, R2 thật.
9. Test toàn bộ API, tile endpoint, click vào pixel.
10. Viết docs/ai-methodology.md.
11. Chạy end-to-end và chụp màn hình demo.

## 7. VẤN ĐỀ TỒN TẠI VÀ RỦI RO

- Training dataset 132 tháng không có thật. Hệ thống phải chạy ở chế độ "reference results" cho đến khi có dữ liệu thật.
- GeoTIFF có outlier giá trị không hợp lệ (NDVI ngoài khoảng -1 đến 1). Cần quyết định xử lý: mask hay chỉ ghi nhận.
- Raster không khai báo nodata, vì vậy phải ước lượng vùng hình học TP.HCM từ GeoJSON để loại pixel nằm ngoài AOI.
- Chưa kiểm chứng được thư mục PostgreSQL/PostGIS trên máy này.
- Chưa chạy bất kỳ script nào. Hiện tại mới là "source code đã viết", chưa được kiểm chứng thực tế.

## 8. CÁCH CHẠY (HƯỚNG DẪN, CHƯA KIỂM CHỨNG)

Các lệnh dưới đây chạy trong PowerShell tại thư mục D:\NDVI\ndvi-ai-web:

    cd D:\NDVI\ndvi-ai-web
    .\setup.ps1
    .\start.ps1

- Website: http://localhost:5173
- Backend API docs: http://localhost:8000/docs

## 9. GHI CHÚ CUỐI

Báo cáo này phản ánh trạng thái tại thời điểm biên soạn. Các mục đánh dấu CHƯA CHẠY là chưa được kiểm chứng thực tế.