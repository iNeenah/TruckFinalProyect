import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { Provider } from 'react-redux';
import { store } from '@store/index';
import Header from '@components/layout/Header';
import { useTheme } from '@contexts/ThemeContext';
import { useAuth } from '@contexts/AuthContext';

// Mock de los contextos
jest.mock('@contexts/ThemeContext', () => ({
  useTheme: jest.fn(),
}));

jest.mock('@contexts/AuthContext', () => ({
  useAuth: jest.fn(),
}));

// Mock de react-router-dom
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn(),
}));

// Mock de las funciones de los contextos
const mockToggleTheme = jest.fn();
const mockLogout = jest.fn();

describe('Header Component', () => {
  beforeEach(() => {
    (useTheme as jest.Mock).mockReturnValue({
      actualTheme: 'light',
      toggleTheme: mockToggleTheme,
    });
    
    (useAuth as jest.Mock).mockReturnValue({
      user: {
        id: '1',
        email: 'test@example.com',
        full_name: 'Test User',
        role: 'admin',
        company_id: null,
        is_active: true,
        created_at: '2023-01-01',
      },
      logout: mockLogout,
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  const renderHeader = () => {
    return render(
      <Provider store={store}>
        <BrowserRouter>
          <Header />
        </BrowserRouter>
      </Provider>
    );
  };

  it('debería renderizar correctamente el componente Header', () => {
    renderHeader();
    
    // Verificar que se muestra el nombre del usuario
    expect(screen.getByText('Test User')).toBeInTheDocument();
    
    // Verificar que se muestra el botón de tema
    expect(screen.getByRole('button', { name: /theme/i })).toBeInTheDocument();
    
    // Verificar que se muestra el botón de logout
    expect(screen.getByRole('button', { name: /logout/i })).toBeInTheDocument();
  });

  it('debería cambiar el tema cuando se hace clic en el botón de tema', () => {
    renderHeader();
    
    const themeButton = screen.getByRole('button', { name: /theme/i });
    fireEvent.click(themeButton);
    
    expect(mockToggleTheme).toHaveBeenCalledTimes(1);
  });

  it('debería cerrar sesión cuando se hace clic en el botón de logout', () => {
    renderHeader();
    
    const logoutButton = screen.getByRole('button', { name: /logout/i });
    fireEvent.click(logoutButton);
    
    expect(mockLogout).toHaveBeenCalledTimes(1);
  });

  it('debería mostrar el menú de usuario cuando se hace clic en el avatar', () => {
    renderHeader();
    
    const avatarButton = screen.getByRole('button', { name: 'Test User' });
    fireEvent.click(avatarButton);
    
    // Verificar que se muestra el menú de usuario
    expect(screen.getByText(/perfil/i)).toBeInTheDocument();
    expect(screen.getByText(/configuración/i)).toBeInTheDocument();
    expect(screen.getByText(/logout/i)).toBeInTheDocument();
  });
});