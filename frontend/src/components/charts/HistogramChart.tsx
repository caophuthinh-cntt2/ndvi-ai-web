import React, { useEffect, useRef } from 'react';
import * as echarts from 'echarts';
import type { Histogram } from '../../types';

interface HistogramChartProps {
  data: Histogram;
  title?: string;
}

export const HistogramChart: React.FC<HistogramChartProps> = ({ data, title = 'Phân bố NDVI' }) => {
  const chartRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!chartRef.current || !data.bins.length) return;

    const chart = echarts.init(chartRef.current);

    const option: echarts.EChartsOption = {
      title: {
        text: title,
        left: 'center',
        textStyle: {
          fontSize: 16,
          fontWeight: 'normal',
        },
      },
      tooltip: {
        trigger: 'axis',
        axisPointer: {
          type: 'shadow',
        },
        formatter: (params: any) => {
          const param = params[0];
          const binStart = data.bins[param.dataIndex];
          const binEnd = data.bins[param.dataIndex + 1] || binStart + 0.02;
          return `NDVI: ${binStart.toFixed(2)} - ${binEnd.toFixed(2)}<br/>Số pixel: ${Number(param.value).toLocaleString()}`;
        },
      },
      grid: {
        left: '10%',
        right: '5%',
        bottom: '10%',
        top: '15%',
      },
      xAxis: {
        type: 'category',
        data: data.bins.map(b => b.toFixed(2)),
        name: 'NDVI',
        nameLocation: 'middle',
        nameGap: 30,
        axisLabel: {
          interval: Math.floor(data.bins.length / 10),
          rotate: 45,
        },
      },
      yAxis: {
        type: 'value',
        name: 'Số pixel',
        nameLocation: 'middle',
        nameGap: 50,
        axisLabel: {
          formatter: (value: number) => value.toLocaleString(),
        },
      },
      series: [
        {
          name: 'Số pixel',
          type: 'bar',
          data: data.counts,
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: '#10b981' },
              { offset: 1, color: '#14b8a6' },
            ]),
          },
        },
      ],
    };

    chart.setOption(option);

    const handleResize = () => chart.resize();
    window.addEventListener('resize', handleResize);

    return () => {
      window.removeEventListener('resize', handleResize);
      chart.dispose();
    };
  }, [data, title]);

  return <div ref={chartRef} className="w-full h-96" />;
};

export default HistogramChart;
