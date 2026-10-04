# Demo Script

Kịch bản demo presentation cho project NDVI AI WebGIS (5-10 phút).

## Chuẩn bị trước Demo

### Technical Setup
- [ ] Khởi động backend: `cd backend && .\venv\Scripts\Activate.ps1 && uvicorn app.main:app --reload`
- [ ] Khởi động frontend: `cd frontend && npm run dev`
- [ ] Verify http://localhost:5173 hoạt động
- [ ] Mở browser với tabs sẵn sàng
- [ ] Test click vài chỗ trên bản đồ
- [ ] Clear browser cache nếu cần

### Presentation Setup
- [ ] Prepare slides (10-12 slides)
- [ ] Backup screenshots nếu demo fail
- [ ] Prepare demo video backup
- [ ] Test projector/screen sharing
- [ ] Close unnecessary applications

### Browser Tabs Ready
1. Dashboard: http://localhost:5173
2. Maps 2015: http://localhost:5173/maps?year=2015
3. Maps 2025: http://localhost:5173/maps?year=2025
4. Analytics: http://localhost:5173/analytics
5. Time Series: http://localhost:5173/timeseries
6. AI Forecast: http://localhost:5173/forecast

## Demo Script (10 phút)

### Slide 1: Title (30s)

**Visual:** Title slide với logo, tên đề tài

**Script:**
> Xin chào thầy cô và các bạn. Em xin trình bày đề tài "Ứng dụng công nghệ WebGIS và Machine Learning trong phân tích và dự báo chỉ số NDVI từ dữ liệu viễn thám Landsat tại TP. Hồ Chí Minh".

**Talking Points:**
- Giới thiệu bản thân, lớp, GVHD
- Đề tài thuộc lĩnh vực GIS, Remote Sensing, AI
- Timeline: Nghiên cứu từ tháng X đến tháng Y

---

### Slide 2: Motivation & Objectives (45s)

**Visual:** Background image TP.HCM từ vệ tinh, highlight urban sprawl

**Script:**
> TP.HCM đang đô thị hóa rất nhanh. Từ 2015 đến 2025, diện tích xây dựng tăng gấp đôi, trong khi diện tích cây xanh giảm đáng kể. NDVI (Normalized Difference Vegetation Index) là chỉ số quan trọng để theo dõi thực vật và môi trường đô thị.

**Objectives:**
1. Xây dựng cơ sở dữ liệu NDVI từ Landsat 8/9 (2015-2025)
2. Phân tích xu hướng biến động NDVI qua 11 năm
3. Ứng dụng Machine Learning để dự báo NDVI năm 2026
4. Phát triển nền tảng WebGIS để trực quan hóa và phân tích

**Key Stats:**
- 11 năm dữ liệu (2015-2025)
- 1,000+ ảnh Landsat được xử lý
- Diện tích nghiên cứu: ~2,095 km²

---

### Slide 3: Methodology Overview (1 phút)

**Visual:** Workflow diagram

**Script:**
> Quy trình nghiên cứu gồm 4 bước chính:

**Workflow:**
```
1. Data Collection
   ↓
   - Download Landsat 8/9 từ USGS Earth Explorer
   - Cloud cover < 20%
   - Path/Row: 125/53
   
2. Preprocessing
   ↓
   - Atmospheric correction
   - Cloud masking
   - Calculate NDVI = (NIR - Red) / (NIR + Red)
   
3. Time Series Analysis
   ↓
   - Aggregate by year
   - Statistical analysis
   - Trend detection
   
4. ML Forecasting
   ↓
   - Feature engineering (lag, rolling stats)
   - Train 5 models
   - Walk-forward validation
   - Select best model
```

**Technical Stack:**
- GIS: QGIS, Python (Rasterio, GeoPandas)
- ML: scikit-learn (Random Forest)
- Web: React + FastAPI + PostgreSQL/PostGIS

---

### Slide 4: Live Demo - Dashboard (45s)

**Action:** Switch to browser → Dashboard

**Script:**
> Bây giờ em xin demo hệ thống WebGIS đã xây dựng.

**Show:**
1. **Summary cards** phía trên:
   - "11 years of data from 2015 to 2025"
   - "Total datasets: 11"
   - "Coverage area: 2,095 km²"

2. **Latest NDVI map** (2025):
   - Point ra color scheme: Red (low) → Green (high)
   - "Khu vực màu đỏ là khu đô thị, màu xanh là công viên, rừng"

