import React, { useState, useEffect } from 'react';
import { vehicleService } from '../../services/vehicleService';
import {
  Vehicle,
  VehicleFormData,
  CreateVehicleRequest,
  UpdateVehicleRequest,
  FUEL_TYPES,
  FuelType,
  DEFAULT_VEHICLE,
  validateVehicleData,
  VehicleValidationError,
} from '../../types/vehicle';
import { XMarkIcon } from '@heroicons/react/24/outline';
import { toast } from 'react-hot-toast';
import LoadingSpinner from '../UI/LoadingSpinner';

interface VehicleFormProps {
  vehicle?: Vehicle | null;
  onSubmit: () => void;
  onCancel: () => void;
}

function VehicleForm({ vehicle, onSubmit, onCancel }: VehicleFormProps) {
  const [formData, setFormData] = useState<VehicleFormData>({
    ...DEFAULT_VEHICLE,
  } as VehicleFormData);
  
  const [errors, setErrors] = useState<VehicleValidationError[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isCheckingLicensePlate, setIsCheckingLicensePlate] = useState(false);
  const [licensePlateAvailable, setLicensePlateAvailable] = useState<boolean | null>(null);

  const isEditing = !!vehicle;

  // Initialize form data when vehicle prop changes
  useEffect(() => {
    if (vehicle) {
      setFormData({
        name: vehicle.name,
        license_plate: vehicle.license_plate,
        fuel_type: vehicle.fuel_type,
        fuel_consumption: vehicle.fuel_consumption.toString(),
        max_weight: vehicle.max_weight.toString(),
        max_volume: vehicle.max_volume.toString(),
        length: vehicle.length.toString(),
        width: vehicle.width.toString(),
        height: vehicle.height.toString(),
      });
    } else {
      setFormData({ ...DEFAULT_VEHICLE } as VehicleFormData);
    }
    setErrors([]);
    setLicensePlateAvailable(null);
  }, [vehicle]);

  // Check license plate availability when it changes
  useEffect(() => {
    const checkLicensePlate = async () => {
      if (!formData.license_plate || formData.license_plate.length < 6) {
        setLicensePlateAvailable(null);
        return;
      }

      // Don't check if it's the same as the current vehicle's license plate
      if (vehicle && formData.license_plate === vehicle.license_plate) {
        setLicensePlateAvailable(true);
        return;
      }

      try {
        setIsCheckingLicensePlate(true);
        const available = await vehicleService.checkLicensePlateAvailability(
          formData.license_plate,
          vehicle?.id
        );
        setLicensePlateAvailable(available);
      } catch (error) {
        console.error('Error checking license plate:', error);
        setLicensePlateAvailable(null);
      } finally {
        setIsCheckingLicensePlate(false);
      }
    };

    const timeoutId = setTimeout(checkLicensePlate, 500);
    return () => clearTimeout(timeoutId);
  }, [formData.license_plate, vehicle]);

  const handleInputChange = (field: keyof VehicleFormData, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    
    // Clear field-specific errors
    setErrors(prev => prev.filter(error => error.field !== field));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate form data
    const validationErrors = validateVehicleData(formData);
    
    // Check license plate availability
    if (!isEditing && licensePlateAvailable === false) {
      validationErrors.push({
        field: 'license_plate',
        message: 'License plate is already in use',
        code: 'LICENSE_PLATE_EXISTS',
      });
    }
    
    if (validationErrors.length > 0) {
      setErrors(validationErrors);
      return;
    }

    try {
      setIsSubmitting(true);
      
      const requestData = {
        name: formData.name.trim(),
        license_plate: formData.license_plate.trim().toUpperCase(),
        fuel_type: formData.fuel_type,
        fuel_consumption: parseFloat(formData.fuel_consumption),
        max_weight: parseFloat(formData.max_weight),
        max_volume: parseFloat(formData.max_volume),
        length: parseFloat(formData.length),
        width: parseFloat(formData.width),
        height: parseFloat(formData.height),
      };

      if (isEditing) {
        await vehicleService.updateVehicle(vehicle!.id, requestData as UpdateVehicleRequest);
        toast.success('Vehicle updated successfully');
      } else {
        await vehicleService.createVehicle(requestData as CreateVehicleRequest);
        toast.success('Vehicle created successfully');
      }
      
      onSubmit();
    } catch (error: any) {
      console.error('Error saving vehicle:', error);
      
      // Handle validation errors from server
      if (error.response?.status === 422) {
        const serverErrors = error.response.data.detail || [];
        if (Array.isArray(serverErrors)) {
          setErrors(serverErrors.map((err: any) => ({
            field: err.loc?.[1] || 'general',
            message: err.msg || 'Validation error',
            code: err.type,
          })));
        }
      } else {
        toast.error(isEditing ? 'Failed to update vehicle' : 'Failed to create vehicle');
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const getFieldError = (field: string) => {
    return errors.find(error => error.field === field);
  };

  const renderFieldError = (field: string) => {
    const error = getFieldError(field);
    if (!error) return null;
    
    return (
      <p className="mt-1 text-sm text-red-600 dark:text-red-400">
        {error.message}
      </p>
    );
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      <div className="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        {/* Background overlay */}
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={onCancel} />

        {/* Modal panel */}
        <div className="inline-block align-bottom bg-white dark:bg-gray-800 rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full">
          {/* Header */}
          <div className="bg-white dark:bg-gray-800 px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg leading-6 font-medium text-gray-900 dark:text-white">
                {isEditing ? 'Edit Vehicle' : 'Add New Vehicle'}
              </h3>
              <button
                onClick={onCancel}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                <XMarkIcon className="h-6 w-6" />
              </button>
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Basic Information */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="form-label">
                    Vehicle Name *
                  </label>
                  <input
                    type="text"
                    value={formData.name}
                    onChange={(e) => handleInputChange('name', e.target.value)}
                    className={`form-input ${getFieldError('name') ? 'border-red-500' : ''}`}
                    placeholder="e.g., Truck-001"
                    disabled={isSubmitting}
                  />
                  {renderFieldError('name')}
                </div>

                <div>
                  <label className="form-label">
                    License Plate *
                  </label>
                  <div className="relative">
                    <input
                      type="text"
                      value={formData.license_plate}
                      onChange={(e) => handleInputChange('license_plate', e.target.value.toUpperCase())}
                      className={`form-input ${getFieldError('license_plate') ? 'border-red-500' : ''}`}
                      placeholder="e.g., ABC-123"
                      disabled={isSubmitting}
                    />
                    {isCheckingLicensePlate && (
                      <div className="absolute right-3 top-2">
                        <LoadingSpinner size="sm" />
                      </div>
                    )}
                    {!isCheckingLicensePlate && licensePlateAvailable !== null && (
                      <div className="absolute right-3 top-2">
                        {licensePlateAvailable ? (
                          <svg className="h-5 w-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                          </svg>
                        ) : (
                          <svg className="h-5 w-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                          </svg>
                        )}
                      </div>
                    )}
                  </div>
                  {renderFieldError('license_plate')}
                </div>
              </div>

              {/* Fuel Information */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="form-label">
                    Fuel Type *
                  </label>
                  <select
                    value={formData.fuel_type}
                    onChange={(e) => handleInputChange('fuel_type', e.target.value)}
                    className={`form-input ${getFieldError('fuel_type') ? 'border-red-500' : ''}`}
                    disabled={isSubmitting}
                  >
                    {Object.entries(FUEL_TYPES).map(([value, label]) => (
                      <option key={value} value={value}>
                        {label}
                      </option>
                    ))}
                  </select>
                  {renderFieldError('fuel_type')}
                </div>

                <div>
                  <label className="form-label">
                    Fuel Consumption (L/100km) *
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    min="5"
                    max="100"
                    value={formData.fuel_consumption}
                    onChange={(e) => handleInputChange('fuel_consumption', e.target.value)}
                    className={`form-input ${getFieldError('fuel_consumption') ? 'border-red-500' : ''}`}
                    placeholder="25.0"
                    disabled={isSubmitting}
                  />
                  {renderFieldError('fuel_consumption')}
                </div>
              </div>

              {/* Capacity */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="form-label">
                    Max Weight (kg) *
                  </label>
                  <input
                    type="number"
                    min="500"
                    max="50000"
                    value={formData.max_weight}
                    onChange={(e) => handleInputChange('max_weight', e.target.value)}
                    className={`form-input ${getFieldError('max_weight') ? 'border-red-500' : ''}`}
                    placeholder="3500"
                    disabled={isSubmitting}
                  />
                  {renderFieldError('max_weight')}
                </div>

                <div>
                  <label className="form-label">
                    Max Volume (m³) *
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    min="1"
                    max="200"
                    value={formData.max_volume}
                    onChange={(e) => handleInputChange('max_volume', e.target.value)}
                    className={`form-input ${getFieldError('max_volume') ? 'border-red-500' : ''}`}
                    placeholder="15.0"
                    disabled={isSubmitting}
                  />
                  {renderFieldError('max_volume')}
                </div>
              </div>

              {/* Dimensions */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="form-label">
                    Length (m) *
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    min="1"
                    max="25"
                    value={formData.length}
                    onChange={(e) => handleInputChange('length', e.target.value)}
                    className={`form-input ${getFieldError('length') ? 'border-red-500' : ''}`}
                    placeholder="6.0"
                    disabled={isSubmitting}
                  />
                  {renderFieldError('length')}
                </div>

                <div>
                  <label className="form-label">
                    Width (m) *
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    min="1"
                    max="25"
                    value={formData.width}
                    onChange={(e) => handleInputChange('width', e.target.value)}
                    className={`form-input ${getFieldError('width') ? 'border-red-500' : ''}`}
                    placeholder="2.5"
                    disabled={isSubmitting}
                  />
                  {renderFieldError('width')}
                </div>

                <div>
                  <label className="form-label">
                    Height (m) *
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    min="1"
                    max="25"
                    value={formData.height}
                    onChange={(e) => handleInputChange('height', e.target.value)}
                    className={`form-input ${getFieldError('height') ? 'border-red-500' : ''}`}
                    placeholder="3.0"
                    disabled={isSubmitting}
                  />
                  {renderFieldError('height')}
                </div>
              </div>

              {/* General errors */}
              {errors.filter(error => error.field === 'general').map((error, index) => (
                <div key={index} className="alert alert-error">
                  {error.message}
                </div>
              ))}
            </form>
          </div>

          {/* Footer */}
          <div className="bg-gray-50 dark:bg-gray-700 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
            <button
              type="submit"
              onClick={handleSubmit}
              disabled={isSubmitting || licensePlateAvailable === false}
              className="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-blue-600 text-base font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:ml-3 sm:w-auto sm:text-sm disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {isSubmitting ? (
                <>
                  <LoadingSpinner size="sm" color="white" />
                  <span className="ml-2">
                    {isEditing ? 'Updating...' : 'Creating...'}
                  </span>
                </>
              ) : (
                isEditing ? 'Update Vehicle' : 'Create Vehicle'
              )}
            </button>
            <button
              type="button"
              onClick={onCancel}
              disabled={isSubmitting}
              className="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 dark:border-gray-600 shadow-sm px-4 py-2 bg-white dark:bg-gray-800 text-base font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Cancel
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default VehicleForm;