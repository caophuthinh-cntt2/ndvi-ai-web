# Installation Guide

Hướng dẫn cài đặt chi tiết hệ thống NDVI AI WebGIS.

## Prerequisites

### 1. Python 3.11+

**Download và cài đặt:**
1. Truy cập https://www.python.org/downloads/
2. Download Python 3.11 hoặc cao hơn
3. Chạy installer
4. **Quan trọng**: Check "Add Python to PATH"
5. Click "Install Now"

**Verify:**
```powershell
python --version
# Output: Python 3.11.x
```

### 2. Node.js 18+

**Download và cài đặt:**
1. Truy cập https://nodejs.org/
2. Download LTS version (18+)
3. Chạy installer với tùy chọn mặc định
4. Installer sẽ tự động thêm vào PATH

**Verify:**
```powershell
node --version
# Output: v18.x.x hoặc cao hơn

npm --version
# Output: 9.x.x hoặc cao hơn
```

### 3. Docker Desktop

**Download và cài đặt:**
1. Truy cập https://www.docker.com/products/docker-desktop/
2. Download Docker Desktop for Windows
3. Chạy installer
4. Khởi động lại máy tính nếu được yêu cầu
5. Mở Docker Desktop và đợi khởi động hoàn tất

**Verify:**
```powershell
docker --version
# Output: Docker version 24.x.x

docker-compose --version
# Output: Docker Compose version v2.x.x
```

**Lưu ý**: Docker Desktop yêu cầu:
- Windows 10 64-bit: Pro, Enterprise, or Education (Build 19041 or higher)
- WSL 2 backend (sẽ được cài tự động)

### 4. Git (Optional)

Nếu muốn clone từ repository:
```powershell
winget install --id Git.Git -e --source winget
```

## Cài đặt Project

### Bước 1: Clone/Extract Project

**Nếu có Git:**
```powershell
cd D:\NDVI
git clone <repository-url> ndvi-ai-web
cd ndvi-ai-web
```

**Nếu có file ZIP:**
1. Extract file ZIP vào `D:\NDVI\ndvi-ai-web`
2. Mở PowerShell và cd vào thư mục:
```powershell
cd D:\NDVI\ndvi-ai-web
```

### Bước 2: Kiểm tra cấu trúc

Đảm bảo các thư mục sau tồn tại:
```
ndvi-ai-web/
├── backend/
├── frontend/
├── data/
├── database/
├── scripts/
├── setup.ps1
└── start.ps1
```

### Bước 3: Cấu hình Environment Variables

**Tự động:**
```powershell
.\setup.ps1
```

**Thủ công:**
1. Copy `.env.example` thành `.env`:
```powershell
Copy-Item .env.example .env
```

2. Mở file `.env` và cập nhật các giá trị:
```env
# Database
DATABASE_URL=postgresql://ndvi_user:ndvi_password@localhost:5432/ndvi_db
POSTGRES_USER=ndvi_user
POSTGRES_PASSWORD=ndvi_password
POSTGRES_DB=ndvi_db

# Backend
BACKEND_PORT=8000
DEBUG=True

# Frontend
VITE_API_URL=http://localhost:8000
VITE_APP_TITLE=NDVI AI - TP.HCM

# Paths
DATA_DIR=D:/NDVI/ndvi-ai-web/data
MODELS_DIR=D:/NDVI/ndvi-ai-web/models
```

### Bước 4: Setup Database

**1. Khởi động PostgreSQL container:**
```powershell
docker-compose up -d
```

**2. Đợi 10-15 giây để PostgreSQL khởi động hoàn tất**

**3. Verify container đang chạy:**
```powershell
docker ps
# Nên thấy container tên "ndvi-postgres"
```

**4. Tạo database schema:**
```powershell
docker exec -i ndvi-postgres psql -U ndvi_user -d ndvi_db < database\init.sql
```

**5. Import seed data:**
```powershell
cd backend
python database\seed_data.py
```

### Bước 5: Setup Backend

**1. Tạo virtual environment:**
```powershell
cd backend
python -m venv venv
```

**2. Activate virtual environment:**
```powershell
.\venv\Scripts\Activate.ps1
```

Nếu gặp lỗi execution policy:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\venv\Scripts\Activate.ps1
```

**3. Install dependencies:**
```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

Quá trình này có thể mất 5-10 phút.

**4. Verify installation:**
```powershell
python -c "import fastapi; import sqlalchemy; import rasterio; print('All imports OK')"
```

### Bước 6: Setup Frontend

**1. Navigate to frontend:**
```powershell
cd ..\frontend
```

**2. Install dependencies:**
```powershell
npm install
```

Quá trình này có thể mất 3-5 phút.

**3. Verify installation:**
```powershell
npm list react
# Nên hiển thị React version
```

### Bước 7: Prepare Data Files

