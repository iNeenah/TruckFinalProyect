import { useState, useEffect, useCallback } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { vehicleService } from '../services/vehicleService';
import {
  Vehicle,
  VehicleListResponse,
  VehicleFilters,
  VehicleSort,
  VehicleStats,
  CreateVehicleRequest,
  UpdateVehicleRequest,
  VehicleBulkOperation,
} from '../types/vehicle';
import { toast } from 'react-hot-toast';

// Query keys
export const VEHICLE_QUERY_KEYS = {
  all: ['vehicles'] as const,
  lists: () => [...VEHICLE_QUERY_KEYS.all, 'list'] as const,
  list: (filters?: VehicleFilters, page?: number, perPage?: number, sort?: VehicleSort) =>
    [...VEHICLE_QUERY_KEYS.lists(), { filters, page, perPage, sort }] as const,
  details: () => [...VEHICLE_QUERY_KEYS.all, 'detail'] as const,
  detail: (id: string) => [...VEHICLE_QUERY_KEYS.details(), id] as const,
  stats: () => [...VEHICLE_QUERY_KEYS.all, 'stats'] as const,
  usage: () => [...VEHICLE_QUERY_KEYS.all, 'usage'] as const,
};

// Hook for vehicle list with pagination and filtering
export function useVehicles(
  filters?: VehicleFilters,
  page: number = 1,
  perPage: number = 20,
  sort?: VehicleSort
) {
  return useQuery({
    queryKey: VEHICLE_QUERY_KEYS.list(filters, page, perPage, sort),
    queryFn: () => vehicleService.getVehicles(filters, page, perPage, sort),
    keepPreviousData: true,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// Hook for single vehicle
export function useVehicle(id: string) {
  return useQuery({
    queryKey: VEHICLE_QUERY_KEYS.detail(id),
    queryFn: () => vehicleService.getVehicle(id),
    enabled: !!id,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// Hook for vehicle statistics
export function useVehicleStats() {
  return useQuery({
    queryKey: VEHICLE_QUERY_KEYS.stats(),
    queryFn: () => vehicleService.getVehicleStats(),
    staleTime: 10 * 60 * 1000, // 10 minutes
  });
}

// Hook for vehicle mutations
export function useVehicleMutations() {
  const queryClient = useQueryClient();

  const createVehicle = useMutation({
    mutationFn: (data: CreateVehicleRequest) => vehicleService.createVehicle(data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: VEHICLE_QUERY_KEYS.lists() });
      queryClient.invalidateQueries({ queryKey: VEHICLE_QUERY_KEYS.stats() });
      toast.success('Vehicle created successfully');
    },
    onError: (error: any) => {
      console.error('Error creating vehicle:', error);
      toast.error('Failed to create vehicle');
    },
  });

  const updateVehicle = useMutation({
    mutationFn: ({ id, data }: { id: string; data: UpdateVehicleRequest }) =>
      vehicleService.updateVehicle(id, data),
    onSuccess: (updatedVehicle) => {
      queryClient.invalidateQueries({ queryKey: VEHICLE_QUERY_KEYS.lists() });
      queryClient.invalidateQueries({ queryKey: VEHICLE_QUERY_KEYS.stats() });
      queryClient.setQueryData(
        VEHICLE_QUERY_KEYS.detail(updatedVehicle.id),
        updatedVehicle
      );
      toast.success('Vehicle updated successfully');
    },
    onError: (error: any) => {
      console.error('Error updating vehicle:', error);
      toast.error('Failed to update vehicle');
    },
  });

  const deleteVehicle = useMutation({
    mutationFn: (id: string) => vehicleService.deleteVehicle(id),
    onSuccess: (_, deletedId) => {
      queryClient.invalidateQueries({ queryKey: VEHICLE_QUERY_KEYS.lists() });
      queryClient.invalidateQueries({ queryKey: VEHICLE_QUERY_KEYS.stats() });
      queryClient.removeQueries({ queryKey: VEHICLE_QUERY_KEYS.detail(deletedId) });
      toast.success('Vehicle deleted successfully');
    },
    onError: (error: any) => {
      console.error('Error deleting vehicle:', error);
      toast.error('Failed to delete vehicle');
    },
  });

  const toggleVehicleStatus = useMutation({
    mutationFn: ({ id, isActive }: { id: string; isActive: boolean }) =>
      vehicleService.toggleVehicleStatus(id, isActive),
    onSuccess: (updatedVehicle) => {
      queryClient.invalidateQueries({ queryKey: VEHICLE_QUERY_KEYS.lists() });
      queryClient.invalidateQueries({ queryKey: VEHICLE_QUERY_KEYS.stats() });
      queryClient.setQueryData(
        VEHICLE_QUERY_KEYS.detail(updatedVehicle.id),
        updatedVehicle
      );
      toast.success(
        `Vehicle ${updatedVehicle.is_active ? 'activated' : 'deactivated'} successfully`
      );
    },
    onError: (error: any) => {
      console.error('Error toggling vehicle status:', error);
      toast.error('Failed to update vehicle status');
    },
  });

  const bulkOperation = useMutation({
    mutationFn: (operation: VehicleBulkOperation) => vehicleService.bulkOperation(operation),
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: VEHICLE_QUERY_KEYS.lists() });
      queryClient.invalidateQueries({ queryKey: VEHICLE_QUERY_KEYS.stats() });
      toast.success(
        `Bulk operation completed: ${result.success} successful, ${result.failed} failed`
      );
    },
    onError: (error: any) => {
      console.error('Error performing bulk operation:', error);
      toast.error('Failed to perform bulk operation');
    },
  });

  return {
    createVehicle,
    updateVehicle,
    deleteVehicle,
    toggleVehicleStatus,
    bulkOperation,
  };
}

// Hook for license plate availability check
export function useLicensePlateCheck() {
  const [isChecking, setIsChecking] = useState(false);
  const [isAvailable, setIsAvailable] = useState<boolean | null>(null);

  const checkAvailability = useCallback(
    async (licensePlate: string, excludeId?: string) => {
      if (!licensePlate || licensePlate.length < 6) {
        setIsAvailable(null);
        return;
      }

      try {
        setIsChecking(true);
        const available = await vehicleService.checkLicensePlateAvailability(
          licensePlate,
          excludeId
        );
        setIsAvailable(available);
      } catch (error) {
        console.error('Error checking license plate:', error);
        setIsAvailable(null);
      } finally {
        setIsChecking(false);
      }
    },
    []
  );

  const reset = useCallback(() => {
    setIsAvailable(null);
    setIsChecking(false);
  }, []);

  return {
    isChecking,
    isAvailable,
    checkAvailability,
    reset,
  };
}

// Hook for vehicle suggestions
export function useVehicleSuggestions() {
  return useMutation({
    mutationFn: (requirements: {
      max_weight?: number;
      max_volume?: number;
      fuel_type?: string;
      route_distance?: number;
    }) => vehicleService.getVehicleSuggestions(requirements),
  });
}

// Hook for vehicle usage data
export function useVehicleUsage(
  vehicleId?: string,
  startDate?: string,
  endDate?: string
) {
  return useQuery({
    queryKey: [...VEHICLE_QUERY_KEYS.usage(), { vehicleId, startDate, endDate }],
    queryFn: () => vehicleService.getVehicleUsage(vehicleId, startDate, endDate),
    enabled: !!vehicleId || !!startDate || !!endDate,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}

// Hook for vehicle export
export function useVehicleExport() {
  return useMutation({
    mutationFn: (filters?: VehicleFilters) => vehicleService.exportVehicles(filters),
    onSuccess: () => {
      toast.success('Vehicles exported successfully');
    },
    onError: (error: any) => {
      console.error('Error exporting vehicles:', error);
      toast.error('Failed to export vehicles');
    },
  });
}

// Hook for vehicle import
export function useVehicleImport() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (data: any[]) => vehicleService.importVehicles(data),
    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: VEHICLE_QUERY_KEYS.lists() });
      queryClient.invalidateQueries({ queryKey: VEHICLE_QUERY_KEYS.stats() });
      
      if (result.error_count > 0) {
        toast.error(
          `Import completed with errors: ${result.success_count} successful, ${result.error_count} failed`
        );
      } else {
        toast.success(`Successfully imported ${result.success_count} vehicles`);
      }
    },
    onError: (error: any) => {
      console.error('Error importing vehicles:', error);
      toast.error('Failed to import vehicles');
    },
  });
}

