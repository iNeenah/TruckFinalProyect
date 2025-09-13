# Design Document - Optimizador de Rutas con IA

## Overview

El Optimizador de Rutas con IA es una aplicación web SaaS que utiliza algoritmos de enrutamiento y datos geográficos para calcular rutas optimizadas por costo para empresas de transporte en Misiones. La arquitectura está diseñada para ser escalable, mantenible y optimizada para el contexto regional específico.

### Objetivos de Diseño
- **Precisión**: Cálculos exactos de costos basados en datos reales de combustible y peajes
- **Performance**: Respuestas rápidas en cálculo de rutas (< 3 segundos)
- **Escalabilidad**: Capacidad de manejar múltiples empresas y cálculos concurrentes
- **Mantenibilidad**: Código modular y bien documentado
- **Usabilidad**: Interfaz intuitiva para usuarios no técnicos

## Architecture

### Arquitectura General
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   External      │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   Services      │
│                 │    │                 │    │                 │
│ • Dashboard     │    │ • REST API      │    │ • OSRM Engine   │
│ • Maps UI       │    │ • Auth Service  │    │ • Google APIs   │
│ • Fleet Mgmt    │    │ • Route Engine  │    │ • OpenStreetMap │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐
                       │   Database      │
                       │  (PostgreSQL    │
                       │   + PostGIS)    │
                       └─────────────────┘
```

### Stack Tecnológico

**Frontend:**
- **Framework**: React.js 18+ con TypeScript
- **UI Library**: Material-UI (MUI) v5 para componentes consistentes
- **Maps**: Mapbox GL JS para visualización de mapas y rutas
- **State Management**: Redux Toolkit para gestión de estado global
- **HTTP Client**: Axios para comunicación con API
- **Build Tool**: Vite para desarrollo y build optimizado

**Backend:**
- **Framework**: FastAPI con Python 3.11+
- **Database**: PostgreSQL 15+ con extensión PostGIS
- **ORM**: SQLAlchemy 2.0 con Alembic para migraciones
- **Authentication**: JWT tokens con FastAPI-Users
- **Validation**: Pydantic v2 para validación de datos
- **HTTP Client**: httpx para llamadas a APIs externas

**Servicios Externos:**
- **Routing Engine**: OSRM (Open Source Routing Machine) en contenedor Docker
- **Geocoding**: Google Geocoding API para conversión dirección ↔ coordenadas
- **Maps Data**: OpenStreetMap como fuente de datos geográficos

**Infraestructura:**
- **Containerization**: Docker y Docker Compose
- **Cloud**: AWS (EC2, RDS, S3, CloudFront)
- **CI/CD**: GitHub Actions
- **Monitoring**: CloudWatch para logs y métricas

## Components and Interfaces

### Frontend Components

#### 1. Authentication Module
```typescript
interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
}

interface User {
  id: string;
  email: string;
  company: Company;
  role: 'admin' | 'operator';
}
```

#### 2. Fleet Management Module
```typescript
interface Vehicle {
  id: string;
  license_plate: string;
  model: string;
  fuel_consumption: number; // L/100km
  fuel_type: 'diesel_500' | 'diesel_premium';
  dimensions: {
    height: number; // meters
    width: number;  // meters
  };
  max_weight: number; // kg
  company_id: string;
}
```

#### 3. Route Calculator Module
```typescript
interface RouteRequest {
  origin: string | Coordinates;
  destination: string | Coordinates;
  vehicle_id: string;
}

interface RouteResponse {
  recommended_route: Route;
  alternative_routes: Route[];
  savings_analysis: SavingsAnalysis;
}

