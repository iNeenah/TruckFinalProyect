import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { Provider } from 'react-redux';
import { store } from '@store/index';
import AdminPanelPage from '@pages/Admin/AdminPanelPage';
import { useAuth } from '@contexts/AuthContext';

// Mock de los contextos
jest.mock('@contexts/AuthContext', () => ({
  useAuth: jest.fn(),
}));

// Mock de las funciones de los contextos
const mockUser = {
  id: '1',
  email: 'admin@example.com',
  full_name: 'Admin User',
  role: 'admin' as const,
  company_id: null,
  is_active: true,
  created_at: '2023-01-01',
};

describe('AdminPanelPage Component', () => {
  beforeEach(() => {
    (useAuth as jest.Mock).mockReturnValue({
      user: mockUser,
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  const renderAdminPanel = () => {
    return render(
      <Provider store={store}>
        <BrowserRouter>
          <AdminPanelPage />
        </BrowserRouter>
      </Provider>
    );
  };

  it('debería renderizar correctamente el panel de administración', () => {
    renderAdminPanel();
    
    // Verificar que se muestra el título
    expect(screen.getByText(/panel de administración/i)).toBeInTheDocument();
    
    // Verificar que se muestran las secciones de administración
    expect(screen.getByText(/gestión de peajes/i)).toBeInTheDocument();
    expect(screen.getByText(/precios de combustible/i)).toBeInTheDocument();
    expect(screen.getByText(/gestión de usuarios/i)).toBeInTheDocument();
    expect(screen.getByText(/configuración del sistema/i)).toBeInTheDocument();
  });

  it('debería mostrar las tarjetas de estadísticas', () => {
    renderAdminPanel();
    
    // Verificar que se muestran las tarjetas de estadísticas
    expect(screen.getByText(/vehículos/i)).toBeInTheDocument();
    expect(screen.getByText(/rutas/i)).toBeInTheDocument();
    expect(screen.getByText(/usuarios/i)).toBeInTheDocument();
    expect(screen.getByText(/empresas/i)).toBeInTheDocument();
  });

  it('debería mostrar los enlaces de navegación administrativa', () => {
    renderAdminPanel();
    
    // Verificar que se muestran los enlaces
    expect(screen.getByText(/peajes/i).closest('a')).toHaveAttribute('href', '/admin/tolls');
    expect(screen.getByText(/combustible/i).closest('a')).toHaveAttribute('href', '/admin/fuel-prices');
    expect(screen.getByText(/usuarios/i).closest('a')).toHaveAttribute('href', '/admin/users');
    expect(screen.getByText(/empresas/i).closest('a')).toHaveAttribute('href', '/admin/companies');
  });
});