import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { Provider } from 'react-redux';
import { store } from '@store/index';
import VehicleTable from '@components/Vehicles/VehicleTable';
import { useVehicles } from '@hooks/useVehicles';

// Mock de los hooks
jest.mock('@hooks/useVehicles', () => ({
  useVehicles: jest.fn(),
}));

// Mock de react-router-dom
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

// Mock de las funciones del hook
const mockDeleteVehicle = jest.fn();

describe('VehicleTable Component', () => {
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
    {
      id: '2',
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
      created_at: '2023-01-02',
      updated_at: '2023-01-02',
    },
  ];

  beforeEach(() => {
    (useVehicles as jest.Mock).mockReturnValue({
      deleteVehicle: mockDeleteVehicle,
      loading: false,
      error: null,
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  const renderVehicleTable = (vehicles = mockVehicles) => {
    return render(
      <Provider store={store}>
        <BrowserRouter>
          <VehicleTable vehicles={vehicles} onEdit={jest.fn()} />
        </BrowserRouter>
      </Provider>
    );
  };

  it('debería renderizar correctamente la tabla de vehículos', () => {
    renderVehicleTable();
    
    // Verificar que se muestran los encabezados de la tabla
    expect(screen.getByText(/patente/i)).toBeInTheDocument();
    expect(screen.getByText(/marca/i)).toBeInTheDocument();
    expect(screen.getByText(/modelo/i)).toBeInTheDocument();
    expect(screen.getByText(/año/i)).toBeInTheDocument();
    expect(screen.getByText(/combustible/i)).toBeInTheDocument();
    expect(screen.getByText(/eficiencia/i)).toBeInTheDocument();
    
    // Verificar que se muestran los datos de los vehículos
    expect(screen.getByText('ABC123')).toBeInTheDocument();
    expect(screen.getByText('Toyota')).toBeInTheDocument();
    expect(screen.getByText('Corolla')).toBeInTheDocument();
    expect(screen.getByText('2020')).toBeInTheDocument();
    expect(screen.getByText('gasoline')).toBeInTheDocument();
    expect(screen.getByText('12.5')).toBeInTheDocument();
    
    expect(screen.getByText('XYZ789')).toBeInTheDocument();
    expect(screen.getByText('Honda')).toBeInTheDocument();
    expect(screen.getByText('Civic')).toBeInTheDocument();
    expect(screen.getByText('2021')).toBeInTheDocument();
    expect(screen.getByText('diesel')).toBeInTheDocument();
    expect(screen.getByText('15')).toBeInTheDocument();
  });

  it('debería mostrar mensaje cuando no hay vehículos', () => {
    renderVehicleTable([]);
    
    expect(screen.getByText(/no se encontraron vehículos/i)).toBeInTheDocument();
  });

  it('debería llamar a onEdit cuando se hace clic en el botón de editar', () => {
    const mockOnEdit = jest.fn();
    render(
      <Provider store={store}>
        <BrowserRouter>
          <VehicleTable vehicles={mockVehicles} onEdit={mockOnEdit} />
        </BrowserRouter>
      </Provider>
    );
    
    const editButtons = screen.getAllByRole('button', { name: /editar/i });
    fireEvent.click(editButtons[0]);
    
    expect(mockOnEdit).toHaveBeenCalledWith(mockVehicles[0]);
  });

  it('debería confirmar antes de eliminar un vehículo', () => {
    // Mock de window.confirm
    const mockConfirm = jest.spyOn(window, 'confirm').mockImplementation(() => true);
    
    renderVehicleTable();
    
    const deleteButtons = screen.getAllByRole('button', { name: /eliminar/i });
    fireEvent.click(deleteButtons[0]);
    
    expect(mockConfirm).toHaveBeenCalledWith('¿Está seguro de que desea eliminar este vehículo?');
    expect(mockDeleteVehicle).toHaveBeenCalledWith('1');
    
    mockConfirm.mockRestore();
  });

  it('debería navegar a la página de creación cuando se hace clic en el botón de nuevo vehículo', () => {
    renderVehicleTable();
    
    const newButton = screen.getByRole('button', { name: /nuevo vehículo/i });
    fireEvent.click(newButton);
    
    expect(mockNavigate).toHaveBeenCalledWith('/vehicles/new');
  });
});