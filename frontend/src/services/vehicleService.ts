import { AxiosResponse } from 'axios';
import apiService from './api';
import { Vehicle, CreateVehicleRequest, UpdateVehicleRequest } from '@types';
import { cacheService } from './CacheService';

const VEHICLE_ENDPOINT = '/vehicles';

// Obtener todos los vehículos
export const fetchVehicles = async (): Promise<Vehicle[]> => {
  // Verificar caché primero
  const cachedVehicles = cacheService.getCachedVehicles();
  if (cachedVehicles) {
    console.log('Returning vehicles from cache');
    return cachedVehicles;
  }
  
  try {
    const response = await apiService.get<Vehicle[]>(VEHICLE_ENDPOINT);
    // Guardar en caché
    cacheService.cacheVehicles(response);
    return response;
  } catch (error) {
    console.error('Error fetching vehicles:', error);
    throw error;
  }
};

// Obtener un vehículo por ID
export const fetchVehicleById = async (id: string): Promise<Vehicle> => {
  try {
    const response = await apiService.get<Vehicle>(`${VEHICLE_ENDPOINT}/${id}`);
    return response;
  } catch (error) {
    console.error(`Error fetching vehicle ${id}:`, error);
    throw error;
  }
};

// Crear un nuevo vehículo
export const createVehicle = async (vehicleData: CreateVehicleRequest): Promise<Vehicle> => {
  try {
    const response = await apiService.post<Vehicle>(VEHICLE_ENDPOINT, vehicleData);
    // Limpiar caché de vehículos
    cacheService.remove('vehicles');
    return response;
  } catch (error) {
    console.error('Error creating vehicle:', error);
    throw error;
  }
};

// Actualizar un vehículo
export const updateVehicle = async (id: string, vehicleData: UpdateVehicleRequest): Promise<Vehicle> => {
  try {
    const response = await apiService.put<Vehicle>(`${VEHICLE_ENDPOINT}/${id}`, vehicleData);
    // Limpiar caché de vehículos
    cacheService.remove('vehicles');
    return response;
  } catch (error) {
    console.error(`Error updating vehicle ${id}:`, error);
    throw error;
  }
};

// Eliminar un vehículo
export const deleteVehicle = async (id: string): Promise<void> => {
  try {
    await apiService.delete(`${VEHICLE_ENDPOINT}/${id}`);
    // Limpiar caché de vehículos
    cacheService.remove('vehicles');
  } catch (error) {
    console.error(`Error deleting vehicle ${id}:`, error);
    throw error;
  }
};

// Calcular consumo de combustible
export const calculateFuelConsumption = (distance: number, fuelEfficiency: number): number => {
  return (distance / 100) * fuelEfficiency;
};

class VehicleService {
  private readonly baseURL = '/vehicles';

  /**
   * Get list of vehicles with optional filters and pagination
   */
  async getVehicles(
    filters?: VehicleFilters,
    page: number = 1,
    perPage: number = 20,
    sort?: VehicleSort
  ): Promise<VehicleListResponse> {
    try {
      const params = new URLSearchParams();
      
      if (filters?.search) params.append('search', filters.search);
      if (filters?.fuel_type) params.append('fuel_type', filters.fuel_type);
      if (filters?.is_active !== undefined) params.append('is_active', filters.is_active.toString());
      if (filters?.company_id) params.append('company_id', filters.company_id);
      
      params.append('page', page.toString());
      params.append('per_page', perPage.toString());
      
      if (sort) {
        params.append('sort_by', sort.field);
        params.append('sort_direction', sort.direction);
      }

      const response: AxiosResponse<VehicleListResponse> = await apiClient.get(
        `${this.baseURL}?${params.toString()}`
      );
      
      return response.data;
    } catch (error: any) {
      console.error('Error fetching vehicles:', error);
      throw error;
    }
  }

  /**
   * Get a single vehicle by ID
   */
  async getVehicle(id: string): Promise<Vehicle> {
    try {
      const response: AxiosResponse<Vehicle> = await apiClient.get(`${this.baseURL}/${id}`);
      return response.data;
    } catch (error: any) {
      console.error('Error fetching vehicle:', error);
      throw error;
    }
  }

