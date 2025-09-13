import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { Provider } from 'react-redux';
import { store } from '@store/index';
import RouteCalculationForm from '@components/Routes/RouteCalculationForm';
import { useRoutes } from '@hooks/useRoutes';
import { useVehicles } from '@hooks/useVehicles';

// Mock de los hooks
jest.mock('@hooks/useRoutes', () => ({
  useRoutes: jest.fn(),
}));

jest.mock('@hooks/useVehicles', () => ({
  useVehicles: jest.fn(),
}));

// Mock de react-router-dom
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

// Mock de las funciones de los hooks
const mockCalculateRoutes = jest.fn();
const mockClearRoutes = jest.fn();

describe('RouteCalculationForm Component', () => {
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
    (useRoutes as jest.Mock).mockReturnValue({
      calculateRoutes: mockCalculateRoutes,
      clearRoutes: mockClearRoutes,
      loading: false,
      error: null,
    });
    
    (useVehicles as jest.Mock).mockReturnValue({
      vehicles: mockVehicles,
      loading: false,
      error: null,
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  const renderRouteForm = () => {
    return render(
      <Provider store={store}>
        <BrowserRouter>
          <RouteCalculationForm />
        </BrowserRouter>
      </Provider>
    );
  };

  it('debería renderizar correctamente el formulario de cálculo de rutas', () => {
    renderRouteForm();
    
    // Verificar que se muestran los campos del formulario
    expect(screen.getByLabelText(/origen/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/destino/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/vehículo/i)).toBeInTheDocument();
    
    // Verificar que se muestran los botones
    expect(screen.getByRole('button', { name: /calcular rutas/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /limpiar/i })).toBeInTheDocument();
  });

  it('debería mostrar los vehículos disponibles en el selector', () => {
    renderRouteForm();
    
    const vehicleSelect = screen.getByLabelText(/vehículo/i);
    expect(vehicleSelect).toBeInTheDocument();
    
    // Verificar que se muestra el vehículo en las opciones
    expect(screen.getByText('ABC123 - Toyota Corolla')).toBeInTheDocument();
  });

  it('debería llamar a calculateRoutes cuando se envía el formulario', async () => {
    renderRouteForm();
    
    // Llenar el formulario
    fireEvent.change(screen.getByLabelText(/origen/i), { target: { value: 'Buenos Aires' } });
    fireEvent.change(screen.getByLabelText(/destino/i), { target: { value: 'Rosario' } });
    
    // Seleccionar un vehículo
    fireEvent.change(screen.getByLabelText(/vehículo/i), { target: { value: '1' } });
    
    // Enviar el formulario
    fireEvent.click(screen.getByRole('button', { name: /calcular rutas/i }));
    
    // Verificar que se llama a calculateRoutes
    await waitFor(() => {
      expect(mockCalculateRoutes).toHaveBeenCalledWith({
        origin: 'Buenos Aires',
        destination: 'Rosario',
        vehicleId: '1',
      });
    });
  });

  it('debería llamar a clearRoutes cuando se hace clic en limpiar', () => {
    renderRouteForm();
    
    fireEvent.click(screen.getByRole('button', { name: /limpiar/i }));
    
    expect(mockClearRoutes).toHaveBeenCalledTimes(1);
  });

  it('debería mostrar mensaje de error cuando hay un error', () => {
    (useRoutes as jest.Mock).mockReturnValue({
      calculateRoutes: mockCalculateRoutes,
      clearRoutes: mockClearRoutes,
      loading: false,
      error: 'Error al calcular rutas',
    });
    
    renderRouteForm();
    
    expect(screen.getByText(/error al calcular rutas/i)).toBeInTheDocument();
  });

  it('debería mostrar estado de carga cuando está calculando', () => {
    (useRoutes as jest.Mock).mockReturnValue({
      calculateRoutes: mockCalculateRoutes,
      clearRoutes: mockClearRoutes,
      loading: true,
      error: null,
    });
    
    renderRouteForm();
    
    expect(screen.getByText(/calculando/i)).toBeInTheDocument();
  });
});