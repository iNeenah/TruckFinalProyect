"""
Pydantic schemas for User model.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from uuid import UUID

from app.models.user import UserRole


class UserBase(BaseModel):
    """Base user schema with common fields."""
    email: EmailStr = Field(..., description="User email address")
    first_name: str = Field(..., min_length=1, max_length=100, description="First name")
    last_name: str = Field(..., min_length=1, max_length=100, description="Last name")
    role: UserRole = Field(default=UserRole.OPERATOR, description="User role")


class UserCreate(UserBase):
    """Schema for creating a new user."""
    password: str = Field(..., min_length=8, max_length=100, description="User password")
    company_id: UUID = Field(..., description="Company ID the user belongs to")


class UserUpdate(BaseModel):
    """Schema for updating user information."""
    email: Optional[EmailStr] = None
    first_name: Optional[str] = Field(None, min_length=1, max_length=100)
    last_name: Optional[str] = Field(None, min_length=1, max_length=100)
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None


class UserLogin(BaseModel):
    """Schema for user login."""
    email: EmailStr = Field(..., description="User email")
    password: str = Field(..., description="User password")


class UserResponse(UserBase):
    """Schema for user API responses."""
    id: UUID
    is_active: bool
    is_verified: bool
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    company_id: UUID
    
    # Computed fields
    full_name: str
    is_admin: bool
    is_operator: bool

    class Config:
        from_attributes = True


class UserWithCompany(UserResponse):
    """User response with company information."""
    from .company import CompanyResponse
    company: CompanyResponse


class TokenResponse(BaseModel):
    """Schema for authentication token response."""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class PasswordChange(BaseModel):
    """Schema for password change."""
    current_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, max_length=100, description="New password")