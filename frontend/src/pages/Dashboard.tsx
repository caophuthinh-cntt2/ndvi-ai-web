import React, { useEffect, useState } from 'react';
import { Card } from '../components/common/Card';
import { ForecastChart } from '../components/charts/ForecastChart';
import { api } from '../api/client';
import type { ForecastResult } from '../types';

export const Dashboard: React.FC = () => {
  const [forecast, setForecast] = useState<ForecastResult | null>(null);

  useEffect(() => {
    let active = true;
    api.getForecast2026()
      .then((forecastData) => {
        if (active) setForecast(forecastData);
      })
      .catch((error) => console.error('Error loading dashboard data:', error));
    return () => { active = false; };
  }, []);

  const stats = [
    { label: 'Giai đoạn', value: '2015-2026', icon: '📅' },
    { label: 'Nguồn dữ liệu', value: 'Landsat 8/9', icon: '🛰️' },
    { label: 'Độ phân giải', value: '30m', icon: '📏' },
    { label: 'Mô hình', value: 'Random Forest', icon: '🌲' },
    { label: 'RMSE', value: '0.02734', icon: '📊' },
    { label: 'NDVI TB 2026', value: forecast?.statistics.mean.toFixed(4) || '0.5554', icon: '🎯' },
  ];

  return (
    <div className="space-y-6">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-primary-600 to-teal-600 text-white rounded-lg p-8 shadow-lg">
        <h1 className="text-4xl font-bold mb-4">NDVI AI - TP. Hồ Chí Minh</h1>
        <p className="text-xl opacity-90">
          Hệ thống phân tích và dự báo chỉ số thực vật NDVI sử dụng trí tuệ nhân tạo
        </p>
        <p className="mt-4 text-lg opacity-80">
          Theo dõi sự thay đổi độ phủ xanh và dự báo xu hướng phát triển thực vật trong khu vực TP.HCM
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        {stats.map((stat, index) => (
          <Card key={index} className="text-center">
            <div className="text-3xl mb-2">{stat.icon}</div>
            <div className="text-sm text-gray-600 mb-1">{stat.label}</div>
            <div className="text-xl font-bold text-gray-800">{stat.value}</div>
          </Card>
        ))}
      </div>

      {/* Overview */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card title="Giới thiệu">
          <div className="space-y-4 text-gray-700">
            <p>
              Hệ thống NDVI AI cung cấp phân tích chuyên sâu về chỉ số thực vật NDVI 
              (Normalized Difference Vegetation Index) trên địa bàn TP. Hồ Chí Minh.
            </p>
            <p>
              Sử dụng dữ liệu vệ tinh Landsat 8/9 từ năm 2015-2025. Các mô hình học máy được đánh giá bằng walk-forward validation; Random Forest được chọn cho dự báo cuối cùng.
            </p>
            <ul className="list-disc list-inside space-y-2 text-sm">
              <li>Raster quan sát: đầy đủ từ năm 2015 đến 2025</li>
              <li>Độ phân giải không gian: 30m x 30m</li>
              <li>Phạm vi: Toàn bộ địa bàn TP.HCM</li>
              <li>Mô hình tham chiếu: Random Forest (R² = 0.221)</li>
            </ul>
          </div>
        </Card>

        <Card title="Bản đồ xem trước">
          <div className="bg-gray-100 rounded-lg h-64 flex items-center justify-center">
            <div className="text-center text-gray-500">
              <div className="text-5xl mb-4">🗺️</div>
              <p>Xem bản đồ chi tiết tại mục "Bản đồ NDVI"</p>
            </div>
          </div>
        </Card>
      </div>

      {/* Forecast Preview */}
      {forecast && (
        <Card title="Dự báo NDVI 2026">
          <ForecastChart data={forecast} title="" />
          <div className="mt-4 grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="text-sm text-gray-600">Tối thiểu</div>
              <div className="text-xl font-bold text-gray-800">{forecast.statistics.min.toFixed(4)}</div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Trung bình</div>
              <div className="text-xl font-bold text-primary-600">{forecast.statistics.mean.toFixed(4)}</div>
            </div>
            <div>
              <div className="text-sm text-gray-600">Tối đa</div>
              <div className="text-xl font-bold text-gray-800">{forecast.statistics.max.toFixed(4)}</div>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
};

export default Dashboard;
