import React, { useEffect, useRef } from 'react';
import * as echarts from 'echarts';
import type { Boxplot } from '../../types';

export const BoxplotChart: React.FC<{ data: Boxplot[]; labels?: string[] }> = ({ data, labels }) => {
  const chartRef = useRef<HTMLDivElement>(null);
  useEffect(() => {
    if (!chartRef.current || !data.length) return;
    const chart = echarts.init(chartRef.current);
    chart.setOption({ title: { text: 'So sánh phân bố NDVI', left: 'center' }, tooltip: { trigger: 'item' }, grid: { left: '8%', right: '5%', bottom: '12%', top: '18%', containLabel: true }, xAxis: { type: 'category', data: labels ?? data.map(item => item.dataset_id) }, yAxis: { type: 'value', name: 'NDVI' }, series: [{ type: 'boxplot', data: data.map(item => [item.lower_whisker, item.q1, item.median, item.q3, item.upper_whisker]), itemStyle: { color: '#99f6e4', borderColor: '#0f766e' } }] });
    const resize = () => chart.resize(); window.addEventListener('resize', resize);
    return () => { window.removeEventListener('resize', resize); chart.dispose(); };
  }, [data, labels]);
  return <div ref={chartRef} className="w-full h-80" />;
};
export default BoxplotChart;
