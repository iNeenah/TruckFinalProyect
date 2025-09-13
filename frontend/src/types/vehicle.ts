// Vehicle types
export interface Vehicle {
  id: string;
  name: string;
  license_plate: string;
  fuel_type: FuelType;
  fuel_consumption: number; // L/100km
  max_weight: number; // kg
  max_volume: number; // m³
  length: number; // m
  width: number; // m
  height: number; // m
  company_id: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
  last_used?: string;
}

// Fuel types
export type FuelType = 'diesel_500' | 'diesel_premium' | 'gasoline_regular' | 'gasoline_premium';

export const FUEL_TYPES: Record<FuelType, string> = {
  diesel_500: 'Diesel 500 ppm',
  diesel_premium: 'Diesel Premium',
  gasoline_regular: 'Gasoline Regular',
  gasoline_premium: 'Gasoline Premium',
};

// Vehicle creation/update types
export interface CreateVehicleRequest {
  name: string;
  license_plate: string;
  fuel_type: FuelType;
  fuel_consumption: number;
  max_weight: number;
  max_volume: number;
  length: number;
  width: number;
  height: number;
}

export interface UpdateVehicleRequest extends Partial<CreateVehicleRequest> {
  is_active?: boolean;
}

// Vehicle list filters
export interface VehicleFilters {
  search?: string;
  fuel_type?: FuelType;
  is_active?: boolean;
  company_id?: string;
}

