import { 
  RouteRequest, 
  RouteResponse, 
  RouteHistoryResponse, 
  RouteStatistics,
  GeocodingResponse,
  RouteReportRequest,
  RouteReportResponse
} from '@types/route';
import { apiService } from './api';

class RouteService {
  async calculateRoute(request: RouteRequest): Promise<RouteResponse> {
    return await apiService.post<RouteResponse>('/routes/calculate', request);
  }

  async getRouteHistory(params?: {
    page?: number;
    size?: number;
    vehicleId?: string;
  }): Promise<RouteHistoryResponse> {
    return await apiService.get<RouteHistoryResponse>('/routes/history', { params });
  }

  async getRouteStatistics(days: number = 30): Promise<RouteStatistics> {
    return await apiService.get<RouteStatistics>('/routes/statistics', {
      params: { days },
    });
  }

  async geocodeAddress(
    address: string,
    options?: {
      limit?: number;
      country?: string;
    }
  ): Promise<GeocodingResponse> {
    return await apiService.get<GeocodingResponse>('/routes/geocode', {
      params: {
        address,
        ...options,
      },
    });
  }

  async generateReport(request: RouteReportRequest): Promise<RouteReportResponse> {
    return await apiService.post<RouteReportResponse>('/routes/reports', request);
  }

  async downloadReport(reportId: string): Promise<void> {
    await apiService.downloadFile(`/routes/reports/${reportId}/download`);
  }

  async getUserStatistics(params?: {
    days?: number;
    vehicleId?: string;
  }): Promise<any> {
    return await apiService.get('/routes/statistics/user', { params });
  }

  async getCompanyStatistics(days: number = 30): Promise<any> {
    return await apiService.get('/routes/statistics/company', {
      params: { days },
    });
  }

  async getTrendStatistics(params: {
    days?: number;
    interval?: 'daily' | 'weekly' | 'monthly';
    scope?: 'user' | 'company';
  }): Promise<any> {
    return await apiService.get('/routes/statistics/trends', { params });
  }

  async getCostBreakdownStatistics(params: {
    days?: number;
    scope?: 'user' | 'company';
  }): Promise<any> {
    return await apiService.get('/routes/statistics/cost-breakdown', { params });
  }

  async checkHealth(): Promise<any> {
    return await apiService.get('/routes/health');
  }
}

export const routeService = new RouteService();
export default routeService;