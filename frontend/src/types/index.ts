export type DatasetType = `ndvi_${number}` | 'ndvi_change';
export interface Dataset { id: string; name: string; type: DatasetType; year?: number; resolution: string; dimensions: { width: number; height: number }; crs: string; source: string; nodata?: number | null; file_type?: string; data_status?: 'observed' | 'forecast'; bounds: { minLat: number; maxLat: number; minLng: number; maxLng: number }; }
export interface Statistics { min: number; max: number; mean: number; median: number; std: number; valid_pixels: number; total_pixels: number; }
export interface Histogram { bins: number[]; counts: number[]; }
export interface Boxplot { dataset_id: string; min: number; q1: number; median: number; q3: number; max: number; lower_whisker: number; upper_whisker: number; }
export interface ChangeSummary { dataset_id: string; threshold: number; decreasing_pixels: number; stable_pixels: number; increasing_pixels: number; valid_pixels: number; decreasing_percent: number; stable_percent: number; increasing_percent: number; }
export interface TimeSeriesPoint { date: string; value: number; }
export interface TimeSeries { data: TimeSeriesPoint[]; statistics: { min: number; max: number; mean: number; median: number; std: number }; status?: string; source_note?: string; }
export interface ModelMetrics { model_name: string; mae: number; rmse: number; r2: number; }
export interface ForecastResult { model: string; forecast_period: string; values: number[]; months: string[]; statistics: { min: number; max: number; mean: number }; status?: string; source_note?: string; }
export interface ForecastMap { month: number; label: string; url: string; }
export interface MapLayer { id: string; name: string; visible: boolean; opacity: number; }
