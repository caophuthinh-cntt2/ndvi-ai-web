import React, { useEffect, useRef } from 'react';
import * as echarts from 'echarts';
import type { ModelMetrics } from '../../types';

interface ModelMetricsChartProps {
  data: ModelMetrics[];
  title?: string;
}

export const ModelMetricsChart: React.FC<ModelMetricsChartProps> = ({ 
  data, 
  title = 'So sánh hiệu năng mô hình' 
}) => {
  const chartRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!chartRef.current || !data.length) return;

    const chart = echarts.init(chartRef.current);

    const modelNames = data.map(d => d.model_name);
    const mae = data.map(d => d.mae);
    const rmse = data.map(d => d.rmse);
    const r2 = data.map(d => d.r2);

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
      },
      legend: {
        data: ['MAE', 'RMSE', 'R²'],
        top: 40,
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '15%',
        top: '20%',
        containLabel: true,
      },
      xAxis: {
        type: 'category',
        data: modelNames,
        axisLabel: {
          rotate: 30,
          interval: 0,
        },
      },
      yAxis: [
        {
          type: 'value',
          name: 'MAE / RMSE',
          position: 'left',
          axisLabel: {
            formatter: '{value}',
          },
        },
        {
          type: 'value',
          name: 'R²',
          position: 'right',
          axisLabel: {
            formatter: '{value}',
          },
        },
      ],
      series: [
        {
          name: 'MAE',
          type: 'bar',
          data: mae,
          itemStyle: {
            color: '#10b981',
          },
        },
        {
          name: 'RMSE',
          type: 'bar',
          data: rmse,
          itemStyle: {
            color: '#14b8a6',
          },
        },
        {
          name: 'R²',
          type: 'line',
          yAxisIndex: 1,
          data: r2,
          itemStyle: {
            color: '#f59e0b',
          },
          lineStyle: {
            width: 3,
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

export default ModelMetricsChart;
