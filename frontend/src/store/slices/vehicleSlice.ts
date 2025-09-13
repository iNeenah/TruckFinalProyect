import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { Vehicle, CreateVehicleRequest, UpdateVehicleRequest } from '@types/vehicle';
import { vehicleService } from '@services/vehicleService';

interface VehicleState {
  vehicles: Vehicle[];
  selectedVehicle: Vehicle | null;
  isLoading: boolean;
  error: string | null;
  lastUpdated: Date | null;
}

const initialState: VehicleState = {
  vehicles: [],
  selectedVehicle: null,
  isLoading: false,
  error: null,
  lastUpdated: null,
};

// Async thunks
export const fetchVehicles = createAsyncThunk(
  'vehicles/fetchVehicles',
  async (_, { rejectWithValue }) => {
    try {
      const vehicles = await vehicleService.getVehicles();
      return vehicles;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch vehicles');
    }
  }
);

export const createVehicle = createAsyncThunk(
  'vehicles/createVehicle',
  async (vehicleData: CreateVehicleRequest, { rejectWithValue }) => {
    try {
      const vehicle = await vehicleService.createVehicle(vehicleData);
      return vehicle;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to create vehicle');
    }
  }
);

export const updateVehicle = createAsyncThunk(
  'vehicles/updateVehicle',
  async ({ id, data }: { id: string; data: UpdateVehicleRequest }, { rejectWithValue }) => {
    try {
      const vehicle = await vehicleService.updateVehicle(id, data);
      return vehicle;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to update vehicle');
    }
  }
);

export const deleteVehicle = createAsyncThunk(
  'vehicles/deleteVehicle',
  async (id: string, { rejectWithValue }) => {
    try {
      await vehicleService.deleteVehicle(id);
      return id;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to delete vehicle');
    }
  }
);

const vehicleSlice = createSlice({
  name: 'vehicles',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    setSelectedVehicle: (state, action: PayloadAction<Vehicle | null>) => {
      state.selectedVehicle = action.payload;
    },
    clearSelectedVehicle: (state) => {
      state.selectedVehicle = null;
    },
  },
  extraReducers: (builder) => {
    builder
      // Fetch vehicles
      .addCase(fetchVehicles.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(fetchVehicles.fulfilled, (state, action) => {
        state.isLoading = false;
        state.vehicles = action.payload;
        state.lastUpdated = new Date();
        state.error = null;
      })
      .addCase(fetchVehicles.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Create vehicle
      .addCase(createVehicle.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(createVehicle.fulfilled, (state, action) => {
        state.isLoading = false;
        state.vehicles.push(action.payload);
        state.error = null;
      })
      .addCase(createVehicle.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Update vehicle
      .addCase(updateVehicle.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(updateVehicle.fulfilled, (state, action) => {
        state.isLoading = false;
        const index = state.vehicles.findIndex(v => v.id === action.payload.id);
        if (index !== -1) {
          state.vehicles[index] = action.payload;
        }
        if (state.selectedVehicle?.id === action.payload.id) {
          state.selectedVehicle = action.payload;
        }
        state.error = null;
      })
      .addCase(updateVehicle.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      })
      // Delete vehicle
      .addCase(deleteVehicle.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(deleteVehicle.fulfilled, (state, action) => {
        state.isLoading = false;
        state.vehicles = state.vehicles.filter(v => v.id !== action.payload);
        if (state.selectedVehicle?.id === action.payload) {
          state.selectedVehicle = null;
        }
        state.error = null;
      })
      .addCase(deleteVehicle.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.payload as string;
      });
  },
});

export const { clearError, setSelectedVehicle, clearSelectedVehicle } = vehicleSlice.actions;
export default vehicleSlice.reducer;