interface Route {
  id: string;
  geometry: GeoJSON.LineString;
  distance: number; // km
  duration: number; // minutes
  cost_breakdown: CostBreakdown;
  toll_points: TollPoint[];
}
```

#### 4. Map Visualization Module
```typescript
interface MapComponent {
  center: Coordinates;
  zoom: number;
  routes: Route[];
  selected_route: string | null;
  toll_markers: TollPoint[];
}
```

### Backend API Endpoints

#### Authentication Endpoints
```python
POST /auth/register
POST /auth/login
POST /auth/refresh
DELETE /auth/logout
```

#### Fleet Management Endpoints
```python
GET    /vehicles/           # List company vehicles
POST   /vehicles/           # Create vehicle
GET    /vehicles/{id}       # Get vehicle details
PUT    /vehicles/{id}       # Update vehicle
DELETE /vehicles/{id}       # Delete vehicle
```

#### Route Calculation Endpoints
```python
POST   /routes/calculate    # Calculate optimized routes
GET    /routes/{id}         # Get route details
POST   /routes/{id}/report  # Generate route report
```

#### Administration Endpoints
```python
GET    /admin/fuel-prices   # Get current fuel prices
PUT    /admin/fuel-prices   # Update fuel prices
GET    /admin/tolls         # Get toll data
PUT    /admin/tolls/{id}    # Update toll information
POST   /admin/tolls/import  # Bulk import toll data
```

### Backend Services Architecture

#### 1. Route Optimization Service
```python
class RouteOptimizationService:
    def __init__(self, osrm_client: OSRMClient, toll_service: TollService):
        self.osrm = osrm_client
        self.toll_service = toll_service
    
    async def calculate_optimal_route(
        self, 
        request: RouteRequest
    ) -> RouteResponse:
        # 1. Get multiple route alternatives from OSRM
        # 2. Calculate fuel costs for each route
        # 3. Identify and calculate toll costs
        # 4. Rank routes by total cost
        # 5. Return optimized recommendation
```

#### 2. Cost Calculation Service
```python
class CostCalculationService:
    async def calculate_fuel_cost(
        self, 
        distance_km: float, 
        vehicle: Vehicle
    ) -> float:
        fuel_price = await self.get_current_fuel_price(vehicle.fuel_type)
        consumption = (distance_km / 100) * vehicle.fuel_consumption
        return consumption * fuel_price
    
    async def calculate_toll_costs(
        self, 
        route_geometry: LineString
    ) -> List[TollCost]:
        # Use PostGIS to find tolls intersecting with route
        # Return list of toll points and costs
```

#### 3. OSRM Integration Service
```python
class OSRMClient:
    async def get_route_alternatives(
        self, 
        origin: Coordinates, 
        destination: Coordinates,
        alternatives: int = 3
    ) -> List[OSRMRoute]:
        # Call OSRM API for route alternatives
        # Return parsed route data with geometry and metadata
