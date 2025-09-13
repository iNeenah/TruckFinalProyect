import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { Provider } from 'react-redux';
import { store } from '@store/index';
import RouteResultsDisplay from '@components/Routes/RouteResultsDisplay';
import { useRoutes } from '@hooks/useRoutes';

// Mock de los hooks
jest.mock('@hooks/useRoutes', () => ({
  useRoutes: jest.fn(),
}));

// Mock de react-router-dom
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

// Mock de las funciones del hook
const mockSelectRoute = jest.fn();
const mockSaveRoute = jest.fn();

describe('RouteResultsDisplay Component', () => {
  const mockRoutes = [
    {
      id: '1',
      origin: 'Buenos Aires',
      destination: 'Rosario',
      distance: 300,
      duration: 180,
      fuelCost: 1500,
      tollCost: 500,
      totalCost: 2000,
      savings: 0,
      geometry: [],
      vehicleId: '1',
      createdAt: '2023-01-01',
    },
    {
      id: '2',
      origin: 'Buenos Aires',
      destination: 'Rosario',
      distance: 320,
      duration: 200,
      fuelCost: 1600,
      tollCost: 300,
      totalCost: 1900,
      savings: 100,
      geometry: [],
      vehicleId: '1',
      createdAt: '2023-01-01',
    },
  ];

  beforeEach(() => {
    (useRoutes as jest.Mock).mockReturnValue({
      selectRoute: mockSelectRoute,
      saveRoute: mockSaveRoute,
      selectedRoute: null,
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  const renderRouteResults = (routes = mockRoutes) => {
    return render(
      <Provider store={store}>
        <BrowserRouter>
          <RouteResultsDisplay routes={routes} />
        </BrowserRouter>
      </Provider>
    );
  };

  it('debería renderizar correctamente los resultados de rutas', () => {
    renderRouteResults();
    
    // Verificar que se muestran las rutas
    expect(screen.getByText(/ruta 1/i)).toBeInTheDocument();
    expect(screen.getByText(/ruta 2/i)).toBeInTheDocument();
    
    // Verificar que se muestran los datos de las rutas
    expect(screen.getByText('300 km')).toBeInTheDocument();
    expect(screen.getByText('180 min')).toBeInTheDocument();
    expect(screen.getByText('$2000')).toBeInTheDocument();
    
    expect(screen.getByText('320 km')).toBeInTheDocument();
    expect(screen.getByText('200 min')).toBeInTheDocument();
    expect(screen.getByText('$1900')).toBeInTheDocument();
    expect(screen.getByText('$100')).toBeInTheDocument();
  });

  it('debería mostrar mensaje cuando no hay rutas', () => {
    renderRouteResults([]);
    
    expect(screen.getByText(/no se encontraron rutas/i)).toBeInTheDocument();
  });

  it('debería llamar a selectRoute cuando se selecciona una ruta', () => {
    renderRouteResults();
    
    const routeCards = screen.getAllByRole('button', { name: /seleccionar ruta/i });
    fireEvent.click(routeCards[0]);
    
    expect(mockSelectRoute).toHaveBeenCalledWith(mockRoutes[0]);
  });

  it('debería llamar a saveRoute cuando se guarda una ruta', () => {
    renderRouteResults();
    
    const saveButtons = screen.getAllByRole('button', { name: /guardar/i });
    fireEvent.click(saveButtons[0]);
    
    expect(mockSaveRoute).toHaveBeenCalledWith(mockRoutes[0]);
  });

  it('debería mostrar la ruta seleccionada con estilo diferente', () => {
    (useRoutes as jest.Mock).mockReturnValue({
      selectRoute: mockSelectRoute,
      saveRoute: mockSaveRoute,
      selectedRoute: mockRoutes[0],
    });
    
    renderRouteResults();
    
    // Verificar que la ruta seleccionada tiene un estilo diferente
    const selectedRouteCard = screen.getByText(/ruta 1/i).closest('.bg-blue-50');
    expect(selectedRouteCard).toBeInTheDocument();
  });
});