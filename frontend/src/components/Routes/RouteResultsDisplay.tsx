import React, { useState } from 'react';
import {
  RouteFeature,
  formatDistance,
  formatDuration,
} from '../../types/map';
import { Vehicle, formatFuelConsumption } from '../../types/vehicle';
import {
  formatRouteCost,
  calculateRouteSavings,
  getRouteEfficiencyScore,
} from '../../hooks/useRoutes';
import {
  ClockIcon,
  MapIcon,
  CurrencyDollarIcon,
  FireIcon,
  TruckIcon,
  StarIcon,
  EyeIcon,
  EyeSlashIcon,
  ArrowDownTrayIcon,
  BookmarkIcon,
} from '@heroicons/react/24/outline';
import {
  StarIcon as StarIconSolid,
  BookmarkIcon as BookmarkIconSolid,
} from '@heroicons/react/24/solid';

interface RouteResultsDisplayProps {
  routes: RouteFeature[];
  selectedRouteId?: string | null;
  onRouteSelect: (routeId: string) => void;
  showAllRoutes: boolean;
  onToggleShowAll: () => void;
  selectedVehicle: Vehicle | null;
}

function RouteResultsDisplay({
  routes,
  selectedRouteId,
  onRouteSelect,
  showAllRoutes,
  onToggleShowAll,
  selectedVehicle,
}: RouteResultsDisplayProps) {
  const [savedRoutes, setSavedRoutes] = useState<Set<string>>(new Set());

  if (routes.length === 0) {
    return null;
  }

  const recommendedRoute = routes.find(route => route.properties.route_type === 'recommended');
  const fastestRoute = routes.find(route => route.properties.route_type === 'fastest');
  const shortestRoute = routes.find(route => route.properties.route_type === 'shortest');

  const getRouteTypeLabel = (type: string) => {
    switch (type) {
      case 'fastest':
        return 'Fastest Route';
      case 'shortest':
        return 'Shortest Route';
      case 'recommended':
        return 'Recommended Route';
      default:
        return 'Alternative Route';
    }
  };

  const getRouteTypeIcon = (type: string) => {
    switch (type) {
      case 'fastest':
        return <ClockIcon className="h-4 w-4" />;
      case 'shortest':
        return <MapIcon className="h-4 w-4" />;
      case 'recommended':
        return <StarIcon className="h-4 w-4" />;
      default:
        return <MapIcon className="h-4 w-4" />;
    }
  };

  const getRouteColor = (type: string, isSelected: boolean = false) => {
    if (isSelected) {
      return 'border-blue-500 bg-blue-50 dark:bg-blue-900/20';
    }
    
    switch (type) {
      case 'fastest':
        return 'border-red-200 dark:border-red-800 hover:border-red-300 dark:hover:border-red-700';
      case 'shortest':
        return 'border-blue-200 dark:border-blue-800 hover:border-blue-300 dark:hover:border-blue-700';
      case 'recommended':
        return 'border-green-200 dark:border-green-800 hover:border-green-300 dark:hover:border-green-700';
      default:
        return 'border-gray-200 dark:border-gray-700 hover:border-gray-300 dark:hover:border-gray-600';
    }
  };

  const handleSaveRoute = (routeId: string) => {
    setSavedRoutes(prev => {
      const newSet = new Set(prev);
      if (newSet.has(routeId)) {
        newSet.delete(routeId);
      } else {
        newSet.add(routeId);
      }
      return newSet;
    });
  };

  const handleExportRoute = (routeId: string) => {
    // Implement route export functionality
    console.log('Export route:', routeId);
    
    // Find the route to export
    const routeToExport = routes.find(route => route.properties.route_id === routeId);
    
    if (!routeToExport) {
      console.error('Route not found for export:', routeId);
      return;
    }
    
    // Prepare route data for export
    const exportData = {
      id: routeToExport.properties.route_id,
      origin: routeToExport.properties.origin,
      destination: routeToExport.properties.destination,
      distance: routeToExport.properties.distance,
      duration: routeToExport.properties.duration,
      fuelCost: routeToExport.properties.fuel_cost,
      tollCost: routeToExport.properties.toll_cost,
      totalCost: routeToExport.properties.total_cost,
      routeType: routeToExport.properties.route_type,
      geometry: routeToExport.geometry,
      timestamp: new Date().toISOString()
    };
    
    // Show export options modal or directly export to PDF
    exportRouteToPDF(exportData);
  };

  const exportRouteToPDF = (routeData: any) => {
    // In a real implementation, this would call an API endpoint
    // to generate and download a PDF report for the route
    console.log('Exporting route to PDF:', routeData);
    
    // Show success message
    alert(`Ruta exportada exitosamente a PDF. Origen: ${routeData.origin}, Destino: ${routeData.destination}`);
    
    // In a real app, you would:
    // 1. Call API to generate PDF
    // 2. Download the generated file
    // 3. Show loading state during generation
  };

  return (
    <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
      {/* Header */}
      <div className="px-6 py-4 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center justify-between">
          <h2 className="text-lg font-semibold text-gray-900 dark:text-white">
            Route Results
          </h2>
          <div className="flex items-center space-x-2">
            <button
              onClick={onToggleShowAll}
              className="btn btn-secondary btn-sm"
            >
              {showAllRoutes ? (
                <>
                  <EyeSlashIcon className="h-4 w-4 mr-1" />
                  Hide Alternatives
                </>
              ) : (
                <>
                  <EyeIcon className="h-4 w-4 mr-1" />
                  Show All
                </>
              )}
            </button>
          </div>
        </div>
        
        {/* Summary */}
        <div className="mt-2 text-sm text-gray-600 dark:text-gray-400">
          {routes.length} route{routes.length !== 1 ? 's' : ''} found
          {selectedVehicle && (
            <span className="ml-2">
              • Vehicle: {selectedVehicle.name} ({formatFuelConsumption(selectedVehicle.fuel_consumption)})
            </span>
          )}
        </div>
      </div>

      {/* Routes */}
      <div className="p-6 space-y-4">
        {routes.map((route, index) => {
          const isSelected = route.properties.route_id === selectedRouteId;
          const isSaved = savedRoutes.has(route.properties.route_id);
          const efficiencyScore = getRouteEfficiencyScore(route);

          return (
            <div
              key={route.properties.route_id}
              className={`border-2 rounded-lg p-4 cursor-pointer transition-all duration-200 ${getRouteColor(route.properties.route_type, isSelected)}`}
              onClick={() => onRouteSelect(route.properties.route_id)}
            >
              {/* Route Header */}
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center space-x-2">
                  {getRouteTypeIcon(route.properties.route_type)}
                  <h3 className="font-semibold text-gray-900 dark:text-white">
                    {getRouteTypeLabel(route.properties.route_type)}
                  </h3>
                  {route.properties.route_type === 'recommended' && (
                    <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                      <StarIconSolid className="h-3 w-3 mr-1" />
                      Best Choice
                    </span>
                  )}
                </div>
                
                <div className="flex items-center space-x-2">
                  {/* Efficiency Score */}
                  <div className="flex items-center space-x-1">
                    <span className="text-xs text-gray-500 dark:text-gray-400">Efficiency:</span>
                    <span className={`text-xs font-medium ${
                      efficiencyScore >= 80 ? 'text-green-600 dark:text-green-400' :
                      efficiencyScore >= 60 ? 'text-yellow-600 dark:text-yellow-400' :
                      'text-red-600 dark:text-red-400'
                    }`}>
                      {efficiencyScore}%
                    </span>
                  </div>
                  
                  {/* Actions */}
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleSaveRoute(route.properties.route_id);
                    }}
                    className="text-gray-400 hover:text-yellow-500 dark:hover:text-yellow-400"
                    title={isSaved ? 'Remove from saved' : 'Save route'}
                  >
                    {isSaved ? (
                      <BookmarkIconSolid className="h-4 w-4" />
                    ) : (
                      <BookmarkIcon className="h-4 w-4" />
                    )}
                  </button>
                  
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleExportRoute(route.properties.route_id);
                    }}
                    className="text-gray-400 hover:text-blue-500 dark:hover:text-blue-400"
                    title="Export route"
                  >
                    <ArrowDownTrayIcon className="h-4 w-4" />
                  </button>
                </div>
              </div>

              {/* Route Metrics */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-3">
                <div className="text-center">
                  <div className="flex items-center justify-center mb-1">
                    <MapIcon className="h-4 w-4 text-gray-400 mr-1" />
                    <span className="text-xs text-gray-500 dark:text-gray-400">Distance</span>
                  </div>
                  <p className="text-sm font-semibold text-gray-900 dark:text-white">
                    {formatDistance(route.properties.distance)}
                  </p>
                </div>
                
                <div className="text-center">
                  <div className="flex items-center justify-center mb-1">
                    <ClockIcon className="h-4 w-4 text-gray-400 mr-1" />
                    <span className="text-xs text-gray-500 dark:text-gray-400">Duration</span>
                  </div>
                  <p className="text-sm font-semibold text-gray-900 dark:text-white">
                    {formatDuration(route.properties.duration)}
                  </p>
                </div>
                
                <div className="text-center">
                  <div className="flex items-center justify-center mb-1">
                    <FireIcon className="h-4 w-4 text-gray-400 mr-1" />
                    <span className="text-xs text-gray-500 dark:text-gray-400">Fuel Cost</span>
                  </div>
                  <p className="text-sm font-semibold text-gray-900 dark:text-white">
                    {formatRouteCost(route.properties.fuel_cost)}
                  </p>
                </div>
                
                <div className="text-center">
                  <div className="flex items-center justify-center mb-1">
                    <CurrencyDollarIcon className="h-4 w-4 text-gray-400 mr-1" />
                    <span className="text-xs text-gray-500 dark:text-gray-400">Toll Cost</span>
                  </div>
                  <p className="text-sm font-semibold text-gray-900 dark:text-white">
                    {formatRouteCost(route.properties.toll_cost)}
                  </p>
                </div>
              </div>

              {/* Total Cost */}
              <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
                <div className="flex items-center">
                  <TruckIcon className="h-5 w-5 text-gray-400 mr-2" />
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                    Total Cost
                  </span>
                </div>
                <span className="text-lg font-bold text-gray-900 dark:text-white">
                  {formatRouteCost(route.properties.total_cost)}
                </span>
              </div>

              {/* Savings Indicator */}
              {route.properties.route_type === 'recommended' && fastestRoute && (
                <div className="mt-3 p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center">
                      <StarIconSolid className="h-4 w-4 text-green-600 dark:text-green-400 mr-2" />
                      <span className="text-sm font-medium text-green-800 dark:text-green-200">
                        Savings vs Fastest Route
                      </span>
                    </div>
                    <span className="text-sm font-bold text-green-800 dark:text-green-200">
                      {(() => {
                        const savings = calculateRouteSavings(route, fastestRoute);
                        return savings > 0 ? `+${formatRouteCost(savings)}` : 'No savings';
                      })()}
                    </span>
                  </div>
                  {(() => {
                    const savings = calculateRouteSavings(route, fastestRoute);
                    const timeDiff = fastestRoute.properties.duration - route.properties.duration;
                    if (savings > 0 && timeDiff > 0) {
                      return (
                        <p className="text-xs text-green-700 dark:text-green-300 mt-1">
                          Save money with only {formatDuration(timeDiff)} extra travel time
                        </p>
                      );
                    }
                    return null;
                  })()}
                </div>
              )}

              {/* Route Details (when selected) */}
              {isSelected && (
                <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs text-gray-600 dark:text-gray-400">
                    <div>
                      <span className="font-medium">Cost per km:</span>
                      <span className="ml-1">
                        {formatRouteCost(route.properties.total_cost / (route.properties.distance / 1000))}
                      </span>
                    </div>
                    <div>
                      <span className="font-medium">Average speed:</span>
                      <span className="ml-1">
                        {Math.round((route.properties.distance / 1000) / (route.properties.duration / 3600))} km/h
                      </span>
                    </div>
                    {selectedVehicle && (
                      <>
                        <div>
                          <span className="font-medium">Estimated fuel:</span>
                          <span className="ml-1">
                            {((route.properties.distance / 1000) * (selectedVehicle.fuel_consumption / 100)).toFixed(1)}L
                          </span>
                        </div>
                        <div>
                          <span className="font-medium">Fuel efficiency:</span>
                          <span className="ml-1">
                            {((route.properties.fuel_cost / ((route.properties.distance / 1000) * (selectedVehicle.fuel_consumption / 100))) * 100).toFixed(0)}% of expected
                          </span>
                        </div>
                      </>
                    )}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Summary Footer */}
      {routes.length > 1 && (
        <div className="px-6 py-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-700">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div className="text-center">
              <p className="text-gray-500 dark:text-gray-400">Best Time</p>
              <p className="font-semibold text-gray-900 dark:text-white">
                {fastestRoute ? formatDuration(fastestRoute.properties.duration) : 'N/A'}
              </p>
            </div>
            <div className="text-center">
              <p className="text-gray-500 dark:text-gray-400">Best Distance</p>
              <p className="font-semibold text-gray-900 dark:text-white">
                {shortestRoute ? formatDistance(shortestRoute.properties.distance) : 'N/A'}
              </p>
            </div>
            <div className="text-center">
              <p className="text-gray-500 dark:text-gray-400">Best Cost</p>
              <p className="font-semibold text-gray-900 dark:text-white">
                {recommendedRoute ? formatRouteCost(recommendedRoute.properties.total_cost) : 'N/A'}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default RouteResultsDisplay;