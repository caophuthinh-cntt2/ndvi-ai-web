import { useEffect, useState } from 'react';
import { Card } from '../components/common/Card';
import { Loading } from '../components/common/Loading';
import { HistogramChart } from '../components/charts/HistogramChart';
import { ModelMetricsChart } from '../components/charts/ModelMetricsChart';
import { BoxplotChart } from '../components/charts/BoxplotChart';
import { api } from '../api/client';
import type { Boxplot, ChangeSummary, Dataset, Histogram, ModelMetrics, Statistics } from '../types';

const names: Record<string, string> = { ndvi_2015: 'NDVI 2015', ndvi_2025: 'NDVI 2025', ndvi_change: 'Change 2015–2025' };
export default function Analytics() {
  const [datasets, setDatasets] = useState<Dataset[]>([]); const [selected, setSelected] = useState('ndvi_2025');
  const [stats, setStats] = useState<Statistics | null>(null); const [histogram, setHistogram] = useState<Histogram | null>(null); const [boxplots, setBoxplots] = useState<Boxplot[]>([]); const [change, setChange] = useState<ChangeSummary | null>(null); const [metrics, setMetrics] = useState<ModelMetrics[]>([]); const [loading, setLoading] = useState(true); const [error, setError] = useState('');
  useEffect(() => { api.getDatasets().then(setDatasets).then(() => api.getModelMetrics().then(setMetrics)).catch(() => setError('Không tải được dữ liệu phân tích')).finally(() => setLoading(false)); }, []);
  useEffect(() => { if (!datasets.length) return; setLoading(true); Promise.all([api.getStatistics(selected), api.getHistogram(selected), api.getBoxplot('ndvi_2015'), api.getBoxplot('ndvi_2025'), api.getChangeSummary('ndvi_change')]).then(([s, h, b1, b2, c]) => { setStats(s); setHistogram(h); setBoxplots([b1, b2]); setChange(c); }).catch(() => setError('Không tính được thống kê raster')).finally(() => setLoading(false)); }, [selected, datasets.length]);
  if (loading && !stats) return <Loading />;
  return <div className="space-y-6"><Card title="Phân tích NDVI">
    <div className="flex flex-wrap items-center gap-3"><label className="font-medium">Dataset:</label><select className="border rounded px-3 py-2" value={selected} onChange={e => setSelected(e.target.value)}>{datasets.map(d => <option key={d.id} value={d.id}>{d.name}</option>)}</select></div>
    {error && <p className="mt-3 p-3 rounded bg-red-50 text-red-700">{error}</p>}
    {stats && <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 mt-5">{[['Min', stats.min], ['Max', stats.max], ['Mean', stats.mean], ['Median', stats.median], ['Std dev', stats.std], ['Valid pixels', stats.valid_pixels.toLocaleString()]].map(([label, value]) => <div key={String(label)} className="bg-gray-50 rounded p-3"><div className="text-xs text-gray-500">{label}</div><div className="font-bold text-lg">{typeof value === 'number' && label !== 'Valid pixels' ? value.toFixed(4) : value}</div></div>)}</div>}
  </Card>
  {histogram && <Card title={`Histogram — ${names[selected]}`}><HistogramChart data={histogram} /></Card>}
  <Card title="Boxplot so sánh NDVI 2015 và 2025"><BoxplotChart data={boxplots} labels={['NDVI 2015', 'NDVI 2025']} /></Card>
  {change && <Card title="Tóm tắt biến động 2015–2025"><p className="text-sm text-gray-600 mb-4">Quy ước: giảm &lt; -0.05, ổn định trong khoảng ±0.05, tăng &gt; 0.05.</p><div className="grid grid-cols-3 gap-4 text-center">{[['Giảm', change.decreasing_percent, 'text-red-600'], ['Ổn định', change.stable_percent, 'text-gray-600'], ['Tăng', change.increasing_percent, 'text-green-600']].map(([label, value, color]) => <div key={String(label)}><div className={`text-2xl font-bold ${color}`}>{Number(value).toFixed(2)}%</div><div className="text-sm">{label}</div></div>)}</div></Card>}
  <Card title="So sánh mô hình tham chiếu"><ModelMetricsChart data={metrics} /></Card>
  </div>;
}
