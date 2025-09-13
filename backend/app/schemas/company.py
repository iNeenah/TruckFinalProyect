"""
Pydantic schemas for Company model.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


class CompanyBase(BaseModel):
    """Base company schema with common fields."""
    name: str = Field(..., min_length=1, max_length=255, description="Company name")
    email: EmailStr = Field(..., description="Company email address")
    phone: Optional[str] = Field(None, max_length=50, description="Company phone number")
    address: Optional[str] = Field(None, max_length=500, description="Company address")
    tax_id: Optional[str] = Field(None, max_length=50, description="Tax ID (CUIT/CUIL)")


class CompanyCreate(CompanyBase):
    """Schema for creating a new company."""
    pass


class CompanyUpdate(BaseModel):
    """Schema for updating company information."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = Field(None, max_length=500)
    tax_id: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None


class CompanyResponse(CompanyBase):
    """Schema for company API responses."""
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    # Optional related data
    user_count: Optional[int] = Field(None, description="Number of users in company")
    vehicle_count: Optional[int] = Field(None, description="Number of vehicles in company")

    class Config:
        from_attributes = True


class CompanyListResponse(BaseModel):
    """Schema for paginated company list responses."""
    companies: List[CompanyResponse]
    total: int
    page: int
    size: int
    pages: int