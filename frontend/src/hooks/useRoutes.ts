import { useState, useCallback } from 'react';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { routeService } from '../services/routeService';
import {
  RouteRequest,
  RouteResponse,
  RouteFeature,
  Location,
} from '../types/map';
import { toast } from 'react-hot-toast';

// Query keys
export const ROUTE_QUERY_KEYS = {
  all: ['routes'] as const,
  calculations: () => [...ROUTE_QUERY_KEYS.all, 'calculations'] as const,
  calculation: (id: string) => [...ROUTE_QUERY_KEYS.calculations(), id] as const,
  history: () => [...ROUTE_QUERY_KEYS.all, 'history'] as const,
  statistics: () => [...ROUTE_QUERY_KEYS.all, 'statistics'] as const,
};

// Hook for route calculation
export function useRouteCalculation() {
  const queryClient = useQueryClient();

  const calculateRoute = useMutation({
    mutationFn: (request: RouteRequest) => routeService.calculateRoute(request),
    onSuccess: (data) => {
      // Cache the successful calculation
      queryClient.setQueryData(
        ROUTE_QUERY_KEYS.calculation(generateRouteId(data)),
        data
      );
      
      // Invalidate route history to include new calculation
      queryClient.invalidateQueries({ queryKey: ROUTE_QUERY_KEYS.history() });
      queryClient.invalidateQueries({ queryKey: ROUTE_QUERY_KEYS.statistics() });
    },
    onError: (error: any) => {
      console.error('Route calculation error:', error);
      const errorMessage = error.response?.data?.detail || 'Failed to calculate route';
      toast.error(errorMessage);
    },
  });

  return {
    calculateRoute,
    isCalculating: calculateRoute.isLoading,
    error: calculateRoute.error,
  };
}

