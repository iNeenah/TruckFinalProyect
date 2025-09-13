import { renderHook, act } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useRouteCalculation, useRouteManagement } from '../../hooks/useRoutes';

// Mock the route service
jest.mock('../../services/routeService', () => ({
  routeService: {
    calculateRoute: jest.fn(),
    getRouteHistory: jest.fn(),
    getRouteStatistics: jest.fn(),
    saveRoute: jest.fn(),
    exportRoute: jest.fn(),
  },
}));

const mockRouteService = require('../../services/routeService');

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <QueryClientProvider client={queryClient}>
    {children}
  </QueryClientProvider>
);

describe('useRoutes', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    queryClient.clear();
  });

  describe('useRouteCalculation', () => {
    it('should call routeService.calculateRoute when mutate is called', async () => {
      const mockResponse = {
        routes: [],
        toll_points: [],
        fuel_stations: [],
      };
      
      mockRouteService.routeService.calculateRoute.mockResolvedValue(mockResponse);

      const { result } = renderHook(() => useRouteCalculation(), { wrapper });

      await act(async () => {
        await result.current.calculateRoute({} as any);
      });

      expect(mockRouteService.routeService.calculateRoute).toHaveBeenCalledWith({});
    });

    it('should set loading state correctly', async () => {
      mockRouteService.routeService.calculateRoute.mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve({}), 100))
      );

      const { result } = renderHook(() => useRouteCalculation(), { wrapper });

      expect(result.current.isCalculating).toBe(false);

      act(() => {
        result.current.calculateRoute({} as any);
      });

      expect(result.current.isCalculating).toBe(true);
    });
  });

  describe('useRouteManagement', () => {
    it('should handle route selection', () => {
      const { result } = renderHook(() => useRouteManagement(), { wrapper });

      act(() => {
        result.current.selectRoute('route-1');
      });

      expect(result.current.selectedRoutes).toContain('route-1');
    });

    it('should handle multiple route selection', () => {
      const { result } = renderHook(() => useRouteManagement(), { wrapper });

      act(() => {
        result.current.selectAllRoutes(['route-1', 'route-2', 'route-3']);
      });

      expect(result.current.selectedRoutes).toEqual(['route-1', 'route-2', 'route-3']);
    });

    it('should clear selection', () => {
      const { result } = renderHook(() => useRouteManagement(), { wrapper });

      act(() => {
        result.current.selectAllRoutes(['route-1', 'route-2']);
        result.current.clearSelection();
      });

      expect(result.current.selectedRoutes).toEqual([]);
    });

    it('should update filters', () => {
      const { result } = renderHook(() => useRouteManagement(), { wrapper });

      act(() => {
        result.current.updateFilters({ vehicle_id: 'vehicle-1' });
      });

      expect(result.current.routeFilters.vehicle_id).toBe('vehicle-1');
    });
  });
});