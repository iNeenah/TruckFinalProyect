import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import VehicleSelector from '../../components/Routes/VehicleSelector';

// Mock the useVehicles hook
jest.mock('../../hooks/useVehicles', () => ({
  useVehicles: jest.fn(),
}));

const mockUseVehicles = require('../../hooks/useVehicles');

const mockVehicles = [
  {
    id: '1',
    name: 'Camión Mercedes Benz',
    license_plate: 'ABC123',
    fuel_type: 'diesel',
    fuel_consumption: 8.5,
    is_active: true,
    company_id: '1',
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z',
  },
  {
    id: '2',
    name: 'Camión Volvo',
    license_plate: 'DEF456',
    fuel_type: 'diesel',
    fuel_consumption: 7.2,
    is_active: true,
    company_id: '1',
    created_at: '2023-01-01T00:00:00Z',
    updated_at: '2023-01-01T00:00:00Z',
  },
];

const queryClient = new QueryClient();

const renderWithProviders = (component: React.ReactElement) => {
  return render(
    <QueryClientProvider client={queryClient}>
      {component}
    </QueryClientProvider>
  );
};

describe('VehicleSelector', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders loading state', () => {
    mockUseVehicles.useVehicles.mockReturnValue({
      data: null,
      isLoading: true,
      error: null,
    });

    renderWithProviders(
      <VehicleSelector
        selectedVehicle={null}
        onVehicleSelect={jest.fn()}
      />
    );

    expect(screen.getByText('Loading vehicles...')).toBeInTheDocument();
  });

  it('renders error state', () => {
    mockUseVehicles.useVehicles.mockReturnValue({
      data: null,
      isLoading: false,
      error: new Error('Failed to load vehicles'),
    });

    renderWithProviders(
      <VehicleSelector
        selectedVehicle={null}
        onVehicleSelect={jest.fn()}
      />
    );

    expect(screen.getByText('Error loading vehicles')).toBeInTheDocument();
  });

  it('renders empty state', () => {
    mockUseVehicles.useVehicles.mockReturnValue({
      data: { vehicles: [], total: 0 },
      isLoading: false,
      error: null,
    });

    renderWithProviders(
      <VehicleSelector
        selectedVehicle={null}
        onVehicleSelect={jest.fn()}
      />
    );

    expect(screen.getByText('No active vehicles available')).toBeInTheDocument();
  });

  it('renders vehicle list', () => {
    mockUseVehicles.useVehicles.mockReturnValue({
      data: { vehicles: mockVehicles, total: 2 },
      isLoading: false,
      error: null,
    });

    renderWithProviders(
      <VehicleSelector
        selectedVehicle={null}
        onVehicleSelect={jest.fn()}
      />
    );

    expect(screen.getByText('Select a vehicle...')).toBeInTheDocument();
    fireEvent.click(screen.getByText('Select a vehicle...'));
    
    expect(screen.getByText('Camión Mercedes Benz')).toBeInTheDocument();
    expect(screen.getByText('Camión Volvo')).toBeInTheDocument();
  });

  it('handles vehicle selection', () => {
    const mockOnVehicleSelect = jest.fn();
    mockUseVehicles.useVehicles.mockReturnValue({
      data: { vehicles: mockVehicles, total: 2 },
      isLoading: false,
      error: null,
    });

    renderWithProviders(
      <VehicleSelector
        selectedVehicle={null}
        onVehicleSelect={mockOnVehicleSelect}
      />
    );

    fireEvent.click(screen.getByText('Select a vehicle...'));
    fireEvent.click(screen.getByText('Camión Mercedes Benz'));
    
    expect(mockOnVehicleSelect).toHaveBeenCalledWith(mockVehicles[0]);
  });

  it('displays selected vehicle', () => {
    mockUseVehicles.useVehicles.mockReturnValue({
      data: { vehicles: mockVehicles, total: 2 },
      isLoading: false,
      error: null,
    });

    renderWithProviders(
      <VehicleSelector
        selectedVehicle={mockVehicles[0]}
        onVehicleSelect={jest.fn()}
      />
    );

    expect(screen.getByText('Camión Mercedes Benz')).toBeInTheDocument();
    expect(screen.getByText('ABC123')).toBeInTheDocument();
  });
});