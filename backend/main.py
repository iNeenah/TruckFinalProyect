"""
Main FastAPI application for Optimizador de Rutas con IA.
"""
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import logging
import time

from app.config import get_settings
from app.middleware.cors_middleware import setup_cors
from app.middleware.auth_middleware import AuthMiddleware
from app.middleware.rate_limit_middleware import RateLimitMiddleware
from app.middleware.validation_middleware import ValidationMiddleware
from app.api.auth import router as auth_router
from app.api.vehicles import router as vehicles_router
from app.api.routes import router as routes_router
from app.api.admin import router as admin_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Sistema SaaS web para empresas de transporte de Misiones que optimiza rutas considerando costos de combustible y peajes.",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    openapi_url="/openapi.json" if settings.debug else None
)

# Add middleware (order matters - last added is executed first)
app.add_middleware(ValidationMiddleware)
app.add_middleware(RateLimitMiddleware, requests_per_minute=settings.rate_limit_per_minute)
app.add_middleware(AuthMiddleware)
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])  # Configure properly in production

# Setup CORS
setup_cors(app)

# Add request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add processing time header to responses."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(vehicles_router, prefix="/api")
app.include_router(routes_router, prefix="/api")
app.include_router(admin_router, prefix="/api")

# Health check endpoints
@app.get("/health")
async def health_check():
    """
    Health check endpoint.
    
    Returns the health status of the application.
    """
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment
    }

@app.get("/")
async def root():
    """
    Root endpoint.
    
    Returns basic information about the API.
    """
    return {
        "message": "Optimizador de Rutas con IA - API",
        "version": settings.app_version,
        "docs": "/docs" if settings.debug else "Documentation not available in production",
        "health": "/health"
    }

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled exceptions.
    
    Args:
        request: HTTP request
        exc: Exception that occurred
        
    Returns:
        JSON error response
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "type": "internal_error"
        }
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    """
    Application startup event.
    
    Performs initialization tasks when the application starts.
    """
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.environment}")
    logger.info(f"Debug mode: {settings.debug}")
    
    # Initialize database tables if needed
    try:
        from app.database import create_tables
        create_tables()
        logger.info("Database tables initialized")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
    
    # Create seed data if in development
    if settings.environment == "development":
        try:
            from app.seed_data import create_seed_data
            from app.database import SessionLocal
            
            db = SessionLocal()
            try:
                create_seed_data(db)
                logger.info("Seed data created")
            finally:
                db.close()
        except Exception as e:
            logger.warning(f"Failed to create seed data: {e}")

# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """
    Application shutdown event.
    
    Performs cleanup tasks when the application shuts down.
    """
    logger.info(f"Shutting down {settings.app_name}")

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level="info"
    )