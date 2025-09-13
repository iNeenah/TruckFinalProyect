import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { Provider } from 'react-redux';
import { store } from '@store/index';
import VehicleForm from '@components/Vehicles/VehicleForm';
import { useVehicles } from '@hooks/useVehicles';

// Mock de los hooks
jest.mock('@hooks/useVehicles', () => ({
  useVehicles: jest.fn(),
}));

// Mock de react-router-dom
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

// Mock de las funciones del hook
const mockAddVehicle = jest.fn();
const mockUpdateVehicle = jest.fn();

describe('VehicleForm Component', () => {
  const mockVehicleData = {
    id: '1',
    license_plate: 'ABC123',
    brand: 'Toyota',
    model: 'Corolla',
    year: 2020,
    fuel_type: 'gasoline' as const,
    fuel_efficiency: 12.5,
    tank_capacity: 50,
    weight: 1500,
    dimensions: {
      length: 4.5,
      width: 1.8,
      height: 1.5,
    },
    company_id: '1',
    created_at: '2023-01-01',
    updated_at: '2023-01-01',
  };

  beforeEach(() => {
    (useVehicles as jest.Mock).mockReturnValue({
      addVehicle: mockAddVehicle,
      updateVehicle: mockUpdateVehicle,
      loading: false,
      error: null,
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  const renderVehicleForm = (initialData = null) => {
    return render(
      <Provider store={store}>
        <BrowserRouter>
          <VehicleForm initialData={initialData} />
        </BrowserRouter>
      </Provider>
    );
  };

  it('debería renderizar correctamente el formulario de vehículo', () => {
    renderVehicleForm();
    
    // Verificar que se muestran los campos del formulario
    expect(screen.getByLabelText(/patente/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/marca/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/modelo/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/año/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/tipo de combustible/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/eficiencia/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/capacidad/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/peso/i)).toBeInTheDocument();
    
    // Verificar que se muestran los botones
    expect(screen.getByRole('button', { name: /guardar/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /cancelar/i })).toBeInTheDocument();
  });

  it('debería mostrar los datos iniciales cuando se proporcionan', () => {
    renderVehicleForm(mockVehicleData);
    
    // Verificar que los campos se llenan con los datos iniciales
    expect(screen.getByLabelText(/patente/i)).toHaveValue('ABC123');
    expect(screen.getByLabelText(/marca/i)).toHaveValue('Toyota');
    expect(screen.getByLabelText(/modelo/i)).toHaveValue('Corolla');
    expect(screen.getByLabelText(/año/i)).toHaveValue(2020);
  });

  it('debería llamar a addVehicle cuando se envía un formulario nuevo', async () => {
    renderVehicleForm();
    
    // Llenar el formulario
    fireEvent.change(screen.getByLabelText(/patente/i), { target: { value: 'XYZ789' } });
    fireEvent.change(screen.getByLabelText(/marca/i), { target: { value: 'Honda' } });
    fireEvent.change(screen.getByLabelText(/modelo/i), { target: { value: 'Civic' } });
    fireEvent.change(screen.getByLabelText(/año/i), { target: { value: '2021' } });
    fireEvent.change(screen.getByLabelText(/tipo de combustible/i), { target: { value: 'diesel' } });
    fireEvent.change(screen.getByLabelText(/eficiencia/i), { target: { value: '15' } });
    fireEvent.change(screen.getByLabelText(/capacidad/i), { target: { value: '55' } });
    fireEvent.change(screen.getByLabelText(/peso/i), { target: { value: '1400' } });
    
    // Enviar el formulario
    fireEvent.click(screen.getByRole('button', { name: /guardar/i }));
    
    // Verificar que se llama a addVehicle
    await waitFor(() => {
      expect(mockAddVehicle).toHaveBeenCalledTimes(1);
    });
  });

  it('debería llamar a updateVehicle cuando se envía un formulario de edición', async () => {
    renderVehicleForm(mockVehicleData);
    
    // Cambiar un valor
    fireEvent.change(screen.getByLabelText(/modelo/i), { target: { value: 'Camry' } });
    
    // Enviar el formulario
    fireEvent.click(screen.getByRole('button', { name: /guardar/i }));
    
    // Verificar que se llama a updateVehicle
    await waitFor(() => {
      expect(mockUpdateVehicle).toHaveBeenCalledWith({
        ...mockVehicleData,
        model: 'Camry',
      });
    });
  });

  it('debería navegar hacia atrás cuando se hace clic en cancelar', () => {
    renderVehicleForm();
    
    fireEvent.click(screen.getByRole('button', { name: /cancelar/i }));
    
    expect(mockNavigate).toHaveBeenCalledWith(-1);
  });
});