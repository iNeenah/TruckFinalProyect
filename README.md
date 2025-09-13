# Optimizador de Rutas con IA

Sistema SaaS web para empresas de transporte de Misiones que optimiza rutas considerando costos de combustible y peajes.

## Propuesta de Valor
"Te mostramos la ruta más barata, no solo la más rápida, para tus viajes. Ahorra en combustible y peajes"

## Stack Tecnológico

### Frontend
- React.js 18+ con TypeScript
- Material-UI (MUI) v5
- Mapbox GL JS
- Redux Toolkit
- Vite

### Backend
- FastAPI con Python 3.11+
- PostgreSQL 15+ con PostGIS
- SQLAlchemy 2.0
- JWT Authentication
- OSRM para cálculo de rutas

### Infraestructura
- Docker y Docker Compose
- AWS (EC2, RDS, S3, CloudFront)
- GitHub Actions

## Estructura del Proyecto

```
optimizador-rutas-ia/
├── frontend/          # React TypeScript app
├── backend/           # FastAPI Python app
├── docker/           # Docker configurations
├── docs/             # Documentation
└── .github/          # CI/CD workflows
```

## Desarrollo Local

### Prerrequisitos
- Docker y Docker Compose
- Node.js 18+
- Python 3.11+

### Configuración Inicial

1. Clonar el repositorio
```bash
git clone <repository-url>
cd optimizador-rutas-ia
```

2. Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env con tus configuraciones
```

3. Levantar servicios con Docker
```bash
docker-compose up -d
```

4. Instalar dependencias del frontend
```bash
cd frontend
npm install
npm run dev
```

5. Instalar dependencias del backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

## URLs de Desarrollo
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- PostgreSQL: localhost:5432
- OSRM: http://localhost:5000

## Comandos Útiles

### Docker
```bash
# Levantar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f

# Reiniciar servicios
docker-compose restart

# Limpiar todo
docker-compose down -v
```

### Base de Datos
```bash
# Ejecutar migraciones
cd backend
alembic upgrade head

# Crear nueva migración
alembic revision --autogenerate -m "descripcion"
```

### Testing
```bash
# Tests backend
cd backend
pytest

# Tests frontend
cd frontend
npm test
```

## Contribución

1. Fork el proyecto
2. Crear feature branch (`git checkout -b feature/nueva-funcionalidad`)
3. Commit cambios (`git commit -am 'Agregar nueva funcionalidad'`)
4. Push al branch (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.