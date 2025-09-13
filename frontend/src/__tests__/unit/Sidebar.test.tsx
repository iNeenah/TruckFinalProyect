import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { Provider } from 'react-redux';
import { store } from '@store/index';
import Sidebar from '@components/layout/Sidebar';
import { useAuth } from '@contexts/AuthContext';

// Mock de los contextos
jest.mock('@contexts/AuthContext', () => ({
  useAuth: jest.fn(),
}));

// Mock de react-router-dom
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useLocation: () => ({ pathname: '/' }),
}));

// Mock de las funciones de los contextos
const mockUser = {
  id: '1',
  email: 'test@example.com',
  full_name: 'Test User',
  role: 'admin' as const,
  company_id: null,
  is_active: true,
  created_at: '2023-01-01',
};

describe('Sidebar Component', () => {
  beforeEach(() => {
    (useAuth as jest.Mock).mockReturnValue({
      user: mockUser,
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  const renderSidebar = () => {
    return render(
      <Provider store={store}>
        <BrowserRouter>
          <Sidebar />
        </BrowserRouter>
      </Provider>
    );
  };

  it('debería renderizar correctamente el componente Sidebar', () => {
    renderSidebar();
    
    // Verificar que se muestra el logo
    expect(screen.getByText(/Kiro/i)).toBeInTheDocument();
    
    // Verificar que se muestran los elementos de navegación
    expect(screen.getByText(/Dashboard/i)).toBeInTheDocument();
    expect(screen.getByText(/Rutas/i)).toBeInTheDocument();
    expect(screen.getByText(/Vehículos/i)).toBeInTheDocument();
    expect(screen.getByText(/Reportes/i)).toBeInTheDocument();
  });

  it('debería mostrar elementos adicionales para usuarios administradores', () => {
    renderSidebar();
    
    // Verificar que se muestra el panel de administración para usuarios admin
    expect(screen.getByText(/Administración/i)).toBeInTheDocument();
  });

  it('debería tener los enlaces de navegación correctos', () => {
    renderSidebar();
    
    // Verificar que los enlaces tienen las rutas correctas
    expect(screen.getByText(/Dashboard/i).closest('a')).toHaveAttribute('href', '/');
    expect(screen.getByText(/Rutas/i).closest('a')).toHaveAttribute('href', '/routes');
    expect(screen.getByText(/Vehículos/i).closest('a')).toHaveAttribute('href', '/vehicles');
    expect(screen.getByText(/Reportes/i).closest('a')).toHaveAttribute('href', '/reports');
    expect(screen.getByText(/Administración/i).closest('a')).toHaveAttribute('href', '/admin');
  });
});