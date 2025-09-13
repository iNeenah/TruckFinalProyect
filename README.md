# Truck Route Optimizer with AI

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18+-61DAFB.svg)](https://reactjs.org/)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg)](https://www.docker.com/)

> **Advanced AI-Powered Route Optimization System for Transportation Companies in Misiones Province, Argentina**

This is a cutting-edge SaaS web platform designed specifically for transportation companies in Misiones, Argentina. Unlike traditional route planners that focus solely on time optimization, this system revolutionizes logistics by optimizing routes based on **total cost** - considering fuel expenses, toll fees, and vehicle efficiency to maximize your operational savings.

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

### Diagram

```
graph TB
    A[Client Browser] --> B[React Frontend]
    B --> C{API Gateway}
    
    C --> D[Auth Service]
    C --> E[Vehicle Service]
    C --> F[Route Service]
    C --> G[Admin Service]
    C --> H[Report Service]
    
    D --> I[(PostgreSQL + PostGIS)]
    E --> I
    F --> I
    G --> I
    H --> I
    
    F --> J[OSRM Engine]
    B --> K[Mapbox Maps]
    
    L[Admin User] --> M[Terraform]
    M --> N[AWS Cloud]
    
    O[GitHub Actions] --> P[Docker Images]
    P --> Q[Container Registry]
    Q --> N
    
    R[Prometheus] --> S[Grafana]
    S --> T[Monitoring Dashboard]
    
    style A fill:#4285F4,stroke:#333
    style B fill:#34A853,stroke:#333
    style C fill:#FBBC05,stroke:#333
    style D fill:#EA4335,stroke:#333
    style E fill:#EA4335,stroke:#333
    style F fill:#EA4335,stroke:#333
    style G fill:#EA4335,stroke:#333
    style H fill:#EA4335,stroke:#333
    style I fill:#4285F4,stroke:#333
    style J fill:#FBBC05,stroke:#333
    style K fill:#4285F4,stroke:#333
    style L fill:#999,stroke:#333
    style M fill:#FBBC05,stroke:#333
    style N fill:#34A853,stroke:#333
    style O fill:#EA4335,stroke:#333
    style P fill:#FBBC05,stroke:#333
    style Q fill:#4285F4,stroke:#333
    style R fill:#FBBC05,stroke:#333
    style S fill:#34A853,stroke:#333
    style T fill:#4285F4,stroke:#333
```

### Directory Structure

```
truck-route-optimizer/
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