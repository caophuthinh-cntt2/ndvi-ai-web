# NDVI AI Web - PowerShell Scripts Guide

Hướng dẫn sử dụng các scripts quản lý hệ thống NDVI AI Web.

## 📋 Danh sách Scripts

### 1. `setup.ps1` - Cài đặt hệ thống

**Mục đích:** Cài đặt và khởi tạo toàn bộ hệ thống lần đầu tiên.

**Các bước thực hiện:**
- Kiểm tra Python 3.11+
- Kiểm tra Node.js 18+
- Kiểm tra Docker Desktop
- Tạo Python virtual environment
- Cài đặt Python packages
- Cài đặt Node packages
- Tạo file .env từ .env.example
- Khởi động PostgreSQL với Docker Compose
- Khởi tạo database
- Nạp dữ liệu mẫu

**Cách sử dụng:**
```powershell
.\setup.ps1
```

**Lưu ý:**
- Chỉ chạy một lần khi setup hệ thống lần đầu
- Cần cập nhật file `.env` theo hướng dẫn khi script yêu cầu
- Script sẽ kiểm tra tất cả requirements trước khi tiếp tục

---

### 2. `start.ps1` - Khởi động hệ thống

**Mục đích:** Khởi động backend và frontend để chạy ứng dụng.

**Các bước thực hiện:**
- Kiểm tra file .env tồn tại
- Khởi động PostgreSQL (nếu chưa chạy)
- Khởi động Backend (uvicorn) trong window mới
- Khởi động Frontend (vite) trong window mới
- Tự động mở trình duyệt tại http://localhost:5173

**Cách sử dụng:**
```powershell
.\start.ps1
```

**URLs:**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Redoc: http://localhost:8000/redoc

**Lưu ý:**
- Backend và Frontend chạy trong các PowerShell windows riêng
- Cả hai services đều có hot-reload tự động
- Đóng window hoặc nhấn Ctrl+C để dừng từng service

---

### 3. `stop.ps1` - Dừng hệ thống

**Mục đích:** Dừng tất cả các services đang chạy.

**Các bước thực hiện:**
- Dừng Backend (port 8000)
- Dừng Frontend (port 5173)
- Dừng Docker Compose (PostgreSQL)
- Dọn dẹp các processes còn sót

**Cách sử dụng:**
```powershell
.\stop.ps1
```

**Lưu ý:**
- Script sẽ tự động tìm và dừng tất cả processes liên quan
- An toàn để chạy ngay cả khi một số services không chạy

---

### 4. `check_requirements.ps1` - Kiểm tra môi trường

**Mục đích:** Kiểm tra tất cả requirements và cấu hình hệ thống.

**Các mục kiểm tra:**
1. Python version và pip
2. Node.js version và npm
3. Docker và Docker Compose
4. Cấu trúc thư mục project
5. Python virtual environment
6. Dependencies (requirements.txt, node_modules)
7. Configuration files (.env, docker-compose.yml)
8. PostgreSQL connection
9. Running services (Backend, Frontend)

**Cách sử dụng:**
```powershell
.\check_requirements.ps1
```

**Output:**
- ✓ (xanh): Pass
- ⚠ (vàng): Warning
- ✗ (đỏ): Error
- ○ (xám): Không chạy (bình thường)

**Lưu ý:**
- Chạy script này khi gặp vấn đề để chẩn đoán
- Hữu ích để kiểm tra trước khi deploy hoặc demo

---

### 5. `reset_database.ps1` - Reset database

**Mục đích:** Xóa toàn bộ database và tạo lại từ đầu (development only).

**Các bước thực hiện:**
- Yêu cầu xác nhận 2 lần
- Dừng tất cả services
- Dừng và xóa Docker containers
- Xóa Docker volume (database data)
- Khởi động lại containers
- Chạy setup_database.py
- Nạp lại dữ liệu mẫu

**Cách sử dụng:**
```powershell
.\reset_database.ps1
```