3. **Quick statistics**:
   - Mean NDVI 2025: ~0.432
   - Giảm 4.3% so với 2015

**Talking Points:**
> Dashboard cho cái nhìn tổng quan. Ta thấy NDVI đang có xu hướng giảm, phản ánh quá trình đô thị hóa.

---

### Slide 5: Live Demo - NDVI Map 2015 (1 phút)

**Action:** Click "Maps" → Select Year: 2015

**Script:**
> Đây là bản đồ NDVI năm 2015, năm baseline của nghiên cứu.

**Show & Interact:**
1. **Zoom vào một khu vực** (ví dụ: Quận 12):
   - "Khu vực này năm 2015 còn nhiều cây xanh"

2. **Click vào pixel màu xanh đậm**:
   - Popup shows: "NDVI: 0.68 - Very High"
   - "Giá trị 0.68 thể hiện thực vật rất dày đặc"

3. **Click vào pixel màu đỏ** (khu đô thị):
   - Popup shows: "NDVI: 0.15 - Very Low"
   - "Giá trị 0.15 là khu xây dựng, không có thực vật"

**Talking Points:**
- NDVI range từ -1 đến 1
- Giá trị càng cao → càng nhiều thực vật
- Màu sắc giúp nhận biết nhanh các khu vực

---

### Slide 6: Live Demo - NDVI Map 2025 (1 phút)

**Action:** Select Year: 2025

**Script:**
> Bây giờ ta xem bản đồ năm 2025, sau 11 năm.

**Show & Compare:**
1. **Zoom vào cùng khu vực Quận 12**:
   - "Thấy rõ khu vực này đã bị xây dựng, màu chuyển sang đỏ/vàng"

2. **Click vào pixel cùng vị trí**:
   - Popup shows: "NDVI: 0.42 - Moderate"
   - "Giảm từ 0.68 xuống 0.42, giảm 38%"

3. **Pan đến khu vực khác** (ví dụ: Quận 1):
   - "Quận 1 đã đô thị hóa từ lâu nên NDVI ổn định, không đổi nhiều"

**Talking Points:**
> Sự thay đổi rõ rệt nhất ở các quận ngoại thành như Quận 12, Hóc Môn, Bình Tân - đang trong quá trình đô thị hóa mạnh.

---

### Slide 7: Live Demo - Compare View (1 phút)

**Action:** Click "Compare" button → 2015 vs 2025 split view

**Script:**
> Chức năng Compare giúp so sánh trực quan 2 năm cạnh nhau.

**Show:**
1. **Kéo thanh chia giữa** trái/phải:
   - "Bên trái 2015, bên phải 2025"
   - "Thấy rõ sự khác biệt màu sắc"

2. **Zoom vào một điểm thay đổi lớn**:
   - "Khu vực này từ xanh đậm thành vàng/đỏ"
   - "Đây có thể là khu công nghiệp mới hoặc khu dân cư"

**Talking Points:**
> Split map rất hữu ích để identify hotspots of change - các khu vực thay đổi nhanh cần quan tâm.

---

### Slide 8: Live Demo - Change Map & Statistics (1 phút)

**Action:** Click "Change Analysis" → Select 2015 vs 2025 → Generate

**Script:**
> Bản đồ thay đổi (change map) highlight các khu vực tăng/giảm NDVI.

**Show:**
1. **Change map**:
   - Blue = increased NDVI (cải thiện thực vật)
   - Red = decreased NDVI (mất thực vật)
   - Gray = no significant change

2. **Statistics panel**:
   - "67% pixels giảm NDVI"
   - "20% pixels tăng NDVI (công viên mới)"
   - "13% không đổi"
   - "Mean change: -0.018 (-4.3%)"

3. **Histogram**:
   - "Phân bố shift về bên trái → xu hướng giảm"

**Talking Points:**
> Nhìn chung, TP.HCM mất 4.3% NDVI trong 11 năm. Tuy nhiên có một số khu vực tăng nhờ các công viên mới như Đầm Sen, Vinhomes Central Park.

---

### Slide 9: Live Demo - Time Series (45s)

**Action:** Click "Time Series" menu

**Script:**
> Biểu đồ time series cho thấy xu hướng NDVI qua 11 năm.

**Show:**
1. **Line chart**:
   - X-axis: 2015-2025
   - Y-axis: Mean NDVI
   - "2015: 0.450 → 2025: 0.432"