```

## Data Models

### Database Schema

#### Users and Companies
```sql
CREATE TABLE companies (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    company_id UUID REFERENCES companies(id),
    role VARCHAR(50) DEFAULT 'operator',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Fleet Management
```sql
CREATE TABLE vehicles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id UUID REFERENCES companies(id),
    license_plate VARCHAR(20) UNIQUE NOT NULL,
    model VARCHAR(255) NOT NULL,
    fuel_consumption DECIMAL(5,2) NOT NULL, -- L/100km
    fuel_type VARCHAR(50) NOT NULL,
    height DECIMAL(4,2), -- meters
    width DECIMAL(4,2),  -- meters
    max_weight INTEGER,  -- kg
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Pricing and Tolls
```sql
CREATE TABLE fuel_prices (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    fuel_type VARCHAR(50) NOT NULL,
    region VARCHAR(100) NOT NULL,
    price_per_liter DECIMAL(10,2) NOT NULL,
    effective_date DATE NOT NULL,
    updated_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE tolls (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    location GEOMETRY(POINT, 4326) NOT NULL,
    route_code VARCHAR(50), -- e.g., 'RN12', 'RN14'
    tariff DECIMAL(10,2) NOT NULL,
    direction VARCHAR(50), -- 'both', 'north_south', etc.
    is_active BOOLEAN DEFAULT true,
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_tolls_location ON tolls USING GIST (location);
```

#### Route History
```sql
CREATE TABLE calculated_routes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    vehicle_id UUID REFERENCES vehicles(id),
    origin_address TEXT,
    destination_address TEXT,
    origin_coords GEOMETRY(POINT, 4326),
    destination_coords GEOMETRY(POINT, 4326),
    selected_route_geometry GEOMETRY(LINESTRING, 4326),
    total_distance DECIMAL(8,2), -- km
    total_duration INTEGER,      -- minutes
    fuel_cost DECIMAL(10,2),
    toll_cost DECIMAL(10,2),
    total_cost DECIMAL(10,2),
    savings_amount DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Error Handling

### Frontend Error Handling
```typescript
interface ApiError {
  code: string;
  message: string;
  details?: any;
}

class ErrorHandler {
  static handleRouteCalculationError(error: ApiError): string {
    switch (error.code) {
      case 'GEOCODING_FAILED':
        return 'No se pudo encontrar la dirección especificada';
      case 'NO_ROUTE_FOUND':
        return 'No se encontró una ruta válida entre los puntos';
      case 'OSRM_UNAVAILABLE':
        return 'Servicio de rutas temporalmente no disponible';
      default:
        return 'Error inesperado al calcular la ruta';
    }
  }
}
```

### Backend Error Handling
```python
class RouteCalculationError(Exception):
    def __init__(self, code: str, message: str, details: dict = None):
        self.code = code
        self.message = message
        self.details = details or {}

@app.exception_handler(RouteCalculationError)
async def route_error_handler(request: Request, exc: RouteCalculationError):
    return JSONResponse(
        status_code=400,
        content={
            "code": exc.code,
            "message": exc.message,
            "details": exc.details
        }
    )
```

### Error Recovery Strategies
- **OSRM Unavailable**: Fallback to cached routes or Google Directions API
- **Geocoding Failures**: Suggest alternative address formats
- **Database Timeouts**: Implement retry logic with exponential backoff
- **Invalid Vehicle Data**: Provide clear validation messages

## Testing Strategy

### Frontend Testing
```typescript
// Unit Tests - Jest + React Testing Library
describe('RouteCalculator', () => {
  test('should calculate route when valid inputs provided', async () => {
    // Test route calculation component
  });
  
  test('should show error when invalid address entered', () => {
    // Test error handling
  });
});

// Integration Tests - Cypress
describe('Route Calculation Flow', () => {
  it('should complete full route calculation workflow', () => {
    // End-to-end test of route calculation
  });
});
```

### Backend Testing
```python
# Unit Tests - pytest
class TestRouteOptimizationService:
    async def test_calculate_optimal_route_success(self):
        # Test successful route calculation
        pass
    
    async def test_calculate_optimal_route_no_route_found(self):
        # Test error handling when no route exists
        pass

# Integration Tests
class TestRouteAPI:
    async def test_calculate_route_endpoint(self, client: TestClient):
        # Test API endpoint with real database
        pass
```

### Performance Testing
- **Load Testing**: Simulate 100+ concurrent route calculations
- **Database Performance**: Test PostGIS queries with large datasets
- **OSRM Performance**: Measure response times for different route complexities
- **Memory Usage**: Monitor memory consumption during peak usage

### Test Data Strategy
- **Synthetic Data**: Generate test routes covering major highways (RN12, RN14)
- **Real Coordinates**: Use actual Misiones locations for realistic testing
- **Edge Cases**: Test with invalid coordinates, extreme distances, missing toll data
- **Performance Data**: Large datasets to test scalability limits

## Security Considerations

### Authentication & Authorization
- JWT tokens with 24-hour expiration
- Role-based access control (Admin vs Operator)
- Password hashing with bcrypt
- Rate limiting on authentication endpoints

### Data Protection
- HTTPS enforcement in production
- Input validation and sanitization
- SQL injection prevention via ORM
- XSS protection with Content Security Policy

### API Security
- CORS configuration for frontend domain only
- Request size limits to prevent DoS
- API rate limiting per user/company
- Audit logging for sensitive operations

### Infrastructure Security
- VPC with private subnets for database
- Security groups restricting database access
- Regular security updates for dependencies
- Encrypted data at rest and in transit