import { useEffect, useState } from 'react';
import { Card } from '../components/common/Card';
import { Loading } from '../components/common/Loading';
import { TimeSeriesChart } from '../components/charts/TimeSeriesChart';
import { api } from '../api/client';
import type { TimeSeries as TimeSeriesData } from '../types';

export default function TimeSeries() {
  const [data, setData] = useState<TimeSeriesData | null>(null);
  useEffect(() => { api.getTimeSeries().then(setData); }, []);
  if (!data) return <Loading />;
  return <div className="space-y-6"><Card title="Chuỗi thời gian NDVI quan sát">
    <p className="mb-4 text-sm text-blue-700 bg-blue-50 border border-blue-200 rounded p-3">Biểu đồ hiển thị NDVI trung bình theo từng năm từ 2015 đến 2025, được tính trực tiếp từ 11 raster GeoTIFF quan sát. Dữ liệu tháng chưa có trong thư mục.</p>
    <TimeSeriesChart data={data} />
    <div className="grid grid-cols-3 gap-4 text-center mt-4"><div><span className="text-gray-500 text-sm">Thấp nhất</span><div className="font-bold">{data.statistics.min.toFixed(4)}</div></div><div><span className="text-gray-500 text-sm">Trung bình</span><div className="font-bold">{data.statistics.mean.toFixed(4)}</div></div><div><span className="text-gray-500 text-sm">Cao nhất</span><div className="font-bold">{data.statistics.max.toFixed(4)}</div></div></div>
  </Card></div>;
}
