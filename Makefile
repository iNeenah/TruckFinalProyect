# Optimizador de Rutas - Development Makefile

.PHONY: help setup dev-up dev-down clean test lint format install-deps

# Default target
help:
	@echo "Available commands:"
	@echo "  setup        - Initial project setup"
	@echo "  dev-up       - Start development environment"
	@echo "  dev-down     - Stop development environment"
	@echo "  clean        - Clean up containers and volumes"
	@echo "  test         - Run all tests"
	@echo "  lint         - Run linting on all code"
	@echo "  format       - Format all code"
	@echo "  install-deps - Install all dependencies"

# Initial setup
setup:
	@echo "Setting up Optimizador de Rutas development environment..."
	cp .env.example .env
	@echo "Please edit .env file with your configuration"
	docker-compose pull
	make install-deps
	@echo "Setup complete! Run 'make dev-up' to start development"

# Start development environment
dev-up:
	@echo "Starting development environment..."
	docker-compose up -d postgres redis osrm
	@echo "Waiting for services to be ready..."
	sleep 10
	@echo "Services are ready!"
	@echo "Frontend: http://localhost:3000"
	@echo "Backend: http://localhost:8000"
	@echo "API Docs: http://localhost:8000/docs"

# Stop development environment
dev-down:
	@echo "Stopping development environment..."
	docker-compose down

# Clean up everything
clean:
	@echo "Cleaning up containers and volumes..."
	docker-compose down -v
	docker system prune -f

# Install dependencies
install-deps:
	@echo "Installing backend dependencies..."
	cd backend && pip install -r requirements.txt
	@echo "Installing frontend dependencies..."
	cd frontend && npm install

# Run tests
test:
	@echo "Running backend tests..."
	cd backend && pytest
	@echo "Running frontend tests..."
	cd frontend && npm test

# Run linting
lint:
	@echo "Linting backend code..."
	cd backend && black --check . && isort --check-only . && flake8 .
	@echo "Linting frontend code..."
	cd frontend && npm run lint

# Format code
format:
	@echo "Formatting backend code..."
	cd backend && black . && isort .
	@echo "Formatting frontend code..."
	cd frontend && npm run format

# Database operations
db-migrate:
	@echo "Running database migrations..."
	cd backend && alembic upgrade head

db-reset:
	@echo "Resetting database..."
	docker-compose down postgres
	docker volume rm optimizador-rutas-ia_postgres_data
	docker-compose up -d postgres
	sleep 10
	make db-migrate

# Development helpers
logs:
	docker-compose logs -f

logs-backend:
	docker-compose logs -f backend

logs-frontend:
	docker-compose logs -f frontend

logs-postgres:
	docker-compose logs -f postgres

logs-osrm:
	docker-compose logs -f osrm

# Production build
build:
	@echo "Building production images..."
	docker-compose build

# Download OSRM data (Argentina)
download-osrm-data:
	@echo "Downloading Argentina OSM data for OSRM..."
	mkdir -p osrm-data
	cd osrm-data && \
	wget -O argentina-latest.osm.pbf https://download.geofabrik.de/south-america/argentina-latest.osm.pbf && \
	docker run -t -v $(PWD)/osrm-data:/data osrm/osrm-backend osrm-extract -p /opt/car.lua /data/argentina-latest.osm.pbf && \
	docker run -t -v $(PWD)/osrm-data:/data osrm/osrm-backend osrm-partition /data/argentina-latest.osrm && \
	docker run -t -v $(PWD)/osrm-data:/data osrm/osrm-backend osrm-customize /data/argentina-latest.osrm
	@echo "OSRM data ready!"