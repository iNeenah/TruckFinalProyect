import React, { createContext, useContext, useEffect, useState, ReactNode } from 'react';
import { authService } from '../services/authService';
import { AuthUser, LoginRequest, RegisterRequest } from '../types/auth';
import { toast } from 'react-hot-toast';

interface AuthContextType {
  user: AuthUser | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (credentials: LoginRequest) => Promise<void>;
  register: (userData: RegisterRequest) => Promise<void>;
  logout: () => void;
  refreshToken: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const isAuthenticated = !!user;

  // Initialize auth on mount
  useEffect(() => {
    const initializeAuth = async () => {
      try {
        const token = localStorage.getItem('access_token');
        if (token) {
          const currentUser = await authService.getCurrentUser();
          setUser(currentUser);
        }
      } catch (error) {
        console.error('Failed to initialize auth:', error);
        // Clear invalid token
        localStorage.removeItem('access_token');
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, []);

  const login = async (credentials: LoginRequest) => {
    try {
      setIsLoading(true);
      const { access_token, user: userData } = await authService.login(credentials);
      
      localStorage.setItem('access_token', access_token);
      setUser(userData);
      
      toast.success('¡Bienvenido!');
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Error al iniciar sesión';
      toast.error(errorMessage);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (userData: RegisterRequest) => {
    try {
      setIsLoading(true);
      const { access_token, user: newUser } = await authService.register(userData);
      
      localStorage.setItem('access_token', access_token);
      setUser(newUser);
      
      toast.success('¡Cuenta creada exitosamente!');
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || 'Error al crear la cuenta';
      toast.error(errorMessage);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    setUser(null);
    toast.success('Sesión cerrada');
  };

  const refreshToken = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        throw new Error('No token available');
      }

      // In a real implementation, you'd call a refresh token endpoint
      // For now, we'll just try to get the current user to validate the token
      const currentUser = await authService.getCurrentUser();
      setUser(currentUser);
    } catch (error) {
      console.error('Failed to refresh token:', error);
      logout();
    }
  };

  const value = {
    user,
    isLoading,
    isAuthenticated,
    login,
    register,
    logout,
    refreshToken,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextType {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}