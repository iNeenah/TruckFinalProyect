"""
Pydantic schemas for Vehicle model.
"""
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from decimal import Decimal

from app.models.vehicle import FuelType


class VehicleBase(BaseModel):
    """Base vehicle schema with common fields."""
    license_plate: str = Field(..., min_length=1, max_length=20, description="Vehicle license plate")
    model: str = Field(..., min_length=1, max_length=255, description="Vehicle model")
    brand: Optional[str] = Field(None, max_length=100, description="Vehicle brand")
    year: Optional[int] = Field(None, ge=1900, le=2030, description="Vehicle year")
    fuel_consumption: Decimal = Field(..., gt=0, le=100, description="Fuel consumption in L/100km")
    fuel_type: FuelType = Field(default=FuelType.DIESEL_500, description="Type of fuel")
    height: Optional[Decimal] = Field(None, gt=0, le=10, description="Vehicle height in meters")
    width: Optional[Decimal] = Field(None, gt=0, le=5, description="Vehicle width in meters")
    length: Optional[Decimal] = Field(None, gt=0, le=30, description="Vehicle length in meters")
    max_weight: Optional[int] = Field(None, gt=0, le=100000, description="Maximum weight in kg")
    empty_weight: Optional[int] = Field(None, gt=0, le=50000, description="Empty weight in kg")
    notes: Optional[str] = Field(None, max_length=1000, description="Additional notes")

    @validator('license_plate')
    def validate_license_plate(cls, v):
        """Validate license plate format using VehicleValidator."""
        from app.validators.vehicle_validators import VehicleValidator
        try:
            return VehicleValidator.validate_license_plate(v)
        except Exception as e:
            raise ValueError(str(e))

    @validator('fuel_consumption')
    def validate_fuel_consumption(cls, v):
        """Validate fuel consumption using VehicleValidator."""
        from app.validators.vehicle_validators import VehicleValidator
        try:
            return VehicleValidator.validate_fuel_consumption(v)
        except Exception as e:
            raise ValueError(str(e))

    @validator('fuel_type')
    def validate_fuel_type(cls, v):
        """Validate fuel type using VehicleValidator."""
        from app.validators.vehicle_validators import VehicleValidator
        try:
            return VehicleValidator.validate_fuel_type(v.value if hasattr(v, 'value') else v)
        except Exception as e:
            raise ValueError(str(e))

    @validator('height', 'width', 'length')
    def validate_dimensions(cls, v, field):
        """Validate vehicle dimensions."""
        if v is not None:
            from app.validators.vehicle_validators import VehicleValidator
            try:
                # Create a dict with just this dimension for validation
                dim_dict = {field.name: v}
                VehicleValidator.validate_dimensions(**dim_dict)
                return v
            except Exception as e:
                raise ValueError(str(e))
        return v

    @validator('empty_weight', 'max_weight')
    def validate_weights(cls, v, values, field):
        """Validate weight values using VehicleValidator."""
        if v is not None:
            from app.validators.vehicle_validators import VehicleValidator
            try:
                # Get the other weight value if available
                if field.name == 'empty_weight':
                    max_weight = values.get('max_weight')
                    VehicleValidator.validate_weights(max_weight=max_weight, empty_weight=v)
                else:  # max_weight
                    empty_weight = values.get('empty_weight')
                    VehicleValidator.validate_weights(max_weight=v, empty_weight=empty_weight)
                return v
            except Exception as e:
                raise ValueError(str(e))
        return v

    @validator('year')
    def validate_year(cls, v):
        """Validate vehicle year using VehicleValidator."""
        if v is not None:
            from app.validators.vehicle_validators import VehicleValidator
            try:
                return VehicleValidator.validate_year(v)
            except Exception as e:
                raise ValueError(str(e))
        return v

    @validator('model')
    def validate_model(cls, v):
        """Validate vehicle model."""
        from app.validators.vehicle_validators import VehicleValidator
        try:
            result = VehicleValidator.validate_model_and_brand(v)
            return result['model']
        except Exception as e:
            raise ValueError(str(e))

    @validator('brand')
    def validate_brand(cls, v, values):
        """Validate vehicle brand."""
        if v is not None:
            from app.validators.vehicle_validators import VehicleValidator
            try:
                model = values.get('model', 'DefaultModel')
                result = VehicleValidator.validate_model_and_brand(model, v)
                return result.get('brand')
            except Exception as e:
                raise ValueError(str(e))
        return v

    @validator('notes')
    def validate_notes(cls, v):
        """Validate notes field."""
        if v is not None:
            v = v.strip()
            if len(v) > 1000:
                raise ValueError('Notes cannot exceed 1000 characters')
            return v if v else None
        return v


class VehicleCreate(VehicleBase):
    """Schema for creating a new vehicle."""
    company_id: UUID = Field(..., description="Company ID the vehicle belongs to")


