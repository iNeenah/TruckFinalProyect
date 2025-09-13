"""
Application configuration settings.
"""
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    
    # App info
    app_name: str = "Optimizador de Rutas con IA"
    app_version: str = "1.0.0"
    
    # Database
    database_url: str = "postgresql://user:password@localhost/test_db"
    
    # JWT
    secret_key: str = "test-secret-key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # OSRM
    osrm_url: str = "http://localhost:5000"
    
    # Geocoding APIs
    mapbox_access_token: Optional[str] = None
    google_maps_api_key: Optional[str] = None
    
    # Redis (for caching)
    redis_url: str = "redis://localhost:6379"
    
    # Rate limiting
    rate_limit_per_minute: int = 60
    
    # Environment
    environment: str = "development"
    debug: bool = True
    
    class Config:
        env_file = ".env"


def get_settings() -> Settings:
    """Get application settings."""
    return Settings()