**1. Đảm bảo các file GeoTIFF tồn tại trong `data/`:**
```
data/
├── ndvi_2015.tif
├── ndvi_2016.tif
├── ndvi_2017.tif
├── ndvi_2018.tif
├── ndvi_2019.tif
├── ndvi_2020.tif
├── ndvi_2021.tif
├── ndvi_2022.tif
├── ndvi_2023.tif
├── ndvi_2024.tif
└── ndvi_2025.tif
```

**2. Nếu thiếu file, cần xử lý từ ảnh Landsat gốc** (xem AI Methodology docs)

### Bước 8: Train AI Models

```powershell
cd ..\scripts
python train_models.py
```

Script sẽ:
- Load time series data từ database
- Thực hiện feature engineering
- Train 5 models (Linear, Ridge, Lasso, SVR, Random Forest)
- Evaluate với walk-forward validation
- Lưu models vào `models/`
- Lưu metrics vào database

Quá trình này mất khoảng 2-5 phút.

## Verification Steps

### 1. Test Database Connection

```powershell
cd backend
python -c "from app.database import engine; engine.connect(); print('Database OK')"
```

### 2. Test Backend

**Start backend:**
```powershell
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Test trong browser khác:**
- http://localhost:8000 → Nên thấy welcome message
- http://localhost:8000/docs → Nên thấy Swagger UI
- http://localhost:8000/health → `{"status": "healthy"}`

**Stop với Ctrl+C**

### 3. Test Frontend

**Start frontend:**
```powershell
cd frontend
npm run dev
```

**Test trong browser:**
- http://localhost:5173 → Nên thấy homepage

**Stop với Ctrl+C**

### 4. Test Full Stack

**Sử dụng start script:**
```powershell
cd D:\NDVI\ndvi-ai-web
.\start.ps1
```

Script sẽ mở 2 terminals:
1. Backend terminal (port 8000)
2. Frontend terminal (port 5173)

**Test các chức năng:**
- ✅ Dashboard loads
- ✅ Map hiển thị NDVI 2025
- ✅ Click vào pixel hiển thị giá trị
- ✅ Analytics charts load
- ✅ Time Series chart hiển thị
- ✅ AI Forecast page hiển thị models

## Troubleshooting

### Database Connection Error

**Lỗi:** `could not connect to server`

**Giải pháp:**
```powershell
# Check Docker container
docker ps -a

# Restart container nếu stopped
docker start ndvi-postgres

# Xem logs
docker logs ndvi-postgres
```

### Port Already in Use

**Lỗi:** `Address already in use: 8000` hoặc `5173`

**Giải pháp:**
```powershell
# Tìm process đang dùng port
netstat -ano | findstr :8000

# Kill process (thay <PID> bằng số thực tế)
taskkill /PID <PID> /F
```

### Python Import Errors

**Lỗi:** `ModuleNotFoundError`

**Giải pháp:**
```powershell
# Đảm bảo venv đang active
.\venv\Scripts\Activate.ps1

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Rasterio Installation Error

**Lỗi:** `ERROR: Failed building wheel for rasterio`

**Giải pháp:**
Cài đặt pre-built wheel:
```powershell
pip install rasterio --find-links=https://girder.github.io/large_image_wheels
```

### npm Install Errors

**Lỗi:** `ERESOLVE` hoặc dependency conflicts

**Giải pháp:**
```powershell
# Clear cache
npm cache clean --force

# Delete node_modules và package-lock.json
Remove-Item -Recurse -Force node_modules, package-lock.json

# Reinstall
npm install --legacy-peer-deps
```

### Docker Desktop Not Starting

**Giải pháp:**
1. Khởi động lại Docker Desktop
2. Nếu vẫn lỗi, restart máy tính
3. Check WSL 2:
```powershell
wsl --status
wsl --update
```

### File Encoding Issues

**Lỗi:** Vietnamese text hiển thị sai

**Giải pháp:**
Đảm bảo files lưu với UTF-8 encoding:
- VS Code: Click encoding ở status bar → "Save with Encoding" → UTF-8
- Notepad++: Encoding → UTF-8

## Next Steps

Sau khi cài đặt thành công:

1. Đọc [User Guide](user-guide.md) để hiểu cách sử dụng
2. Đọc [Demo Script](demo-script.md) để chuẩn bị presentation
3. Đọc [AI Methodology](ai-methodology.md) để hiểu phương pháp nghiên cứu
4. Tham khảo [Development Guide](development.md) nếu muốn phát triển thêm

## Quick Start Command (sau khi cài đặt lần đầu)

Những lần sau chỉ cần:
```powershell
cd D:\NDVI\ndvi-ai-web
.\start.ps1
```

Hoặc thủ công:
```powershell
# Terminal 1 - Backend
cd backend
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload

# Terminal 2 - Frontend
cd frontend
npm run dev
```
