import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { Provider } from 'react-redux';
import { store } from '@store/index';
import ReportsPage from '@pages/Reports/ReportsPage';
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
const mockGenerateReport = jest.fn();
const mockExportToPDF = jest.fn();

describe('ReportsPage Component', () => {
  const mockSavedRoutes = [
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
  ];

  beforeEach(() => {
    (useRoutes as jest.Mock).mockReturnValue({
      savedRoutes: mockSavedRoutes,
      generateReport: mockGenerateReport,
      exportToPDF: mockExportToPDF,
      loading: false,
      error: null,
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  const renderReportsPage = () => {
    return render(
      <Provider store={store}>
        <BrowserRouter>
          <ReportsPage />
        </BrowserRouter>
      </Provider>
    );
  };

  it('debería renderizar correctamente la página de reportes', () => {
    renderReportsPage();
    
    // Verificar que se muestra el título
    expect(screen.getByText(/reportes/i)).toBeInTheDocument();
    
    // Verificar que se muestran las secciones
    expect(screen.getByText(/estadísticas/i)).toBeInTheDocument();
    expect(screen.getByText(/rutas guardadas/i)).toBeInTheDocument();
    expect(screen.getByText(/análisis de costos/i)).toBeInTheDocument();
  });

  it('debería mostrar las rutas guardadas', () => {
    renderReportsPage();
    
    // Verificar que se muestran las rutas guardadas
    expect(screen.getByText('Buenos Aires')).toBeInTheDocument();
    expect(screen.getByText('Rosario')).toBeInTheDocument();
    expect(screen.getByText('300 km')).toBeInTheDocument();
    expect(screen.getByText('$2000')).toBeInTheDocument();
  });

  it('debería llamar a generateReport cuando se hace clic en generar reporte', () => {
    renderReportsPage();
    
    const generateButton = screen.getByRole('button', { name: /generar reporte/i });
    fireEvent.click(generateButton);
    
    expect(mockGenerateReport).toHaveBeenCalledTimes(1);
  });

  it('debería llamar a exportToPDF cuando se hace clic en exportar a PDF', () => {
    renderReportsPage();
    
    const exportButton = screen.getByRole('button', { name: /exportar a pdf/i });
    fireEvent.click(exportButton);
    
    expect(mockExportToPDF).toHaveBeenCalledTimes(1);
  });

  it('debería mostrar mensaje cuando no hay rutas guardadas', () => {
    (useRoutes as jest.Mock).mockReturnValue({
      savedRoutes: [],
      generateReport: mockGenerateReport,
      exportToPDF: mockExportToPDF,
      loading: false,
      error: null,
    });
    
    renderReportsPage();
    
    expect(screen.getByText(/no hay rutas guardadas/i)).toBeInTheDocument();
  });

  it('debería mostrar estado de carga cuando está generando reporte', () => {
    (useRoutes as jest.Mock).mockReturnValue({
      savedRoutes: mockSavedRoutes,
      generateReport: mockGenerateReport,
      exportToPDF: mockExportToPDF,
      loading: true,
      error: null,
    });
    
    renderReportsPage();
    
    expect(screen.getByText(/generando reporte/i)).toBeInTheDocument();
  });
});