2. **Hover vào các data points**:
   - Show exact values
   - "2019 có spike giảm do hạn hán"
   - "2020-2022 ổn định"
   - "2023-2025 giảm rõ rệt"

3. **Filter by district** (optional):
   - Select "Quận 12"
   - "Quận 12 giảm nhanh hơn trung bình thành phố"

**Talking Points:**
> Overall trend là giảm dần, nhưng không phải tuyến tính. Có những năm fluctuate do yếu tố khí hậu.

---

### Slide 10: Live Demo - AI Models (1 phút)

**Action:** Click "AI Forecast" menu

**Script:**
> Để dự báo NDVI năm 2026, em đã thử nghiệm 5 mô hình Machine Learning.

**Show:**
1. **Model comparison table**:
   - Linear Regression: MAE = 0.0189
   - Ridge: MAE = 0.0187
   - Lasso: MAE = 0.0188
   - SVR: MAE = 0.0165
   - **Random Forest: MAE = 0.0156** ← Best

2. **Metrics explanation**:
   - "MAE = Mean Absolute Error, càng nhỏ càng tốt"
   - "RMSE = Root Mean Squared Error"
   - "R² = 0.22 → model giải thích 22% variance"

3. **Why Random Forest**:
   - Lowest error
   - Robust to overfitting
   - Captures non-linear patterns

**Talking Points:**
> Random Forest cho kết quả tốt nhất với MAE chỉ 0.0156. Tuy nhiên R² = 0.22 cho thấy vẫn còn nhiều factors chưa được model capture được.

---

### Slide 11: Live Demo - Forecast 2026 (1 phút)

**Action:** Scroll to "Forecast Result" section

**Script:**
> Dựa trên Random Forest, dự báo NDVI năm 2026 như sau:

**Show:**
1. **Predicted value**:
   - "NDVI 2026: 0.428 ± 0.020"
   - "Confidence interval: [0.408, 0.448]"

2. **Comparison**:
   - 2025 actual: 0.432
   - 2026 forecast: 0.428
   - Change: -0.004 (-0.9%)

3. **Visualization**:
   - Line chart: Historical + Forecast
   - Confidence band around forecast

4. **Feature importance chart**:
   - NDVI_lag_1: 45% → Năm trước quan trọng nhất
   - Rolling_mean_3: 23% → Trend 3 năm
   - Year: 8% → Temporal trend yếu

**Talking Points:**
> Dự báo 2026 NDVI tiếp tục giảm nhẹ 0.9%, tiếp tục xu hướng đô thị hóa. Model chủ yếu dựa vào giá trị năm trước (lag_1).

---

### Slide 12: Limitations & Future Work (45s)

**Visual:** Bullet points

**Script:**
> Mặc dù đạt được kết quả khả quan, nghiên cứu còn một số hạn chế:

**Limitations:**
1. **Spatial resolution**: 
   - Dự báo chỉ cho mean NDVI toàn khu vực
   - Không dự báo theo pixel (spatial patterns)

2. **Model accuracy**:
   - R² = 0.22 → Limited explanatory power
   - Nhiều factors chưa được include

3. **Exogenous variables**:
   - Chưa có temperature, precipitation data
   - Chưa có LST (Land Surface Temperature)
   - Chưa có urban planning data

4. **Temporal scope**:
   - Chỉ 11 năm data → limited training samples
   - Recursive forecasting accumulates errors

**Future Improvements:**
- [ ] Thêm LST và TVDI analysis
- [ ] Spatial forecasting với Deep Learning (ConvLSTM)
- [ ] Integrate climate data
- [ ] Real-time updates từ Google Earth Engine
- [ ] Extend to other cities

---

### Slide 13: Conclusion (30s)

**Visual:** Summary points với screenshots

**Script:**
> Tóm lại, đề tài đã đạt được các mục tiêu đề ra:

**Achievements:**
✅ Xây dựng thành công cơ sở dữ liệu NDVI 11 năm từ Landsat

✅ Phân tích và phát hiện xu hướng giảm NDVI 4.3% (2015-2025)

✅ Xây dựng và đánh giá 5 models ML, chọn Random Forest (MAE = 0.0156)

✅ Dự báo thành công NDVI 2026

✅ Phát triển hệ thống WebGIS hoàn chỉnh với 6 modules

**Scientific Contribution:**
- Methodology for temporal NDVI forecasting
- Insights về urban sprawl TP.HCM
- Open-source WebGIS platform

**Practical Applications:**
- Urban planning support
- Environmental monitoring
- Green space management

