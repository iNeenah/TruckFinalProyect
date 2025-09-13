# Documentación de Componentes Frontend

## Estructura de Componentes

### Layout
- [Layout](#layout)
- [Header](#header)
- [Sidebar](#sidebar)
- [MainLayout](#mainlayout)

### Autenticación
- [LoginForm](#loginform)
- [RegisterForm](#registerform)
- [AuthLayout](#authlayout)

### Vehículos
- [VehicleTable](#vehicletable)
- [VehicleForm](#vehicleform)
- [VehicleSelector](#vehicleselector)
- [VehicleStatsCards](#vehiclestatscards)
- [VehicleFiltersPanel](#vehiclefilterspanel)

### Rutas
- [RouteCalculationForm](#routecalculationform)
- [RouteResultsDisplay](#routeresultsdisplay)
- [RouteMap](#routemap)
- [RouteLayer](#routelayer)

### Mapas
- [BaseMap](#basemap)
- [MapMarker](#mapmarker)
- [MapControls](#mapcontrols)
- [LocationInput](#locationinput)

### Reportes
- [ReportsPage](#reportspage)
- [StatisticsChart](#statisticschart)
- [CostAnalysis](#costanalysis)

### Administración
- [AdminPanelPage](#adminpanelpage)
- [TollsManagement](#tollsmanagement)
- [FuelPricesManagement](#fuelpricesmanagement)
- [UserManagement](#usermanagement)

## Detalles de Componentes

### Layout

#### Layout
Componente principal que envuelve toda la aplicación con el layout base.

**Props:**
```typescript
interface LayoutProps {
  children?: React.ReactNode;
}
```

#### Header
Barra de encabezado con información del usuario y controles de tema.

**Props:**
```typescript
interface HeaderProps {
  // Sin props específicas
}
```

#### Sidebar
Barra lateral de navegación con enlaces a las diferentes secciones.

**Props:**
```typescript
interface SidebarProps {
  // Sin props específicas
}
```

#### MainLayout
Layout principal que contiene el contenido de las páginas.

**Props:**
```typescript
interface MainLayoutProps {
  children?: React.ReactNode;
}
```

### Autenticación

#### LoginForm
Formulario de inicio de sesión con validación.

**Props:**
```typescript
interface LoginFormProps {
  // Sin props específicas
}
```

#### RegisterForm
Formulario de registro con validación.

**Props:**
```typescript
interface RegisterFormProps {
  // Sin props específicas
}
```

#### AuthLayout
Layout para páginas de autenticación.

**Props:**
```typescript
interface AuthLayoutProps {
  children?: React.ReactNode;
}
```

### Vehículos

#### VehicleTable
Tabla para mostrar la lista de vehículos con acciones.

**Props:**
```typescript
interface VehicleTableProps {
  vehicles: Vehicle[];
  onEdit: (vehicle: Vehicle) => void;
  onDelete?: (vehicleId: string) => void;
  loading?: boolean;
}
```

#### VehicleForm
Formulario para crear/editar vehículos con validación.

**Props:**
```typescript
interface VehicleFormProps {
  initialData?: Vehicle | null;
  onSubmit?: (vehicle: CreateVehicleRequest | UpdateVehicleRequest) => void;
  onCancel?: () => void;
}
```

#### VehicleSelector
Selector de vehículos para usar en formularios.

**Props:**
```typescript
interface VehicleSelectorProps {
  selectedVehicleId?: string;
  onVehicleSelect: (vehicleId: string) => void;
  disabled?: boolean;
}
```

#### VehicleStatsCards
Tarjetas con estadísticas de vehículos.

**Props:**
```typescript
interface VehicleStatsCardsProps {
  vehicles: Vehicle[];
}
```

#### VehicleFiltersPanel
Panel de filtros para la lista de vehículos.

**Props:**
```typescript
interface VehicleFiltersPanelProps {
  onFilterChange: (filters: VehicleFilters) => void;
}
```

### Rutas

#### RouteCalculationForm
Formulario para calcular rutas entre dos puntos.

**Props:**
```typescript
interface RouteCalculationFormProps {
  // Sin props específicas
}
```

#### RouteResultsDisplay
Componente para mostrar los resultados de rutas calculadas.

**Props:**
```typescript
interface RouteResultsDisplayProps {
  routes: CalculatedRoute[];
  selectedRoute?: CalculatedRoute | null;
  onSelectRoute?: (route: CalculatedRoute) => void;
  onSaveRoute?: (route: CalculatedRoute) => void;
}
```

#### RouteMap
Mapa para visualizar rutas calculadas.

**Props:**
```typescript
interface RouteMapProps {
  routes: CalculatedRoute[];
  selectedRoute?: CalculatedRoute | null;
  onRouteSelect?: (route: CalculatedRoute) => void;
}
```

#### RouteLayer
Capa para renderizar una ruta en el mapa.

**Props:**
```typescript
interface RouteLayerProps {
  route: CalculatedRoute;
  isSelected?: boolean;
  onClick?: () => void;
}
```

### Mapas

#### BaseMap
Componente base del mapa usando Mapbox GL JS.

**Props:**
```typescript
interface BaseMapProps {
  center?: [number, number];
  zoom?: number;
  children?: React.ReactNode;
  onMapLoad?: (map: mapboxgl.Map) => void;
}
```

#### MapMarker
Marcador para mostrar puntos en el mapa.

**Props:**
```typescript
interface MapMarkerProps {
  position: [number, number];
  children?: React.ReactNode;
  onClick?: () => void;
}
```

#### MapControls
Controles para el mapa (zoom, ubicación actual, etc.).

**Props:**
```typescript
interface MapControlsProps {
  // Sin props específicas
}
```

#### LocationInput
Campo de entrada con autocompletado para direcciones.

**Props:**
```typescript
interface LocationInputProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  onLocationSelect?: (location: Location) => void;
}
```

### Reportes

#### ReportsPage
Página principal de reportes con estadísticas y análisis.

**Props:**
```typescript
interface ReportsPageProps {
  // Sin props específicas
}
```

#### StatisticsChart
Gráfico de estadísticas de uso.

**Props:**
```typescript
interface StatisticsChartProps {
  data: StatisticsData[];
}
```

#### CostAnalysis
Análisis de costos de rutas.

**Props:**
```typescript
interface CostAnalysisProps {
  routes: CalculatedRoute[];
}
```

### Administración

#### AdminPanelPage
Panel de administración con acceso a gestión de datos maestros.

**Props:**
```typescript
interface AdminPanelPageProps {
  // Sin props específicas
}
```

#### TollsManagement
Gestión de peajes con CRUD.

**Props:**
```typescript
interface TollsManagementProps {
  // Sin props específicas
}
```

#### FuelPricesManagement
Gestión de precios de combustible con CRUD.

**Props:**
```typescript
interface FuelPricesManagementProps {
  // Sin props específicas
}
```

#### UserManagement
Gestión de usuarios con CRUD.

**Props:**
```typescript
interface UserManagementProps {
  // Sin props específicas
}
```

## Hooks Personalizados

### useAuth
Hook para manejar la autenticación del usuario.

**Uso:**
```typescript
const { user, login, logout, register, loading, error } = useAuth();
```

### useVehicles
Hook para manejar la gestión de vehículos.

**Uso:**
```typescript
const { vehicles, fetchVehicles, addVehicle, updateVehicle, deleteVehicle, loading, error } = useVehicles();
```

### useRoutes
Hook para manejar el cálculo y gestión de rutas.

**Uso:**
```typescript
const { 
  calculateRoutes, 
  saveRoute, 
  fetchSavedRoutes, 
  deleteRoute, 
  routes, 
  savedRoutes, 
  selectedRoute, 
  selectRoute, 
  loading, 
  error 
} = useRoutes();
```

### useMap
Hook para manejar la interacción con el mapa.

**Uso:**
```typescript
const { map, setMap, addMarker, removeMarker, fitBounds } = useMap();
```

### useOptimizedMap
Hook para optimizar el rendimiento del mapa.

**Uso:**
```typescript
const { 
  mapState, 
  setupMapOptimizations, 
  useMarkerOptimization, 
  optimizeLayerUpdate, 
  mapRef 
} = useOptimizedMap(options);
```

## Servicios

### AuthService
Servicio para manejar la autenticación con el backend.

**Métodos:**
- `login(credentials: LoginRequest): Promise<LoginResponse>`
- `register(userData: RegisterRequest): Promise<User>`
- `logout(): Promise<void>`
- `refreshToken(): Promise<LoginResponse>`

### VehicleService
Servicio para manejar la gestión de vehículos con el backend.

**Métodos:**
- `fetchVehicles(): Promise<Vehicle[]>`
- `fetchVehicleById(id: string): Promise<Vehicle>`
- `createVehicle(vehicleData: CreateVehicleRequest): Promise<Vehicle>`
- `updateVehicle(id: string, vehicleData: UpdateVehicleRequest): Promise<Vehicle>`
- `deleteVehicle(id: string): Promise<void>`
- `calculateFuelConsumption(distance: number, fuelEfficiency: number): number`

### RouteService
Servicio para manejar el cálculo y gestión de rutas con el backend.

**Métodos:**
- `calculateRoutes(request: CalculateRouteRequest): Promise<CalculatedRoute[]>`
- `fetchSavedRoutes(): Promise<CalculatedRoute[]>`
- `saveRoute(routeData: SaveRouteRequest): Promise<CalculatedRoute>`
- `fetchSavedRouteById(id: string): Promise<CalculatedRoute>`
- `deleteSavedRoute(id: string): Promise<void>`

### ReportService
Servicio para manejar la generación de reportes con el backend.

**Métodos:**
- `fetchStatistics(): Promise<Statistics>`
- `generateReport(reportData: GenerateReportRequest): Promise<Report>`
- `exportToPDF(reportId: string): Promise<Blob>`

### ApiService
Cliente HTTP base para comunicarse con el backend.

**Métodos:**
- `get<T>(url: string): Promise<T>`
- `post<T>(url: string, data: any): Promise<T>`
- `put<T>(url: string, data: any): Promise<T>`
- `delete<T>(url: string): Promise<T>`
- `uploadFile<T>(url: string, file: File): Promise<T>`