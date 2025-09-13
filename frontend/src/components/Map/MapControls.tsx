import React, { useState } from 'react';
import {
  RouteFeature,
  formatDistance,
  formatDuration,
  getRouteColor,
} from '../../types/map';
import {
  EyeIcon,
  EyeSlashIcon,
  ArrowsPointingOutIcon,
  InformationCircleIcon,
  ChevronUpIcon,
  ChevronDownIcon,
} from '@heroicons/react/24/outline';

interface MapControlsProps {
  routes: RouteFeature[];
  selectedRouteId?: string;
  onRouteSelect?: (routeId: string) => void;
  onFitToRoute?: () => void;
  showRouteInfo?: boolean;
}

function MapControls({
  routes,
  selectedRouteId,
  onRouteSelect,
  onFitToRoute,
  showRouteInfo = true,
}: MapControlsProps) {
  const [isExpanded, setIsExpanded] = useState(true);
  const [showAllRoutes, setShowAllRoutes] = useState(true);

  if (!showRouteInfo || routes.length === 0) {
    return null;
  }

  const selectedRoute = routes.find(route => route.properties.route_id === selectedRouteId);
  const displayRoutes = showAllRoutes ? routes : selectedRoute ? [selectedRoute] : routes.slice(0, 1);

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('es-AR', {
      style: 'currency',
      currency: 'ARS',
    }).format(amount);
  };

  const getRouteTypeLabel = (type: string) => {
    switch (type) {
      case 'fastest':
        return 'Fastest';
      case 'shortest':
        return 'Shortest';
      case 'recommended':
        return 'Recommended';
      default:
        return 'Alternative';
    }
  };

  return (
    <div className="absolute top-4 left-4 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 max-w-sm">
      {/* Header */}
      <div className="flex items-center justify-between p-3 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-2">
          <InformationCircleIcon className="h-5 w-5 text-blue-600 dark:text-blue-400" />
          <h3 className="text-sm font-medium text-gray-900 dark:text-white">
            Route Information
          </h3>
        </div>
        <div className="flex items-center space-x-1">
          <button
            onClick={() => setShowAllRoutes(!showAllRoutes)}
            className="p-1 rounded text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            title={showAllRoutes ? 'Hide alternative routes' : 'Show all routes'}
          >
            {showAllRoutes ? (
              <EyeSlashIcon className="h-4 w-4" />
            ) : (
              <EyeIcon className="h-4 w-4" />
            )}
          </button>
          <button
            onClick={onFitToRoute}
            className="p-1 rounded text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            title="Fit to route"
          >
            <ArrowsPointingOutIcon className="h-4 w-4" />
          </button>
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="p-1 rounded text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
          >
            {isExpanded ? (
              <ChevronUpIcon className="h-4 w-4" />
            ) : (
              <ChevronDownIcon className="h-4 w-4" />
            )}
          </button>
        </div>
      </div>

      {/* Content */}
      {isExpanded && (
        <div className="p-3 space-y-3 max-h-96 overflow-y-auto">
          {displayRoutes.map((route, index) => {
            const isSelected = route.properties.route_id === selectedRouteId;
            const routeColor = getRouteColor(route.properties.route_type, isSelected);

            return (
              <div
                key={route.properties.route_id}
                className={`p-3 rounded-lg border cursor-pointer transition-colors ${
                  isSelected
                    ? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
                    : 'border-gray-200 dark:border-gray-600 hover:border-gray-300 dark:hover:border-gray-500'
                }`}
                onClick={() => onRouteSelect?.(route.properties.route_id)}
              >
                {/* Route header */}
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center space-x-2">
                    <div
                      className="w-3 h-3 rounded-full"
                      style={{ backgroundColor: routeColor }}
                    />
                    <span className="text-sm font-medium text-gray-900 dark:text-white">
                      {getRouteTypeLabel(route.properties.route_type)}
                    </span>
                    {route.properties.route_type === 'recommended' && (
                      <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                        Best
                      </span>
                    )}
                  </div>
                  <span className="text-lg font-bold text-gray-900 dark:text-white">
                    {formatCurrency(route.properties.total_cost)}
                  </span>
                </div>

                {/* Route details */}
                <div className="grid grid-cols-2 gap-2 text-xs text-gray-600 dark:text-gray-400">
                  <div>
                    <span className="block font-medium">Distance</span>
                    <span>{formatDistance(route.properties.distance)}</span>
                  </div>
                  <div>
                    <span className="block font-medium">Duration</span>
                    <span>{formatDuration(route.properties.duration)}</span>
                  </div>
                  <div>
                    <span className="block font-medium">Fuel Cost</span>
                    <span>{formatCurrency(route.properties.fuel_cost)}</span>
                  </div>
                  <div>
                    <span className="block font-medium">Toll Cost</span>
                    <span>{formatCurrency(route.properties.toll_cost)}</span>
                  </div>
                </div>

                {/* Savings indicator */}
                {route.properties.route_type === 'recommended' && routes.length > 1 && (
                  <div className="mt-2 p-2 bg-green-50 dark:bg-green-900/20 rounded border border-green-200 dark:border-green-800">
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-medium text-green-800 dark:text-green-200">
                        Savings vs Fastest:
                      </span>
                      <span className="text-xs font-bold text-green-800 dark:text-green-200">
                        {(() => {
                          const fastestRoute = routes.find(r => r.properties.route_type === 'fastest');
                          if (fastestRoute) {
                            const savings = fastestRoute.properties.total_cost - route.properties.total_cost;
                            return savings > 0 ? formatCurrency(savings) : 'No savings';
                          }
                          return 'N/A';
                        })()}
                      </span>
                    </div>
                  </div>
                )}
              </div>
            );
          })}

          {/* Summary */}
          {routes.length > 1 && (
            <div className="pt-2 border-t border-gray-200 dark:border-gray-700">
              <div className="text-xs text-gray-500 dark:text-gray-400">
                <div className="flex justify-between">
                  <span>Routes found:</span>
                  <span className="font-medium">{routes.length}</span>
                </div>
                {selectedRoute && (
                  <div className="flex justify-between mt-1">
                    <span>Selected:</span>
                    <span className="font-medium">
                      {getRouteTypeLabel(selectedRoute.properties.route_type)}
                    </span>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default MapControls;