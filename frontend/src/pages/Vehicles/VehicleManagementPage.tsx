import React, { useState } from 'react';
import { useVehicles, useCreateVehicle, useUpdateVehicle, useDeleteVehicle } from '../../hooks/useVehicles';
import { Vehicle, VehicleCreateRequest, VehicleUpdateRequest, FuelType } from '../../types/vehicle';
import { useForm } from 'react-hook-form';
import LoadingSpinner from '../../components/UI/LoadingSpinner';
import {
  TruckIcon,
  PlusIcon,
  PencilIcon,
  TrashIcon,
  XMarkIcon,
  CheckIcon,
} from '@heroicons/react/24/outline';
import { toast } from 'react-hot-toast';

interface VehicleFormData {
  name: string;
  license_plate: string;
  fuel_type: FuelType;
  fuel_consumption: number;
  is_active: boolean;
}

function VehicleManagementPage() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingVehicle, setEditingVehicle] = useState<Vehicle | null>(null);
  const [page, setPage] = useState(1);
  const [filters, setFilters] = useState({ is_active: undefined as boolean | undefined });

  // Hooks
  const { data: vehiclesData, isLoading } = useVehicles(filters, page, 10);
  const createVehicle = useCreateVehicle();
  const updateVehicle = useUpdateVehicle();
  const deleteVehicle = useDeleteVehicle();

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<VehicleFormData>();

  const vehicles = vehiclesData?.vehicles || [];
  const total = vehiclesData?.total || 0;
  const totalPages = Math.ceil(total / 10);

  const handleCreateVehicle = () => {
    setEditingVehicle(null);
    reset({
      name: '',
      license_plate: '',
      fuel_type: 'gasoline',
      fuel_consumption: 8.0,
      is_active: true,
    });
    setIsModalOpen(true);
  };

  const handleEditVehicle = (vehicle: Vehicle) => {
    setEditingVehicle(vehicle);
    reset({
      name: vehicle.name,
      license_plate: vehicle.license_plate,
      fuel_type: vehicle.fuel_type,
      fuel_consumption: vehicle.fuel_consumption,
      is_active: vehicle.is_active,
    });
    setIsModalOpen(true);
  };

  const handleDeleteVehicle = async (vehicleId: string) => {
    if (window.confirm('¿Estás seguro de que quieres eliminar este vehículo?')) {
      try {
        await deleteVehicle.mutateAsync(vehicleId);
        toast.success('Vehículo eliminado exitosamente');
      } catch (error) {
        console.error('Error deleting vehicle:', error);
      }
    }
  };

  const onSubmit = async (data: VehicleFormData) => {
    try {
      if (editingVehicle) {
        const updateData: VehicleUpdateRequest = { ...data };
        await updateVehicle.mutateAsync({ id: editingVehicle.id, data: updateData });
        toast.success('Vehículo actualizado exitosamente');
      } else {
        const createData: VehicleCreateRequest = { ...data };
        await createVehicle.mutateAsync(createData);
        toast.success('Vehículo creado exitosamente');
      }
      setIsModalOpen(false);
      reset();
    } catch (error) {
      console.error('Error saving vehicle:', error);
    }
  };

  const getFuelTypeLabel = (fuelType: FuelType) => {
    const labels = {
      gasoline: 'Gasolina',
      diesel: 'Diésel',
      electric: 'Eléctrico',
      hybrid: 'Híbrido',
    };
    return labels[fuelType];
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              Gestión de Vehículos
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              Administra tu flota de vehículos y configuraciones de consumo
            </p>
          </div>
          <button
            onClick={handleCreateVehicle}
            className="btn btn-primary"
          >
            <PlusIcon className="w-5 h-5 mr-2" />
            Nuevo Vehículo
          </button>
        </div>
      </div>

      {/* Filters */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
        <div className="flex flex-wrap items-center gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Estado
            </label>
            <select
              value={filters.is_active === undefined ? '' : filters.is_active ? 'true' : 'false'}
              onChange={(e) => {
                const value = e.target.value;
                setFilters({
                  ...filters,
                  is_active: value === '' ? undefined : value === 'true',
                });
                setPage(1);
              }}
              className="form-input"
            >
              <option value="">Todos</option>
              <option value="true">Activos</option>
              <option value="false">Inactivos</option>
            </select>
          </div>
        </div>
      </div>

      {/* Vehicles Table */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg overflow-hidden">
        {vehicles.length === 0 ? (
          <div className="text-center py-12">
            <TruckIcon className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
              No hay vehículos
            </h3>
            <p className="text-gray-500 dark:text-gray-400 mb-4">
              Comienza agregando tu primer vehículo
            </p>
            <button
              onClick={handleCreateVehicle}
              className="btn btn-primary"
            >
              <PlusIcon className="w-5 h-5 mr-2" />
              Agregar Vehículo
            </button>
          </div>
        ) : (
          <>
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                <thead className="bg-gray-50 dark:bg-gray-700">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Vehículo
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Patente
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Combustible
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Consumo
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Estado
                    </th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                      Acciones
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
                  {vehicles.map((vehicle) => (
                    <tr key={vehicle.id} className="hover:bg-gray-50 dark:hover:bg-gray-700">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <TruckIcon className="w-8 h-8 text-gray-400 mr-3" />
                          <div>
                            <div className="text-sm font-medium text-gray-900 dark:text-white">
                              {vehicle.name}
                            </div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                        {vehicle.license_plate}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                        {getFuelTypeLabel(vehicle.fuel_type)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                        {vehicle.fuel_consumption}L/100km
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          vehicle.is_active
                            ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                            : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                        }`}>
                          {vehicle.is_active ? 'Activo' : 'Inactivo'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                        <div className="flex items-center justify-end space-x-2">
                          <button
                            onClick={() => handleEditVehicle(vehicle)}
                            className="text-blue-600 hover:text-blue-500 dark:text-blue-400"
                            title="Editar"
                          >
                            <PencilIcon className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => handleDeleteVehicle(vehicle.id)}
                            className="text-red-600 hover:text-red-500 dark:text-red-400"
                            title="Eliminar"
                          >
                            <TrashIcon className="w-4 h-4" />
                          </button>
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
                      onClick={() => setPage(Math.max(1, page - 1))}
                      disabled={page === 1}
                      className="btn btn-secondary"
                    >
                      Anterior
                    </button>
                    <button
                      onClick={() => setPage(Math.min(totalPages, page + 1))}
                      disabled={page === totalPages}
                      className="btn btn-secondary"
                    >
                      Siguiente
                    </button>
                  </div>
                  <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                    <div>
                      <p className="text-sm text-gray-700 dark:text-gray-300">
                        Mostrando{' '}
                        <span className="font-medium">{((page - 1) * 10) + 1}</span>
                        {' '}a{' '}
                        <span className="font-medium">{Math.min(page * 10, total)}</span>
                        {' '}de{' '}
                        <span className="font-medium">{total}</span>
                        {' '}resultados
                      </p>
                    </div>
                    <div>
                      <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
                        {Array.from({ length: totalPages }, (_, i) => i + 1).map((pageNum) => (
                          <button
                            key={pageNum}
                            onClick={() => setPage(pageNum)}
                            className={`relative inline-flex items-center px-4 py-2 border text-sm font-medium ${
                              pageNum === page
                                ? 'z-10 bg-blue-50 border-blue-500 text-blue-600'
                                : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                            } ${pageNum === 1 ? 'rounded-l-md' : ''} ${
                              pageNum === totalPages ? 'rounded-r-md' : ''
                            }`}
                          >
                            {pageNum}
                          </button>
                        ))}
                      </nav>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {/* Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white dark:bg-gray-800">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white">
                {editingVehicle ? 'Editar Vehículo' : 'Nuevo Vehículo'}
              </h3>
              <button
                onClick={() => setIsModalOpen(false)}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                <XMarkIcon className="w-6 h-6" />
              </button>
            </div>

            <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
              {/* Name */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Nombre del Vehículo
                </label>
                <input
                  {...register('name', { required: 'El nombre es requerido' })}
                  type="text"
                  className="form-input"
                  placeholder="Ej: Camión Mercedes Benz"
                />
                {errors.name && (
                  <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                    {errors.name.message}
                  </p>
                )}
              </div>

              {/* License Plate */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Patente
                </label>
                <input
                  {...register('license_plate', { required: 'La patente es requerida' })}
                  type="text"
                  className="form-input"
                  placeholder="ABC123"
                />
                {errors.license_plate && (
                  <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                    {errors.license_plate.message}
                  </p>
                )}
              </div>

              {/* Fuel Type */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Tipo de Combustible
                </label>
                <select
                  {...register('fuel_type', { required: 'El tipo de combustible es requerido' })}
                  className="form-input"
                >
                  <option value="gasoline">Gasolina</option>
                  <option value="diesel">Diésel</option>
                  <option value="electric">Eléctrico</option>
                  <option value="hybrid">Híbrido</option>
                </select>
                {errors.fuel_type && (
                  <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                    {errors.fuel_type.message}
                  </p>
                )}
              </div>

              {/* Fuel Consumption */}
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Consumo de Combustible (L/100km)
                </label>
                <input
                  {...register('fuel_consumption', {
                    required: 'El consumo es requerido',
                    min: { value: 1, message: 'El consumo debe ser mayor a 1' },
                    max: { value: 50, message: 'El consumo debe ser menor a 50' },
                  })}
                  type="number"
                  step="0.1"
                  className="form-input"
                  placeholder="8.5"
                />
                {errors.fuel_consumption && (
                  <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                    {errors.fuel_consumption.message}
                  </p>
                )}
              </div>

              {/* Active Status */}
              <div className="flex items-center">
                <input
                  {...register('is_active')}
                  type="checkbox"
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <label className="ml-2 block text-sm text-gray-900 dark:text-gray-300">
                  Vehículo activo
                </label>
              </div>

              {/* Buttons */}
              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="btn btn-secondary"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  disabled={createVehicle.isLoading || updateVehicle.isLoading}
                  className="btn btn-primary"
                >
                  {createVehicle.isLoading || updateVehicle.isLoading ? (
                    <>
                      <LoadingSpinner size="sm" color="white" />
                      <span className="ml-2">Guardando...</span>
                    </>
                  ) : (
                    <>
                      <CheckIcon className="w-4 h-4 mr-2" />
                      {editingVehicle ? 'Actualizar' : 'Crear'}
                    </>
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default VehicleManagementPage;