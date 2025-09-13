"""
Vehicle model for fleet management.
"""
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Enum, Numeric, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.database import Base


class FuelType(str, enum.Enum):
    """Types of fuel for vehicles."""
    DIESEL_500 = "diesel_500"
    DIESEL_PREMIUM = "diesel_premium"
    GASOLINE = "gasoline"  # For future use


class Vehicle(Base):
    """
    Model for company vehicles.
    
    Stores vehicle information including fuel consumption,
    dimensions, and other characteristics needed for route optimization.
    """
    __tablename__ = "vehicles"

    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4,
        index=True
    )
    license_plate = Column(String(20), unique=True, nullable=False, index=True)
    model = Column(String(255), nullable=False)
    brand = Column(String(100), nullable=True)
    year = Column(Integer, nullable=True)
    
    # Fuel consumption and type
    fuel_consumption = Column(
        Numeric(5, 2), 
        nullable=False,
        comment="Fuel consumption in L/100km"
    )
    fuel_type = Column(
        Enum(FuelType), 
        default=FuelType.DIESEL_500, 
        nullable=False
    )
    
    # Vehicle dimensions (in meters)
    height = Column(
        Numeric(4, 2), 
        nullable=True,
        comment="Vehicle height in meters"
    )
    width = Column(
        Numeric(4, 2), 
        nullable=True,
        comment="Vehicle width in meters"
    )
    length = Column(
        Numeric(5, 2), 
        nullable=True,
        comment="Vehicle length in meters"
    )
    
    # Weight capacity
    max_weight = Column(
        Integer, 
        nullable=True,
        comment="Maximum weight capacity in kg"
    )
    empty_weight = Column(
        Integer, 
        nullable=True,
        comment="Empty vehicle weight in kg"
    )
    
    # Status and metadata
    is_active = Column(Boolean, default=True, nullable=False)
    notes = Column(String(1000), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )

    # Foreign Keys
    company_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("companies.id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )

    # Relationships
    company = relationship("Company", back_populates="vehicles")
    calculated_routes = relationship("CalculatedRoute", back_populates="vehicle")

    @property
    def display_name(self) -> str:
        """Get vehicle display name."""
        if self.brand:
            return f"{self.brand} {self.model} ({self.license_plate})"
        return f"{self.model} ({self.license_plate})"

    @property
    def fuel_type_display(self) -> str:
        """Get human-readable fuel type."""
        fuel_type_map = {
            FuelType.DIESEL_500: "Diesel 500",
            FuelType.DIESEL_PREMIUM: "Diesel Premium",
            FuelType.GASOLINE: "Nafta"
        }
        return fuel_type_map.get(self.fuel_type, self.fuel_type.value)

    def calculate_fuel_cost(self, distance_km: float, fuel_price_per_liter: float) -> float:
        """
        Calculate fuel cost for a given distance.
        
        Args:
            distance_km: Distance in kilometers
            fuel_price_per_liter: Price per liter of fuel
            
        Returns:
            Total fuel cost
        """
        if distance_km <= 0 or fuel_price_per_liter <= 0:
            return 0.0
            
        fuel_needed = (distance_km / 100) * float(self.fuel_consumption)
        return fuel_needed * fuel_price_per_liter

    def __repr__(self):
        return f"<Vehicle(id={self.id}, license_plate='{self.license_plate}', model='{self.model}')>"

    def __str__(self):
        return self.display_name