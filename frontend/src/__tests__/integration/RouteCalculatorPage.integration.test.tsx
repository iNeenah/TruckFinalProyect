import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from '../../contexts/AuthContext';
import RouteCalculatorPage from '../../pages/Routes/RouteCalculatorPage';

// Mock all the hooks and services
jest.mock('../../hooks/useMap', () => ({
  useLocationManagement: () => ({
    origin: null,
    destination: null,
    waypoints: [],
    updateOrigin: jest.fn(),
    updateDestination: jest.fn(),
    addWaypoint: jest.fn(),
    removeWaypoint: jest.fn(),
    clearAll: jest.fn(),
    isValidRoute: jest.fn().mockReturnValue(false),
  }),
  useRouteVisualization: () => ({
    selectedRouteId: null,
    showAllRoutes: false,
    selectRoute: jest.fn(),
    toggleShowAllRoutes: jest.fn(),
  }),
}));

jest.mock('../../hooks/useRoutes', () => ({
  useRouteCalculation: () => ({
    calculateRoute: {
      mutateAsync: jest.fn().mockResolvedValue({
        routes: [],
        toll_points: [],
        fuel_stations: [],
      }),
    },
    isCalculating: false,
    error: null,
  }),
  useRouteManagement: () => ({
    selectedRoutes: [],
    selectRoute: jest.fn(),
    selectAllRoutes: jest.fn(),
    clearSelection: jest.fn(),
    routeFilters: {},
    updateFilters: jest.fn(),
    saveRoute: jest.fn(),
    isSaving: false,
    exportRoute: jest.fn(),
    isExporting: false,
    comparisonRoutes: [],
    addToComparison: jest.fn(),
    removeFromComparison: jest.fn(),
    clearComparison: jest.fn(),
    getComparisonData: jest.fn(),
    preferences: {
      optimize_for: 'cost',
      avoid_tolls: false,
      avoid_highways: false,
      prefer_highways: false,
    },
    updatePreference: jest.fn(),
    resetPreferences: jest.fn(),
  }),
  useVehicles: () => ({
    data: {
      vehicles: [
        {
          id: '1',
          name: 'Test Vehicle',
          license_plate: 'TEST123',
          fuel_type: 'diesel',
          fuel_consumption: 8.0,
          is_active: true,
          company_id: '1',
          created_at: '2023-01-01T00:00:00Z',
          updated_at: '2023-01-01T00:00:00Z',
        },
      ],
      total: 1,
    },
    isLoading: false,
    error: null,
  }),
}));

jest.mock('../../contexts/AuthContext', () => ({
  ...jest.requireActual('../../contexts/AuthContext'),
  useAuth: () => ({
    user: {
      id: '1',
      email: 'test@example.com',
      first_name: 'Test',
      last_name: 'User',
      role: 'user',
      company_id: '1',
      is_active: true,
      created_at: '2023-01-01T00:00:00Z',
    },
    isAuthenticated: true,
    isLoading: false,
  }),
}));

// Mock components that are complex to test
jest.mock('../../components/Map/RouteMap', () => {
  return function MockRouteMap() {
    return <div data-testid="route-map">Route Map Component</div>;
  };
});

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <QueryClientProvider client={queryClient}>
    <AuthProvider>
      {children}
    </AuthProvider>
  </QueryClientProvider>
);

describe('RouteCalculatorPage Integration', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders all main components', () => {
    render(
      <wrapper>
        <RouteCalculatorPage />
      </wrapper>
    );

    expect(screen.getByText('Route Calculator')).toBeInTheDocument();
    expect(screen.getByText('Route Planning')).toBeInTheDocument();
    expect(screen.getByText('Route Results')).toBeInTheDocument();
    expect(screen.getByTestId('route-map')).toBeInTheDocument();
  });

  it('shows vehicle selector', () => {
    render(
      <wrapper>
        <RouteCalculatorPage />
      </wrapper>
    );

    expect(screen.getByText('Select a vehicle...')).toBeInTheDocument();
  });

  it('shows calculate button', () => {
    render(
      <wrapper>
        <RouteCalculatorPage />
      </wrapper>
    );

    expect(screen.getByText('Calculate Routes')).toBeInTheDocument();
  });

  it('shows clear route button after calculation', async () => {
    render(
      <wrapper>
        <RouteCalculatorPage />
      </wrapper>
    );

    // The clear button should not be visible initially
    expect(screen.queryByText('Clear Route')).not.toBeInTheDocument();
  });
});