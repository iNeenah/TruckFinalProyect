# Kiro Route Optimizer with AI

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://www.docker.com/)

> **Advanced AI-Powered Route Optimization System for Transportation Companies in Misiones Province, Argentina**

Kiro is a cutting-edge SaaS web platform designed specifically for transportation companies in Misiones, Argentina. Unlike traditional route planners that focus solely on time optimization, Kiro revolutionizes logistics by optimizing routes based on **total cost** - considering fuel expenses, toll fees, and vehicle efficiency to maximize your operational savings.

## 🚀 Key Features

### Cost-Based Route Optimization
- **Smart Cost Calculation**: Real-time analysis of fuel consumption and toll costs
- **Multi-Route Comparison**: Evaluate multiple route alternatives with detailed cost breakdowns
- **Vehicle-Specific Optimization**: Custom algorithms based on vehicle type, fuel efficiency, and load capacity

### Comprehensive Fleet Management
- **Vehicle Database**: Complete CRUD operations for vehicle management
- **Performance Analytics**: Track fuel efficiency, maintenance schedules, and cost metrics
- **Multi-Company Support**: Secure multi-tenant architecture for fleet operators

### Advanced Administrative Dashboard
- **Toll Management**: Dynamic toll pricing and route impact analysis
- **Fuel Price Tracking**: Real-time fuel cost monitoring and forecasting
- **User & Company Management**: Role-based access control with admin/operator permissions

### Data-Driven Insights & Reporting
- **Interactive Analytics**: Visual dashboards with key performance indicators
- **Export Capabilities**: Generate PDF, Excel, and CSV reports
- **Route History**: Save and compare historical route data

### Enterprise-Grade Security
- **JWT Authentication**: Secure token-based authentication system
- **Role-Based Access Control**: Admin and operator permission levels
- **Data Encryption**: End-to-end encryption for sensitive information

## 🛠️ Technology Stack

### Frontend
- **React 18+** with TypeScript for robust UI development
- **Material-UI (MUI) v5** for responsive, accessible components
- **Mapbox GL JS** for interactive map visualization
- **Redux Toolkit** for state management
- **Vite** for lightning-fast development and build processes
- **Tailwind CSS** for utility-first styling

### Backend
- **FastAPI** with Python 3.11+ for high-performance API development
- **PostgreSQL 15+** with PostGIS extension for geospatial data
- **SQLAlchemy 2.0** for ORM and database operations
- **Alembic** for database migrations
- **JWT Authentication** for secure access control
- **OSRM (Open Source Routing Machine)** for route calculation

### Infrastructure & DevOps
- **Docker & Docker Compose** for containerization and orchestration
- **GitHub Actions** for CI/CD pipelines
- **Terraform** for Infrastructure as Code (AWS)
- **Nginx** for reverse proxy and load balancing
- **Prometheus & Grafana** for monitoring and observability

## 📁 Project Architecture

```
kiro-route-optimizer/
├── backend/                    # FastAPI Python application
│   ├── app/                    # Core application code
│   │   ├── api/                # REST API endpoints
│   │   ├── models/             # Database models (SQLAlchemy)
│   │   ├── schemas/            # Pydantic schemas for validation
│   │   ├── services/           # Business logic and services
│   │   ├── auth/               # Authentication and authorization
│   │   ├── middleware/         # Custom middleware components
│   │   └── utils/              # Utility functions
│   ├── tests/                  # Unit and integration tests
│   ├── alembic/                # Database migrations
│   └── requirements.txt        # Python dependencies
├── frontend/                   # React TypeScript application
│   ├── src/                    # Source code
│   │   ├── components/         # Reusable UI components
│   │   ├── pages/              # Application pages
│   │   ├── services/           # API service clients
│   │   ├── store/              # Redux store configuration
│   │   ├── hooks/              # Custom React hooks
│   │   ├── contexts/           # React context providers
│   │   ├── types/              # TypeScript type definitions
│   │   └── utils/              # Utility functions
│   ├── __tests__/              # Frontend tests
│   └── package.json            # Node.js dependencies
├── docker/                     # Docker configurations
├── terraform/                  # Infrastructure as Code
├── docs/                       # Comprehensive documentation
├── scripts/                    # Utility scripts
├── .github/workflows/          # GitHub Actions CI/CD
└── docker-compose.yml          # Service orchestration
```

## 🚀 Quick Start Guide

### Prerequisites
- **Docker** and **Docker Compose** (v2.0+)
- **Node.js** 18+ with npm
- **Python** 3.11+
- **Git** for version control
- **6GB+ RAM** recommended for optimal performance

### Installation & Setup

1. **Clone the Repository**
```bash
git clone https://github.com/iNeenah/TruckFinalProyect.git
cd TruckFinalProyect
```

2. **Environment Configuration**
```bash
# Backend environment variables
cp .env.example .env
# Edit .env with your configurations

# Frontend environment variables
cp frontend/.env.example frontend/.env
# Edit frontend/.env with your configurations
```

3. **Launch Development Environment**
```bash
# Start all services with Docker Compose
docker-compose up -d

# Install frontend dependencies
cd frontend
npm install

# Start frontend development server
npm run dev
```

4. **Database Initialization**
```bash
# Run database migrations
cd backend
alembic upgrade head

# Seed initial data (optional)
python app/seed_data.py
```

### Development URLs
- **Frontend Application**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Database**: localhost:5432 (PostgreSQL with PostGIS)
- **OSRM Service**: http://localhost:5000
- **Mapbox Studio**: Access via Mapbox account

## 🔧 Advanced Development Commands