  /**
   * Create a new vehicle
   */
  async createVehicle(data: CreateVehicleRequest): Promise<Vehicle> {
    try {
      const response: AxiosResponse<Vehicle> = await apiClient.post(this.baseURL, data);
      return response.data;
    } catch (error: any) {
      console.error('Error creating vehicle:', error);
      throw error;
    }
  }

  /**
   * Update an existing vehicle
   */
  async updateVehicle(id: string, data: UpdateVehicleRequest): Promise<Vehicle> {
    try {
      const response: AxiosResponse<Vehicle> = await apiClient.put(`${this.baseURL}/${id}`, data);
      return response.data;
    } catch (error: any) {
      console.error('Error updating vehicle:', error);
      throw error;
    }
  }

  /**
   * Delete a vehicle
   */
  async deleteVehicle(id: string): Promise<void> {
    try {
      await apiClient.delete(`${this.baseURL}/${id}`);
    } catch (error: any) {
      console.error('Error deleting vehicle:', error);
      throw error;
    }
  }

  /**
   * Activate/deactivate a vehicle
   */
  async toggleVehicleStatus(id: string, isActive: boolean): Promise<Vehicle> {
    try {
      const response: AxiosResponse<Vehicle> = await apiClient.patch(
        `${this.baseURL}/${id}/status`,
        { is_active: isActive }
      );
      return response.data;
    } catch (error: any) {
      console.error('Error toggling vehicle status:', error);
      throw error;
    }
  }

  /**
   * Get vehicle statistics
   */
  async getVehicleStats(): Promise<VehicleStats> {
    try {
      const response: AxiosResponse<VehicleStats> = await apiClient.get(`${this.baseURL}/stats`);
      return response.data;
    } catch (error: any) {
      console.error('Error fetching vehicle stats:', error);
      throw error;
    }
  }

  /**
   * Get vehicle usage data
   */
  async getVehicleUsage(
    vehicleId?: string,
    startDate?: string,
    endDate?: string
  ): Promise<VehicleUsage[]> {
    try {
      const params = new URLSearchParams();
      
      if (vehicleId) params.append('vehicle_id', vehicleId);
      if (startDate) params.append('start_date', startDate);
      if (endDate) params.append('end_date', endDate);

      const response: AxiosResponse<VehicleUsage[]> = await apiClient.get(
        `${this.baseURL}/usage?${params.toString()}`
      );
      
      return response.data;
    } catch (error: any) {
      console.error('Error fetching vehicle usage:', error);
      throw error;
    }
  }

  /**
   * Perform bulk operations on vehicles
   */
  async bulkOperation(operation: VehicleBulkOperation): Promise<{ success: number; failed: number }> {
    try {
      const response: AxiosResponse<{ success: number; failed: number }> = await apiClient.post(
        `${this.baseURL}/bulk`,
        operation
      );
      return response.data;
    } catch (error: any) {
      console.error('Error performing bulk operation:', error);
      throw error;
    }
  }

  /**
   * Import vehicles from CSV data
   */
  async importVehicles(data: VehicleImportData[]): Promise<VehicleImportResult> {
    try {
      const response: AxiosResponse<VehicleImportResult> = await apiClient.post(
        `${this.baseURL}/import`,
        { vehicles: data }
      );
      return response.data;
    } catch (error: any) {
      console.error('Error importing vehicles:', error);
      throw error;
    }
  }

  /**
   * Export vehicles to CSV
   */
  async exportVehicles(filters?: VehicleFilters): Promise<void> {
    try {
      const params = new URLSearchParams();
      
      if (filters?.search) params.append('search', filters.search);
      if (filters?.fuel_type) params.append('fuel_type', filters.fuel_type);
      if (filters?.is_active !== undefined) params.append('is_active', filters.is_active.toString());
      if (filters?.company_id) params.append('company_id', filters.company_id);

      await apiClient.downloadFile(
        `${this.baseURL}/export?${params.toString()}`,
        'vehicles.csv'
      );
    } catch (error: any) {
      console.error('Error exporting vehicles:', error);
      throw error;
    }
  }

