"""
Pydantic schemas for API request/response validation.
"""

from .company import CompanyCreate, CompanyUpdate, CompanyResponse
from .user import UserCreate, UserUpdate, UserResponse, UserLogin
from .vehicle import VehicleCreate, VehicleUpdate, VehicleResponse
from .route import RouteRequest, RouteResponse, RouteCalculation
from .fuel_price import FuelPriceCreate, FuelPriceUpdate, FuelPriceResponse
from .toll import TollCreate, TollUpdate, TollResponse

__all__ = [
    # Company schemas
    "CompanyCreate",
    "CompanyUpdate", 
    "CompanyResponse",
    
    # User schemas
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "UserLogin",
    
    # Vehicle schemas
    "VehicleCreate",
    "VehicleUpdate",
    "VehicleResponse",
    
    # Route schemas
    "RouteRequest",
    "RouteResponse",
    "RouteCalculation",
    
    # Fuel price schemas
    "FuelPriceCreate",
    "FuelPriceUpdate",
    "FuelPriceResponse",
    
    # Toll schemas
    "TollCreate",
    "TollUpdate",
    "TollResponse"
]