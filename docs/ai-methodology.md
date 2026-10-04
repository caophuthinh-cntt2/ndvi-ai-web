# Phuong phap AI va gioi han du lieu

## Pham vi

Ung dung chi xu ly chi so NDVI cho khu vuc TP.HCM. Cac lop raster nguon gom NDVI nam 2015, NDVI nam 2025 va raster thay doi 2015-2025. Raster co kich thuoc 4603 x 4381, CRS EPSG:4326 va do phan giai xap xi 30 m.

## Du lieu quan sat

Backend doc truc tiep ba GeoTIFF trong `D:\NDVI` bang Rasterio. Thong ke, histogram va gia tri pixel duoc tinh tu raster tai thoi diem API duoc goi; khong co so lieu thong ke gia hoac noi suy thay the. Raster khong khai bao nodata, vi vay cac gia tri khong huu han duoc loai khoi thong ke. Hai gia tri ngoai lai duoc ghi nhan trong bao cao audit va chua tu dong xoa khoi du lieu nguon.

## Du bao nam 2026

File `HCM_NDVI_Forecast_Maps_2026.csv` trong ZIP nguon cung cap 12 gia tri NDVI trung binh theo thang. API doc truc tiep file nay va tra ve nhan `reference_results`. Day la du bao trung binh cho toan TP.HCM, khong phai du bao rieng cho tung pixel 30 m.

## Mo hinh

Random Forest la mo hinh duoc chon trong tai lieu tham chieu. Cac metrics hien thi trong ung dung la ket qua tham chieu do giang vien cung cap. Chuoi training 132 thang (2015-2025) chua co trong thu muc nguon, do do chua duoc phep huan luyen lai hoac trinh bay cac metrics tren nhu ket qua tai lap doc lap.

## Hien thi ban do

Tile endpoint tao PNG RGBA 256 x 256 tu raster nguon. Mau duoc chuan hoa trong khoang [-1, 1] cho NDVI va [-0.5, 0.5] cho raster thay doi. Tile ngoai vung raster duoc tra ve anh trong suot.

## Trang thai trien khai

Ung dung co the chay backend truc tiep bang Python va frontend bang Vite ma khong can database cho cac chuc nang doc du lieu nguon. PostgreSQL/PostGIS van duoc giu trong kien truc de mo rong ingestion va luu tru production khi Docker/PostGIS duoc cai dat.
