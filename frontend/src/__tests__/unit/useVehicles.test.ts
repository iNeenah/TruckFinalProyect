import { renderHook, act } from '@testing-library/react';
import { useVehicles } from '@hooks/useVehicles';
import * as vehicleService from '@services/vehicleService';

// Mock del servicio de vehículos
jest.mock('@services/vehicleService');

describe('useVehicles Hook', () => {
  const mockVehicles = [
    {
      id: '1',
      license_plate: 'ABC123',
      brand: 'Toyota',
      model: 'Corolla',
      year: 2020,
      fuel_type: 'gasoline' as const,
      fuel_efficiency: 12.5,
      tank_capacity: 50,
      weight: 1500,
      dimensions: {
        length: 4.5,
        width: 1.8,
        height: 1.5,
      },
      company_id: '1',
      created_at: '2023-01-01',
      updated_at: '2023-01-01',
    },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('debería cargar vehículos correctamente', async () => {
    (vehicleService.fetchVehicles as jest.Mock).mockResolvedValue(mockVehicles);
    
    const { result } = renderHook(() => useVehicles());
    
    // Verificar estado inicial
    expect(result.current.vehicles).toEqual([]);
    expect(result.current.loading).toBe(true);
    expect(result.current.error).toBeNull();
    
    // Esperar a que se carguen los vehículos
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });
    
    // Verificar estado después de cargar
    expect(result.current.vehicles).toEqual(mockVehicles);
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('debería manejar errores al cargar vehículos', async () => {
    const errorMessage = 'Error al cargar vehículos';
    (vehicleService.fetchVehicles as jest.Mock).mockRejectedValue(new Error(errorMessage));
    
    const { result } = renderHook(() => useVehicles());
    
    // Esperar a que se intente cargar los vehículos
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });
    
    // Verificar estado de error
    expect(result.current.vehicles).toEqual([]);
    expect(result.current.loading).toBe(false);
    expect(result.current.error).toBe(errorMessage);
  });

  it('debería agregar un vehículo correctamente', async () => {
    const newVehicle = {
      license_plate: 'XYZ789',
      brand: 'Honda',
      model: 'Civic',
      year: 2021,
      fuel_type: 'diesel' as const,
      fuel_efficiency: 15,
      tank_capacity: 55,
      weight: 1400,
      dimensions: {
        length: 4.7,
        width: 1.8,
        height: 1.4,
      },
      company_id: '1',
    };
    
    const createdVehicle = { ...newVehicle, id: '2', created_at: '2023-01-02', updated_at: '2023-01-02' };
    (vehicleService.createVehicle as jest.Mock).mockResolvedValue(createdVehicle);
    (vehicleService.fetchVehicles as jest.Mock).mockResolvedValue(mockVehicles);
    
    const { result } = renderHook(() => useVehicles());
    
    // Esperar a que se carguen los vehículos iniciales
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });
    
    // Agregar un nuevo vehículo
    await act(async () => {
      await result.current.addVehicle(newVehicle);
    });
    
    // Verificar que se llamó al servicio de creación
    expect(vehicleService.createVehicle).toHaveBeenCalledWith(newVehicle);
    
    // Verificar que se actualizó la lista de vehículos
    expect(result.current.vehicles).toContainEqual(createdVehicle);
  });

  it('debería actualizar un vehículo correctamente', async () => {
    const updatedVehicle = { ...mockVehicles[0], model: 'Camry' };
    (vehicleService.updateVehicle as jest.Mock).mockResolvedValue(updatedVehicle);
    (vehicleService.fetchVehicles as jest.Mock).mockResolvedValue([updatedVehicle]);
    
    const { result } = renderHook(() => useVehicles());
    
    // Esperar a que se carguen los vehículos iniciales
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });
    
    // Actualizar un vehículo
    await act(async () => {
      await result.current.updateVehicle(updatedVehicle);
    });
    
    // Verificar que se llamó al servicio de actualización
    expect(vehicleService.updateVehicle).toHaveBeenCalledWith(updatedVehicle);
    
    // Verificar que se actualizó la lista de vehículos
    expect(result.current.vehicles[0]).toEqual(updatedVehicle);
  });

  it('debería eliminar un vehículo correctamente', async () => {
    (vehicleService.deleteVehicle as jest.Mock).mockResolvedValue({});
    (vehicleService.fetchVehicles as jest.Mock).mockResolvedValue([]);
    
    const { result } = renderHook(() => useVehicles());
    
    // Esperar a que se carguen los vehículos iniciales
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0));
    });
    
    // Eliminar un vehículo
    await act(async () => {
      await result.current.deleteVehicle('1');
    });
    
    // Verificar que se llamó al servicio de eliminación
    expect(vehicleService.deleteVehicle).toHaveBeenCalledWith('1');
    
    // Verificar que se actualizó la lista de vehículos
    expect(result.current.vehicles).toEqual([]);
  });
});