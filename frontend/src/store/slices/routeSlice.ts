import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { 
  RouteRequest, 
  RouteResponse, 
  RouteHistory, 
  RouteStatistics,
  RoutePlanningState,
  RouteCalculationProgress 
} from '@types/route';
import { routeService } from '@services/routeService';

interface RouteState {
  // Current route calculation
  currentRouteResponse: RouteResponse | null;
  isCalculating: boolean;
  calculationProgress: RouteCalculationProgress | null;
  
  // Route history
  routeHistory: RouteHistory[];
  historyLoading: boolean;
  historyTotal: number;
  
  // Route statistics
  statistics: RouteStatistics | null;
  statisticsLoading: boolean;
  
  // Route planning state
  planning: RoutePlanningState;
  
  // UI state
  selectedRouteId: string | null;
  showAlternatives: boolean;
  showTolls: boolean;
  
  // Error handling
  error: string | null;
  lastUpdated: Date | null;
}

const initialState: RouteState = {
  currentRouteResponse: null,
  isCalculating: false,
  calculationProgress: null,
  
  routeHistory: [],
  historyLoading: false,
  historyTotal: 0,
  
  statistics: null,
  statisticsLoading: false,
  
  planning: {
    origin: { address: '', coordinates: null },
    destination: { address: '', coordinates: null },
    selectedVehicle: null,
    optimizationCriteria: 'cost',
    avoidTolls: false,
    maxAlternatives: 3,
  },
  
  selectedRouteId: null,
  showAlternatives: true,
  showTolls: true,
  
  error: null,
  lastUpdated: null,
};

// Async thunks
export const calculateRoute = createAsyncThunk(
  'routes/calculateRoute',
  async (request: RouteRequest, { rejectWithValue, dispatch }) => {
    try {
      // Set initial progress
      dispatch(setCalculationProgress({
        step: 'geocoding',
        progress: 10,
        message: 'Geocodificando direcciones...'
      }));
      
      const response = await routeService.calculateRoute(request);
      
      // Set completion progress
      dispatch(setCalculationProgress({
        step: 'complete',
        progress: 100,
        message: 'Cálculo completado'
      }));
      
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to calculate route');
    }
  }
);

export const fetchRouteHistory = createAsyncThunk(
  'routes/fetchRouteHistory',
  async (params: { page?: number; size?: number; vehicleId?: string }, { rejectWithValue }) => {
    try {
      const response = await routeService.getRouteHistory(params);
      return response;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch route history');
    }
  }
);

export const fetchRouteStatistics = createAsyncThunk(
  'routes/fetchRouteStatistics',
  async (days: number = 30, { rejectWithValue }) => {
    try {
      const statistics = await routeService.getRouteStatistics(days);
      return statistics;
    } catch (error: any) {
      return rejectWithValue(error.response?.data?.detail || 'Failed to fetch route statistics');
    }
  }
);

const routeSlice = createSlice({
  name: 'routes',
  initialState,
  reducers: {
    clearError: (state) => {
      state.error = null;
    },
    
    // Planning state management
    setOrigin: (state, action: PayloadAction<{ address: string; coordinates?: any }>) => {
      state.planning.origin = {
        address: action.payload.address,
        coordinates: action.payload.coordinates || null,
      };
    },
    
    setDestination: (state, action: PayloadAction<{ address: string; coordinates?: any }>) => {
      state.planning.destination = {
        address: action.payload.address,
        coordinates: action.payload.coordinates || null,
      };
    },
    
    setSelectedVehicle: (state, action: PayloadAction<string | null>) => {
      state.planning.selectedVehicle = action.payload;
    },
    
    setOptimizationCriteria: (state, action: PayloadAction<'cost' | 'time' | 'distance'>) => {
      state.planning.optimizationCriteria = action.payload;
    },
    
    setAvoidTolls: (state, action: PayloadAction<boolean>) => {
      state.planning.avoidTolls = action.payload;
    },
    
    setMaxAlternatives: (state, action: PayloadAction<number>) => {
      state.planning.maxAlternatives = action.payload;
    },
    
    // UI state management
    setSelectedRouteId: (state, action: PayloadAction<string | null>) => {
      state.selectedRouteId = action.payload;
    },
    
    setShowAlternatives: (state, action: PayloadAction<boolean>) => {
      state.showAlternatives = action.payload;
    },
    
    setShowTolls: (state, action: PayloadAction<boolean>) => {
      state.showTolls = action.payload;
    },
    
    // Calculation progress
    setCalculationProgress: (state, action: PayloadAction<RouteCalculationProgress>) => {
      state.calculationProgress = action.payload;
    },
    
    clearCalculationProgress: (state) => {
      state.calculationProgress = null;
    },
    
    // Clear current route
    clearCurrentRoute: (state) => {
      state.currentRouteResponse = null;
      state.selectedRouteId = null;
      state.calculationProgress = null;
    },
    
    // Reset planning state
    resetPlanning: (state) => {
      state.planning = initialState.planning;
    },
  },
  extraReducers: (builder) => {
    builder
      // Calculate route
      .addCase(calculateRoute.pending, (state) => {
        state.isCalculating = true;
        state.error = null;
        state.currentRouteResponse = null;
      })
      .addCase(calculateRoute.fulfilled, (state, action) => {
        state.isCalculating = false;
        state.currentRouteResponse = action.payload;
        state.selectedRouteId = action.payload.recommended_route.id;
        state.lastUpdated = new Date();
        state.error = null;
        state.calculationProgress = null;
      })
      .addCase(calculateRoute.rejected, (state, action) => {
        state.isCalculating = false;
        state.error = action.payload as string;
        state.calculationProgress = null;
      })
      
      // Fetch route history
      .addCase(fetchRouteHistory.pending, (state) => {
        state.historyLoading = true;
        state.error = null;
      })
      .addCase(fetchRouteHistory.fulfilled, (state, action) => {
        state.historyLoading = false;
        state.routeHistory = action.payload.routes;
        state.historyTotal = action.payload.total;
        state.error = null;
      })
      .addCase(fetchRouteHistory.rejected, (state, action) => {
        state.historyLoading = false;
        state.error = action.payload as string;
      })
      
      // Fetch route statistics
      .addCase(fetchRouteStatistics.pending, (state) => {
        state.statisticsLoading = true;
        state.error = null;
      })
      .addCase(fetchRouteStatistics.fulfilled, (state, action) => {
        state.statisticsLoading = false;
        state.statistics = action.payload;
        state.error = null;
      })
      .addCase(fetchRouteStatistics.rejected, (state, action) => {
        state.statisticsLoading = false;
        state.error = action.payload as string;
      });
  },
});

export const {
  clearError,
  setOrigin,
  setDestination,
  setSelectedVehicle,
  setOptimizationCriteria,
  setAvoidTolls,
  setMaxAlternatives,
  setSelectedRouteId,
  setShowAlternatives,
  setShowTolls,
  setCalculationProgress,
  clearCalculationProgress,
  clearCurrentRoute,
  resetPlanning,
} = routeSlice.actions;

export default routeSlice.reducer;