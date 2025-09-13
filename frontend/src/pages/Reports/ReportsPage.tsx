import React from 'react';
import ReportGenerator from '../../components/Reports/ReportGenerator';

function ReportsPage() {
  return (
    <div className=\"space-y-6\">
      {/* Header */}
      <div className=\"bg-white dark:bg-gray-800 shadow rounded-lg p-6\">
        <div className=\"flex items-center justify-between\">
          <div>
            <h1 className=\"text-2xl font-bold text-gray-900 dark:text-white\">
              Reportes y Análisis
            </h1>
            <p className=\"text-gray-600 dark:text-gray-400 mt-1\">
              Analiza el rendimiento y optimización de tus rutas
            </p>
          </div>
        </div>
      </div>
      
      {/* Report Generator */}
      <ReportGenerator />
      
      {/* Additional Reports */}
      <div className=\"grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6\">
        {/* Vehicle Efficiency Report */}
        <div className=\"bg-white dark:bg-gray-800 shadow rounded-lg p-6\">
          <h2 className=\"text-lg font-semibold text-gray-900 dark:text-white mb-4\">
            Eficiencia por Vehículo
          </h2>
          <div className=\"space-y-4\">
            <div className=\"flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg\">
              <div className=\"flex items-center\">
                <div className=\"w-3 h-3 rounded-full bg-blue-500 mr-3\"></div>
                <span className=\"text-sm text-gray-900 dark:text-white\">Camión 001</span>
              </div>
              <span className=\"text-sm font-medium text-green-600 dark:text-green-400\">85%</span>
            </div>
            <div className=\"flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg\">
              <div className=\"flex items-center\">
                <div className=\"w-3 h-3 rounded-full bg-green-500 mr-3\"></div>
                <span className=\"text-sm text-gray-900 dark:text-white\">Camión 002</span>
              </div>
              <span className=\"text-sm font-medium text-green-600 dark:text-green-400\">92%</span>
            </div>
            <div className=\"flex items-center justify-between p-3 bg-gray-50 dark:bg-gray-700 rounded-lg\">
              <div className=\"flex items-center\">
                <div className=\"w-3 h-3 rounded-full bg-yellow-500 mr-3\"></div>
                <span className=\"text-sm text-gray-900 dark:text-white\">Camión 003</span>
              </div>
              <span className=\"text-sm font-medium text-yellow-600 dark:text-yellow-400\">78%</span>
            </div>
          </div>
        </div>
        
        {/* Cost Analysis */}
        <div className=\"bg-white dark:bg-gray-800 shadow rounded-lg p-6\">
          <h2 className=\"text-lg font-semibold text-gray-900 dark:text-white mb-4\">
            Análisis de Costos
          </h2>
          <div className=\"space-y-4\">
            <div className=\"flex items-center justify-between\">
              <span className=\"text-sm text-gray-600 dark:text-gray-400\">Combustible</span>
              <span className=\"text-sm font-medium text-gray-900 dark:text-white\">65%</span>
            </div>
            <div className=\"w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2\">
              <div className=\"bg-blue-600 h-2 rounded-full\" style={{ width: '65%' }}></div>
            </div>
            
            <div className=\"flex items-center justify-between\">
              <span className=\"text-sm text-gray-600 dark:text-gray-400\">Peajes</span>
              <span className=\"text-sm font-medium text-gray-900 dark:text-white\">25%</span>
            </div>
            <div className=\"w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2\">
              <div className=\"bg-green-600 h-2 rounded-full\" style={{ width: '25%' }}></div>
            </div>
            
            <div className=\"flex items-center justify-between\">
              <span className=\"text-sm text-gray-600 dark:text-gray-400\">Mantenimiento</span>
              <span className=\"text-sm font-medium text-gray-900 dark:text-white\">10%</span>
            </div>
            <div className=\"w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2\">
              <div className=\"bg-yellow-600 h-2 rounded-full\" style={{ width: '10%' }}></div>
            </div>
          </div>
        </div>
        
        {/* Route Comparison */}
        <div className=\"bg-white dark:bg-gray-800 shadow rounded-lg p-6\">
          <h2 className=\"text-lg font-semibold text-gray-900 dark:text-white mb-4\">
            Comparación de Rutas
          </h2>
          <div className=\"text-center py-8\">
            <div className=\"inline-flex items-center justify-center w-16 h-16 bg-blue-100 dark:bg-blue-900 rounded-full mb-4\">
              <svg className=\"w-8 h-8 text-blue-600 dark:text-blue-400\" fill=\"none\" stroke=\"currentColor\" viewBox=\"0 0 24 24\" xmlns=\"http://www.w3.org/2000/svg\">
                <path strokeLinecap=\"round\" strokeLinejoin=\"round\" strokeWidth=\"2\" d=\"M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z\"></path>
              </svg>
            </div>
            <p className=\"text-gray-600 dark:text-gray-400 text-sm\">
              Comparativa de rutas próximamente
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ReportsPage;