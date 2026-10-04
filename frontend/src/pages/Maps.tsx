import { useEffect, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Card } from '../components/common/Card';
import { Loading } from '../components/common/Loading';
import { MapViewer } from '../components/map/MapViewer';
import { Legend } from '../components/map/Legend';
import { api } from '../api/client';
import type { Dataset } from '../types';

export default function Maps() {
  const [searchParams] = useSearchParams(); const [datasets, setDatasets] = useState<Dataset[]>([]); const [selected, setSelected] = useState(searchParams.get('dataset') || 'ndvi_2025'); const [compare, setCompare] = useState(false); const [pixel, setPixel] = useState<{ lat: number; lng: number; value: number | null; dataset: string } | null>(null); const [loading, setLoading] = useState(true); const [error, setError] = useState('');
  useEffect(() => { api.getDatasets().then(setDatasets).catch(() => setError('Không tải được danh mục raster')).finally(() => setLoading(false)); }, []);
  const current = datasets.find(d => d.id === selected); const getPixel = (dataset: string) => (lat: number, lng: number, value: number | null) => setPixel({ lat, lng, value, dataset });
  if (loading) return <Loading />;
  return <div className="space-y-6"><Card title="Bản đồ NDVI WebGIS"><div className="flex flex-wrap items-center gap-4 mb-4"><label className="font-medium">Lớp:</label><select className="border rounded px-3 py-2" value={selected} onChange={e => { setSelected(e.target.value); setPixel(null); }} disabled={compare}>{datasets.map(d => <option key={d.id} value={d.id}>{d.name}</option>)}</select><label className="flex items-center gap-2"><input type="checkbox" checked={compare} onChange={e => setCompare(e.target.checked)} /> So sánh 2015 ↔ 2025</label></div>{error && <div className="bg-red-50 text-red-700 p-3 rounded mb-3">{error}</div>}<div className={`grid gap-4 ${compare ? 'grid-cols-1 lg:grid-cols-2' : 'grid-cols-1'}`}><div className="h-[600px] rounded overflow-hidden border"><MapViewer datasetId={compare ? 'ndvi_2015' : selected} syncId={compare ? 'compare' : undefined} onPixelClick={getPixel(compare ? 'ndvi_2015' : selected)} /></div>{compare && <div className="h-[600px] rounded overflow-hidden border"><MapViewer datasetId="ndvi_2025" syncId="compare" onPixelClick={getPixel('ndvi_2025')} /></div>}</div><div className="grid grid-cols-1 lg:grid-cols-4 gap-4 mt-4"><div className="lg:col-span-3 text-sm text-gray-600">{compare ? 'Hai bản đồ được đồng bộ pan/zoom để so sánh trực quan NDVI 2015 và 2025.' : 'Click lên raster để đọc NDVI tại pixel. Dữ liệu được xử lý server-side qua XYZ tile, không tải GeoTIFF raw xuống trình duyệt.'}</div><div><Legend dataset={compare ? datasets.find(d => d.id === 'ndvi_2025') : current} /></div></div>{pixel && <div className="mt-4 p-4 bg-blue-50 rounded text-sm"><strong>Giá trị pixel</strong> — Dataset: {pixel.dataset}; tọa độ: {pixel.lat.toFixed(6)}, {pixel.lng.toFixed(6)}; NDVI: {pixel.value == null ? 'NoData' : pixel.value.toFixed(6)}</div>}</Card></div>;
}
