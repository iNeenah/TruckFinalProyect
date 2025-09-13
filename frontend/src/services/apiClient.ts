import axios, { AxiosError, AxiosResponse } from 'axios';
import { toast } from 'react-hot-toast';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// API Error types
export interface ApiError {
  detail: string;
  error_code?: string;
  field_errors?: Record<string, string[]>;
}

// Create axios instance with improved configuration
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token and loading states
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Add request timestamp for debugging
    config.metadata = { startTime: new Date() };
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling and logging
api.interceptors.response.use(
  (response: AxiosResponse) => {
    // Log successful requests in development
    if (import.meta.env.DEV) {
      const duration = new Date().getTime() - response.config.metadata?.startTime?.getTime();
      console.log(`✅ ${response.config.method?.toUpperCase()} ${response.config.url} - ${duration}ms`);
    }
    
    return response;
  },
  (error: AxiosError<ApiError>) => {
    // Log errors in development
    if (import.meta.env.DEV) {
      const duration = error.config?.metadata?.startTime 
        ? new Date().getTime() - error.config.metadata.startTime.getTime()
        : 0;
      console.error(`❌ ${error.config?.method?.toUpperCase()} ${error.config?.url} - ${duration}ms`, error);
    }
    
    // Handle different error types
    if (error.response?.status === 401) {
      // Token expired or invalid
      localStorage.removeItem('access_token');
      if (window.location.pathname !== '/login') {
        toast.error('Sesión expirada. Por favor, inicia sesión nuevamente.');
        window.location.href = '/login';
      }
    } else if (error.response?.status === 403) {
      toast.error('No tienes permisos para realizar esta acción.');
    } else if (error.response?.status === 404) {
      toast.error('Recurso no encontrado.');
    } else if (error.response?.status >= 500) {
      toast.error('Error del servidor. Por favor, inténtalo más tarde.');
    } else if (error.code === 'ECONNABORTED') {
      toast.error('La solicitud tardó demasiado tiempo. Inténtalo nuevamente.');
    } else if (!error.response) {
      toast.error('Error de conexión. Verifica tu conexión a internet.');
    }
    
    return Promise.reject(error);
  }
);

// Helper function to handle API errors
export const handleApiError = (error: any): string => {
  if (error.response?.data?.detail) {
    return error.response.data.detail;
  }
  if (error.response?.data?.message) {
    return error.response.data.message;
  }
  if (error.message) {
    return error.message;
  }
  return 'Error desconocido. Por favor, inténtalo más tarde.';
};

// Helper function to check if we're online
export const checkConnection = async (): Promise<boolean> => {
  try {
    await api.get('/health', { timeout: 5000 });
    return true;
  } catch {
    return false;
  }
};

// Types for common API responses
export interface ApiResponse<T> {
  data: T;
  message?: string;
  status: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
  has_next: boolean;
  has_prev: boolean;
}

// Loading state management
export class LoadingManager {
  private static loadingRequests = new Set<string>();
  
  static addRequest(key: string) {
    this.loadingRequests.add(key);
  }
  
  static removeRequest(key: string) {
    this.loadingRequests.delete(key);
  }
  
  static isLoading(key?: string): boolean {
    if (key) {
      return this.loadingRequests.has(key);
    }
    return this.loadingRequests.size > 0;
  }
  
  static clear() {
    this.loadingRequests.clear();
  }
}

// Add loading management to axios
api.interceptors.request.use((config) => {
  const loadingKey = `${config.method?.toUpperCase()}_${config.url}`;
  LoadingManager.addRequest(loadingKey);
  config.metadata = { ...config.metadata, loadingKey };
  return config;
});

api.interceptors.response.use(
  (response) => {
    const loadingKey = response.config.metadata?.loadingKey;
    if (loadingKey) {
      LoadingManager.removeRequest(loadingKey);
    }
    return response;
  },
  (error) => {
    const loadingKey = error.config?.metadata?.loadingKey;
    if (loadingKey) {
      LoadingManager.removeRequest(loadingKey);
    }
    return Promise.reject(error);
  }
);

export default api;