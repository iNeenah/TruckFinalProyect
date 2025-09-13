"""
Pydantic schemas for FuelPrice model.
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID
from decimal import Decimal


class FuelPriceBase(BaseModel):
    """Base fuel price schema with common fields."""
    fuel_type: str = Field(..., description="Type of fuel")
    region: str = Field(..., description="Region code")
    price_per_liter: Decimal = Field(..., gt=0, description="Price per liter in ARS")
    effective_date: date = Field(..., description="Date when price becomes effective")
    source: Optional[str] = Field(None, max_length=255, description="Data source")
    notes: Optional[str] = Field(None, max_length=500, description="Additional notes")


class FuelPriceCreate(FuelPriceBase):
    """Schema for creating a new fuel price."""
    pass


class FuelPriceUpdate(BaseModel):
    """Schema for updating fuel price information."""
    price_id: Optional[int] = Field(None, description="Price ID for bulk updates")
    price_per_liter: Decimal = Field(..., gt=0, description="New price per liter")
    effective_date: Optional[date] = Field(None, description="Effective date for price")
    is_active: Optional[bool] = Field(None, description="Whether price is active")
    source: Optional[str] = Field(None, max_length=255)
    notes: Optional[str] = Field(None, max_length=500)


class FuelPriceResponse(FuelPriceBase):
    """Schema for fuel price API responses."""
    id: int
    is_active: bool = Field(default=True, description="Whether price is currently active")
    created_at: datetime
    updated_at: Optional[datetime] = None
    updated_by: Optional[str] = None
    
    # Computed fields
    last_updated: Optional[datetime] = None
    data_age_days: int = Field(default=0, description="Days since effective date")

    class Config:
        from_attributes = True


class FuelPriceListResponse(BaseModel):
    """Schema for paginated fuel price list responses."""
    fuel_prices: List[FuelPriceResponse]
    total: int
    page: int
    size: int
    pages: int


class CurrentFuelPricesResponse(BaseModel):
    """Schema for current fuel prices by type."""
    diesel_500: Optional[FuelPriceResponse]
    diesel_premium: Optional[FuelPriceResponse]
    gasoline: Optional[FuelPriceResponse]
    region: str
    last_updated: Optional[datetime]


class FuelPriceBulkImport(BaseModel):
    """Schema for bulk importing fuel prices."""
    fuel_prices: List[FuelPriceCreate]
    region: str = Field(default="NEA", description="Default region for all prices")


class FuelPriceHistory(BaseModel):
    """Schema for individual fuel price history record."""
    id: int
    price_per_liter: Decimal
    effective_date: date
    updated_at: Optional[datetime]
    updated_by: Optional[str]
    is_active: bool

    class Config:
        from_attributes = True


class FuelPriceAuditLog(BaseModel):
    """Schema for fuel price audit log entries."""
    id: int
    fuel_type: str
    region: str
    price_per_liter: Decimal
    effective_date: date
    action: str = Field(..., description="Action performed (CREATE/UPDATE/DELETE)")
    updated_at: datetime
    updated_by: str
    is_active: bool

    class Config:
        from_attributes = True


class FuelPriceHistoryResponse(BaseModel):
    """Schema for fuel price history."""
    fuel_type: str
    region: str
    prices: List[FuelPriceResponse]
    date_range: dict