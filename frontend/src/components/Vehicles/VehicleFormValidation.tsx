import React from 'react';
import {
  VehicleFormData,
  VehicleValidationError,
  validateVehicleData,
  isValidLicensePlate,
  VEHICLE_CONSTRAINTS,
} from '../../types/vehicle';
import {
  CheckCircleIcon,
  XCircleIcon,
  ExclamationTriangleIcon,
} from '@heroicons/react/24/outline';

interface VehicleFormValidationProps {
  formData: VehicleFormData;
  errors: VehicleValidationError[];
  licensePlateAvailable?: boolean | null;
  isCheckingLicensePlate?: boolean;
}

interface ValidationRule {
  field: keyof VehicleFormData;
  label: string;
  isValid: boolean;
  message?: string;
  severity: 'error' | 'warning' | 'success';
}

function VehicleFormValidation({
  formData,
  errors,
  licensePlateAvailable,
  isCheckingLicensePlate,
}: VehicleFormValidationProps) {
  const getValidationRules = (): ValidationRule[] => {
    const rules: ValidationRule[] = [];

    // Name validation
    const nameLength = formData.name?.trim().length || 0;
    rules.push({
      field: 'name',
      label: 'Vehicle name',
      isValid: nameLength >= VEHICLE_CONSTRAINTS.NAME.MIN_LENGTH && nameLength <= VEHICLE_CONSTRAINTS.NAME.MAX_LENGTH,
      message: nameLength === 0 
        ? 'Name is required'
        : nameLength < VEHICLE_CONSTRAINTS.NAME.MIN_LENGTH
        ? `Name must be at least ${VEHICLE_CONSTRAINTS.NAME.MIN_LENGTH} characters`
        : nameLength > VEHICLE_CONSTRAINTS.NAME.MAX_LENGTH
        ? `Name must be no more than ${VEHICLE_CONSTRAINTS.NAME.MAX_LENGTH} characters`
        : undefined,
      severity: nameLength === 0 || nameLength < VEHICLE_CONSTRAINTS.NAME.MIN_LENGTH || nameLength > VEHICLE_CONSTRAINTS.NAME.MAX_LENGTH ? 'error' : 'success',
    });

    // License plate validation
    const licensePlateValid = formData.license_plate && isValidLicensePlate(formData.license_plate);
    rules.push({
      field: 'license_plate',
      label: 'License plate format',
      isValid: !!licensePlateValid,
      message: !formData.license_plate 
        ? 'License plate is required'
        : !licensePlateValid
        ? 'Invalid license plate format'
        : undefined,
      severity: !licensePlateValid ? 'error' : 'success',
    });

    // License plate availability
    if (formData.license_plate && licensePlateValid) {
      rules.push({
        field: 'license_plate',
        label: 'License plate availability',
        isValid: licensePlateAvailable === true,
        message: isCheckingLicensePlate
          ? 'Checking availability...'
          : licensePlateAvailable === false
          ? 'License plate is already in use'
          : licensePlateAvailable === true
          ? 'License plate is available'
          : 'Availability unknown',
        severity: isCheckingLicensePlate
          ? 'warning'
          : licensePlateAvailable === false
          ? 'error'
          : licensePlateAvailable === true
          ? 'success'
          : 'warning',
      });
    }

    // Fuel consumption validation
    const fuelConsumption = parseFloat(formData.fuel_consumption || '0');
    const fuelConsumptionValid = !isNaN(fuelConsumption) && 
      fuelConsumption >= VEHICLE_CONSTRAINTS.FUEL_CONSUMPTION.MIN && 
      fuelConsumption <= VEHICLE_CONSTRAINTS.FUEL_CONSUMPTION.MAX;
    rules.push({
      field: 'fuel_consumption',
      label: 'Fuel consumption',
      isValid: fuelConsumptionValid,
      message: !formData.fuel_consumption
        ? 'Fuel consumption is required'
        : !fuelConsumptionValid
        ? `Must be between ${VEHICLE_CONSTRAINTS.FUEL_CONSUMPTION.MIN} and ${VEHICLE_CONSTRAINTS.FUEL_CONSUMPTION.MAX} L/100km`
        : undefined,
      severity: !fuelConsumptionValid ? 'error' : 'success',
    });

    // Weight validation
    const maxWeight = parseFloat(formData.max_weight || '0');
    const weightValid = !isNaN(maxWeight) && 
      maxWeight >= VEHICLE_CONSTRAINTS.MAX_WEIGHT.MIN && 
      maxWeight <= VEHICLE_CONSTRAINTS.MAX_WEIGHT.MAX;
    rules.push({
      field: 'max_weight',
      label: 'Maximum weight',
      isValid: weightValid,
      message: !formData.max_weight
        ? 'Maximum weight is required'
        : !weightValid
        ? `Must be between ${VEHICLE_CONSTRAINTS.MAX_WEIGHT.MIN} and ${VEHICLE_CONSTRAINTS.MAX_WEIGHT.MAX} kg`
        : undefined,
      severity: !weightValid ? 'error' : 'success',
    });

    // Volume validation
    const maxVolume = parseFloat(formData.max_volume || '0');
    const volumeValid = !isNaN(maxVolume) && 
      maxVolume >= VEHICLE_CONSTRAINTS.MAX_VOLUME.MIN && 
      maxVolume <= VEHICLE_CONSTRAINTS.MAX_VOLUME.MAX;
    rules.push({
      field: 'max_volume',
      label: 'Maximum volume',
      isValid: volumeValid,
      message: !formData.max_volume
        ? 'Maximum volume is required'
        : !volumeValid
        ? `Must be between ${VEHICLE_CONSTRAINTS.MAX_VOLUME.MIN} and ${VEHICLE_CONSTRAINTS.MAX_VOLUME.MAX} m³`
        : undefined,
      severity: !volumeValid ? 'error' : 'success',
    });

    // Dimensions validation
    const length = parseFloat(formData.length || '0');
    const width = parseFloat(formData.width || '0');
    const height = parseFloat(formData.height || '0');

    const lengthValid = !isNaN(length) && 
      length >= VEHICLE_CONSTRAINTS.DIMENSIONS.MIN && 
      length <= VEHICLE_CONSTRAINTS.DIMENSIONS.MAX;
    const widthValid = !isNaN(width) && 
      width >= VEHICLE_CONSTRAINTS.DIMENSIONS.MIN && 
      width <= VEHICLE_CONSTRAINTS.DIMENSIONS.MAX;
    const heightValid = !isNaN(height) && 
      height >= VEHICLE_CONSTRAINTS.DIMENSIONS.MIN && 
      height <= VEHICLE_CONSTRAINTS.DIMENSIONS.MAX;

    rules.push({
      field: 'length',
      label: 'Vehicle dimensions',
      isValid: lengthValid && widthValid && heightValid,
      message: !lengthValid || !widthValid || !heightValid
        ? `All dimensions must be between ${VEHICLE_CONSTRAINTS.DIMENSIONS.MIN} and ${VEHICLE_CONSTRAINTS.DIMENSIONS.MAX} meters`
        : undefined,
      severity: (!lengthValid || !widthValid || !heightValid) ? 'error' : 'success',
    });

    return rules;
  };

  const validationRules = getValidationRules();
  const hasErrors = validationRules.some(rule => rule.severity === 'error');
  const hasWarnings = validationRules.some(rule => rule.severity === 'warning');

  const getIcon = (severity: 'error' | 'warning' | 'success') => {
    switch (severity) {
      case 'error':
        return <XCircleIcon className="h-4 w-4 text-red-500" />;
      case 'warning':
        return <ExclamationTriangleIcon className="h-4 w-4 text-yellow-500" />;
      case 'success':
        return <CheckCircleIcon className="h-4 w-4 text-green-500" />;
    }
  };

  const getTextColor = (severity: 'error' | 'warning' | 'success') => {
    switch (severity) {
      case 'error':
        return 'text-red-700 dark:text-red-300';
      case 'warning':
        return 'text-yellow-700 dark:text-yellow-300';
      case 'success':
        return 'text-green-700 dark:text-green-300';
    }
  };

  const getBgColor = (severity: 'error' | 'warning' | 'success') => {
    switch (severity) {
      case 'error':
        return 'bg-red-50 dark:bg-red-900';
      case 'warning':
        return 'bg-yellow-50 dark:bg-yellow-900';
      case 'success':
        return 'bg-green-50 dark:bg-green-900';
    }
  };

  return (
    <div className="space-y-3">
      {/* Overall validation status */}
      <div className={`p-3 rounded-md ${
        hasErrors 
          ? 'bg-red-50 dark:bg-red-900' 
          : hasWarnings 
          ? 'bg-yellow-50 dark:bg-yellow-900' 
          : 'bg-green-50 dark:bg-green-900'
      }`}>
        <div className="flex items-center">
          {hasErrors ? (
            <XCircleIcon className="h-5 w-5 text-red-500 mr-2" />
          ) : hasWarnings ? (
            <ExclamationTriangleIcon className="h-5 w-5 text-yellow-500 mr-2" />
          ) : (
            <CheckCircleIcon className="h-5 w-5 text-green-500 mr-2" />
          )}
          <span className={`text-sm font-medium ${
            hasErrors 
              ? 'text-red-800 dark:text-red-200' 
              : hasWarnings 
              ? 'text-yellow-800 dark:text-yellow-200' 
              : 'text-green-800 dark:text-green-200'
          }`}>
            {hasErrors 
              ? 'Please fix the errors below' 
              : hasWarnings 
              ? 'Please review the warnings below' 
              : 'All validations passed'}
          </span>
        </div>
      </div>

      {/* Individual validation rules */}
      <div className="space-y-2">
        {validationRules
          .filter(rule => rule.severity === 'error' || rule.message)
          .map((rule, index) => (
            <div
              key={`${rule.field}-${index}`}
              className={`flex items-start p-2 rounded-md ${getBgColor(rule.severity)}`}
            >
              <div className="flex-shrink-0 mt-0.5">
                {getIcon(rule.severity)}
              </div>
              <div className="ml-2 flex-1">
                <p className={`text-sm font-medium ${getTextColor(rule.severity)}`}>
                  {rule.label}
                </p>
                {rule.message && (
                  <p className={`text-xs mt-1 ${getTextColor(rule.severity)} opacity-75`}>
                    {rule.message}
                  </p>
                )}
              </div>
            </div>
          ))}
      </div>

      {/* Server-side errors */}
      {errors.length > 0 && (
        <div className="space-y-2">
          <h4 className="text-sm font-medium text-red-800 dark:text-red-200">
            Server Validation Errors:
          </h4>
          {errors.map((error, index) => (
            <div
              key={index}
              className="flex items-start p-2 rounded-md bg-red-50 dark:bg-red-900"
            >
              <XCircleIcon className="h-4 w-4 text-red-500 mt-0.5 flex-shrink-0" />
              <div className="ml-2">
                <p className="text-sm text-red-700 dark:text-red-300">
                  <span className="font-medium capitalize">{error.field}:</span> {error.message}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default VehicleFormValidation;