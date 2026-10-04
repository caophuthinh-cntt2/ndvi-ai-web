import React, { useEffect, useRef } from 'react';
import * as echarts from 'echarts';
import type { ForecastResult } from '../../types';

interface ForecastChartProps {
  data: ForecastResult;
  title?: string;
}

export const ForecastChart: React.FC<ForecastChartProps> = ({ 
  data, 
  title = 'Dự báo NDVI 2026' 
}) => {
  const chartRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!chartRef.current || !data.values.length) return;

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
        bottom: '10%',
        top: '15%',
      },
      xAxis: {
        type: 'category',
        data: data.months,
        name: 'Tháng',
        nameLocation: 'middle',
        nameGap: 30,
      },
      yAxis: {
        type: 'value',
        name: 'NDVI',
        nameLocation: 'middle',
        nameGap: 50,
        min: 0.5,
        max: 0.6,
      },
      series: [
        {
          name: 'Dự báo NDVI',
          type: 'line',
          data: data.values,
          smooth: true,
          lineStyle: {
            color: '#f59e0b',
            width: 3,
          },
          itemStyle: {
            color: '#f59e0b',
          },
          areaStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(245, 158, 11, 0.3)' },
              { offset: 1, color: 'rgba(245, 158, 11, 0.05)' },
            ]),
          },
          markLine: {
            data: [
              {
                yAxis: 0.5554,
                name: 'Trung bình 0.5554',
                label: {
                  formatter: 'TB: 0.5554',
                },
              },
            ],
            lineStyle: {
              color: '#ef4444',
              type: 'dashed',
            },
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

export default ForecastChart;
