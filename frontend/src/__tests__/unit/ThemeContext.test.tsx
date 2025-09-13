import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { ThemeProvider } from '@contexts/ThemeContext';

// Mock de localStorage
const mockLocalStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};

beforeEach(() => {
  Object.defineProperty(window, 'localStorage', {
    value: mockLocalStorage,
  });
  
  // Limpiar mocks
  jest.clearAllMocks();
});

describe('ThemeContext', () => {
  const TestComponent = () => {
    const { actualTheme, toggleTheme } = React.useContext(ThemeProvider);
    
    return (
      <div>
        <span data-testid="theme-value">{actualTheme}</span>
        <button onClick={toggleTheme}>Toggle Theme</button>
      </div>
    );
  };

  it('debería usar el tema claro por defecto', () => {
    mockLocalStorage.getItem.mockReturnValue(null);
    
    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );
    
    expect(screen.getByTestId('theme-value')).toHaveTextContent('light');
  });

  it('debería usar el tema oscuro cuando está guardado en localStorage', () => {
    mockLocalStorage.getItem.mockReturnValue('dark');
    
    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );
    
    expect(screen.getByTestId('theme-value')).toHaveTextContent('dark');
  });

  it('debería cambiar el tema cuando se llama a toggleTheme', () => {
    mockLocalStorage.getItem.mockReturnValue(null);
    
    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );
    
    // Verificar tema inicial
    expect(screen.getByTestId('theme-value')).toHaveTextContent('light');
    
    // Cambiar tema
    fireEvent.click(screen.getByText('Toggle Theme'));
    
    // Verificar que el tema cambió
    expect(screen.getByTestId('theme-value')).toHaveTextContent('dark');
    
    // Verificar que se guardó en localStorage
    expect(mockLocalStorage.setItem).toHaveBeenCalledWith('theme', 'dark');
  });

  it('debería guardar el tema en localStorage cuando cambia', () => {
    mockLocalStorage.getItem.mockReturnValue(null);
    
    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );
    
    fireEvent.click(screen.getByText('Toggle Theme'));
    
    expect(mockLocalStorage.setItem).toHaveBeenCalledWith('theme', 'dark');
  });
});