// Hook for comprehensive vehicle management
export function useVehicleManagement() {
  const [filters, setFilters] = useState<VehicleFilters>({});
  const [sort, setSort] = useState<VehicleSort>({
    field: 'created_at',
    direction: 'desc',
  });
  const [currentPage, setCurrentPage] = useState(1);
  const [perPage] = useState(20);

  const vehiclesQuery = useVehicles(filters, currentPage, perPage, sort);
  const statsQuery = useVehicleStats();
  const mutations = useVehicleMutations();
  const exportMutation = useVehicleExport();

  const handleFiltersChange = useCallback((newFilters: VehicleFilters) => {
    setFilters(newFilters);
    setCurrentPage(1);
  }, []);

  const handleSortChange = useCallback((newSort: VehicleSort) => {
    setSort(newSort);
    setCurrentPage(1);
  }, []);

  const handlePageChange = useCallback((page: number) => {
    setCurrentPage(page);
  }, []);

  return {
    // Data
    vehicles: vehiclesQuery.data?.vehicles || [],
    totalPages: vehiclesQuery.data?.total_pages || 1,
    totalVehicles: vehiclesQuery.data?.total || 0,
    stats: statsQuery.data,
    
    // Loading states
    isLoading: vehiclesQuery.isLoading,
    isLoadingStats: statsQuery.isLoading,
    
    // Error states
    error: vehiclesQuery.error,
    statsError: statsQuery.error,
    
    // Filters and pagination
    filters,
    sort,
    currentPage,
    perPage,
    
    // Actions
    handleFiltersChange,
    handleSortChange,
    handlePageChange,
    
    // Mutations
    ...mutations,
    exportVehicles: exportMutation.mutate,
    isExporting: exportMutation.isLoading,
    
    // Refetch
    refetch: vehiclesQuery.refetch,
    refetchStats: statsQuery.refetch,
  };
}