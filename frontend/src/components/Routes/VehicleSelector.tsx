import React, { useState, useEffect } from 'react';
import { Vehicle, formatFuelType, formatFuelConsumption } from '../../types/vehicle';
import { useVehicles } from '../../hooks/useVehicles';
import LoadingSpinner from '../UI/LoadingSpinner';
import {
  TruckIcon,
  ChevronUpDownIcon,
  CheckIcon,
} from '@heroicons/react/24/outline';

interface VehicleSelectorProps {
  selectedVehicle: Vehicle | null;
  onVehicleSelect: (vehicle: Vehicle | null) => void;
  disabled?: boolean;
  className?: string;
}

function VehicleSelector({
  selectedVehicle,
  onVehicleSelect,
  disabled = false,
  className = '',
}: VehicleSelectorProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  // Fetch vehicles
  const { data: vehiclesData, isLoading, error } = useVehicles(
    { is_active: true }, // Only show active vehicles
    1,
    50 // Get more vehicles for selection
  );

  const vehicles = vehiclesData?.vehicles || [];

  // Filter vehicles based on search query
  const filteredVehicles = vehicles.filter(vehicle =>
    vehicle.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    vehicle.license_plate.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleVehicleSelect = (vehicle: Vehicle) => {
    onVehicleSelect(vehicle);
    setIsOpen(false);
    setSearchQuery('');
  };

  const handleClear = () => {
    onVehicleSelect(null);
    setIsOpen(false);
    setSearchQuery('');
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as Element;
      if (!target.closest('.vehicle-selector')) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isOpen]);

  if (isLoading) {
    return (
      <div className={`relative ${className}`}>
        <div className="form-input flex items-center justify-center">
          <LoadingSpinner size="sm" />
          <span className="ml-2 text-sm text-gray-500">Loading vehicles...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`relative ${className}`}>
        <div className="form-input text-red-500 text-sm">
          Error loading vehicles
        </div>
      </div>
    );
  }

  if (vehicles.length === 0) {
    return (
      <div className={`relative ${className}`}>
        <div className="form-input text-gray-500 text-sm">
          No active vehicles available
        </div>
      </div>
    );
  }

  return (
    <div className={`relative vehicle-selector ${className}`}>
      {/* Selected vehicle display / dropdown trigger */}
      <button
        type="button"
        onClick={() => !disabled && setIsOpen(!isOpen)}
        disabled={disabled}
        className={`form-input w-full flex items-center justify-between ${
          disabled ? 'cursor-not-allowed' : 'cursor-pointer'
        }`}
      >
        {selectedVehicle ? (
          <div className="flex items-center">
            <TruckIcon className="h-5 w-5 text-gray-400 mr-2" />
            <div className="text-left">
              <p className="text-sm font-medium text-gray-900 dark:text-white">
                {selectedVehicle.name}
              </p>
              <p className="text-xs text-gray-500 dark:text-gray-400">
                {selectedVehicle.license_plate} • {formatFuelType(selectedVehicle.fuel_type)}
              </p>
            </div>
          </div>
        ) : (
          <div className="flex items-center">
            <TruckIcon className="h-5 w-5 text-gray-400 mr-2" />
            <span className="text-gray-500 dark:text-gray-400">Select a vehicle...</span>
          </div>
        )}
        <ChevronUpDownIcon className="h-5 w-5 text-gray-400" />
      </button>

      {/* Dropdown */}
      {isOpen && (
        <div className="absolute z-50 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md shadow-lg max-h-80 overflow-hidden">
          {/* Search input */}
          <div className="p-3 border-b border-gray-200 dark:border-gray-700">
            <input
              type="text"
              placeholder="Search vehicles..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              autoFocus
            />
          </div>

          {/* Vehicle list */}
          <div className="max-h-60 overflow-y-auto">
            {/* Clear selection option */}
            {selectedVehicle && (
              <button
                type="button"
                onClick={handleClear}
                className="w-full px-4 py-3 text-left hover:bg-gray-50 dark:hover:bg-gray-700 focus:bg-gray-50 dark:focus:bg-gray-700 focus:outline-none border-b border-gray-200 dark:border-gray-700"
              >
                <div className="flex items-center">
                  <div className="w-5 h-5 mr-3"></div>
                  <span className="text-sm text-gray-500 dark:text-gray-400 italic">
                    Clear selection
                  </span>
                </div>
              </button>
            )}

            {filteredVehicles.length > 0 ? (
              filteredVehicles.map((vehicle) => (
                <button
                  key={vehicle.id}
                  type="button"
                  onClick={() => handleVehicleSelect(vehicle)}
                  className="w-full px-4 py-3 text-left hover:bg-gray-50 dark:hover:bg-gray-700 focus:bg-gray-50 dark:focus:bg-gray-700 focus:outline-none"
                >
                  <div className="flex items-center">
                    <div className="w-5 h-5 mr-3 flex items-center justify-center">
                      {selectedVehicle?.id === vehicle.id && (
                        <CheckIcon className="h-4 w-4 text-blue-600 dark:text-blue-400" />
                      )}
                    </div>
                    <TruckIcon className="h-5 w-5 text-gray-400 mr-3" />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center justify-between">
                        <p className="text-sm font-medium text-gray-900 dark:text-white truncate">
                          {vehicle.name}
                        </p>
                        <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200">
                          {vehicle.license_plate}
                        </span>
                      </div>
                      <div className="flex items-center justify-between mt-1">
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          {formatFuelType(vehicle.fuel_type)}
                        </p>
                        <p className="text-xs text-gray-500 dark:text-gray-400">
                          {formatFuelConsumption(vehicle.fuel_consumption)}
                        </p>
                      </div>
                    </div>
                  </div>
                </button>
              ))
            ) : (
              <div className="px-4 py-3 text-sm text-gray-500 dark:text-gray-400 text-center">
                {searchQuery ? `No vehicles found for "${searchQuery}"` : 'No vehicles available'}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default VehicleSelector;