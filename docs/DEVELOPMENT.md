# Development Guide

## Configuración del Entorno de Desarrollo

### Prerrequisitos

- Docker y Docker Compose
- Node.js 18+
- Python 3.11+
- Git

### Configuración Inicial

1. **Clonar el repositorio**
```bash
git clone <repository-url>
cd optimizador-rutas-ia
```

2. **Configurar el entorno**
```bash
make setup
```

3. **Editar variables de entorno**
```bash
# Editar .env con tus configuraciones
cp .env.example .env
```

4. **Descargar datos de OSRM (opcional)**
```bash
make download-osrm-data
```

5. **Iniciar servicios de desarrollo**
```bash
make dev-up
```

## Estructura del Proyecto

```
optimizador-rutas-ia/
├── backend/                 # FastAPI backend
│   ├── app/                # Application code
│   ├── alembic/            # Database migrations
│   ├── tests/              # Backend tests
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile         # Backend container
├── frontend/               # React frontend
│   ├── src/               # Source code
│   ├── public/            # Static assets
│   ├── tests/             # Frontend tests
│   ├── package.json       # Node dependencies
│   └── Dockerfile         # Frontend container
├── docker/                # Docker configurations
├── docs/                  # Documentation
├── .github/               # CI/CD workflows
└── docker-compose.yml     # Development services
```

## Comandos de Desarrollo

### Servicios
```bash
make dev-up      # Iniciar servicios
make dev-down    # Detener servicios
make clean       # Limpiar todo
make logs        # Ver logs de todos los servicios
```

### Base de Datos
```bash
make db-migrate  # Ejecutar migraciones
make db-reset    # Resetear base de datos
```

### Testing
```bash
make test        # Ejecutar todos los tests
make lint        # Verificar código
make format      # Formatear código
```

## Desarrollo Backend

### Estructura del Backend
```
backend/
├── app/
│   ├── main.py            # FastAPI app
│   ├── config.py          # Configuration
│   ├── database.py        # Database setup
│   ├── models/            # SQLAlchemy models
│   ├── schemas/           # Pydantic schemas
│   ├── api/               # API routes
│   ├── services/          # Business logic
│   └── utils/             # Utilities
├── alembic/               # Database migrations
└── tests/                 # Tests
```

### Ejecutar Backend Localmente
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Crear Nueva Migración
```bash
cd backend
alembic revision --autogenerate -m "descripcion del cambio"
alembic upgrade head
```

### Testing Backend
```bash
cd backend
pytest                    # Todos los tests
pytest tests/test_routes.py  # Test específico
pytest --cov=app         # Con coverage
```

## Desarrollo Frontend

### Estructura del Frontend
```
frontend/
├── src/
│   ├── components/        # React components
│   ├── pages/            # Page components
│   ├── hooks/            # Custom hooks
│   ├── store/            # Redux store
│   ├── services/         # API services
│   ├── utils/            # Utilities
│   └── types/            # TypeScript types
├── public/               # Static assets
└── tests/                # Tests
```

### Ejecutar Frontend Localmente
```bash
cd frontend
npm install
npm run dev
```

### Testing Frontend
```bash
cd frontend
npm test                  # Unit tests
npm run test:coverage     # Con coverage
npx cypress open          # E2E tests
```

## APIs Externas

### Google Maps API
- Geocoding API para convertir direcciones a coordenadas
- Configurar `GOOGLE_MAPS_API_KEY` en `.env`

### Mapbox
- Para visualización de mapas
- Configurar `MAPBOX_ACCESS_TOKEN` en `.env`

### OSRM
- Motor de cálculo de rutas
- Se ejecuta en contenedor Docker
- Datos de Argentina descargables con `make download-osrm-data`

## Base de Datos

### PostgreSQL con PostGIS
- Puerto: 5432
- Usuario: postgres
- Password: password (configurable en .env)
- Base de datos: optimizador_rutas

### Conexión
```bash
psql -h localhost -U postgres -d optimizador_rutas
```

### Consultas Espaciales Ejemplo
```sql
-- Encontrar peajes cerca de una ruta
SELECT name, tariff 
FROM tolls 
WHERE ST_DWithin(location, ST_GeomFromText('LINESTRING(...)'), 1000);
```

## Debugging

### Backend Debugging
```bash
# Ver logs del backend
make logs-backend

# Conectar a la base de datos
make logs-postgres

# Debug con pdb
import pdb; pdb.set_trace()
```

### Frontend Debugging
```bash
# Ver logs del frontend
make logs-frontend

# React DevTools en el navegador
# Redux DevTools extension
```

## Deployment

### Desarrollo
```bash
make dev-up
```

### Producción
```bash
make build
docker-compose --profile production up -d
```

### CI/CD
- GitHub Actions configurado en `.github/workflows/ci.yml`
- Tests automáticos en cada push
- Deploy automático a AWS en branch main

## Troubleshooting

### Problemas Comunes

1. **Puerto ocupado**
```bash
# Verificar puertos en uso
netstat -tulpn | grep :8000
# Cambiar puerto en docker-compose.yml
```

2. **Base de datos no conecta**
```bash
# Verificar que PostgreSQL esté corriendo
docker-compose ps postgres
# Resetear base de datos
make db-reset
```

3. **OSRM no responde**
```bash
# Verificar servicio OSRM
curl http://localhost:5000/health
# Descargar datos si es necesario
make download-osrm-data
```

4. **Dependencias desactualizadas**
```bash
# Reinstalar dependencias
make clean
make install-deps
```

## Contribución

1. Fork el proyecto
2. Crear feature branch (`git checkout -b feature/nueva-funcionalidad`)
3. Hacer cambios y tests
4. Verificar que pasan todos los tests (`make test`)
5. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
6. Push al branch (`git push origin feature/nueva-funcionalidad`)
7. Crear Pull Request

### Estándares de Código

- **Backend**: Black, isort, flake8
- **Frontend**: ESLint, Prettier
- **Commits**: Conventional Commits
- **Tests**: Mínimo 80% coverage