import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Card } from '../components/common/Card';
import { Loading } from '../components/common/Loading';
import { api } from '../api/client';
import type { Dataset, ForecastResult } from '../types';

export default function DataCatalog() {
  const [datasets, setDatasets] = useState<Dataset[]>([]); const [forecast, setForecast] = useState<ForecastResult | null>(null); const [loading, setLoading] = useState(true);
  useEffect(() => { Promise.all([api.getDatasets(), api.getForecast2026()]).then(([d, f]) => { setDatasets(d); setForecast(f); }).finally(() => setLoading(false)); }, []);
  if (loading) return <Loading />;
  return <div className="space-y-6"><Card title="Danh mục dữ liệu"><div className="overflow-auto"><table className="min-w-full text-sm"><thead><tr className="border-b text-left"><th className="p-3">Dataset</th><th className="p-3">Loại</th><th className="p-3">CRS</th><th className="p-3">Kích thước</th><th className="p-3">NoData</th><th className="p-3">Nguồn / mô tả</th><th className="p-3">Thao tác</th></tr></thead><tbody>{datasets.map(d => <tr key={d.id} className="border-b align-top"><td className="p-3 font-medium">{d.name}</td><td className="p-3">Observed GeoTIFF</td><td className="p-3">{d.crs}</td><td className="p-3">{d.dimensions.width} × {d.dimensions.height}<br />{d.resolution}</td><td className="p-3">{d.nodata ?? 'Không khai báo'}</td><td className="p-3">{d.source}<br /><span className="text-gray-500">NDVI raster thật</span></td><td className="p-3"><Link to={`/maps?dataset=${d.id}`} className="text-primary-700 underline">Xem bản đồ</Link></td></tr>)}{forecast && <tr className="border-b align-top"><td className="p-3 font-medium">Forecast NDVI 2026</td><td className="p-3">Forecast CSV + PNG</td><td className="p-3">N/A</td><td className="p-3">12 tháng</td><td className="p-3">N/A</td><td className="p-3">ZIP do giảng viên cung cấp<br /><span className="text-amber-700">Dự báo trung bình toàn TP.HCM</span></td><td className="p-3"><Link to="/forecast" className="text-primary-700 underline">Xem dự báo</Link></td></tr>}</tbody></table></div></Card><Card title="Training dataset"><p className="text-sm text-amber-800 bg-amber-50 border border-amber-200 rounded p-4">Chưa có CSV/dữ liệu thô 132 tháng (01/2015–12/2025) trong source hiện tại. Pipeline đã có sẵn nhưng chưa train live và không hiển thị chuỗi giả.</p></Card></div>;
}
