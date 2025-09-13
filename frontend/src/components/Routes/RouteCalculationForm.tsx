import React, { useState } from 'react';
import { Location } from '../../types/map';
import { Vehicle } from '../../types/vehicle';
import LocationInput from '../Map/LocationInput';
import VehicleSelector from './VehicleSelector';
import LoadingSpinner from '../UI/LoadingSpinner';
import {
  MapPinIcon,
  FlagIcon,
  PlusIcon,
  XMarkIcon,
  CalculatorIcon,
} from '@heroicons/react/24/outline';

interface RouteCalculationFormProps {
  origin: Location | null;
  destination: Location | null;
  waypoints: Location[];
  selectedVehicle: Vehicle | null;
  onOriginChange: (location: Location | null) => void;
  onDestinationChange: (location: Location | null) => void;
  onAddWaypoint: (location: Location) => void;
  onRemoveWaypoint: (index: number) => void;
  onVehicleSelect: (vehicle: Vehicle | null) => void;
  onCalculate: () => void;
  isCalculating: boolean;
  canCalculate: boolean;
}

function RouteCalculationForm({
  origin,
  destination,
  waypoints,
  selectedVehicle,
  onOriginChange,
  onDestinationChange,
  onAddWaypoint,
  onRemoveWaypoint,
  onVehicleSelect,
  onCalculate,
  isCalculating,
  canCalculate,
}: RouteCalculationFormProps) {
  const [newWaypoint, setNewWaypoint] = useState<Location | null>(null);
  const [showWaypointInput, setShowWaypointInput] = useState(false);

  const handleAddWaypoint = () => {
    if (newWaypoint) {
      onAddWaypoint(newWaypoint);
      setNewWaypoint(null);
      setShowWaypointInput(false);
    }
  };

  const handleCancelWaypoint = () => {
    setNewWaypoint(null);
    setShowWaypointInput(false);
  };

  const proximity: [number, number] | undefined = origin 
    ? origin.coordinates 
    : destination 
    ? destination.coordinates 
    : [-55.9, -27.4]; // Default to Posadas, Misiones

  return (
    <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
      <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
        Route Planning
      </h2>

      <div className="space-y-4">
        {/* Origin */}
        <div>
          <div className="flex items-center mb-2">
            <div className="w-3 h-3 rounded-full bg-green-500 mr-2"></div>
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Origin
            </label>
          </div>
          <LocationInput
            value={origin}
            onChange={onOriginChange}
            placeholder="Enter starting location..."
            proximity={proximity}
            disabled={isCalculating}
          />
        </div>

        {/* Waypoints */}
        {waypoints.map((waypoint, index) => (
          <div key={index}>
            <div className="flex items-center justify-between mb-2">
              <div className="flex items-center">
                <div className="w-3 h-3 rounded-full bg-blue-500 mr-2"></div>
                <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                  Waypoint {index + 1}
                </label>
              </div>
              <button
                type="button"
                onClick={() => onRemoveWaypoint(index)}
                className="text-red-500 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300"
                disabled={isCalculating}
              >
                <XMarkIcon className="h-4 w-4" />
              </button>
            </div>
            <div className="bg-gray-50 dark:bg-gray-700 p-3 rounded-md">
              <div className="flex items-center">
                <MapPinIcon className="h-4 w-4 text-blue-500 mr-2" />
                <div>
                  <p className="text-sm font-medium text-gray-900 dark:text-white">
                    {waypoint.name}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {waypoint.address}
                  </p>
                </div>
              </div>
            </div>
          </div>
        ))}

        {/* Add Waypoint */}
        {showWaypointInput ? (
          <div>
            <div className="flex items-center mb-2">
              <div className="w-3 h-3 rounded-full bg-blue-500 mr-2"></div>
              <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                New Waypoint
              </label>
            </div>
            <LocationInput
              value={newWaypoint}
              onChange={setNewWaypoint}
              placeholder="Enter waypoint location..."
              proximity={proximity}
              disabled={isCalculating}
            />
            <div className="flex space-x-2 mt-2">
              <button
                type="button"
                onClick={handleAddWaypoint}
                disabled={!newWaypoint || isCalculating}
                className="btn btn-primary btn-sm"
              >
                Add
              </button>
              <button
                type="button"
                onClick={handleCancelWaypoint}
                disabled={isCalculating}
                className="btn btn-secondary btn-sm"
              >
                Cancel
              </button>
            </div>
          </div>
        ) : (
          <button
            type="button"
            onClick={() => setShowWaypointInput(true)}
            disabled={isCalculating || waypoints.length >= 5}
            className="w-full flex items-center justify-center px-3 py-2 border-2 border-dashed border-gray-300 dark:border-gray-600 rounded-md text-sm text-gray-600 dark:text-gray-400 hover:border-gray-400 dark:hover:border-gray-500 hover:text-gray-700 dark:hover:text-gray-300 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <PlusIcon className="h-4 w-4 mr-2" />
            Add Waypoint {waypoints.length >= 5 && '(Max 5)'}
          </button>
        )}

        {/* Destination */}
        <div>
          <div className="flex items-center mb-2">
            <div className="w-3 h-3 rounded-full bg-red-500 mr-2"></div>
            <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Destination
            </label>
          </div>
          <LocationInput
            value={destination}
            onChange={onDestinationChange}
            placeholder="Enter destination..."
            proximity={proximity}
            disabled={isCalculating}
          />
        </div>

        {/* Vehicle Selection */}
        <div>
          <label className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 block">
            Vehicle
          </label>
          <VehicleSelector
            selectedVehicle={selectedVehicle}
            onVehicleSelect={onVehicleSelect}
            disabled={isCalculating}
          />
        </div>

        {/* Route Preferences */}
        <div className="border-t border-gray-200 dark:border-gray-700 pt-4">
          <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
            Route Preferences
          </h3>
          <div className="space-y-2">
            <label className="flex items-center">
              <input
                type="checkbox"
                className="rounded border-gray-300 dark:border-gray-600 text-blue-600 focus:ring-blue-500"
                disabled={isCalculating}
              />
              <span className="ml-2 text-sm text-gray-600 dark:text-gray-400">
                Avoid tolls when possible
              </span>
            </label>
            <label className="flex items-center">
              <input
                type="checkbox"
                className="rounded border-gray-300 dark:border-gray-600 text-blue-600 focus:ring-blue-500"
                disabled={isCalculating}
              />
              <span className="ml-2 text-sm text-gray-600 dark:text-gray-400">
                Prefer highways
              </span>
            </label>
          </div>
        </div>

        {/* Calculate Button */}
        <button
          type="button"
          onClick={onCalculate}
          disabled={!canCalculate || isCalculating}
          className="w-full btn btn-primary"
        >
          {isCalculating ? (
            <>
              <LoadingSpinner size="sm" color="white" />
              <span className="ml-2">Calculating Routes...</span>
            </>
          ) : (
            <>
              <CalculatorIcon className="h-5 w-5 mr-2" />
              Calculate Routes
            </>
          )}
        </button>

        {/* Route Summary */}
        {origin && destination && (
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-3">
            <div className="flex items-center">
              <FlagIcon className="h-4 w-4 text-blue-600 dark:text-blue-400 mr-2" />
              <span className="text-sm font-medium text-blue-800 dark:text-blue-200">
                Route Summary
              </span>
            </div>
            <div className="mt-2 text-xs text-blue-700 dark:text-blue-300">
              <p>From: {origin.name}</p>
              {waypoints.length > 0 && (
                <p>Via: {waypoints.map(wp => wp.name).join(', ')}</p>
              )}
              <p>To: {destination.name}</p>
              {selectedVehicle && (
                <p>Vehicle: {selectedVehicle.name} ({selectedVehicle.license_plate})</p>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default RouteCalculationForm;