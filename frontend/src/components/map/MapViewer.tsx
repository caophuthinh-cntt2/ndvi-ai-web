import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, useMap, useMapEvents } from 'react-leaflet';
import type { Map as LeafletMap } from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { api } from '../../api/client';

interface Props { datasetId: string; onPixelClick?: (lat: number, lng: number, value: number | null) => void; syncId?: string; }
const extent: [[number, number], [number, number]] = [[10.32, 106.33], [11.50, 107.57]];
const syncMaps: Record<string, LeafletMap[]> = {};
let syncing = false;
function ResetControl() { const map = useMap(); return <button onClick={() => map.fitBounds(extent)} className="absolute top-3 left-3 z-[1000] bg-white rounded shadow px-3 py-2 text-sm">Đặt lại extent</button>; }
function ClickHandler({ datasetId, onPixelClick, onError }: Props & { onError: (message: string) => void }) { useMapEvents({ click: async event => { if (!onPixelClick) return; try { const value = await api.getPixelValue(datasetId, event.latlng.lat, event.latlng.lng); onPixelClick(event.latlng.lat, event.latlng.lng, value.value); } catch { onError('Không đọc được giá trị pixel tại vị trí này.'); } } }); return null; }
function SyncController({ syncId }: { syncId?: string }) { const map = useMap(); useEffect(() => { if (!syncId) return; const group = syncMaps[syncId] ?? (syncMaps[syncId] = []); group.push(map); const handler = () => { if (syncing) return; syncing = true; group.filter(other => other !== map).forEach(other => other.setView(map.getCenter(), map.getZoom(), { animate: false })); window.setTimeout(() => { syncing = false; }, 0); }; map.on('moveend', handler); return () => { map.off('moveend', handler); const index = group.indexOf(map); if (index >= 0) group.splice(index, 1); }; }, [map, syncId]); return null; }
export function MapViewer({ datasetId, onPixelClick, syncId }: Props) {
  const [opacity, setOpacity] = useState(1); const [loading, setLoading] = useState(true); const [error, setError] = useState('');
  return <div className="relative h-full w-full"><div className="absolute top-3 right-3 z-[1000] bg-white p-3 rounded shadow text-sm"><label>Độ mờ: {Math.round(opacity * 100)}%</label><input aria-label="Độ mờ" type="range" min="0" max="100" value={opacity * 100} onChange={e => setOpacity(Number(e.target.value) / 100)} className="block w-32" /></div>{loading && <div className="absolute bottom-3 left-3 z-[1000] bg-white px-3 py-2 rounded shadow text-sm">Đang tải tile…</div>}{error && <div className="absolute bottom-3 left-3 z-[1000] bg-red-50 text-red-700 px-3 py-2 rounded shadow text-sm">{error}</div>}<MapContainer key={datasetId} center={[10.8, 106.7]} zoom={10} maxBounds={extent} className="h-full w-full" style={{ background: '#f0f0f0' }}><TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" attribution="&copy; OpenStreetMap contributors" /><TileLayer url={`/api/tiles/${datasetId}/{z}/{x}/{y}.png`} opacity={opacity} eventHandlers={{ load: () => setLoading(false), tileerror: () => { setLoading(false); setError('Không tải được tile raster.'); } }} /><ResetControl /><SyncController syncId={syncId} /><ClickHandler datasetId={datasetId} onPixelClick={onPixelClick} onError={setError} /></MapContainer></div>;
}
export default MapViewer;