// Hook for route history
export function useRouteHistory(
  page: number = 1,
  perPage: number = 20,
  filters?: {
    start_date?: string;
    end_date?: string;
    vehicle_id?: string;
  }
) {
  return useQuery({
    queryKey: [...ROUTE_QUERY_KEYS.history(), { page, perPage, filters }],
    queryFn: () => routeService.getRouteHistory(page, perPage, filters),
    keepPreviousData: true,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// Hook for route statistics
export function useRouteStatistics(
  startDate?: string,
  endDate?: string,
  vehicleId?: string
) {
  return useQuery({
    queryKey: [...ROUTE_QUERY_KEYS.statistics(), { startDate, endDate, vehicleId }],
    queryFn: () => routeService.getRouteStatistics(startDate, endDate, vehicleId),
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}

// Hook for saving/favoriting routes
export function useRouteSave() {
  const queryClient = useQueryClient();

  const saveRoute = useMutation({
    mutationFn: (data: {
      route_id: string;
      name: string;
      description?: string;
    }) => routeService.saveRoute(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ROUTE_QUERY_KEYS.history() });
      toast.success('Route saved successfully');
    },
    onError: (error: any) => {
      console.error('Save route error:', error);
      toast.error('Failed to save route');
    },
  });

  return {
    saveRoute,
    isSaving: saveRoute.isLoading,
  };
}

// Hook for route comparison
export function useRouteComparison() {
  const [comparisonRoutes, setComparisonRoutes] = useState<RouteFeature[]>([]);

  const addToComparison = useCallback((route: RouteFeature) => {
    setComparisonRoutes(prev => {
      // Avoid duplicates
      if (prev.some(r => r.properties.route_id === route.properties.route_id)) {
        return prev;
      }
      // Limit to 3 routes for comparison
      if (prev.length >= 3) {
        return [route, ...prev.slice(0, 2)];
      }
      return [route, ...prev];
    });
  }, []);

  const removeFromComparison = useCallback((routeId: string) => {
    setComparisonRoutes(prev => 
      prev.filter(route => route.properties.route_id !== routeId)
    );
  }, []);

  const clearComparison = useCallback(() => {
    setComparisonRoutes([]);
  }, []);

  const getComparisonData = useCallback(() => {
    if (comparisonRoutes.length === 0) return null;

    const totalDistance = comparisonRoutes.reduce(
      (sum, route) => sum + route.properties.distance, 0
    );
    const totalDuration = comparisonRoutes.reduce(
      (sum, route) => sum + route.properties.duration, 0
    );
    const totalCost = comparisonRoutes.reduce(
      (sum, route) => sum + route.properties.total_cost, 0
    );

    const avgDistance = totalDistance / comparisonRoutes.length;
    const avgDuration = totalDuration / comparisonRoutes.length;
    const avgCost = totalCost / comparisonRoutes.length;

    const bestRoute = comparisonRoutes.reduce((best, current) => 
      current.properties.total_cost < best.properties.total_cost ? current : best
    );

    return {
      routes: comparisonRoutes,
      summary: {
        count: comparisonRoutes.length,
        avgDistance,
        avgDuration,
        avgCost,
        totalDistance,
        totalDuration,
        totalCost,
        bestRoute,
      },
    };
  }, [comparisonRoutes]);

  return {
    comparisonRoutes,
    addToComparison,
    removeFromComparison,
    clearComparison,
    getComparisonData,
  };
}

// Hook for route optimization preferences
export function useRoutePreferences() {
  const [preferences, setPreferences] = useState({
    optimize_for: 'cost' as 'time' | 'distance' | 'cost',
    avoid_tolls: false,
    avoid_highways: false,
    prefer_highways: false,
  });

  const updatePreference = useCallback((
    key: keyof typeof preferences,
    value: any
  ) => {
    setPreferences(prev => ({ ...prev, [key]: value }));
  }, []);

  const resetPreferences = useCallback(() => {
    setPreferences({
      optimize_for: 'cost',
      avoid_tolls: false,
      avoid_highways: false,
      prefer_highways: false,
    });
  }, []);

  return {
    preferences,
    updatePreference,
    resetPreferences,
  };
}

// Hook for route export
export function useRouteExport() {
  const exportRoute = useMutation({
    mutationFn: (data: {
      route_id: string;
      format: 'pdf' | 'excel' | 'gpx';
      include_map?: boolean;
    }) => routeService.exportRoute(data),
    onSuccess: () => {
      toast.success('Route exported successfully');
    },
    onError: (error: any) => {
      console.error('Export route error:', error);
      toast.error('Failed to export route');
    },
  });

  return {
    exportRoute,
    isExporting: exportRoute.isLoading,
  };
}

// Hook for comprehensive route management
export function useRouteManagement() {
  const [selectedRoutes, setSelectedRoutes] = useState<string[]>([]);
  const [routeFilters, setRouteFilters] = useState({
    start_date: '',
    end_date: '',
    vehicle_id: '',
  });

  const { calculateRoute, isCalculating } = useRouteCalculation();
  const { saveRoute, isSaving } = useRouteSave();
  const { exportRoute, isExporting } = useRouteExport();
  const routeComparison = useRouteComparison();
  const routePreferences = useRoutePreferences();

  const selectRoute = useCallback((routeId: string) => {
    setSelectedRoutes(prev => 
      prev.includes(routeId) 
        ? prev.filter(id => id !== routeId)
        : [...prev, routeId]
    );
  }, []);

  const selectAllRoutes = useCallback((routeIds: string[]) => {
    setSelectedRoutes(routeIds);
  }, []);

  const clearSelection = useCallback(() => {
    setSelectedRoutes([]);
  }, []);

  const updateFilters = useCallback((newFilters: Partial<typeof routeFilters>) => {
    setRouteFilters(prev => ({ ...prev, ...newFilters }));
  }, []);

  return {
    // Route calculation
    calculateRoute: calculateRoute.mutate,
    isCalculating,
    
    // Route management
    selectedRoutes,
    selectRoute,
    selectAllRoutes,
    clearSelection,
    
    // Filters
    routeFilters,
    updateFilters,
    
    // Actions
    saveRoute: saveRoute.mutate,
    isSaving,
    exportRoute: exportRoute.mutate,
    isExporting,
    
    // Comparison
    ...routeComparison,
    
    // Preferences
    ...routePreferences,
  };
}

// Utility functions
function generateRouteId(routeData: RouteResponse): string {
  // Generate a unique ID based on route data
  const origin = routeData.waypoints[0];
  const destination = routeData.waypoints[routeData.waypoints.length - 1];
  const timestamp = Date.now();
  
  return `route_${origin?.coordinates[0]}_${origin?.coordinates[1]}_${destination?.coordinates[0]}_${destination?.coordinates[1]}_${timestamp}`;
}

export function formatRouteDistance(meters: number): string {
  if (meters < 1000) {
    return `${Math.round(meters)}m`;
  }
  return `${(meters / 1000).toFixed(1)}km`;
}

export function formatRouteDuration(seconds: number): string {
  const hours = Math.floor(seconds / 3600);
  const minutes = Math.floor((seconds % 3600) / 60);
  
  if (hours > 0) {
    return `${hours}h ${minutes}m`;
  }
  return `${minutes}m`;
}

export function formatRouteCost(cost: number): string {
  return new Intl.NumberFormat('es-AR', {
    style: 'currency',
    currency: 'ARS',
  }).format(cost);
}

export function calculateRouteSavings(
  recommendedRoute: RouteFeature,
  fastestRoute: RouteFeature
): number {
  return fastestRoute.properties.total_cost - recommendedRoute.properties.total_cost;
}

export function getRouteEfficiencyScore(route: RouteFeature): number {
  // Calculate efficiency score based on cost per km
  const costPerKm = route.properties.total_cost / (route.properties.distance / 1000);
  
  // Normalize to 0-100 scale (lower cost per km = higher score)
  // This is a simplified calculation - in reality you'd want to compare against benchmarks
  const maxCostPerKm = 50; // Assume $50/km is very inefficient
  const score = Math.max(0, Math.min(100, 100 - (costPerKm / maxCostPerKm) * 100));
  
  return Math.round(score);
}