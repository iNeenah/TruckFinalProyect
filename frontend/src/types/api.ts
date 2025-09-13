// API related types

export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: 'success' | 'error';
}

export interface ApiErrorResponse {
  detail: string;
  type?: string;
  code?: string;
  field?: string;
}

export interface ApiRequestConfig {
  baseURL?: string;
  timeout?: number;
  headers?: Record<string, string>;
  withCredentials?: boolean;
}

export interface PaginationMeta {
  page: number;
  size: number;
  total: number;
  pages: number;
  has_next: boolean;
  has_prev: boolean;
}

export interface ApiListResponse<T> {
  items: T[];
  meta: PaginationMeta;
}

// Health check response
export interface HealthCheckResponse {
  status: 'healthy' | 'degraded' | 'unhealthy';
  services: {
    database: 'healthy' | 'unhealthy';
    osrm: 'healthy' | 'unavailable';
    geocoding: 'healthy' | 'unavailable';
  };
  timestamp: string;
}

// Admin API types
export interface FuelPriceResponse {
  id: number;
  fuel_type: string;
  price_per_liter: number;
  region: string;
  effective_date: string;
  is_active: boolean;
  last_updated: string | null;
  updated_by: string | null;
  data_age_days: number;
}

export interface TollResponse {
  id: number;
  name: string;
  road_name: string;
  latitude: number;
  longitude: number;
  tariff: number;
  region: string;
  is_active: boolean;
  created_at: string;
  updated_at: string | null;
  updated_by: string | null;
}

export interface DataHealthSummary {
  health_status: 'excellent' | 'good' | 'fair' | 'poor' | 'unknown';
  overall_freshness_percentage: number;
  fuel_prices: {
    total: number;
    fresh: number;
    freshness_percentage: number;
  };
  tolls: {
    total: number;
    fresh: number;
    freshness_percentage: number;
  };
  last_checked: string;
}

export interface StalenessAlert {
  data_type: 'fuel_price' | 'toll';
  identifier: string;
  description: string;
  level: 'warning' | 'stale' | 'critical';
  days_old: number;
  last_updated: string | null;
  recommended_action: string;
  fallback_value?: number;
}

export interface StalenessReport {
  report_date: string;
  total_alerts: number;
  alerts_by_level: Record<string, number>;
  summary: string;
  recommendations: string[];
  alerts: StalenessAlert[];
}

// WebSocket message types
export interface WebSocketMessage {
  type: string;
  payload: any;
  timestamp: string;
}

export interface RouteCalculationUpdate extends WebSocketMessage {
  type: 'route_calculation_update';
  payload: {
    request_id: string;
    step: string;
    progress: number;
    message: string;
  };
}

export interface SystemNotification extends WebSocketMessage {
  type: 'system_notification';
  payload: {
    title: string;
    message: string;
    severity: 'info' | 'warning' | 'error';
    action_url?: string;
  };
}

// File upload types
export interface FileUploadResponse {
  file_id: string;
  filename: string;
  size: number;
  content_type: string;
  upload_url?: string;
}

export interface BulkImportResponse {
  message: string;
  imported_count: number;
  skipped_count: number;
  error_count: number;
  imported_items: any[];
  skipped_items: any[];
  errors: string[];
}