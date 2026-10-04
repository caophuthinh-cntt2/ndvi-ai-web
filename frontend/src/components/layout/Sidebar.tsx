import React from 'react';
import { Link, useLocation } from 'react-router-dom';

const menuItems = [
  { path: '/', label: 'TỔNG QUAN', icon: '📊' },
  { path: '/maps', label: 'BẢN ĐỒ NDVI', icon: '🗺️' },
  { path: '/analytics', label: 'PHÂN TÍCH NDVI', icon: '📈' },
  { path: '/timeseries', label: 'CHUỖI THỜI GIAN', icon: '📉' },
  { path: '/forecast', label: 'DỰ BÁO AI', icon: '🤖' },
  { path: '/catalog', label: 'DỮ LIỆU', icon: '📁' },
];

export const Sidebar: React.FC = () => {
  const location = useLocation();

  return (
    <div className="w-64 bg-white h-screen shadow-lg fixed left-0 top-0 flex flex-col">
      <div className="p-6 border-b border-gray-200">
        <h1 className="text-2xl font-bold text-primary-600">NDVI AI</h1>
        <p className="text-sm text-gray-600 mt-1">TP. Hồ Chí Minh</p>
      </div>
      
      <nav className="flex-1 overflow-y-auto py-4">
        {menuItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <Link
              key={item.path}
              to={item.path}
              className={`flex items-center gap-3 px-6 py-3 transition-colors ${isActive ? 'bg-primary-50 text-primary-700' : 'text-gray-700 hover:bg-gray-50'}`}
            >
              <span className="text-xl">{item.icon}</span>
              <span className="font-medium">{item.label}</span>
            </Link>
          );
        })}
      </nav>

      <div className="p-6 border-t border-gray-200 text-xs text-gray-500">
        <p>© 2026 NDVI AI System</p>
        <p className="mt-1">Phiên bản 1.0.0</p>
      </div>
    </div>
  );
};

export default Sidebar;