### Docker Management
```bash
# Start all services
docker-compose up -d

# View service logs
docker-compose logs -f [service-name]

# Restart specific service
docker-compose restart [service-name]

# Stop all services
docker-compose down

# Clean slate (remove volumes)
docker-compose down -v

# Build services from scratch
docker-compose build --no-cache
```

### Backend Development
```bash
# Navigate to backend directory
cd backend

# Run development server
uvicorn main:app --reload

# Run tests with coverage
pytest --cov=app tests/

# Run linters
flake8 app/
black app/
isort app/

# Create database migration
alembic revision --autogenerate -m "Migration description"

# Apply migrations
alembic upgrade head
```

### Frontend Development
```bash
# Navigate to frontend directory
cd frontend

# Start development server
npm run dev

# Run tests
npm run test

# Run tests with coverage
npm run test:coverage

# Run end-to-end tests
npm run cypress:open

# Build for production
npm run build

# Lint code
npm run lint

# Fix linting issues
npm run lint:fix
```

### Data & Services Management
```bash
# Download OSRM data for Argentina
make download-osrm-data

# Reset database
make db-reset

# Run database migrations
make db-migrate

# Format codebase
make format

# Run all tests
make test
```

## 🧪 Testing Strategy

### Backend Testing
- **Unit Tests**: Service layer functionality testing
- **Integration Tests**: API endpoint validation
- **Contract Tests**: Data validation and schema compliance
- **Performance Tests**: Load and stress testing

### Frontend Testing
- **Unit Tests**: Component and hook testing with Jest
- **Integration Tests**: Page and workflow validation
- **End-to-End Tests**: Cypress for user journey testing
- **Snapshot Tests**: UI consistency verification

### Test Coverage
- **Backend**: 95%+ code coverage target
- **Frontend**: 90%+ component coverage target

## 📊 Monitoring & Observability

### Performance Metrics
- **API Response Times**: Track endpoint latency
- **Database Queries**: Monitor query performance
- **Memory Usage**: Container resource monitoring
- **Error Rates**: Exception and failure tracking

### Logging Strategy
- **Structured Logging**: JSON-formatted application logs
- **Request Tracing**: Correlation IDs for request tracking
- **Audit Logs**: Security and access logging
- **Error Tracking**: Centralized exception reporting

## 🔒 Security Features

### Authentication & Authorization
- **JWT Token Management**: Secure token generation and validation
- **Role-Based Access Control**: Admin/operator permission levels
- **Session Management**: Secure session handling
- **Password Security**: bcrypt hashing with salt

### Data Protection
- **Encryption at Rest**: Database encryption
- **Encryption in Transit**: TLS/SSL for all communications
- **Input Validation**: Comprehensive data sanitization
- **Rate Limiting**: API request throttling

## 🚀 Production Deployment

### Infrastructure Requirements
- **AWS Services**: ECS, RDS, S3, CloudFront, Route 53
- **Container Registry**: ECR for Docker images
- **Load Balancing**: Application Load Balancer
- **Monitoring**: CloudWatch, Prometheus, Grafana

### Deployment Process
1. **Infrastructure Provisioning**: Terraform scripts for AWS setup
2. **CI/CD Pipeline**: GitHub Actions for automated deployment
3. **Container Building**: Docker images for frontend and backend
4. **Service Deployment**: ECS orchestration
5. **Monitoring Setup**: Logging and alerting configuration

### Scalability Features
- **Horizontal Scaling**: Load-balanced container instances
- **Database Scaling**: RDS read replicas and auto-scaling
- **Content Delivery**: CDN for static assets
- **Caching Strategy**: Redis for performance optimization

## 📚 Documentation

### API Documentation
- **Swagger UI**: Interactive API documentation at `/docs`
- **ReDoc**: Alternative API documentation at `/redoc`
- **Postman Collection**: Exportable API testing collection

### Developer Guides
- **Backend Development**: Service architecture and patterns
- **Frontend Development**: Component design and state management
- **Database Schema**: Entity relationship diagrams
- **Deployment Guide**: Production deployment procedures

### User Documentation
- **User Manual**: End-user operation guide
- **Administrator Guide**: System administration procedures
- **API Reference**: Detailed API endpoint documentation
- **Troubleshooting**: Common issues and solutions

## 🤝 Contributing

We welcome contributions from the community! To contribute:

1. **Fork the Repository**
```bash
git fork https://github.com/iNeenah/TruckFinalProyect.git
```

2. **Create a Feature Branch**
```bash
git checkout -b feature/amazing-new-feature
```

3. **Make Your Changes**
- Follow coding standards and best practices
- Write comprehensive tests
- Update documentation as needed

4. **Commit Your Changes**
```bash
git commit -m "Add amazing new feature"
```

5. **Push to Your Fork**
```bash
git push origin feature/amazing-new-feature
```

6. **Open a Pull Request**
- Provide detailed description of changes
- Link related issues
- Request review from maintainers

### Code Quality Standards
- **Backend**: PEP 8 compliance, type hints, docstrings
- **Frontend**: TypeScript strict mode, ESLint, Prettier
- **Testing**: 90%+ code coverage requirement
- **Documentation**: Clear, comprehensive documentation

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenStreetMap** for providing map data
- **OSRM** for route calculation algorithms
- **Mapbox** for mapping visualization tools
- **PostGIS** for geospatial database capabilities
- **All contributors** who have helped shape this project

## 📞 Support

For support, please open an issue on GitHub or contact the development team at support@kiro.com.

---

<p align="center">
  <strong>Built with ❤️ for transportation companies in Misiones, Argentina</strong>
</p>