**Lưu ý:**
- ⚠️ **CẢNH BÁO:** Script này XÓA TẤT CẢ DỮ LIỆU
- Chỉ dùng cho development, KHÔNG dùng trong production
- Cần xác nhận bằng cách nhập "y" và "RESET"

---

## 🔄 Workflow thông thường

### Lần đầu tiên setup:
```powershell
# 1. Clone repository
git clone <repo-url>
cd ndvi-ai-web

# 2. Chạy setup
.\setup.ps1

# 3. Chỉnh sửa .env nếu cần
notepad .env

# 4. Khởi động hệ thống
.\start.ps1
```

### Làm việc hàng ngày:
```powershell
# Khởi động
.\start.ps1

# ... làm việc ...

# Dừng khi xong
.\stop.ps1
```

### Khi gặp vấn đề:
```powershell
# Kiểm tra hệ thống
.\check_requirements.ps1

# Nếu cần reset database
.\reset_database.ps1

# Khởi động lại
.\start.ps1
```

---

## 🛠️ Troubleshooting

### Script báo lỗi "execution policy"
```powershell
# Chạy PowerShell với quyền Administrator và thực hiện:
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Port đã được sử dụng
```powershell
# Kiểm tra process đang dùng port 8000
Get-NetTCPConnection -LocalPort 8000

# Hoặc chạy stop.ps1 để dừng tất cả
.\stop.ps1
```

### Docker không khởi động
1. Mở Docker Desktop
2. Đợi Docker daemon khởi động (biểu tượng Docker màu xanh)
3. Chạy lại script

### Virtual environment bị lỗi
```powershell
# Xóa và tạo lại
Remove-Item -Recurse -Force backend\venv
.\setup.ps1
```

### Database connection failed
```powershell
# Kiểm tra Docker container
docker ps

# Xem logs của PostgreSQL
docker logs ndvi-postgres

# Reset database nếu cần
.\reset_database.ps1
```

---

## 📝 Requirements

### Software cần cài đặt:
- **Python 3.11+** - https://www.python.org/downloads/
- **Node.js 18+** - https://nodejs.org/
- **Docker Desktop** - https://www.docker.com/products/docker-desktop

### Kiểm tra versions:
```powershell
python --version    # Python 3.11.x
node --version      # v18.x.x hoặc cao hơn
docker --version    # Docker version 20.x.x
```

---

## 🔒 Bảo mật

- File `.env` chứa thông tin nhạy cảm, **KHÔNG commit lên Git**
- File `.env.example` là template an toàn để commit
- Passwords trong production phải khác với development
- Không share `.env` file qua email hoặc chat

---

## 📚 Thông tin thêm

### Cấu trúc Project:
```
ndvi-ai-web/
├── backend/           # FastAPI backend
│   ├── app/
│   ├── venv/         # Python virtual environment
│   └── requirements.txt
├── frontend/         # React + Vite frontend
│   ├── src/
│   └── package.json
├── scripts/          # Python utility scripts
│   ├── setup_database.py
│   └── ingest_all.py
├── data/             # Data files
├── .env              # Environment variables (không commit)
├── .env.example      # Environment template
├── docker-compose.yml
├── setup.ps1         # 🔧 Setup script
├── start.ps1         # ▶️ Start script
├── stop.ps1          # ⏹️ Stop script
├── check_requirements.ps1  # ✅ Check script
└── reset_database.ps1      # 🔄 Reset script
```

### Environment Variables (.env):
```env
# Database
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password
POSTGRES_DB=ndvi_db
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/ndvi_db

# API Keys (nếu cần)
OPENAI_API_KEY=your_key_here
GOOGLE_MAPS_API_KEY=your_key_here
```

---

## 🆘 Hỗ trợ

Nếu gặp vấn đề:
1. Chạy `.\check_requirements.ps1` để chẩn đoán
2. Xem logs trong các PowerShell windows của Backend/Frontend
3. Kiểm tra Docker logs: `docker logs ndvi-postgres`
4. Tham khảo README.md chính của project

---

**Phiên bản:** 1.0  
**Cập nhật:** 2026-10-03
