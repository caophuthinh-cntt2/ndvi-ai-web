# NDVI AI - Hệ thống WebGIS dự báo NDVI TP.HCM

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![Node](https://img.shields.io/badge/node-18+-green.svg)

Hệ thống WebGIS và trí tuệ nhân tạo phân tích, theo dõi và dự báo biến động NDVI từ chuỗi thời gian dữ liệu viễn thám Landsat 8/9 tại TP. Hồ Chí Minh (2015-2026).

## 📋 Đề tài nghiên cứu

**Ứng dụng công nghệ WebGIS và Machine Learning trong phân tích và dự báo chỉ số NDVI từ dữ liệu viễn thám Landsat tại TP. Hồ Chí Minh**

Nghiên cứu tập trung vào:
- Xây dựng cơ sở dữ liệu không gian-thời gian từ ảnh vệ tinh Landsat 8/9 (2015-2025)
- Phân tích xu hướng biến động NDVI qua 11 năm
- Áp dụng các mô hình Machine Learning để dự báo NDVI năm 2026
- Phát triển nền tảng WebGIS tương tác để trực quan hóa và phân tích dữ liệu

## ✨ Tính năng chính

### 1. 🗺️ **Interactive Maps**
   - Hiển thị bản đồ NDVI từ 2015-2026
   - Click để xem giá trị NDVI từng pixel
   - So sánh 2 năm bất kỳ (Split Map)
   - Bản đồ thay đổi (Change Map) với phân tích thống kê

### 2. 📊 **Analytics Dashboard**
   - Thống kê tổng quan toàn khu vực
   - Histogram phân bố giá trị NDVI
   - Box plot phân tích xu hướng
   - So sánh các chỉ số qua các năm

### 3. 📈 **Time Series Analysis**
   - Biểu đồ chuỗi thời gian NDVI trung bình 2015-2025
   - Lọc theo quận/huyện
   - Xu hướng tăng/giảm
   - Export dữ liệu CSV

### 4. 🤖 **AI Forecast**
   - Dự báo NDVI năm 2026 bằng Random Forest
   - So sánh 5 mô hình ML (Linear, Ridge, Lasso, SVR, Random Forest)
   - Metrics đánh giá (MAE, RMSE, R²)
   - Visualize feature importance

### 5. 📚 **Data Catalog**
   - Browse toàn bộ datasets (11 năm)
   - Metadata chi tiết (ngày chụp, cloud cover, source)
   - Download GeoTIFF gốc
   - Xem thông tin Landsat scenes

### 6. 📉 **Dashboard Overview**
   - Summary cards (số năm, số datasets, diện tích)
   - Latest NDVI map
   - Quick stats
   - Recent changes

## 🛠️ Stack công nghệ

### Frontend
- **React 18** + **TypeScript** - UI framework
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **Leaflet** - Interactive maps
- **ECharts** - Data visualization
- **React Query** - Data fetching
- **React Router** - Navigation

### Backend
- **FastAPI** - Modern Python web framework
- **Python 3.11** - Core language
- **SQLAlchemy** - ORM
- **Pydantic** - Data validation

### Database & GIS
- **PostgreSQL 15** - Relational database
- **PostGIS 3.3** - Spatial extension
- **Rasterio** - Raster processing
- **Rio-tiler** - Tile server
- **GeoPandas** - Spatial data manipulation

### AI/ML
- **scikit-learn** - Machine learning models
- **NumPy/Pandas** - Data processing
- **Joblib** - Model persistence

## 💻 Yêu cầu hệ thống

- **OS**: Windows 10/11 (64-bit)
- **Python**: 3.11 hoặc cao hơn
- **Node.js**: 18 hoặc cao hơn
- **Docker Desktop**: Mới nhất
- **RAM**: Tối thiểu 8GB (khuyến nghị 16GB)
- **Disk**: Tối thiểu 10GB trống

## 🚀 Cài đặt nhanh

### 1. Clone/Extract project
```bash
cd D:\NDVI\ndvi-ai-web
```

### 2. Setup tự động
```powershell
.\setup.ps1
```

Script sẽ tự động:
- Tạo file `.env` từ `.env.example`
- Khởi động PostgreSQL/PostGIS qua Docker
- Tạo database và tables
- Cài đặt Python dependencies
- Cài đặt Node.js dependencies
- Import dữ liệu mẫu

### 3. Khởi động ứng dụng
```powershell
.\start.ps1
```

### 4. Truy cập ứng dụng
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 📁 Cấu trúc project

```
ndvi-ai-web/
├── frontend/                 # React frontend
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   ├── services/        # API services
│   │   ├── types/           # TypeScript types
│   │   └── App.tsx          # Main app
│   └── package.json
├── backend/                  # FastAPI backend
│   ├── app/
│   │   ├── api/             # API routes
│   │   ├── models/          # SQLAlchemy models
│   │   ├── schemas/         # Pydantic schemas
│   │   ├── services/        # Business logic
│   │   └── main.py          # FastAPI app
│   └── requirements.txt
├── data/                     # GeoTIFF raster files
│   ├── ndvi_2015.tif
│   ├── ndvi_2016.tif
│   └── ...
├── database/                 # Database scripts
│   ├── init.sql             # Schema initialization
│   └── seed_data.py         # Data seeding
├── scripts/                  # Utility scripts
│   ├── train_models.py      # ML model training
│   └── generate_tiles.py    # Tile generation
├── docs/                     # Documentation
├── docker-compose.yml        # Docker configuration
├── setup.ps1                 # Setup script
├── start.ps1                 # Start script
└── README.md                 # This file
```

## 📖 Tài liệu

- [Installation Guide](docs/installation-guide.md) - Hướng dẫn cài đặt chi tiết
- [User Guide](docs/user-guide.md) - Hướng dẫn sử dụng
- [Demo Script](docs/demo-script.md) - Kịch bản demo presentation
- [AI Methodology](docs/ai-methodology.md) - Phương pháp luận AI/ML
- [Data Dictionary](docs/data-dictionary.md) - Cấu trúc database
- [Development Guide](docs/development.md) - Hướng dẫn phát triển
- [Deployment Guide](docs/deployment.md) - Hướng dẫn triển khai
- [Troubleshooting](docs/troubleshooting.md) - Xử lý lỗi thường gặp
- [FAQ](docs/faq.md) - Câu hỏi thường gặp

## 🖼️ Screenshots

[TODO: Add screenshots]

### Dashboard
![Dashboard Overview](docs/images/dashboard.png)

### Interactive Map
![NDVI Map](docs/images/map.png)

### Time Series
![Time Series](docs/images/timeseries.png)

### AI Forecast
![Forecast](docs/images/forecast.png)

## 🔬 Phương pháp nghiên cứu

1. **Thu thập dữ liệu**: Landsat 8/9 từ USGS Earth Explorer
2. **Tiền xử lý**: Atmospheric correction, cloud masking
3. **Tính NDVI**: (NIR - Red) / (NIR + Red)
4. **Time series**: Aggregate theo năm (2015-2025)
5. **Feature engineering**: Lag features, rolling statistics
6. **Model training**: Walk-forward validation
7. **Forecasting**: Recursive multi-step prediction

## 📊 Kết quả

- **Best Model**: Random Forest Regressor
- **MAE**: 0.0156
- **RMSE**: 0.0201
- **R²**: 0.22
- **Forecast**: NDVI 2026 trung bình khu vực

## ⚠️ Limitations

- Dự báo chỉ cho NDVI trung bình toàn khu vực, không theo pixel
- R² = 0.22 cho thấy độ giải thích hạn chế
- Không sử dụng biến ngoại sinh (nhiệt độ, mưa, LST)
- Dự báo đệ quy tích lũy sai số

## 🔮 Hướng phát triển

- [ ] Thêm LST và TVDI analysis
- [ ] Spatial forecasting (theo pixel)
- [ ] Thêm biến khí tượng
- [ ] Deep Learning models (LSTM, Transformer)
- [ ] Real-time data update từ Google Earth Engine
- [ ] Mobile responsive UI
- [ ] User authentication & role management
- [ ] Export reports PDF

## 📄 License

MIT License - xem [LICENSE](LICENSE) để biết chi tiết

## 👥 Liên hệ

- **Tác giả**: [Your Name]
- **Email**: [your.email@example.com]
- **Trường**: [Your University]
- **Khoa**: [Your Department]
- **Năm**: 2026

## 🙏 Acknowledgments

- USGS Earth Explorer for Landsat data
- OpenStreetMap contributors
- scikit-learn community
- FastAPI và React communities

---

**Note**: Đây là project nghiên cứu khoa học. Kết quả dự báo chỉ mang tính chất tham khảo và cần được xác thực thêm trước khi sử dụng cho mục đích ra quyết định thực tế.
