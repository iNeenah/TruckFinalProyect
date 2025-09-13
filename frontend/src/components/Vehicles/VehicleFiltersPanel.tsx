import React, { useState, useEffect } from 'react';
import { VehicleFilters, FUEL_TYPES, FuelType } from '../../types/vehicle';
import { XMarkIcon, MagnifyingGlassIcon } from '@heroicons/react/24/outline';

interface VehicleFiltersPanelProps {
  filters: VehicleFilters;
  onFiltersChange: (filters: VehicleFilters) => void;
  onClose: () => void;
}

function VehicleFiltersPanel({ filters, onFiltersChange, onClose }: VehicleFiltersPanelProps) {
  const [localFilters, setLocalFilters] = useState<VehicleFilters>(filters);

  useEffect(() => {
    setLocalFilters(filters);
  }, [filters]);

  const handleFilterChange = (key: keyof VehicleFilters, value: any) => {
    const newFilters = { ...localFilters, [key]: value };
    setLocalFilters(newFilters);
  };

  const handleApplyFilters = () => {
    onFiltersChange(localFilters);
    onClose();
  };

  const handleClearFilters = () => {
    const clearedFilters = {};
    setLocalFilters(clearedFilters);
    onFiltersChange(clearedFilters);
    onClose();
  };

  const hasActiveFilters = Object.keys(localFilters).some(key => {
    const value = localFilters[key as keyof VehicleFilters];
    return value !== undefined && value !== '' && value !== null;
  });

  return (
    <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-medium text-gray-900 dark:text-white">
          Filter Vehicles
        </h3>
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
        >
          <XMarkIcon className="h-5 w-5" />
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        {/* Search */}
        <div>
          <label className="form-label">
            Search
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              value={localFilters.search || ''}
              onChange={(e) => handleFilterChange('search', e.target.value)}
              className="form-input pl-10"
              placeholder="Search by name or license plate..."
            />
          </div>
        </div>

        {/* Fuel Type */}
        <div>
          <label className="form-label">
            Fuel Type
          </label>
          <select
            value={localFilters.fuel_type || ''}
            onChange={(e) => handleFilterChange('fuel_type', e.target.value || undefined)}
            className="form-input"
          >
            <option value="">All Fuel Types</option>
            {Object.entries(FUEL_TYPES).map(([value, label]) => (
              <option key={value} value={value}>
                {label}
              </option>
            ))}
          </select>
        </div>

        {/* Status */}
        <div>
          <label className="form-label">
            Status
          </label>
          <select
            value={localFilters.is_active !== undefined ? localFilters.is_active.toString() : ''}
            onChange={(e) => {
              const value = e.target.value;
              handleFilterChange('is_active', value === '' ? undefined : value === 'true');
            }}
            className="form-input"
          >
            <option value="">All Statuses</option>
            <option value="true">Active</option>
            <option value="false">Inactive</option>
          </select>
        </div>

        {/* Company (for admin users) */}
        <div>
          <label className="form-label">
            Company
          </label>
          <select
            value={localFilters.company_id || ''}
            onChange={(e) => handleFilterChange('company_id', e.target.value || undefined)}
            className="form-input"
          >
            <option value="">All Companies</option>
            {/* Company options would be loaded from API */}
          </select>
        </div>
      </div>

      {/* Action buttons */}
      <div className="flex items-center justify-between">
        <div className="text-sm text-gray-500 dark:text-gray-400">
          {hasActiveFilters && (
            <span>
              {Object.keys(localFilters).filter(key => {
                const value = localFilters[key as keyof VehicleFilters];
                return value !== undefined && value !== '' && value !== null;
              }).length} filter(s) active
            </span>
          )}
        </div>
        
        <div className="flex space-x-3">
          <button
            onClick={handleClearFilters}
            className="btn btn-secondary"
            disabled={!hasActiveFilters}
          >
            Clear All
          </button>
          <button
            onClick={handleApplyFilters}
            className="btn btn-primary"
          >
            Apply Filters
          </button>
        </div>
      </div>
    </div>
  );
}

export default VehicleFiltersPanel;