  /**
   * Check if license plate is available
   */
  async checkLicensePlateAvailability(licensePlate: string, excludeId?: string): Promise<boolean> {
    try {
      const params = new URLSearchParams();
      params.append('license_plate', licensePlate);
      if (excludeId) params.append('exclude_id', excludeId);

      const response: AxiosResponse<{ available: boolean }> = await apiClient.get(
        `${this.baseURL}/check-license-plate?${params.toString()}`
      );
      
      return response.data.available;
    } catch (error: any) {
      console.error('Error checking license plate availability:', error);
      throw error;
    }
  }

  /**
   * Get vehicle maintenance reminders
   */
  async getMaintenanceReminders(vehicleId?: string): Promise<any[]> {
    try {
      const params = vehicleId ? `?vehicle_id=${vehicleId}` : '';
      const response: AxiosResponse<any[]> = await apiClient.get(
        `${this.baseURL}/maintenance-reminders${params}`
      );
      return response.data;
    } catch (error: any) {
      console.error('Error fetching maintenance reminders:', error);
      throw error;
    }
  }

  /**
   * Get fuel efficiency report for a vehicle
   */
  async getFuelEfficiencyReport(
    vehicleId: string,
    startDate?: string,
    endDate?: string
  ): Promise<any> {
    try {
      const params = new URLSearchParams();
      if (startDate) params.append('start_date', startDate);
      if (endDate) params.append('end_date', endDate);

      const response: AxiosResponse<any> = await apiClient.get(
        `${this.baseURL}/${vehicleId}/fuel-efficiency?${params.toString()}`
      );
      
      return response.data;
    } catch (error: any) {
      console.error('Error fetching fuel efficiency report:', error);
      throw error;
    }
  }

  /**
   * Get vehicle route history
   */
  async getVehicleRouteHistory(
    vehicleId: string,
    page: number = 1,
    perPage: number = 20
  ): Promise<any> {
    try {
      const params = new URLSearchParams();
      params.append('page', page.toString());
      params.append('per_page', perPage.toString());

      const response: AxiosResponse<any> = await apiClient.get(
        `${this.baseURL}/${vehicleId}/routes?${params.toString()}`
      );
      
      return response.data;
    } catch (error: any) {
      console.error('Error fetching vehicle route history:', error);
      throw error;
    }
  }

  /**
   * Upload vehicle image
   */
  async uploadVehicleImage(vehicleId: string, file: File): Promise<{ image_url: string }> {
    try {
      const response: AxiosResponse<{ image_url: string }> = await apiClient.uploadFile(
        `${this.baseURL}/${vehicleId}/image`,
        file,
        'image'
      );
      return response.data;
    } catch (error: any) {
      console.error('Error uploading vehicle image:', error);
      throw error;
    }
  }

  /**
   * Delete vehicle image
   */
  async deleteVehicleImage(vehicleId: string): Promise<void> {
    try {
      await apiClient.delete(`${this.baseURL}/${vehicleId}/image`);
    } catch (error: any) {
      console.error('Error deleting vehicle image:', error);
      throw error;
    }
  }

  /**
   * Get vehicle suggestions based on route requirements
   */
  async getVehicleSuggestions(requirements: {
    max_weight?: number;
    max_volume?: number;
    fuel_type?: string;
    route_distance?: number;
  }): Promise<Vehicle[]> {
    try {
      const params = new URLSearchParams();
      
      if (requirements.max_weight) params.append('max_weight', requirements.max_weight.toString());
      if (requirements.max_volume) params.append('max_volume', requirements.max_volume.toString());
      if (requirements.fuel_type) params.append('fuel_type', requirements.fuel_type);
      if (requirements.route_distance) params.append('route_distance', requirements.route_distance.toString());

      const response: AxiosResponse<Vehicle[]> = await apiClient.get(
        `${this.baseURL}/suggestions?${params.toString()}`
      );
      
      return response.data;
    } catch (error: any) {
      console.error('Error fetching vehicle suggestions:', error);
      throw error;
    }
  }
}

// Create and export singleton instance
export const vehicleService = new VehicleService();