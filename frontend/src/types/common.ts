// Common types used throughout the application

export interface Coordinates {
  longitude: number;
  latitude: number;
}

export interface PaginationParams {
  page: number;
  size: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

export interface ApiError {
  detail: string;
  type?: string;
  code?: string;
}

export interface LoadingState {
  isLoading: boolean;
  error: string | null;
}

export interface DateRange {
  start: Date;
  end: Date;
}

export type SortDirection = 'asc' | 'desc';

export interface SortParams {
  field: string;
  direction: SortDirection;
}

export interface FilterParams {
  [key: string]: string | number | boolean | null | undefined;
}

// Generic form state
export interface FormState<T> {
  data: T;
  errors: Partial<Record<keyof T, string>>;
  isSubmitting: boolean;
  isDirty: boolean;
}

// Generic async operation state
export interface AsyncState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  lastUpdated: Date | null;
}

// File upload types
export interface FileUpload {
  file: File;
  progress: number;
  status: 'pending' | 'uploading' | 'success' | 'error';
  error?: string;
}

// Theme mode
export type ThemeMode = 'light' | 'dark';

// Language codes
export type Language = 'es' | 'en';

// Currency
export type Currency = 'ARS' | 'USD';

// Distance units
export type DistanceUnit = 'km' | 'mi';

// Fuel types
export type FuelType = 'diesel_500' | 'diesel_premium' | 'gasoline_regular' | 'gasoline_premium';

// Route optimization criteria
export type OptimizationCriteria = 'cost' | 'time' | 'distance';

// Alert severity levels
export type AlertSeverity = 'success' | 'info' | 'warning' | 'error';

// Data staleness levels
export type StalenessLevel = 'fresh' | 'warning' | 'stale' | 'critical';