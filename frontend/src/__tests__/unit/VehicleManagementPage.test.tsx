import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { Provider } from 'react-redux';
import { store } from '@store/index';
import VehicleManagementPage from '@pages/Vehicles/VehicleManagementPage';
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

const mockFetchVehicles = jest.fn();

describe('VehicleManagementPage Component', () => {
  beforeEach(() => {
    (useVehicles as jest.Mock).mockReturnValue({
      vehicles: mockVehicles,
      fetchVehicles: mockFetchVehicles,
      loading: false,
      error: null,
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  const renderVehicleManagementPage = () => {
    return render(
      <Provider store={store}>
        <BrowserRouter>
          <VehicleManagementPage />
        </BrowserRouter>
      </Provider>
    );
  };

  it('debería renderizar correctamente la página de gestión de vehículos', () => {
    renderVehicleManagementPage();
    
    // Verificar que se muestra el título
    expect(screen.getByText(/gestión de vehículos/i)).toBeInTheDocument();
    
    // Verificar que se muestran los componentes
    expect(screen.getByText(/filtros/i)).toBeInTheDocument();
    expect(screen.getByText(/tabla de vehículos/i)).toBeInTheDocument();
    expect(screen.getByText(/estadísticas/i)).toBeInTheDocument();
  });

  it('debería mostrar los vehículos en la tabla', () => {
    renderVehicleManagementPage();
    
    // Verificar que se muestran los vehículos
    expect(screen.getByText('ABC123')).toBeInTheDocument();
    expect(screen.getByText('Toyota')).toBeInTheDocument();
    expect(screen.getByText('Corolla')).toBeInTheDocument();
  });

  it('debería llamar a fetchVehicles cuando se monta el componente', () => {
    renderVehicleManagementPage();
    
    expect(mockFetchVehicles).toHaveBeenCalledTimes(1);
  });

  it('debería mostrar mensaje de error cuando hay un error', () => {
    (useVehicles as jest.Mock).mockReturnValue({
      vehicles: [],
      fetchVehicles: mockFetchVehicles,
      loading: false,
      error: 'Error al cargar vehículos',
    });
    
    renderVehicleManagementPage();
    
    expect(screen.getByText(/error al cargar vehículos/i)).toBeInTheDocument();
  });

  it('debería mostrar estado de carga cuando está cargando', () => {
    (useVehicles as jest.Mock).mockReturnValue({
      vehicles: [],
      fetchVehicles: mockFetchVehicles,
      loading: true,
      error: null,
    });
    
    renderVehicleManagementPage();
    
    expect(screen.getByText(/cargando vehículos/i)).toBeInTheDocument();
  });

  it('debería mostrar mensaje cuando no hay vehículos', () => {
    (useVehicles as jest.Mock).mockReturnValue({
      vehicles: [],
      fetchVehicles: mockFetchVehicles,
      loading: false,
      error: null,
    });
    
    renderVehicleManagementPage();
    
    expect(screen.getByText(/no se encontraron vehículos/i)).toBeInTheDocument();
  });

  it('debería abrir el formulario de creación cuando se hace clic en nuevo vehículo', () => {
    renderVehicleManagementPage();
    
    const newButton = screen.getByRole('button', { name: /nuevo vehículo/i });
    fireEvent.click(newButton);
    
    // Verificar que se muestra el formulario
    expect(screen.getByText(/crear vehículo/i)).toBeInTheDocument();
  });
});