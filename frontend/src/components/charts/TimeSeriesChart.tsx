import React, { useEffect, useRef } from 'react';
import * as echarts from 'echarts';
import type { TimeSeries } from '../../types';

interface TimeSeriesChartProps {
  data: TimeSeries;
  title?: string;
}

export const TimeSeriesChart: React.FC<TimeSeriesChartProps> = ({ data, title = 'Chuỗi thời gian NDVI' }) => {
  const chartRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!chartRef.current || !data.data.length) return;

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
        formatter: (params: any) => {
          const param = params[0];
          return `${param.name}<br/>NDVI: ${Number(param.value).toFixed(4)}`;
        },
      },
      grid: {
        left: '10%',
        right: '10%',
        bottom: '15%',
        top: '15%',
      },
      xAxis: {
        type: 'category',
        data: data.data.map(d => d.date),
        axisLabel: {
          rotate: 45,
          interval: Math.floor(data.data.length / 12),
        },
      },
      yAxis: {
        type: 'value',
        name: 'NDVI',
        nameLocation: 'middle',
        nameGap: 50,
        min: 0,
        max: 1,
      },
      series: [
        {
          name: 'NDVI',
          type: 'line',
          data: data.data.map(d => d.value),
          smooth: true,
          lineStyle: {
            color: '#10b981',
            width: 2,
          },
          itemStyle: {
            color: '#10b981',
          },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(16, 185, 129, 0.3)' },
              { offset: 1, color: 'rgba(16, 185, 129, 0.05)' },
            ]),
          },
        },
      ],
      dataZoom: [
        {
          type: 'slider',
          start: 0,
          end: 100,
        },
        {
          type: 'inside',
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

export default TimeSeriesChart;
