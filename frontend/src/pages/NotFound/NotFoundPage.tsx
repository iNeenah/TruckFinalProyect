import React from 'react';
import { Link } from 'react-router-dom';
import {
  ExclamationTriangleIcon,
  HomeIcon,
} from '@heroicons/react/24/outline';

function NotFoundPage() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="text-center">
          <ExclamationTriangleIcon className="mx-auto h-20 w-20 text-gray-400" />
          <h1 className="mt-6 text-6xl font-bold text-gray-900 dark:text-white">404</h1>
          <h2 className="mt-4 text-2xl font-bold text-gray-900 dark:text-white">
            Página no encontrada
          </h2>
          <p className="mt-2 text-gray-600 dark:text-gray-400">
            Lo sentimos, no pudimos encontrar la página que estás buscando.
          </p>
        </div>

        <div className="mt-8 text-center">
          <Link
            to="/dashboard"
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <HomeIcon className="mr-2 h-4 w-4" />
            Ir al Dashboard
          </Link>
        </div>

        <div className="mt-6 text-center">
          <button
            onClick={() => window.history.back()}
            className="text-blue-600 hover:text-blue-500 dark:text-blue-400 text-sm font-medium"
          >
            ← Volver atrás
          </button>
        </div>
      </div>
    </div>
  );
}

export default NotFoundPage;