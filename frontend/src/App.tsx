import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom';
import Dashboard from './pages/Dashboard';
import Maps from './pages/Maps';
import Analytics from './pages/Analytics';
import TimeSeries from './pages/TimeSeries';
import AIForecast from './pages/AIForecast';
import DataCatalog from './pages/DataCatalog';
import Sidebar from './components/layout/Sidebar';
import Header from './components/layout/Header';

function Shell() {
  const location = useLocation();
  const titles: Record<string, string> = { '/': 'Tổng quan', '/maps': 'Bản đồ NDVI', '/analytics': 'Phân tích NDVI', '/timeseries': 'Chuỗi thời gian', '/forecast': 'Dự báo AI', '/catalog': 'Dữ liệu' };
  return <div className="min-h-screen bg-gray-50"><Sidebar /><main className="ml-64 min-h-screen"><Header title={`NDVI AI — ${titles[location.pathname] ?? 'TP.HCM'}`} subtitle="WebGIS phân tích và dự báo NDVI tại TP.HCM" /><div className="p-8"><Routes><Route path="/" element={<Dashboard />} /><Route path="/maps" element={<Maps />} /><Route path="/analytics" element={<Analytics />} /><Route path="/timeseries" element={<TimeSeries />} /><Route path="/forecast" element={<AIForecast />} /><Route path="/catalog" element={<DataCatalog />} /></Routes></div></main></div>;
}
export default function App() { return <Router><Shell /></Router>; }