// Vehicle list response
export interface VehicleListResponse {
  vehicles: Vehicle[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

// Vehicle statistics
export interface VehicleStats {
  total_vehicles: number;
  active_vehicles: number;
  inactive_vehicles: number;
  avg_fuel_consumption: number;
  most_used_fuel_type: FuelType;
  total_capacity_weight: number;
  total_capacity_volume: number;
}

// Vehicle usage data
export interface VehicleUsage {
  vehicle_id: string;
  vehicle_name: string;
  total_routes: number;
  total_distance: number; // km
  total_fuel_consumed: number; // L
  total_cost_savings: number; // ARS
  last_route_date?: string;
  avg_fuel_efficiency: number; // L/100km actual vs theoretical
}

// Vehicle validation errors
export interface VehicleValidationError {
  field: string;
  message: string;
  code?: string;
}

// Vehicle form data
export interface VehicleFormData {
  name: string;
  license_plate: string;
  fuel_type: FuelType;
  fuel_consumption: string; // String for form input
  max_weight: string; // String for form input
  max_volume: string; // String for form input
  length: string; // String for form input
  width: string; // String for form input
  height: string; // String for form input
}

// Vehicle table column definitions
export interface VehicleTableColumn {
  key: keyof Vehicle | 'actions';
  label: string;
  sortable?: boolean;
  width?: string;
  align?: 'left' | 'center' | 'right';
  render?: (vehicle: Vehicle) => React.ReactNode;
}

// Vehicle sort options
export type VehicleSortField = 'name' | 'license_plate' | 'fuel_consumption' | 'created_at' | 'last_used';
export type SortDirection = 'asc' | 'desc';

export interface VehicleSort {
  field: VehicleSortField;
  direction: SortDirection;
}

// Vehicle bulk operations
export type VehicleBulkAction = 'activate' | 'deactivate' | 'delete';

export interface VehicleBulkOperation {
  action: VehicleBulkAction;
  vehicle_ids: string[];
}

// Vehicle import/export
export interface VehicleImportData {
  name: string;
  license_plate: string;
  fuel_type: string;
  fuel_consumption: number;
  max_weight: number;
  max_volume: number;
  length: number;
  width: number;
  height: number;
}

export interface VehicleImportResult {
  success_count: number;
  error_count: number;
  errors: Array<{
    row: number;
    errors: VehicleValidationError[];
  }>;
}

// Constants
export const VEHICLE_CONSTRAINTS = {
  NAME: {
    MIN_LENGTH: 2,
    MAX_LENGTH: 100,
  },
  LICENSE_PLATE: {
    MIN_LENGTH: 6,
    MAX_LENGTH: 10,
    PATTERN: /^[A-Z0-9\-\s]+$/,
  },
  FUEL_CONSUMPTION: {
    MIN: 5,
    MAX: 100,
  },
  MAX_WEIGHT: {
    MIN: 500,
    MAX: 50000,
  },
  MAX_VOLUME: {
    MIN: 1,
    MAX: 200,
  },
  DIMENSIONS: {
    MIN: 1,
    MAX: 25,
  },
} as const;

// Default values
export const DEFAULT_VEHICLE: Partial<VehicleFormData> = {
  name: '',
  license_plate: '',
  fuel_type: 'diesel_500',
  fuel_consumption: '25',
  max_weight: '3500',
  max_volume: '15',
  length: '6',
  width: '2.5',
  height: '3',
};

// Utility functions
export function formatFuelType(fuelType: FuelType): string {
  return FUEL_TYPES[fuelType] || fuelType;
}

export function formatWeight(weight: number): string {
  if (weight >= 1000) {
    return `${(weight / 1000).toFixed(1)}t`;
  }
  return `${weight}kg`;
}

export function formatVolume(volume: number): string {
  return `${volume}m³`;
}

export function formatDimensions(length: number, width: number, height: number): string {
  return `${length}m × ${width}m × ${height}m`;
}

export function formatFuelConsumption(consumption: number): string {
  return `${consumption}L/100km`;
}

export function calculateVehicleCapacity(vehicle: Vehicle): {
  weight_capacity: string;
  volume_capacity: string;
  dimensions: string;
} {
  return {
    weight_capacity: formatWeight(vehicle.max_weight),
    volume_capacity: formatVolume(vehicle.max_volume),
    dimensions: formatDimensions(vehicle.length, vehicle.width, vehicle.height),
  };
}

export function isValidLicensePlate(licensePlate: string): boolean {
  return (
    licensePlate.length >= VEHICLE_CONSTRAINTS.LICENSE_PLATE.MIN_LENGTH &&
    licensePlate.length <= VEHICLE_CONSTRAINTS.LICENSE_PLATE.MAX_LENGTH &&
    VEHICLE_CONSTRAINTS.LICENSE_PLATE.PATTERN.test(licensePlate.toUpperCase())
  );
}

export function validateVehicleData(data: VehicleFormData): VehicleValidationError[] {
  const errors: VehicleValidationError[] = [];

  // Name validation
  if (!data.name || data.name.trim().length < VEHICLE_CONSTRAINTS.NAME.MIN_LENGTH) {
    errors.push({
      field: 'name',
      message: `Name must be at least ${VEHICLE_CONSTRAINTS.NAME.MIN_LENGTH} characters`,
      code: 'NAME_TOO_SHORT',
    });
  }

  if (data.name && data.name.length > VEHICLE_CONSTRAINTS.NAME.MAX_LENGTH) {
    errors.push({
      field: 'name',
      message: `Name must be no more than ${VEHICLE_CONSTRAINTS.NAME.MAX_LENGTH} characters`,
      code: 'NAME_TOO_LONG',
    });
  }

  // License plate validation
  if (!data.license_plate || !isValidLicensePlate(data.license_plate)) {
    errors.push({
      field: 'license_plate',
      message: 'Invalid license plate format',
      code: 'INVALID_LICENSE_PLATE',
    });
  }

  // Fuel consumption validation
  const fuelConsumption = parseFloat(data.fuel_consumption);
  if (isNaN(fuelConsumption) || fuelConsumption < VEHICLE_CONSTRAINTS.FUEL_CONSUMPTION.MIN || fuelConsumption > VEHICLE_CONSTRAINTS.FUEL_CONSUMPTION.MAX) {
    errors.push({
      field: 'fuel_consumption',
      message: `Fuel consumption must be between ${VEHICLE_CONSTRAINTS.FUEL_CONSUMPTION.MIN} and ${VEHICLE_CONSTRAINTS.FUEL_CONSUMPTION.MAX} L/100km`,
      code: 'INVALID_FUEL_CONSUMPTION',
    });
  }

  // Weight validation
  const maxWeight = parseFloat(data.max_weight);
  if (isNaN(maxWeight) || maxWeight < VEHICLE_CONSTRAINTS.MAX_WEIGHT.MIN || maxWeight > VEHICLE_CONSTRAINTS.MAX_WEIGHT.MAX) {
    errors.push({
      field: 'max_weight',
      message: `Max weight must be between ${VEHICLE_CONSTRAINTS.MAX_WEIGHT.MIN} and ${VEHICLE_CONSTRAINTS.MAX_WEIGHT.MAX} kg`,
      code: 'INVALID_MAX_WEIGHT',
    });
  }

  // Volume validation
  const maxVolume = parseFloat(data.max_volume);
  if (isNaN(maxVolume) || maxVolume < VEHICLE_CONSTRAINTS.MAX_VOLUME.MIN || maxVolume > VEHICLE_CONSTRAINTS.MAX_VOLUME.MAX) {
    errors.push({
      field: 'max_volume',
      message: `Max volume must be between ${VEHICLE_CONSTRAINTS.MAX_VOLUME.MIN} and ${VEHICLE_CONSTRAINTS.MAX_VOLUME.MAX} m³`,
      code: 'INVALID_MAX_VOLUME',
    });
  }

  // Dimensions validation
  const length = parseFloat(data.length);
  const width = parseFloat(data.width);
  const height = parseFloat(data.height);

  if (isNaN(length) || length < VEHICLE_CONSTRAINTS.DIMENSIONS.MIN || length > VEHICLE_CONSTRAINTS.DIMENSIONS.MAX) {
    errors.push({
      field: 'length',
      message: `Length must be between ${VEHICLE_CONSTRAINTS.DIMENSIONS.MIN} and ${VEHICLE_CONSTRAINTS.DIMENSIONS.MAX} meters`,
      code: 'INVALID_LENGTH',
    });
  }

  if (isNaN(width) || width < VEHICLE_CONSTRAINTS.DIMENSIONS.MIN || width > VEHICLE_CONSTRAINTS.DIMENSIONS.MAX) {
    errors.push({
      field: 'width',
      message: `Width must be between ${VEHICLE_CONSTRAINTS.DIMENSIONS.MIN} and ${VEHICLE_CONSTRAINTS.DIMENSIONS.MAX} meters`,
      code: 'INVALID_WIDTH',
    });
  }

  if (isNaN(height) || height < VEHICLE_CONSTRAINTS.DIMENSIONS.MIN || height > VEHICLE_CONSTRAINTS.DIMENSIONS.MAX) {
    errors.push({
      field: 'height',
      message: `Height must be between ${VEHICLE_CONSTRAINTS.DIMENSIONS.MIN} and ${VEHICLE_CONSTRAINTS.DIMENSIONS.MAX} meters`,
      code: 'INVALID_HEIGHT',
    });
  }

  return errors;
}