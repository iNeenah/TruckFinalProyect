"""
Pydantic schemas for Toll model.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Tuple
from datetime import datetime
from uuid import UUID
from decimal import Decimal


class TollBase(BaseModel):
    """Base toll schema with common fields."""
    name: str = Field(..., min_length=1, max_length=255, description="Toll station name")
    route_code: Optional[str] = Field(None, max_length=50, description="Route code (e.g., RN12)")
    km_marker: Optional[Decimal] = Field(None, ge=0, description="Kilometer marker on route")
    tariff: Decimal = Field(..., gt=0, description="Toll tariff in ARS")
    direction: Optional[str] = Field(None, max_length=50, description="Direction of travel")
    operator: Optional[str] = Field(None, max_length=255, description="Toll operator company")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")


class TollCreate(BaseModel):
    """Schema for creating a new toll."""
    name: str = Field(..., min_length=1, max_length=255, description="Toll station name")
    road_name: str = Field(..., min_length=1, max_length=255, description="Road name (e.g., RN12)")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude coordinate")
    latitude: float = Field(..., ge=-90, le=90, description="Latitude coordinate")
    tariff: Decimal = Field(..., ge=0, description="Toll tariff in ARS")
    region: str = Field(default="NEA", max_length=100, description="Region code")

    @validator('longitude')
    def validate_longitude(cls, v):
        """Validate longitude is within Argentina bounds (approximately)."""
        if not (-73.5 <= v <= -53.6):
            raise ValueError('Longitude should be within Argentina bounds')
        return v

    @validator('latitude')
    def validate_latitude(cls, v):
        """Validate latitude is within Argentina bounds (approximately)."""
        if not (-55.1 <= v <= -21.8):
            raise ValueError('Latitude should be within Argentina bounds')
        return v


class TollUpdate(BaseModel):
    """Schema for updating toll information."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    road_name: Optional[str] = Field(None, min_length=1, max_length=255)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    tariff: Optional[Decimal] = Field(None, ge=0)
    region: Optional[str] = Field(None, max_length=100)
    is_active: Optional[bool] = None


class TollResponse(BaseModel):
    """Schema for toll API responses."""
    id: int
    name: str
    road_name: str
    latitude: float
    longitude: float
    tariff: Decimal
    region: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None

    class Config:
        from_attributes = True


class TollListResponse(BaseModel):
    """Schema for paginated toll list responses."""
    tolls: List[TollResponse]
    total: int
    page: int
    size: int
    pages: int


class TollSearchRequest(BaseModel):
    """Schema for toll search requests."""
    route_code: Optional[str] = None
    min_latitude: Optional[float] = Field(None, ge=-90, le=90)
    max_latitude: Optional[float] = Field(None, ge=-90, le=90)
    min_longitude: Optional[float] = Field(None, ge=-180, le=180)
    max_longitude: Optional[float] = Field(None, ge=-180, le=180)
    operator: Optional[str] = None
    is_active: bool = True


class TollImportRequest(BaseModel):
    """Schema for CSV toll import."""
    csv_data: str = Field(..., description="CSV data as string")
    default_region: str = Field(default="NEA", description="Default region for tolls without region")


class TollBulkImport(BaseModel):
    """Schema for bulk importing tolls."""
    tolls: List[TollCreate]


class TollDistanceResponse(BaseModel):
    """Schema for toll distance calculation."""
    toll_id: UUID
    toll_name: str
    distance_meters: float
    coordinates: Tuple[float, float]


class RouteToллIntersection(BaseModel):
    """Schema for route-toll intersection analysis."""
    toll: TollResponse
    distance_from_route: float
    is_on_route: bool
    estimated_cost: Decimal