class VehicleUpdate(BaseModel):
    """Schema for updating vehicle information."""
    license_plate: Optional[str] = Field(None, min_length=1, max_length=20)
    model: Optional[str] = Field(None, min_length=1, max_length=255)
    brand: Optional[str] = Field(None, max_length=100)
    year: Optional[int] = Field(None, ge=1900, le=2030)
    fuel_consumption: Optional[Decimal] = Field(None, gt=0, le=100)
    fuel_type: Optional[FuelType] = None
    height: Optional[Decimal] = Field(None, gt=0, le=10)
    width: Optional[Decimal] = Field(None, gt=0, le=5)
    length: Optional[Decimal] = Field(None, gt=0, le=30)
    max_weight: Optional[int] = Field(None, gt=0, le=100000)
    empty_weight: Optional[int] = Field(None, gt=0, le=50000)
    notes: Optional[str] = Field(None, max_length=1000)
    is_active: Optional[bool] = None

    @validator('license_plate')
    def validate_license_plate(cls, v):
        """Validate license plate format using VehicleValidator."""
        if v is not None:
            from app.validators.vehicle_validators import VehicleValidator
            try:
                return VehicleValidator.validate_license_plate(v)
            except Exception as e:
                raise ValueError(str(e))
        return v

    @validator('fuel_consumption')
    def validate_fuel_consumption(cls, v):
        """Validate fuel consumption using VehicleValidator."""
        if v is not None:
            from app.validators.vehicle_validators import VehicleValidator
            try:
                return VehicleValidator.validate_fuel_consumption(v)
            except Exception as e:
                raise ValueError(str(e))
        return v

    @validator('fuel_type')
    def validate_fuel_type(cls, v):
        """Validate fuel type using VehicleValidator."""
        if v is not None:
            from app.validators.vehicle_validators import VehicleValidator
            try:
                return VehicleValidator.validate_fuel_type(v.value if hasattr(v, 'value') else v)
            except Exception as e:
                raise ValueError(str(e))
        return v

    @validator('height', 'width', 'length')
    def validate_dimensions(cls, v, field):
        """Validate vehicle dimensions."""
        if v is not None:
            from app.validators.vehicle_validators import VehicleValidator
            try:
                dim_dict = {field.name: v}
                VehicleValidator.validate_dimensions(**dim_dict)
                return v
            except Exception as e:
                raise ValueError(str(e))
        return v

    @validator('empty_weight', 'max_weight')
    def validate_weights(cls, v, values, field):
        """Validate weight values using VehicleValidator."""
        if v is not None:
            from app.validators.vehicle_validators import VehicleValidator
            try:
                if field.name == 'empty_weight':
                    max_weight = values.get('max_weight')
                    VehicleValidator.validate_weights(max_weight=max_weight, empty_weight=v)
                else:
                    empty_weight = values.get('empty_weight')
                    VehicleValidator.validate_weights(max_weight=v, empty_weight=empty_weight)
                return v
            except Exception as e:
                raise ValueError(str(e))
        return v

    @validator('year')
    def validate_year(cls, v):
        """Validate vehicle year using VehicleValidator."""
        if v is not None:
            from app.validators.vehicle_validators import VehicleValidator
            try:
                return VehicleValidator.validate_year(v)
            except Exception as e:
                raise ValueError(str(e))
        return v

    @validator('model')
    def validate_model(cls, v):
        """Validate vehicle model."""
        if v is not None:
            from app.validators.vehicle_validators import VehicleValidator
            try:
                result = VehicleValidator.validate_model_and_brand(v)
                return result['model']
            except Exception as e:
                raise ValueError(str(e))
        return v

    @validator('brand')
    def validate_brand(cls, v, values):
        """Validate vehicle brand."""
        if v is not None:
            from app.validators.vehicle_validators import VehicleValidator
            try:
                model = values.get('model', 'DefaultModel')
                result = VehicleValidator.validate_model_and_brand(model, v)
                return result.get('brand')
            except Exception as e:
                raise ValueError(str(e))
        return v

    @validator('notes')
    def validate_notes(cls, v):
        """Validate notes field."""
        if v is not None:
            v = v.strip()
            if len(v) > 1000:
                raise ValueError('Notes cannot exceed 1000 characters')
            return v if v else None
        return v


class VehicleResponse(VehicleBase):
    """Schema for vehicle API responses."""
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime
    company_id: UUID
    
    # Computed fields
    display_name: str
    fuel_type_display: str

    class Config:
        from_attributes = True


class VehicleWithCompany(VehicleResponse):
    """Vehicle response with company information."""
    from .company import CompanyResponse
    company: CompanyResponse


class VehicleListResponse(BaseModel):
    """Schema for paginated vehicle list responses."""
    vehicles: List[VehicleResponse]
    total: int
    page: int
    size: int
    pages: int


class VehicleFuelCostCalculation(BaseModel):
    """Schema for fuel cost calculation."""
    vehicle_id: UUID
    distance_km: float = Field(..., gt=0, description="Distance in kilometers")
    fuel_price_per_liter: float = Field(..., gt=0, description="Fuel price per liter")
    
    
class VehicleFuelCostResponse(BaseModel):
    """Schema for fuel cost calculation response."""
    vehicle_id: UUID
    distance_km: float
    fuel_consumption: Decimal
    fuel_needed_liters: float
    fuel_price_per_liter: float
    total_fuel_cost: float
    fuel_type: FuelType