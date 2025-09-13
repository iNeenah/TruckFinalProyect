import React, { useState } from 'react';
import { RouteFeature } from '../../types/map';
import { formatRouteDistance, formatRouteDuration, formatRouteCost } from '../../hooks/useRoutes';
import {
  MapPinIcon,
  FlagIcon,
  ClockIcon,
  CurrencyDollarIcon,
  FireIcon,
} from '@heroicons/react/24/outline';

interface MobileRouteSheetProps {
  route: RouteFeature;
  onClose: () => void;
}

function MobileRouteSheet({ route, onClose }: MobileRouteSheetProps) {
  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div 
        className="fixed inset-0 bg-black bg-opacity-50 transition-opacity"
        onClick={onClose}
      />
      
      {/* Sheet */}
      <div className="fixed inset-x-0 bottom-0 bg-white dark:bg-gray-800 rounded-t-xl shadow-lg transform transition-transform duration-300 ease-in-out">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
              Detalles de Ruta
            </h3>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12"></path>
              </svg>
            </button>
          </div>
        </div>
        
        <div className="p-4 max-h-[70vh] overflow-y-auto">
          {/* Route Info */}
          <div className="mb-6">
            <div className="flex items-center mb-2">
              <div className="w-3 h-3 rounded-full bg-green-500 mr-2"></div>
              <span className="text-sm font-medium text-gray-900 dark:text-white">
                {route.properties.origin?.name || 'Punto de inicio'}
              </span>
            </div>
            
            <div className="flex items-center mx-2 mb-2">
              <div className="h-6 w-0.5 bg-gray-300 ml-1"></div>
            </div>
            
            <div className="flex items-center mb-2">
              <div className="w-3 h-3 rounded-full bg-red-500 mr-2"></div>
              <span className="text-sm font-medium text-gray-900 dark:text-white">
                {route.properties.destination?.name || 'Destino'}
              </span>
            </div>
          </div>
          
          {/* Route Metrics */}
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-3">
              <div className="flex items-center mb-1">
                <MapPinIcon className="w-4 h-4 text-blue-600 dark:text-blue-400 mr-1" />
                <span className="text-xs text-gray-500 dark:text-gray-400">Distancia</span>
              </div>
              <p className="text-sm font-semibold text-gray-900 dark:text-white">
                {formatRouteDistance(route.properties.distance)}
              </p>
            </div>
            
            <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-3">
              <div className="flex items-center mb-1">
                <ClockIcon className="w-4 h-4 text-green-600 dark:text-green-400 mr-1" />
                <span className="text-xs text-gray-500 dark:text-gray-400">Duración</span>
              </div>
              <p className="text-sm font-semibold text-gray-900 dark:text-white">
                {formatRouteDuration(route.properties.duration)}
              </p>
            </div>
            
            <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-3">
              <div className="flex items-center mb-1">
                <FireIcon className="w-4 h-4 text-yellow-600 dark:text-yellow-400 mr-1" />
                <span className="text-xs text-gray-500 dark:text-gray-400">Combustible</span>
              </div>
              <p className="text-sm font-semibold text-gray-900 dark:text-white">
                {formatRouteCost(route.properties.fuel_cost)}
              </p>
            </div>
            
            <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-3">
              <div className="flex items-center mb-1">
                <CurrencyDollarIcon className="w-4 h-4 text-red-600 dark:text-red-400 mr-1" />
                <span className="text-xs text-gray-500 dark:text-gray-400">Peajes</span>
              </div>
              <p className="text-sm font-semibold text-gray-900 dark:text-white">
                {formatRouteCost(route.properties.toll_cost)}
              </p>
            </div>
          </div>
          
          {/* Total Cost */}
          <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 mb-6">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Costo Total</span>
              <span className="text-lg font-bold text-gray-900 dark:text-white">
                {formatRouteCost(route.properties.total_cost)}
              </span>
            </div>
          </div>
          
          {/* Route Type */}
          <div className="mb-6">
            <div className="flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg">
              <div className="flex items-center">
                {route.properties.route_type === 'recommended' && (
                  <FlagIcon className="w-5 h-5 text-green-600 dark:text-green-400 mr-2" />
                )}
                {route.properties.route_type === 'fastest' && (
                  <ClockIcon className="w-5 h-5 text-blue-600 dark:text-blue-400 mr-2" />
                )}
                {route.properties.route_type === 'shortest' && (
                  <MapPinIcon className="w-5 h-5 text-purple-600 dark:text-purple-400 mr-2" />
                )}
                <span className="text-sm font-medium text-gray-900 dark:text-white">
                  {route.properties.route_type === 'recommended' && 'Ruta Recomendada'}
                  {route.properties.route_type === 'fastest' && 'Ruta Más Rápida'}
                  {route.properties.route_type === 'shortest' && 'Ruta Más Corta'}
                </span>
              </div>
              {route.properties.route_type === 'recommended' && (
                <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200">
                  Mejor Opción
                </span>
              )}
            </div>
          </div>
          
          {/* Actions */}
          <div className="flex space-x-3">
            <button className="flex-1 btn btn-primary">
              Guardar Ruta
            </button>
            <button className="flex-1 btn btn-secondary">
              Compartir
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default MobileRouteSheet;
