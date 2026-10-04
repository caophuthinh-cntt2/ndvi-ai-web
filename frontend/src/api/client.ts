import axios from 'axios';
import type { Dataset, Statistics, Histogram, Boxplot, ChangeSummary, TimeSeries, ForecastResult, ForecastMap, ModelMetrics } from '../types';

const apiClient = axios.create({ baseURL: '/api', timeout: 30000, headers: { 'Content-Type': 'application/json' } });
export const api = {
  async getDatasets(): Promise<Dataset[]> { return (await apiClient.get<Dataset[]>('/datasets')).data; },
  async getDataset(id: string): Promise<Dataset> { return (await apiClient.get<Dataset>(`/datasets/${id}`)).data; },
  async getStatistics(id: string): Promise<Statistics> { return (await apiClient.get<Statistics>(`/datasets/${id}/statistics`)).data; },
  async getHistogram(id: string, bins = 50): Promise<Histogram> { return (await apiClient.get<Histogram>(`/datasets/${id}/histogram`, { params: { bins } })).data; },
  async getBoxplot(id: string): Promise<Boxplot> { return (await apiClient.get<Boxplot>(`/datasets/${id}/boxplot`)).data; },
  async getChangeSummary(id: string, threshold = 0.05): Promise<ChangeSummary> { return (await apiClient.get<ChangeSummary>(`/datasets/${id}/change-summary`, { params: { threshold } })).data; },
  async getPixelValue(datasetId: string, lat: number, lng: number): Promise<{ value: number | null; lat: number; lng: number }> { return (await apiClient.get(`/raster/value`, { params: { dataset_id: datasetId, lat, lng } })).data; },
  async getTimeSeries(params: { lat?: number; lng?: number; start_date?: string; end_date?: string } = {}): Promise<TimeSeries> { return (await apiClient.get<TimeSeries>('/timeseries', { params })).data; },
  async getForecast2026(): Promise<ForecastResult> { return (await apiClient.get<ForecastResult>('/forecast/2026')).data; },
  async getForecastMaps(): Promise<ForecastMap[]> { return (await apiClient.get<ForecastMap[]>('/forecast/2026/maps')).data; },
  async getModels(): Promise<string[]> { return (await apiClient.get<string[]>('/models')).data; },
  async getModelMetrics(id?: string): Promise<ModelMetrics[]> { return (await apiClient.get<ModelMetrics[]>(id ? `/models/${id}/metrics` : '/models/metrics')).data; },
};
export default api;
