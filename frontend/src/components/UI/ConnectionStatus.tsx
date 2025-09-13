import React from 'react';
import { useConnectionStatus } from '../../hooks/useConnectionStatus';
import {
  WifiIcon,
  ExclamationTriangleIcon,
  ArrowPathIcon,
} from '@heroicons/react/24/outline';

interface ConnectionStatusProps {
  className?: string;
}

function ConnectionStatus({ className = '' }: ConnectionStatusProps) {
  const { isOnline, isApiConnected, isConnected, lastChecked, forceCheck } = useConnectionStatus();

  if (isConnected) {
    return null; // Don't show anything when everything is working
  }

  const handleRetry = () => {
    forceCheck();
  };

  return (
    <div className={`fixed top-4 right-4 z-50 ${className}`}>
      <div className=\"bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-3 shadow-lg max-w-sm\">
        <div className=\"flex items-start\">
          <div className=\"flex-shrink-0\">
            {!isOnline ? (
              <ExclamationTriangleIcon className=\"h-5 w-5 text-red-400\" />
            ) : (
              <WifiIcon className=\"h-5 w-5 text-red-400\" />
            )}
          </div>
          <div className=\"ml-3 flex-1\">
            <h3 className=\"text-sm font-medium text-red-800 dark:text-red-200\">
              {!isOnline ? 'Sin conexión a internet' : 'Sin conexión al servidor'}
            </h3>
            <div className=\"mt-1 text-sm text-red-700 dark:text-red-300\">
              {!isOnline
                ? 'Verifica tu conexión a internet'
                : 'No se puede conectar al servidor. Algunas funciones pueden no estar disponibles.'
              }
            </div>
            {lastChecked && (
              <div className=\"mt-1 text-xs text-red-600 dark:text-red-400\">
                Última verificación: {lastChecked.toLocaleTimeString()}
              </div>
            )}
          </div>
          <div className=\"ml-3 flex-shrink-0\">
            <button
              onClick={handleRetry}
              className=\"inline-flex items-center px-2 py-1 text-xs font-medium text-red-800 dark:text-red-200 hover:bg-red-100 dark:hover:bg-red-800/50 rounded transition-colors\"
              title=\"Reintentar conexión\"
            >
              <ArrowPathIcon className=\"h-3 w-3\" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ConnectionStatus;