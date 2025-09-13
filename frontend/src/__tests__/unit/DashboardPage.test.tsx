import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { Provider } from 'react-redux';
import { store } from '@store/index';
import DashboardPage from '@pages/DashboardPage';
import { useAuth } from '@contexts/AuthContext';
import { useVehicles } from '@hooks/useVehicles';
import { useRoutes } from '@hooks/useRoutes';

// Mock de los contextos y hooks
jest.mock('@contexts/AuthContext', () => ({
  useAuth: jest.fn(),
}));

jest.mock('@hooks/useVehicles', () => ({
  useVehicles: jest.fn(),
}));

jest.mock('@hooks/useRoutes', () => ({
  useRoutes: jest.fn(),
}));

// Mock de las funciones
const mockUser = {
  id: '1',
  email: 'test@example.com',
  full_name: 'Test User',
  role: 'admin' as const,
  company_id: null,
  is_active: true,
  created_at: '2023-01-01',
};

describe('DashboardPage Component', () => {
  beforeEach(() => {
    (useAuth as jest.Mock).mockReturnValue({
      user: mockUser,
    });
    
    (useVehicles as jest.Mock).mockReturnValue({
      vehicles: [
        { id: '1', license_plate: 'ABC123' },
        { id: '2', license_plate: 'XYZ789' },
      ],
      loading: false,
      error: null,
    });
    
    (useRoutes as jest.Mock).mockReturnValue({
      savedRoutes: [
        { id: '1', origin: 'Buenos Aires', destination: 'Rosario' },
        { id: '2', origin: 'Rosario', destination: 'Córdoba' },
      ],
      loading: false,
      error: null,
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  const renderDashboardPage = () => {
    return render(
      <Provider store={store}>
        <BrowserRouter>
          <DashboardPage />
        </BrowserRouter>
      </Provider>
    );
  };

  it('debería renderizar correctamente el dashboard', () => {
    renderDashboardPage();
    
    // Verificar que se muestra el saludo
    expect(screen.getByText(/hola, test user/i)).toBeInTheDocument();
    
    // Verificar que se muestran las tarjetas de estadísticas
    expect(screen.getByText(/vehículos/i)).toBeInTheDocument();
    expect(screen.getByText(/rutas/i)).toBeInTheDocument();
    expect(screen.getByText(/empresas/i)).toBeInTheDocument();
    expect(screen.getByText(/usuarios/i)).toBeInTheDocument();
  });

  it('debería mostrar las estadísticas correctas', () => {
    renderDashboardPage();
    
    // Verificar que se muestran los números correctos
    expect(screen.getByText('2')).toBeInTheDocument(); // 2 vehículos
    expect(screen.getByText('2')).toBeInTheDocument(); // 2 rutas
    expect(screen.getByText('1')).toBeInTheDocument(); // 1 empresa
    expect(screen.getByText('1')).toBeInTheDocument(); // 1 usuario
  });

  it('debería mostrar los enlaces de navegación rápida', () => {
    renderDashboardPage();
    
    // Verificar que se muestran los enlaces
    expect(screen.getByText(/calcular ruta/i).closest('a')).toHaveAttribute('href', '/routes');
    expect(screen.getByText(/gestionar vehículos/i).closest('a')).toHaveAttribute('href', '/vehicles');
    expect(screen.getByText(/ver reportes/i).closest('a')).toHaveAttribute('href', '/reports');
  });

  it('debería mostrar mensaje de bienvenida para usuarios administradores', () => {
    renderDashboardPage();
    
    expect(screen.getByText(/panel de administración/i)).toBeInTheDocument();
  });

  it('debería mostrar las últimas rutas guardadas', () => {
    renderDashboardPage();
    
    // Verificar que se muestran las últimas rutas
    expect(screen.getByText('Buenos Aires')).toBeInTheDocument();
    expect(screen.getByText('Rosario')).toBeInTheDocument();
    expect(screen.getByText('Córdoba')).toBeInTheDocument();
  });

  it('debería mostrar mensaje cuando no hay rutas guardadas', () => {
    (useRoutes as jest.Mock).mockReturnValue({
      savedRoutes: [],
      loading: false,
      error: null,
    });
    
    renderDashboardPage();
    
    expect(screen.getByText(/no hay rutas guardadas/i)).toBeInTheDocument();
  });
});