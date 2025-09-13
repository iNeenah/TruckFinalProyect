import React from 'react';
import {
  Vehicle,
  VehicleSort,
  formatFuelType,
  formatWeight,
  formatVolume,
  formatFuelConsumption,
} from '../../types/vehicle';
import {
  PencilIcon,
  TrashIcon,
  EyeIcon,
  CheckCircleIcon,
  XCircleIcon,
  ChevronUpIcon,
  ChevronDownIcon,
} from '@heroicons/react/24/outline';

interface VehicleTableProps {
  vehicles: Vehicle[];
  sort: VehicleSort;
  onSortChange: (sort: VehicleSort) => void;
  onEdit?: (vehicle: Vehicle) => void;
  onDelete?: (vehicle: Vehicle) => void;
  onToggleStatus?: (vehicle: Vehicle) => void;
  currentPage: number;
  totalPages: number;
  totalItems: number;
  onPageChange: (page: number) => void;
}

function VehicleTable({
  vehicles,
  sort,
  onSortChange,
  onEdit,
  onDelete,
  onToggleStatus,
  currentPage,
  totalPages,
  totalItems,
  onPageChange,
}: VehicleTableProps) {
  const handleSort = (field: VehicleSort['field']) => {
    const direction = sort.field === field && sort.direction === 'asc' ? 'desc' : 'asc';
    onSortChange({ field, direction });
  };

  const getSortIcon = (field: VehicleSort['field']) => {
    if (sort.field !== field) return null;
    return sort.direction === 'asc' ? (
      <ChevronUpIcon className="h-4 w-4" />
    ) : (
      <ChevronDownIcon className="h-4 w-4" />
    );
  };

  const formatDate = (dateString: string) => {
    return new Intl.DateTimeFormat('es-AR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
    }).format(new Date(dateString));
  };

  const generatePageNumbers = () => {
    const pages = [];
    const maxVisiblePages = 5;
    
    let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
    let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);
    
    if (endPage - startPage + 1 < maxVisiblePages) {
      startPage = Math.max(1, endPage - maxVisiblePages + 1);
    }
    
    for (let i = startPage; i <= endPage; i++) {
      pages.push(i);
    }
    
    return pages;
  };

  if (vehicles.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="mx-auto h-12 w-12 flex items-center justify-center rounded-full bg-gray-100 dark:bg-gray-700">
          <svg className="h-6 w-6 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">No vehicles found</h3>
        <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
          Get started by adding your first vehicle.
        </p>
      </div>
    );
  }

  return (
    <div className="overflow-hidden">
      {/* Table */}
      <div className="overflow-x-auto">
        <table className="table">
          <thead className="table-header">
            <tr>
              <th
                className="table-header-cell cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700"
                onClick={() => handleSort('name')}
              >
                <div className="flex items-center space-x-1">
                  <span>Name</span>
                  {getSortIcon('name')}
                </div>
              </th>
              <th
                className="table-header-cell cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700"
                onClick={() => handleSort('license_plate')}
              >
                <div className="flex items-center space-x-1">
                  <span>License Plate</span>
                  {getSortIcon('license_plate')}
                </div>
              </th>
              <th className="table-header-cell">Fuel Type</th>
              <th
                className="table-header-cell cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700"
                onClick={() => handleSort('fuel_consumption')}
              >
                <div className="flex items-center space-x-1">
                  <span>Consumption</span>
                  {getSortIcon('fuel_consumption')}
                </div>
              </th>
              <th className="table-header-cell">Capacity</th>
              <th className="table-header-cell">Status</th>
              <th
                className="table-header-cell cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700"
                onClick={() => handleSort('created_at')}
              >
                <div className="flex items-center space-x-1">
                  <span>Created</span>
                  {getSortIcon('created_at')}
                </div>
              </th>
              <th className="table-header-cell">Actions</th>
            </tr>
          </thead>
          <tbody className="table-body">
            {vehicles.map((vehicle) => (
              <tr key={vehicle.id} className="hover:bg-gray-50 dark:hover:bg-gray-800">
                <td className="table-cell">
                  <div>
                    <div className="text-sm font-medium text-gray-900 dark:text-white">
                      {vehicle.name}
                    </div>
                  </div>
                </td>
                <td className="table-cell">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200">
                    {vehicle.license_plate}
                  </span>
                </td>
                <td className="table-cell">
                  <span className="text-sm text-gray-900 dark:text-white">
                    {formatFuelType(vehicle.fuel_type)}
                  </span>
                </td>
                <td className="table-cell">
                  <span className="text-sm text-gray-900 dark:text-white">
                    {formatFuelConsumption(vehicle.fuel_consumption)}
                  </span>
                </td>
                <td className="table-cell">
                  <div className="text-sm text-gray-900 dark:text-white">
                    <div>{formatWeight(vehicle.max_weight)}</div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">
                      {formatVolume(vehicle.max_volume)}
                    </div>
                  </div>
                </td>
                <td className="table-cell">
                  <span
                    className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      vehicle.is_active
                        ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                        : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                    }`}
                  >
                    {vehicle.is_active ? (
                      <>
                        <CheckCircleIcon className="h-3 w-3 mr-1" />
                        Active
                      </>
                    ) : (
                      <>
                        <XCircleIcon className="h-3 w-3 mr-1" />
                        Inactive
                      </>
                    )}
                  </span>
                </td>
                <td className="table-cell">
                  <span className="text-sm text-gray-900 dark:text-white">
                    {formatDate(vehicle.created_at)}
                  </span>
                </td>
                <td className="table-cell">
                  <div className="flex items-center space-x-2">
                    <button
                      className="text-blue-600 hover:text-blue-900 dark:text-blue-400 dark:hover:text-blue-300"
                      title="View details"
                    >
                      <EyeIcon className="h-4 w-4" />
                    </button>
                    
                    {onEdit && (
                      <button
                        onClick={() => onEdit(vehicle)}
                        className="text-indigo-600 hover:text-indigo-900 dark:text-indigo-400 dark:hover:text-indigo-300"
                        title="Edit vehicle"
                      >
                        <PencilIcon className="h-4 w-4" />
                      </button>
                    )}
                    
                    {onToggleStatus && (
                      <button
                        onClick={() => onToggleStatus(vehicle)}
                        className={`${
                          vehicle.is_active
                            ? 'text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300'
                            : 'text-green-600 hover:text-green-900 dark:text-green-400 dark:hover:text-green-300'
                        }`}
                        title={vehicle.is_active ? 'Deactivate vehicle' : 'Activate vehicle'}
                      >
                        {vehicle.is_active ? (
                          <XCircleIcon className="h-4 w-4" />
                        ) : (
                          <CheckCircleIcon className="h-4 w-4" />
                        )}
                      </button>
                    )}
                    
                    {onDelete && (
                      <button
                        onClick={() => onDelete(vehicle)}
                        className="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300"
                        title="Delete vehicle"
                      >
                        <TrashIcon className="h-4 w-4" />
                      </button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="bg-white dark:bg-gray-800 px-4 py-3 border-t border-gray-200 dark:border-gray-700 sm:px-6">
          <div className="flex items-center justify-between">
            <div className="flex-1 flex justify-between sm:hidden">
              <button
                onClick={() => onPageChange(Math.max(1, currentPage - 1))}
                disabled={currentPage === 1}
                className="relative inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Previous
              </button>
              <button
                onClick={() => onPageChange(Math.min(totalPages, currentPage + 1))}
                disabled={currentPage === totalPages}
                className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Next
              </button>
            </div>
            <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
              <div>
                <p className="text-sm text-gray-700 dark:text-gray-300">
                  Showing{' '}
                  <span className="font-medium">
                    {(currentPage - 1) * 20 + 1}
                  </span>{' '}
                  to{' '}
                  <span className="font-medium">
                    {Math.min(currentPage * 20, totalItems)}
                  </span>{' '}
                  of{' '}
                  <span className="font-medium">{totalItems}</span>{' '}
                  results
                </p>
              </div>
              <div>
                <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                  <button
                    onClick={() => onPageChange(Math.max(1, currentPage - 1))}
                    disabled={currentPage === 1}
                    className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm font-medium text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <span className="sr-only">Previous</span>
                    <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                      <path fillRule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                  </button>
                  
                  {generatePageNumbers().map((page) => (
                    <button
                      key={page}
                      onClick={() => onPageChange(page)}
                      className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${
                        page === currentPage
                          ? 'z-10 bg-blue-50 dark:bg-blue-900 border-blue-500 text-blue-600 dark:text-blue-200'
                          : 'bg-white dark:bg-gray-800 border-gray-300 dark:border-gray-600 text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700'
                      }`}
                    >
                      {page}
                    </button>
                  ))}
                  
                  <button
                    onClick={() => onPageChange(Math.min(totalPages, currentPage + 1))}
                    disabled={currentPage === totalPages}
                    className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm font-medium text-gray-500 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <span className="sr-only">Next</span>
                    <svg className="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                      <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                    </svg>
                  </button>
                </nav>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default VehicleTable;