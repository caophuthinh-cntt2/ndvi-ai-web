import type { Dataset } from '../../types';
export function Legend({ dataset }: { dataset?: Dataset }) {
  const change = dataset?.type === 'ndvi_change';
  const items = change ? [['#b2182b', 'Giảm mạnh'], ['#ef8a62', 'Giảm'], ['#f7f7f7', 'Ổn định (0)'], ['#67a9cf', 'Tăng'], ['#2166ac', 'Tăng mạnh']] : [['#8c510a', '-1.0'], ['#d8b365', '-0.5'], ['#f6e8c3', '0'], ['#c7eae5', '0.3'], ['#5ab4ac', '0.6'], ['#01665e', '1.0']];
  return <div className="bg-white p-4 rounded-lg shadow-md"><h4 className="text-sm font-semibold text-gray-700 mb-3">{change ? 'Biến động NDVI (ΔNDVI)' : 'Chỉ số NDVI'}</h4><div className="space-y-2">{items.map(([color, label]) => <div key={label} className="flex items-center gap-2"><span className="w-8 h-4 rounded border" style={{ backgroundColor: color }} /><span className="text-xs text-gray-600">{label}</span></div>)}</div>{dataset && <div className="mt-4 pt-4 border-t text-xs text-gray-500">{dataset.name}<br />{dataset.resolution} · {dataset.crs}</div>}</div>;
}
export default Legend;
