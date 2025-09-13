"""
Fuel price model for cost calculations.
"""
from sqlalchemy import Column, String, DateTime, Numeric, Date, ForeignKey, Boolean, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base
from app.models.vehicle import FuelType


class FuelPrice(Base):
    """
    Model for fuel prices by type and region.
    
    Stores current and historical fuel prices for different fuel types
    in different regions. Used for accurate cost calculations.
    """
    __tablename__ = "fuel_prices"

    id = Column(Integer, primary_key=True, index=True)
    fuel_type = Column(String(50), nullable=False, index=True)
    region = Column(String(100), nullable=False, index=True)
    price_per_liter = Column(
        Numeric(10, 2), 
        nullable=False,
        comment="Price per liter in ARS"
    )
    effective_date = Column(Date, nullable=False, index=True)
    is_active = Column(Boolean, default=True, nullable=False, index=True)
    source = Column(String(255), nullable=True, comment="Data source")
    notes = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Foreign Keys
    updated_by = Column(String(50), nullable=True, index=True, comment="User ID who updated")

    # Note: updated_by is now a string field for simplicity
    # In a full implementation, this could be a foreign key to users table

    @classmethod
    def get_current_price(cls, session, fuel_type: str, region: str = "NEA"):
        """
        Get the most current price for a fuel type in a region.
        
        Args:
            session: Database session
            fuel_type: Type of fuel (diesel_500, diesel_premium, etc.)
            region: Region code (default: NEA for Northeast Argentina)
            
        Returns:
            FuelPrice object or None
        """
        return session.query(cls).filter(
            cls.fuel_type == fuel_type,
            cls.region == region
        ).order_by(cls.effective_date.desc()).first()

    @property
    def is_current(self) -> bool:
        """Check if this price is current (within last 30 days)."""
        from datetime import date, timedelta
        return (date.today() - self.effective_date).days <= 30

    @property
    def age_days(self) -> int:
        """Get age of price data in days."""
        from datetime import date
        return (date.today() - self.effective_date).days

    def __repr__(self):
        return f"<FuelPrice(fuel_type='{self.fuel_type}', region='{self.region}', price={self.price_per_liter})>"

    def __str__(self):
        return f"{self.fuel_type} - {self.region}: ${self.price_per_liter}/L"