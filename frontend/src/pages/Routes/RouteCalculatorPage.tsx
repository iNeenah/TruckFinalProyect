import React, { useState, useCallback } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import RouteCalculationForm from '../../components/Routes/RouteCalculationForm';
import RouteResultsDisplay from '../../components/Routes/RouteResultsDisplay';
import RouteMap from '../../components/Map/RouteMap';
import { useLocationManagement, useRouteVisualization } from '../../hooks/useMap';
import { useRouteCalculation } from '../../hooks/useRoutes';
import {
  Location,
  RouteFeature,
  TollPoint,
  FuelStation,
} from '../../types/map';
import { Vehicle } from '../../types/vehicle';
import { toast } from 'react-hot-toast';

function RouteCalculatorPage() {
  const { user } = useAuth();
  const [selectedVehicle, setSelectedVehicle] = useState<Vehicle | null>(null);
  const [isCalculating, setIsCalculating] = useState(false);
  const [routes, setRoutes] = useState<RouteFeature[]>([]);
  const [tollPoints, setTollPoints] = useState<TollPoint[]>([]);
  const [fuelStations, setFuelStations] = useState<FuelStation[]>([]);
  const [calculationError, setCalculationError] = useState<string | null>(null);

  // Location management
  const {
    origin,
    destination,
    waypoints,
    updateOrigin,
    updateDestination,
    addWaypoint,
    removeWaypoint,
    clearAll,
    isValidRoute,
  } = useLocationManagement();

  // Route visualization
  const {
    selectedRouteId,
    showAllRoutes,
    selectRoute,
    toggleShowAllRoutes,
  } = useRouteVisualization();

  // Route calculation hook
  const { calculateRoute } = useRouteCalculation();

  const handleCalculateRoute = useCallback(async () => {
    if (!isValidRoute() || !selectedVehicle) {
      toast.error('Please select origin, destination, and vehicle');
      return;
    }

    try {
      setIsCalculating(true);
      setCalculationError(null);

      const routeRequest = {
        origin: origin!,
        destination: destination!,
        waypoints,
        vehicle_id: selectedVehicle.id,
        preferences: {
          optimize_for: 'cost' as const,
        },
      };

      const result = await calculateRoute.mutateAsync(routeRequest);
      
      setRoutes(result.routes);
      setTollPoints(result.toll_points);
      setFuelStations(result.fuel_stations || []);
      
      // Auto-select recommended route
      const recommendedRoute = result.routes.find(
        route => route.properties.route_type === 'recommended'
      );
      if (recommendedRoute) {
        selectRoute(recommendedRoute.properties.route_id);
      }

      toast.success('Routes calculated successfully!');
    } catch (error: any) {
      console.error('Route calculation error:', error);
      const errorMessage = error.response?.data?.detail || 'Failed to calculate routes';
      setCalculationError(errorMessage);
      toast.error(errorMessage);
    } finally {
      setIsCalculating(false);
    }
  }, [
    isValidRoute,
    selectedVehicle,
    origin,
    destination,
    waypoints,
    calculateRoute,
    selectRoute,
  ]);

  const handleClearRoute = useCallback(() => {
    clearAll();
    setRoutes([]);
    setTollPoints([]);
    setFuelStations([]);
    setSelectedVehicle(null);
    setCalculationError(null);
    selectRoute(null);
  }, [clearAll, selectRoute]);

  const handleVehicleSelect = useCallback((vehicle: Vehicle | null) => {
    setSelectedVehicle(vehicle);
    // Clear previous results when vehicle changes
    if (routes.length > 0) {
      setRoutes([]);
      setTollPoints([]);
      setFuelStations([]);
      selectRoute(null);
    }
  }, [routes.length, selectRoute]);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              Route Calculator
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Calculate optimized routes with fuel cost analysis and toll detection.
            </p>
          </div>
          
          {routes.length > 0 && (
            <button
              onClick={handleClearRoute}
              className="btn btn-secondary"
            >
              Clear Route
            </button>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Route Form */}
        <div className="lg:col-span-1 space-y-6">
          <RouteCalculationForm
            origin={origin}
            destination={destination}
            waypoints={waypoints}
            selectedVehicle={selectedVehicle}
            onOriginChange={updateOrigin}
            onDestinationChange={updateDestination}
            onAddWaypoint={addWaypoint}
            onRemoveWaypoint={removeWaypoint}
            onVehicleSelect={handleVehicleSelect}
            onCalculate={handleCalculateRoute}
            isCalculating={isCalculating}
            canCalculate={isValidRoute() && selectedVehicle !== null}
          />

          {/* Route Results */}
          {routes.length > 0 && (
            <RouteResultsDisplay
              routes={routes}
              selectedRouteId={selectedRouteId}
              onRouteSelect={selectRoute}
              showAllRoutes={showAllRoutes}
              onToggleShowAll={toggleShowAllRoutes}
              selectedVehicle={selectedVehicle}
            />
          )}

          {/* Error Display */}
          {calculationError && (
            <div className="bg-red-50 dark:bg-red-900 border border-red-200 dark:border-red-800 rounded-lg p-4">
              <div className="flex">
                <div className="flex-shrink-0">
                  <svg className="h-5 w-5 text-red-400" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                  </svg>
                </div>
                <div className="ml-3">
                  <h3 className="text-sm font-medium text-red-800 dark:text-red-200">
                    Route Calculation Error
                  </h3>
                  <div className="mt-2 text-sm text-red-700 dark:text-red-300">
                    {calculationError}
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Map */}
        <div className="lg:col-span-2">
          <div className="bg-white dark:bg-gray-800 shadow rounded-lg overflow-hidden">
            <RouteMap
              routes={routes}
              selectedRouteId={selectedRouteId}
              onRouteSelect={selectRoute}
              origin={origin}
              destination={destination}
              waypoints={waypoints}
              tollPoints={tollPoints}
              fuelStations={fuelStations}
              showAllRoutes={showAllRoutes}
              showTollPoints={true}
              showFuelStations={false}
              showRouteInfo={true}
              height="600px"
            />
          </div>
        </div>
      </div>
    </div>
  );
}

export default RouteCalculatorPage;