import React from 'react';
import { Marker, Popup } from 'react-map-gl';
import {
  MarkerData,
  TollPoint,
  FuelStation,
  MARKER_ICONS,
} from '../../types/map';
import {
  MapPinIcon,
  FlagIcon,
  CurrencyDollarIcon,
  BuildingStorefrontIcon,
} from '@heroicons/react/24/solid';

interface MapMarkerProps {
  marker: MarkerData;
  showPopup?: boolean;
  onPopupClose?: () => void;
  onClick?: (marker: MarkerData) => void;
  size?: 'small' | 'medium' | 'large';
}

function MapMarker({
  marker,
  showPopup = false,
  onPopupClose,
  onClick,
  size = 'medium',
}: MapMarkerProps) {
  const getMarkerIcon = () => {
    const sizeClasses = {
      small: 'h-4 w-4',
      medium: 'h-6 w-6',
      large: 'h-8 w-8',
    };

    const iconSize = sizeClasses[size];

    switch (marker.type) {
      case 'origin':
        return <FlagIcon className={`${iconSize} text-green-600`} />;
      case 'destination':
        return <FlagIcon className={`${iconSize} text-red-600`} />;
      case 'waypoint':
        return <MapPinIcon className={`${iconSize} text-blue-600`} />;
      case 'toll':
        return <CurrencyDollarIcon className={`${iconSize} text-yellow-600`} />;
      case 'fuel_station':
        return <BuildingStorefrontIcon className={`${iconSize} text-purple-600`} />;
      default:
        return <MapPinIcon className={`${iconSize} text-gray-600`} />;
    }
  };

  const getMarkerColor = () => {
    if (marker.color) return marker.color;
    
    switch (marker.type) {
      case 'origin':
        return '#16a34a'; // green-600
      case 'destination':
        return '#dc2626'; // red-600
      case 'waypoint':
        return '#2563eb'; // blue-600
      case 'toll':
        return '#ca8a04'; // yellow-600
      case 'fuel_station':
        return '#9333ea'; // purple-600
      default:
        return '#4b5563'; // gray-600
    }
  };

  const getMarkerSize = () => {
    switch (size) {
      case 'small':
        return 24;
      case 'medium':
        return 32;
      case 'large':
        return 40;
      default:
        return 32;
    }
  };

  const renderPopupContent = () => {
    if (marker.type === 'toll') {
      const tollData = marker as TollPoint;
      return (
        <div className="p-2 min-w-48">
          <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
            {tollData.data.name}
          </h3>
          <div className="space-y-1 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Cost:</span>
              <span className="font-medium">
                ${tollData.data.cost.toLocaleString('es-AR')}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Highway:</span>
              <span className="font-medium">{tollData.data.highway}</span>
            </div>
            {tollData.data.direction && (
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Direction:</span>
                <span className="font-medium">{tollData.data.direction}</span>
              </div>
            )}
            <div className="mt-2">
              <span className="text-gray-600 dark:text-gray-400">Payment:</span>
              <div className="flex flex-wrap gap-1 mt-1">
                {tollData.data.payment_methods.map((method, index) => (
                  <span
                    key={index}
                    className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200"
                  >
                    {method}
                  </span>
                ))}
              </div>
            </div>
          </div>
        </div>
      );
    }

    if (marker.type === 'fuel_station') {
      const fuelData = marker as FuelStation;
      return (
        <div className="p-2 min-w-48">
          <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
            {fuelData.data.name}
          </h3>
          <div className="space-y-1 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Brand:</span>
              <span className="font-medium">{fuelData.data.brand}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-600 dark:text-gray-400">Status:</span>
              <span className={`font-medium ${
                fuelData.data.is_open 
                  ? 'text-green-600 dark:text-green-400' 
                  : 'text-red-600 dark:text-red-400'
              }`}>
                {fuelData.data.is_open ? 'Open' : 'Closed'}
              </span>
            </div>
            {fuelData.data.hours && (
              <div className="flex justify-between">
                <span className="text-gray-600 dark:text-gray-400">Hours:</span>
                <span className="font-medium">{fuelData.data.hours}</span>
              </div>
            )}
            <div className="mt-2">
              <span className="text-gray-600 dark:text-gray-400">Fuel Prices:</span>
              <div className="mt-1 space-y-1">
                {Object.entries(fuelData.data.prices).map(([fuelType, price]) => (
                  <div key={fuelType} className="flex justify-between">
                    <span className="text-xs text-gray-500 dark:text-gray-400 capitalize">
                      {fuelType.replace('_', ' ')}:
                    </span>
                    <span className="text-xs font-medium">
                      ${price.toLocaleString('es-AR')}
                    </span>
                  </div>
                ))}
              </div>
            </div>
            {fuelData.data.services.length > 0 && (
              <div className="mt-2">
                <span className="text-gray-600 dark:text-gray-400">Services:</span>
                <div className="flex flex-wrap gap-1 mt-1">
                  {fuelData.data.services.map((service, index) => (
                    <span
                      key={index}
                      className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200"
                    >
                      {service}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      );
    }

    // Default popup content
    return (
      <div className="p-2 min-w-32">
        <h3 className="font-semibold text-gray-900 dark:text-white mb-1">
          {marker.title}
        </h3>
        {marker.description && (
          <p className="text-sm text-gray-600 dark:text-gray-400">
            {marker.description}
          </p>
        )}
      </div>
    );
  };

  return (
    <>
      <Marker
        longitude={marker.coordinates[0]}
        latitude={marker.coordinates[1]}
        anchor="bottom"
        onClick={(e) => {
          e.originalEvent.stopPropagation();
          onClick?.(marker);
        }}
      >
        <div
          className="cursor-pointer transform transition-transform hover:scale-110"
          style={{
            width: getMarkerSize(),
            height: getMarkerSize(),
          }}
        >
          <div
            className="w-full h-full rounded-full flex items-center justify-center shadow-lg border-2 border-white dark:border-gray-800"
            style={{ backgroundColor: getMarkerColor() }}
          >
            {getMarkerIcon()}
          </div>
        </div>
      </Marker>

      {showPopup && (
        <Popup
          longitude={marker.coordinates[0]}
          latitude={marker.coordinates[1]}
          anchor="top"
          onClose={onPopupClose}
          closeButton={true}
          closeOnClick={false}
          className="map-popup"
        >
          {renderPopupContent()}
        </Popup>
      )}
    </>
  );
}

export default MapMarker;