import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { AuthProvider, useAuth } from '../../contexts/AuthContext';

// Mock the auth service
jest.mock('../../services/authService', () => ({
  authService: {
    login: jest.fn(),
    register: jest.fn(),
    getCurrentUser: jest.fn(),
  },
}));

const mockAuthService = require('../../services/authService');

describe('AuthContext', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  it('provides initial state correctly', () => {
    const TestComponent = () => {
      const { user, isLoading, isAuthenticated } = useAuth();
      return (
        <div>
          <span data-testid="user">{user ? 'logged-in' : 'logged-out'}</span>
          <span data-testid="loading">{isLoading.toString()}</span>
          <span data-testid="authenticated">{isAuthenticated.toString()}</span>
        </div>
      );
    };

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    expect(screen.getByTestId('user')).toHaveTextContent('logged-out');
    expect(screen.getByTestId('loading')).toHaveTextContent('true');
    expect(screen.getByTestId('authenticated')).toHaveTextContent('false');
  });

  it('initializes with stored token', async () => {
    const mockUser = {
      id: '1',
      email: 'test@example.com',
      first_name: 'Test',
      last_name: 'User',
      role: 'user',
      company_id: null,
      is_active: true,
      created_at: '2023-01-01T00:00:00Z',
    };

    localStorage.setItem('access_token', 'test-token');
    mockAuthService.authService.getCurrentUser.mockResolvedValue(mockUser);

    const TestComponent = () => {
      const { user, isLoading, isAuthenticated } = useAuth();
      return (
        <div>
          <span data-testid="user">{user ? user.email : 'no-user'}</span>
          <span data-testid="loading">{isLoading.toString()}</span>
          <span data-testid="authenticated">{isAuthenticated.toString()}</span>
        </div>
      );
    };

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByTestId('user')).toHaveTextContent('test@example.com');
      expect(screen.getByTestId('loading')).toHaveTextContent('false');
      expect(screen.getByTestId('authenticated')).toHaveTextContent('true');
    });
  });

  it('handles login correctly', async () => {
    const mockLoginResponse = {
      access_token: 'new-token',
      user: {
        id: '1',
        email: 'test@example.com',
        first_name: 'Test',
        last_name: 'User',
        role: 'user',
        company_id: null,
        is_active: true,
        created_at: '2023-01-01T00:00:00Z',
      },
    };

    mockAuthService.authService.login.mockResolvedValue(mockLoginResponse);

    const TestComponent = () => {
      const { user, login } = useAuth();
      return (
        <div>
          <span data-testid="user">{user ? user.email : 'no-user'}</span>
          <button data-testid="login" onClick={() => login({ email: 'test@example.com', password: 'password' })}>
            Login
          </button>
        </div>
      );
    };

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    // Initially no user
    expect(screen.getByTestId('user')).toHaveTextContent('no-user');

    // Perform login
    screen.getByTestId('login').click();

    await waitFor(() => {
      expect(screen.getByTestId('user')).toHaveTextContent('test@example.com');
      expect(localStorage.getItem('access_token')).toBe('new-token');
    });
  });

  it('handles logout correctly', async () => {
    const mockUser = {
      id: '1',
      email: 'test@example.com',
      first_name: 'Test',
      last_name: 'User',
      role: 'user',
      company_id: null,
      is_active: true,
      created_at: '2023-01-01T00:00:00Z',
    };

    localStorage.setItem('access_token', 'test-token');
    mockAuthService.authService.getCurrentUser.mockResolvedValue(mockUser);

    const TestComponent = () => {
      const { user, logout } = useAuth();
      return (
        <div>
          <span data-testid="user">{user ? user.email : 'no-user'}</span>
          <button data-testid="logout" onClick={logout}>
            Logout
          </button>
        </div>
      );
    };

    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    // Wait for initial load
    await waitFor(() => {
      expect(screen.getByTestId('user')).toHaveTextContent('test@example.com');
    });

    // Perform logout
    screen.getByTestId('logout').click();

    expect(screen.getByTestId('user')).toHaveTextContent('no-user');
    expect(localStorage.getItem('access_token')).toBeNull();
  });
});