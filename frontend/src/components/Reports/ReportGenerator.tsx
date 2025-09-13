import React, { useState } from 'react';
import { useRouteStatistics } from '../../hooks/useRoutes';
import { useVehicles } from '../../hooks/useVehicles';
import LoadingSpinner from '../../components/UI/LoadingSpinner';
import {
  DocumentChartBarIcon,
  ArrowDownTrayIcon,
  CalendarIcon,
  TruckIcon,
  MapIcon,
  CurrencyDollarIcon,
} from '@heroicons/react/24/outline';

interface ReportFilters {
  startDate?: string;
  endDate?: string;
  vehicleId?: string;
  reportType: 'summary' | 'detailed' | 'cost-analysis' | 'efficiency';
}

function ReportGenerator() {
  const [filters, setFilters] = useState<ReportFilters>({
    reportType: 'summary',
  });

  const { data: stats, isLoading: isLoadingStats } = useRouteStatistics(
    filters.startDate,
    filters.endDate,
    filters.vehicleId
  );

  const { data: vehiclesData, isLoading: isLoadingVehicles } = useVehicles(
    {},
    1,
    100
  );

  const isLoading = isLoadingStats || isLoadingVehicles;

  const handleExport = (format: 'pdf' | 'excel' | 'csv') => {
    // Implement export functionality
    console.log('Exporting report in', format, 'format');
    
    // Get current filters
    const exportData = {
      filters,
      stats,
      vehicles: vehiclesData?.vehicles || [],
      timestamp: new Date().toISOString()
    };
    
    // Handle different export formats
    switch (format) {
      case 'pdf':
        exportToPDF(exportData);
        break;
      case 'excel':
        exportToExcel(exportData);
        break;
      case 'csv':
        exportToCSV(exportData);
        break;
      default:
        console.warn('Unsupported export format:', format);
    }
  };

  const exportToPDF = (data: any) => {
    // In a real implementation, this would call an API endpoint
    // to generate and download a PDF report
    console.log('Exporting to PDF:', data);
    
    // Show success message
    alert('Reporte PDF generado exitosamente. En una implementación completa, se descargaría automáticamente.');
    
    // In a real app, you would:
    // 1. Call API to generate PDF
    // 2. Download the generated file
    // 3. Show loading state during generation
  };

  const exportToExcel = (data: any) => {
    // In a real implementation, this would generate an Excel file
    console.log('Exporting to Excel:', data);
    
    // Show success message
    alert('Reporte Excel generado exitosamente. En una implementación completa, se descargaría automáticamente.');
    
    // In a real app, you would use a library like xlsx to generate Excel files
  };

  const exportToCSV = (data: any) => {
    // In a real implementation, this would generate a CSV file
    console.log('Exporting to CSV:', data);
    
    // Show success message
    alert('Reporte CSV generado exitosamente. En una implementación completa, se descargaría automáticamente.');
    
    // In a real app, you would generate CSV content and trigger download
  };

  const handleFilterChange = (key: keyof ReportFilters, value: any) => {
    setFilters(prev => ({ ...prev, [key]: value }));
  };

  const vehicles = vehiclesData?.vehicles || [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              Generador de Reportes
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              Genera reportes detallados de uso y análisis de rutas
            </p>
          </div>
          <DocumentChartBarIcon className="w-12 h-12 text-gray-400" />
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
          Filtros de Reporte
        </h2>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {/* Report Type */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Tipo de Reporte
            </label>
            <select
              value={filters.reportType}
              onChange={(e) => handleFilterChange('reportType', e.target.value as any)}
              className="form-input"
            >
              <option value="summary">Resumen General</option>
              <option value="detailed">Reporte Detallado</option>
              <option value="cost-analysis">Análisis de Costos</option>
              <option value="efficiency">Eficiencia de Rutas</option>
            </select>
          </div>

          {/* Date Range */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Fecha Inicio
            </label>
            <div className="relative">
              <input
                type="date"
                value={filters.startDate || ''}
                onChange={(e) => handleFilterChange('startDate', e.target.value)}
                className="form-input pl-10"
              />
              <CalendarIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Fecha Fin
            </label>
            <div className="relative">
              <input
                type="date"
                value={filters.endDate || ''}
                onChange={(e) => handleFilterChange('endDate', e.target.value)}
                className="form-input pl-10"
              />
              <CalendarIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            </div>
          </div>

          {/* Vehicle Filter */}
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Vehículo
            </label>
            <div className="relative">
              <select
                value={filters.vehicleId || ''}
                onChange={(e) => handleFilterChange('vehicleId', e.target.value || undefined)}
                className="form-input pl-10"
              >
                <option value="">Todos los vehículos</option>
                {vehicles.map(vehicle => (
                  <option key={vehicle.id} value={vehicle.id}>
                    {vehicle.name} ({vehicle.license_plate})
                  </option>
                ))}
              </select>
              <TruckIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
            </div>
          </div>
        </div>

        {/* Export Buttons */}
        <div className="mt-6 flex flex-wrap gap-3">
          <button
            onClick={() => handleExport('pdf')}
            className="btn btn-primary flex items-center"
          >
            <ArrowDownTrayIcon className="w-4 h-4 mr-2" />
            Exportar PDF
          </button>
          <button
            onClick={() => handleExport('excel')}
            className="btn btn-secondary flex items-center"
          >
            <ArrowDownTrayIcon className="w-4 h-4 mr-2" />
            Exportar Excel
          </button>
          <button
            onClick={() => handleExport('csv')}
            className="btn btn-secondary flex items-center"
          >
            <ArrowDownTrayIcon className="w-4 h-4 mr-2" />
            Exportar CSV
          </button>
        </div>
      </div>

      {/* Report Content */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        {isLoading ? (
          <div className="flex items-center justify-center h-64">
            <LoadingSpinner size="lg" />
          </div>
        ) : stats ? (
          <>
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
              {filters.reportType === 'summary' && 'Resumen General'}
              {filters.reportType === 'detailed' && 'Reporte Detallado'}
              {filters.reportType === 'cost-analysis' && 'Análisis de Costos'}
              {filters.reportType === 'efficiency' && 'Eficiencia de Rutas'}
            </h2>

            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
              <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                <div className="flex items-center">
                  <MapIcon className="w-8 h-8 text-blue-600 dark:text-blue-400 mr-3" />
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Rutas Totales</p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-white">
                      {stats.total_routes}
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4">
                <div className="flex items-center">
                  <CurrencyDollarIcon className="w-8 h-8 text-green-600 dark:text-green-400 mr-3" />
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Costo Total</p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-white">
                      ${stats.total_cost?.toLocaleString()}
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
                <div className="flex items-center">
                  <CurrencyDollarIcon className="w-8 h-8 text-yellow-600 dark:text-yellow-400 mr-3" />
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Ahorro Total</p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-white">
                      ${stats.total_savings?.toLocaleString()}
                    </p>
                  </div>
                </div>
              </div>

              <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4">
                <div className="flex items-center">
                  <MapIcon className="w-8 h-8 text-red-600 dark:text-red-400 mr-3" />
                  <div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">Distancia Total</p>
                    <p className="text-2xl font-bold text-gray-900 dark:text-white">
                      {(stats.total_distance / 1000).toFixed(0)} km
                    </p>
                  </div>
                </div>
              </div>
            </div>

            {/* Chart Placeholder */}
            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-6 mb-6">
              <h3 className="text-md font-medium text-gray-900 dark:text-white mb-4">
                Gráfico de Rendimiento
              </h3>
              <div className="h-64 flex items-center justify-center bg-white dark:bg-gray-600 rounded-lg">
                <p className="text-gray-500 dark:text-gray-400">
                  Gráfico de rendimiento próximamente
                </p>
              </div>
            </div>

            {/* Recent Routes Table */}
            <div>
              <h3 className="text-md font-medium text-gray-900 dark:text-white mb-4">
                Rutas Recientes
              </h3>
              <div className="overflow-x-auto">
                <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                  <thead className="bg-gray-50 dark:bg-gray-700">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Origen → Destino
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Fecha
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Distancia
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Costo
                      </th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                        Ahorro
                      </th>
                    </tr>
                  </thead>
                  <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                    {stats.recent_routes?.slice(0, 5).map((route: any, index: number) => (
                      <tr key={index} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                          {route.origin} → {route.destination}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                          {new Date(route.created_at).toLocaleDateString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                          {(route.distance / 1000).toFixed(1)} km
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                          ${route.total_cost?.toLocaleString()}
                        </td>
                        <td className="px-6 py-4 whitespace-nowrap text-sm text-green-600 dark:text-green-400">
                          ${route.savings?.toLocaleString()}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </>
        ) : (
          <div className="text-center py-12">
            <DocumentChartBarIcon className="mx-auto h-12 w-12 text-gray-400" />
            <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">Sin datos</h3>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
              No hay estadísticas disponibles para los filtros seleccionados.
            </p>
          </div>
        )}
      </div>
    </div>
  );
}

export default ReportGenerator;
