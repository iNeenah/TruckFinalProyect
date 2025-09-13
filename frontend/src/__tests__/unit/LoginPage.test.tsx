import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { Provider } from 'react-redux';
import { store } from '@store/index';
import LoginPage from '@pages/Auth/LoginPage';
import { useAuth } from '@contexts/AuthContext';

// Mock de los contextos
jest.mock('@contexts/AuthContext', () => ({
  useAuth: jest.fn(),
}));

// Mock de react-router-dom
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

// Mock de las funciones del contexto
const mockLogin = jest.fn();

describe('LoginPage Component', () => {
  beforeEach(() => {
    (useAuth as jest.Mock).mockReturnValue({
      login: mockLogin,
      loading: false,
      error: null,
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  const renderLoginPage = () => {
    return render(
      <Provider store={store}>
        <BrowserRouter>
          <LoginPage />
        </BrowserRouter>
      </Provider>
    );
  };

  it('debería renderizar correctamente el formulario de login', () => {
    renderLoginPage();
    
    // Verificar que se muestran los campos del formulario
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/contraseña/i)).toBeInTheDocument();
    
    // Verificar que se muestran los botones
    expect(screen.getByRole('button', { name: /iniciar sesión/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /registrarse/i })).toBeInTheDocument();
  });

  it('debería llamar a login cuando se envía el formulario', async () => {
    renderLoginPage();
    
    // Llenar el formulario
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'test@example.com' } });
    fireEvent.change(screen.getByLabelText(/contraseña/i), { target: { value: 'password123' } });
    
    // Enviar el formulario
    fireEvent.click(screen.getByRole('button', { name: /iniciar sesión/i }));
    
    // Verificar que se llama a login
    await waitFor(() => {
      expect(mockLogin).toHaveBeenCalledWith({
        email: 'test@example.com',
        password: 'password123',
      });
    });
  });

  it('debería mostrar mensaje de error cuando hay un error de autenticación', () => {
    (useAuth as jest.Mock).mockReturnValue({
      login: mockLogin,
      loading: false,
      error: 'Credenciales inválidas',
    });
    
    renderLoginPage();
    
    expect(screen.getByText(/credenciales inválidas/i)).toBeInTheDocument();
  });

  it('debería mostrar estado de carga cuando está iniciando sesión', () => {
    (useAuth as jest.Mock).mockReturnValue({
      login: mockLogin,
      loading: true,
      error: null,
    });
    
    renderLoginPage();
    
    expect(screen.getByText(/iniciando sesión/i)).toBeInTheDocument();
  });

  it('debería navegar a la página de registro cuando se hace clic en registrarse', () => {
    renderLoginPage();
    
    fireEvent.click(screen.getByRole('button', { name: /registrarse/i }));
    
    expect(mockNavigate).toHaveBeenCalledWith('/register');
  });

  it('debería navegar al dashboard cuando el login es exitoso', async () => {
    (useAuth as jest.Mock).mockReturnValue({
      login: mockLogin,
      loading: false,
      error: null,
      user: {
        id: '1',
        email: 'test@example.com',
        full_name: 'Test User',
        role: 'admin',
        company_id: null,
        is_active: true,
        created_at: '2023-01-01',
      },
    });
    
    renderLoginPage();
    
    // Esperar a que se complete el efecto
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/');
    });
  });
});