---

### Slide 14: Q&A (Remaining time)

**Visual:** Thank you slide với contact info

**Script:**
> Em xin cảm ơn thầy cô và các bạn đã lắng nghe. Em sẵn sàng trả lời câu hỏi.

## Anticipated Questions & Answers

### Q1: "Tại sao R² chỉ 0.22?"

**A:**
> R² = 0.22 nghĩa là model chỉ giải thích được 22% biến động NDVI. Nguyên nhân chính là:
> 1. NDVI bị ảnh hưởng bởi nhiều factors: khí hậu, mưa, nhiệt độ, chính sách quy hoạch - mà em chưa include trong model
> 2. Model chỉ dùng temporal features (lag values), không có spatial context
> 3. 11 năm data còn ít để train model phức tạp hơn
> 
> Tuy nhiên, MAE = 0.0156 vẫn cho thấy prediction error chấp nhận được cho mục đích nghiên cứu.

### Q2: "Tại sao không dự báo theo pixel?"

**A:**
> Dự báo spatial (theo pixel) rất phức tạp vì:
> 1. Cần model học được spatial patterns và temporal patterns đồng thời
> 2. Computational cost rất cao (2M+ pixels)
> 3. Cần nhiều data hơn để train
> 
> Trong tương lai, em dự định dùng Deep Learning (ConvLSTM, Transformer) để dự báo spatial. Hiện tại, mean forecast vẫn hữu ích cho urban planning ở level thành phố.

### Q3: "Landsat resolution thô, sao không dùng Sentinel-2?"

**A:**
> Sentinel-2 có resolution cao hơn (10m vs 30m) nhưng:
> 1. Sentinel-2 mới có data từ 2015, không đủ time series dài
> 2. Landsat có archive từ 1972, phù hợp cho long-term study
> 3. Cho urban-scale analysis, 30m của Landsat đã đủ
> 
> Nếu nghiên cứu park-level hoặc tree-level thì nên dùng Sentinel-2 hoặc UAV.

### Q4: "Cloud cover ảnh hưởng như thế nào?"

**A:**
> Em đã filter chỉ giữ scenes với cloud cover < 20%. Và trong preprocessing có bước cloud masking bằng QA bands của Landsat. Pixels bị mây sẽ được loại bỏ trước khi tính NDVI mean.

### Q5: "Có validate với ground truth không?"

**A:**
> Do thiếu resources, em chưa thực hiện field survey. Nhưng em đã:
> 1. So sánh với Google Earth imagery → consistent
> 2. So sánh với số liệu cây xanh từ Sở Xây dựng TP.HCM → tương đồng về trend
> 3. Cross-validate với nghiên cứu khác về TP.HCM
> 
> Trong tương lai, ground truth validation là cần thiết cho production use.

### Q6: "Hệ thống có thể deploy production không?"

**A:**
> Hiện tại đây là prototype cho nghiên cứu. Để deploy production cần:
> 1. Optimize performance (caching, CDN)
> 2. Add authentication & authorization
> 3. Scale database (sharding, replication)
> 4. Add monitoring & logging
> 5. Responsive mobile UI
> 6. Auto data update pipeline
> 
> Em đã document deployment guide trong docs/.

### Q7: "Có thể áp dụng cho tỉnh khác không?"

**A:**
> Hoàn toàn có thể! Hệ thống được thiết kế generic:
> 1. Thay đổi bounding box trong config
> 2. Download Landsat data cho khu vực mới
> 3. Re-run preprocessing pipeline
> 4. Retrain models
> 5. Update frontend map center
> 
> Em có kế hoạch mở rộng sang Hà Nội, Đà Nẵng trong tương lai.

## Demo Backup Plan

Nếu live demo fail:

### Plan A: Use prepared screenshots
- Folder `docs/images/` có sẵn screenshots mỗi bước
- Explain như live nhưng dùng images

### Plan B: Use recorded video
- Record full demo trước (5 phút)
- Play video và explain over it

### Plan C: Slides only
- Backup slides với screenshots embedded
- Explain workflow và results từ slides

## Post-Demo Checklist

- [ ] Share slides với audience
- [ ] Share GitHub repo link
- [ ] Provide documentation link
- [ ] Collect feedback
- [ ] Note questions for improvement

## Additional Resources

- Full documentation: `docs/`
- Source code: `D:\NDVI\ndvi-ai-web\`
- Contact: [your.email@example.com]

---

**Good luck với presentation! 🎉**
