# Guía para Desarrolladores - Optimizador de Rutas con IA

## Índice
1. [Arquitectura del Sistema](#arquitectura-del-sistema)
2. [Tecnologías Utilizadas](#tecnologías-utilizadas)
3. [Estructura del Proyecto](#estructura-del-proyecto)
4. [Configuración del Entorno de Desarrollo](#configuración-del-entorno-de-desarrollo)
5. [Desarrollo Backend](#desarrollo-backend)
6. [Desarrollo Frontend](#desarrollo-frontend)
7. [Pruebas](#pruebas)
8. [Despliegue](#despliegue)
9. [Monitoreo y Logging](#monitoreo-y-logging)
10. [Contribución](#contribución)

## Arquitectura del Sistema

### Diagrama de Arquitectura
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │   API Gateway    │    │   Backend       │
│   (React)       │◄──►│   (FastAPI)      │◄──►│   (FastAPI)     │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │                         │
                              ▼                         ▼
                       ┌─────────────┐         ┌─────────────────┐
                       │  Database   │         │   Services      │
                       │ (PostgreSQL │         │ (OSRM, Mapbox)  │
                       │  + PostGIS) │         └─────────────────┘
                       └─────────────┘
                              │
                              ▼
                       ┌─────────────┐
                       │   Storage   │
                       │  (Docker    │
                       │   Volumes)  │
                       └─────────────┘
```

### Componentes Principales
1. **Frontend**: Aplicación React con TypeScript
2. **Backend API**: Servidor FastAPI con PostgreSQL
3. **Servicios Externos**: OSRM para rutas, Mapbox para mapas
4. **Base de Datos**: PostgreSQL con PostGIS para datos geoespaciales
5. **Infraestructura**: Docker y Docker Compose

## Tecnologías Utilizadas

### Backend
- **FastAPI**: Framework web para Python
- **PostgreSQL**: Base de datos relacional
- **PostGIS**: Extensión geoespacial para PostgreSQL
- **SQLAlchemy**: ORM para Python
- **Pydantic**: Validación de datos
- **JWT**: Autenticación basada en tokens
- **OSRM**: Servicio de enrutamiento de código abierto
- **Uvicorn**: Servidor ASGI para FastAPI

### Frontend
- **React**: Biblioteca de JavaScript para interfaces de usuario
- **TypeScript**: Superset tipado de JavaScript
- **Material-UI**: Componentes de interfaz de usuario
- **Redux Toolkit**: Manejo de estado de la aplicación
- **React Router**: Enrutamiento de la aplicación
- **Mapbox GL JS**: Biblioteca para mapas interactivos
- **Axios**: Cliente HTTP
- **Jest**: Framework de pruebas
- **Cypress**: Pruebas E2E

### Infraestructura
- **Docker**: Contenedores de aplicación
- **Docker Compose**: Orquestación de contenedores
- **Nginx**: Servidor web y proxy inverso
- **Make**: Herramienta de automatización

## Estructura del Proyecto

```
misiones/
├── backend/                 # Código del backend
│   ├── app/                 # Aplicación FastAPI
│   │   ├── api/             # Endpoints de la API
│   │   ├── core/            # Configuración y seguridad
│   │   ├── models/          # Modelos de base de datos
│   │   ├── schemas/         # Esquemas Pydantic
│   │   ├── services/        # Lógica de negocio
│   │   ├── utils/           # Utilidades
│   │   └── main.py          # Punto de entrada
│   ├── tests/               # Pruebas del backend
│   └── Dockerfile           # Dockerfile del backend
├── frontend/                # Código del frontend
│   ├── src/                 # Código fuente
│   │   ├── components/      # Componentes React
│   │   ├── pages/           # Páginas de la aplicación
│   │   ├── services/        # Servicios API
│   │   ├── store/           # Estado de Redux
│   │   ├── hooks/           # Hooks personalizados
│   │   ├── contexts/        # Contextos de React
│   │   ├── types/           # Tipos TypeScript
│   │   └── utils/           # Utilidades
│   ├── __tests__/           # Pruebas del frontend
│   └── Dockerfile           # Dockerfile del frontend
├── docker/                  # Configuración de Docker
├── docs/                    # Documentación
├── scripts/                 # Scripts de utilidad
├── .github/                 # Configuración de GitHub
└── docker-compose.yml       # Configuración de Docker Compose
```

## Configuración del Entorno de Desarrollo

### Requisitos Previos
1. **Docker** y **Docker Compose**
2. **Node.js** (versión 16 o superior)
3. **Python** (versión 3.9 o superior)
4. **Git**

### Variables de Entorno
Crear archivo `.env` en la raíz del proyecto:

```bash
# Backend
DATABASE_URL=postgresql://user:password@localhost:5432/kiro
SECRET_KEY=your-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Frontend
VITE_API_BASE_URL=http://localhost:8000
VITE_MAPBOX_TOKEN=your-mapbox-token

# OSRM
OSRM_HOST=osrm
OSRM_PORT=5000
```

### Iniciar el Entorno de Desarrollo
```bash
# Clonar el repositorio
git clone <repositorio-url>
cd misiones

# Iniciar servicios con Docker
docker-compose up -d

# Instalar dependencias del frontend
cd frontend
npm install

# Iniciar servidor de desarrollo del frontend
npm run dev
```

## Desarrollo Backend

### Estructura de una API
```python
# app/api/v1/vehicles.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import schemas, services, models
from app.core.database import get_db
from app.core.security import get_current_user

router = APIRouter(prefix="/vehicles", tags=["vehicles"])

@router.get("/", response_model=list[schemas.Vehicle])
def get_vehicles(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return services.vehicle.get_user_vehicles(db, current_user.id)
```

### Crear un Nuevo Endpoint
1. Crear esquema en `app/schemas/`
2. Crear modelo en `app/models/` (si es necesario)
3. Crear servicio en `app/services/`
4. Crear endpoint en `app/api/v1/`

### Migraciones de Base de Datos
```bash
# Crear nueva migración
alembic revision --autogenerate -m "Descripción de cambios"

# Aplicar migraciones
alembic upgrade head
```

## Desarrollo Frontend

### Estructura de un Componente
```typescript
// src/components/Vehicles/VehicleTable.tsx
import React from 'react';
import { Vehicle } from '@types';

interface VehicleTableProps {
  vehicles: Vehicle[];
  onEdit: (vehicle: Vehicle) => void;
  onDelete: (vehicleId: string) => void;
}

const VehicleTable: React.FC<VehicleTableProps> = ({ 
  vehicles, 
  onEdit, 
  onDelete 
}) => {
  return (
    <table>
      <thead>
        <tr>
          <th>Patente</th>
          <th>Marca</th>
          <th>Modelo</th>
          <th>Acciones</th>
        </tr>
      </thead>
      <tbody>
        {vehicles.map(vehicle => (
          <tr key={vehicle.id}>
            <td>{vehicle.license_plate}</td>
            <td>{vehicle.brand}</td>
            <td>{vehicle.model}</td>
            <td>
              <button onClick={() => onEdit(vehicle)}>Editar</button>
              <button onClick={() => onDelete(vehicle.id)}>Eliminar</button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default VehicleTable;
```

### Crear un Nuevo Componente
1. Crear archivo en `src/components/` o `src/pages/`
2. Definir props con interfaces TypeScript
3. Implementar lógica del componente
4. Agregar estilos si es necesario

### Hooks Personalizados
```typescript
// src/hooks/useVehicles.ts
import { useState, useEffect } from 'react';
import { Vehicle } from '@types';
import { vehicleService } from '@services';

export const useVehicles = () => {
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchVehicles = async () => {
    try {
      setLoading(true);
      const data = await vehicleService.fetchVehicles();
      setVehicles(data);
    } catch (err) {
      setError('Error al cargar vehículos');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchVehicles();
  }, []);

  return { vehicles, loading, error, fetchVehicles };
};
```

## Pruebas

### Pruebas Unitarias (Backend)
```bash
# Ejecutar pruebas unitarias
cd backend
pytest tests/

# Ejecutar pruebas con cobertura
pytest --cov=app tests/
```

### Pruebas Unitarias (Frontend)
```bash
# Ejecutar pruebas unitarias
cd frontend
npm run test

# Ejecutar pruebas con cobertura
npm run test:coverage
```

### Pruebas E2E (Frontend)
```bash
# Ejecutar pruebas E2E
cd frontend
npm run cypress:open

# Ejecutar pruebas E2E en modo headless
npm run cypress:run
```

### Escribir Pruebas
```python
# backend/tests/test_vehicles.py
import pytest
from app.services import vehicle

def test_calculate_fuel_consumption():
    distance = 100  # km
    efficiency = 10  # km/l
    expected = 10  # liters
    
    result = vehicle.calculate_fuel_consumption(distance, efficiency)
    
    assert result == expected
```

```typescript
// frontend/src/__tests__/unit/VehicleTable.test.tsx
import { render, screen } from '@testing-library/react';
import VehicleTable from '@components/Vehicles/VehicleTable';

const mockVehicles = [
  {
    id: '1',
    license_plate: 'ABC123',
    brand: 'Toyota',
    model: 'Corolla',
    // ... otros campos
  },
];

describe('VehicleTable', () => {
  it('debería mostrar los vehículos correctamente', () => {
    render(
      <VehicleTable 
        vehicles={mockVehicles} 
        onEdit={jest.fn()} 
        onDelete={jest.fn()} 
      />
    );
    
    expect(screen.getByText('ABC123')).toBeInTheDocument();
    expect(screen.getByText('Toyota')).toBeInTheDocument();
    expect(screen.getByText('Corolla')).toBeInTheDocument();
  });
});
```

## Despliegue

### Configuración de Producción
1. Configurar variables de entorno para producción
2. Configurar dominio y SSL
3. Configurar base de datos de producción
4. Configurar servicios externos (Mapbox, OSRM)

### Despliegue con Docker
```bash
# Construir imágenes
docker-compose build

# Iniciar servicios en modo producción
docker-compose -f docker-compose.yml up -d
```

### Despliegue en AWS
1. Crear instancia EC2
2. Configurar RDS para PostgreSQL
3. Configurar S3 para almacenamiento
4. Configurar Route 53 para DNS
5. Configurar CloudFront para CDN

### CI/CD con GitHub Actions
```yaml
# .github/workflows/deploy.yml
name: Deploy
on:
  push:
    branches: [ main ]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to production
        run: |
          # Comandos de despliegue
          docker-compose pull
          docker-compose up -d
```

## Monitoreo y Logging

### Logging en Backend
```python
# app/core/logging.py
import logging
from app.core.config import settings

logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)
```

### Monitoreo de Rendimiento
- **Backend**: Uso de Prometheus y Grafana
- **Frontend**: Uso de Sentry para errores
- **Base de datos**: Monitoreo de consultas lentas
- **Infraestructura**: Monitoreo de contenedores Docker

### Métricas Clave
- Tiempo de respuesta de API
- Uso de CPU y memoria
- Número de usuarios activos
- Tasa de errores
- Tiempo de carga de página

## Contribución

### Flujo de Trabajo Git
1. Crear rama feature desde `main`
2. Hacer commits con mensajes descriptivos
3. Abrir Pull Request para revisión
4. Pasar pruebas automatizadas
5. Merge a `main` después de aprobación

### Convenciones de Código
- **Backend**: Seguir PEP 8 para Python
- **Frontend**: Seguir guía de estilo de TypeScript/React
- **Commits**: Usar mensajes en presente imperativo en inglés
- **Documentación**: Mantener actualizada la documentación

### Proceso de Revisión
1. Revisión de código por pares
2. Pruebas automatizadas
3. Revisión de documentación
4. Aprobación de mantenedores

### Reporte de Issues
- Usar plantillas de issues
- Incluir pasos para reproducir
- Incluir versión del sistema
- Incluir logs relevantes