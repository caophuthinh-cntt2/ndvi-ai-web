import { useEffect, useState } from 'react';
import { Card } from '../components/common/Card';
import { Loading } from '../components/common/Loading';
import { ForecastChart } from '../components/charts/ForecastChart';
import { ModelMetricsChart } from '../components/charts/ModelMetricsChart';
import { api } from '../api/client';
import type { ForecastMap, ForecastResult, ModelMetrics } from '../types';

export default function AIForecast() {
  const [forecast, setForecast] = useState<ForecastResult | null>(null); const [metrics, setMetrics] = useState<ModelMetrics[]>([]); const [maps, setMaps] = useState<ForecastMap[]>([]); const [month, setMonth] = useState(1); const [loading, setLoading] = useState(true);
  useEffect(() => { Promise.all([api.getForecast2026(), api.getModelMetrics(), api.getForecastMaps()]).then(([f, m, mp]) => { setForecast(f); setMetrics(m); setMaps(mp); }).finally(() => setLoading(false)); }, []);
  if (loading || !forecast) return <Loading />;
  const minIndex = forecast.values.indexOf(forecast.statistics.min); const maxIndex = forecast.values.indexOf(forecast.statistics.max);
  return <div className="space-y-6"><Card title="Dự báo AI NDVI năm 2026"><ForecastChart data={forecast} /><div className="grid grid-cols-2 md:grid-cols-5 gap-3 text-center my-4">{[['Min', forecast.statistics.min.toFixed(4)], ['Max', forecast.statistics.max.toFixed(4)], ['Mean', forecast.statistics.mean.toFixed(4)], ['Thấp nhất', forecast.months[minIndex]], ['Cao nhất', forecast.months[maxIndex]]].map(([label, value]) => <div key={label} className="bg-gray-50 rounded p-3"><div className="text-xs text-gray-500">{label}</div><div className="font-bold">{value}</div></div>)}</div><div className="overflow-auto"><table className="min-w-full text-sm"><thead><tr className="border-b text-left"><th className="p-2">Tháng</th><th className="p-2">NDVI dự báo</th></tr></thead><tbody>{forecast.months.map((m, i) => <tr key={m} className="border-b"><td className="p-2">{m}</td><td className="p-2 font-medium">{forecast.values[i].toFixed(6)}</td></tr>)}</tbody></table></div></Card>
  <Card title="Bản đồ forecast 2026"><p className="text-sm text-gray-600 mb-3">Các ảnh bản đồ trong ZIP nguồn được hiển thị theo tháng; đây là minh họa bản đồ dự báo trung bình, không phải raster dự báo độc lập theo pixel.</p><select className="border rounded px-3 py-2 mb-4" value={month} onChange={e => setMonth(Number(e.target.value))}>{maps.map(m => <option key={m.month} value={m.month}>{m.label}</option>)}</select><div className="bg-gray-100 rounded p-2 flex justify-center"><img src={`/api/forecast/2026/maps/${month}.png`} alt={`Bản đồ forecast tháng ${month}`} className="max-h-[650px] max-w-full object-contain" /></div></Card>
  <Card title="Phương pháp và so sánh mô hình"><div className="grid md:grid-cols-2 gap-6"><div><h4 className="font-semibold mb-2">Target</h4><p className="text-sm mb-3">NDVI_mean</p><h4 className="font-semibold mb-2">Features</h4><p className="text-sm text-gray-700">lag 1, 2, 3, 6, 12; rolling mean 3, 6, 12; rolling std 3; month sin/cos; time index.</p><h4 className="font-semibold mt-4 mb-2">Validation</h4><p className="text-sm">Expanding walk-forward validation. Random Forest được chọn theo RMSE tham chiếu.</p></div><ModelMetricsChart data={metrics} /></div></Card></div>;
}
