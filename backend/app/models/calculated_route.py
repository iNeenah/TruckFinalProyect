"""
Calculated route model for storing route history and analysis.
"""
from sqlalchemy import Column, String, DateTime, Numeric, Integer, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from geoalchemy2 import Geometry
from geoalchemy2.shape import to_shape
import uuid

from app.database import Base


class CalculatedRoute(Base):
    """
    Model for storing calculated routes and their analysis.
    
    Stores route calculations for history, reporting, and analytics.
    Includes origin/destination, selected route geometry, costs, and savings.
    """
    __tablename__ = "calculated_routes"

    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4,
        index=True
    )
    
    # Route endpoints
    origin_address = Column(Text, nullable=True)
    destination_address = Column(Text, nullable=True)
    origin_coords = Column(
        Geometry('POINT', srid=4326), 
        nullable=False,
        comment="Origin coordinates"
    )
    destination_coords = Column(
        Geometry('POINT', srid=4326), 
        nullable=False,
        comment="Destination coordinates"
    )
    
    # Selected route data
    selected_route_geometry = Column(
        Geometry('LINESTRING', srid=4326), 
        nullable=False,
        comment="Selected route geometry"
    )
    total_distance = Column(
        Numeric(8, 2), 
        nullable=False,
        comment="Total distance in kilometers"
    )
    total_duration = Column(
        Integer, 
        nullable=False,
        comment="Total duration in minutes"
    )
    
    # Cost breakdown
    fuel_cost = Column(
        Numeric(10, 2), 
        nullable=False,
        comment="Fuel cost in ARS"
    )
    toll_cost = Column(
        Numeric(10, 2), 
        nullable=False,
        comment="Toll cost in ARS"
    )
    total_cost = Column(
        Numeric(10, 2), 
        nullable=False,
        comment="Total cost in ARS"
    )
    
    # Savings analysis
    savings_amount = Column(
        Numeric(10, 2), 
        nullable=True,
        comment="Savings compared to fastest route in ARS"
    )
    alternative_route_cost = Column(
        Numeric(10, 2), 
        nullable=True,
        comment="Cost of alternative (fastest) route in ARS"
    )
    
    # Route metadata
    route_type = Column(
        String(50), 
        nullable=True,
        comment="Type of route (fastest, cheapest, balanced)"
    )
    weather_conditions = Column(String(100), nullable=True)
    traffic_conditions = Column(String(100), nullable=True)
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Foreign Keys
    user_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("users.id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    vehicle_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("vehicles.id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )
    company_id = Column(
        UUID(as_uuid=True), 
        ForeignKey("companies.id", ondelete="CASCADE"), 
        nullable=False,
        index=True
    )

    # Relationships
    user = relationship("User", back_populates="calculated_routes")
    vehicle = relationship("Vehicle", back_populates="calculated_routes")
    company = relationship("Company", back_populates="calculated_routes")

    @property
    def origin_coordinates(self) -> tuple:
        """Get origin (longitude, latitude) tuple."""
        if self.origin_coords:
            point = to_shape(self.origin_coords)
            return (point.x, point.y)
        return None

    @property
    def destination_coordinates(self) -> tuple:
        """Get destination (longitude, latitude) tuple."""
        if self.destination_coords:
            point = to_shape(self.destination_coords)
            return (point.x, point.y)
        return None

    @property
    def route_coordinates(self) -> list:
        """Get route coordinates as list of [longitude, latitude] pairs."""
        if self.selected_route_geometry:
            line = to_shape(self.selected_route_geometry)
            return [[coord[0], coord[1]] for coord in line.coords]
        return []

    @property
    def savings_percentage(self) -> float:
        """Calculate savings percentage compared to alternative route."""
        if self.alternative_route_cost and self.alternative_route_cost > 0:
            return (float(self.savings_amount or 0) / float(self.alternative_route_cost)) * 100
        return 0.0

    @property
    def cost_per_km(self) -> float:
        """Calculate cost per kilometer."""
        if self.total_distance and self.total_distance > 0:
            return float(self.total_cost) / float(self.total_distance)
        return 0.0

    @property
    def fuel_cost_percentage(self) -> float:
        """Calculate fuel cost as percentage of total cost."""
        if self.total_cost and self.total_cost > 0:
            return (float(self.fuel_cost) / float(self.total_cost)) * 100
        return 0.0

    @property
    def toll_cost_percentage(self) -> float:
        """Calculate toll cost as percentage of total cost."""
        if self.total_cost and self.total_cost > 0:
            return (float(self.toll_cost) / float(self.total_cost)) * 100
        return 0.0

    @classmethod
    def get_company_routes(cls, session, company_id: UUID, limit: int = 100):
        """Get recent routes for a company."""
        return session.query(cls).filter(
            cls.company_id == company_id
        ).order_by(cls.created_at.desc()).limit(limit).all()

    @classmethod
    def get_user_routes(cls, session, user_id: UUID, limit: int = 50):
        """Get recent routes for a user."""
        return session.query(cls).filter(
            cls.user_id == user_id
        ).order_by(cls.created_at.desc()).limit(limit).all()

    @classmethod
    def get_vehicle_routes(cls, session, vehicle_id: UUID, limit: int = 50):
        """Get recent routes for a vehicle."""
        return session.query(cls).filter(
            cls.vehicle_id == vehicle_id
        ).order_by(cls.created_at.desc()).limit(limit).all()

    def __repr__(self):
        return f"<CalculatedRoute(id={self.id}, distance={self.total_distance}km, cost=${self.total_cost})>"

    def __str__(self):
        origin = self.origin_address or f"({self.origin_coordinates})"
        destination = self.destination_address or f"({self.destination_coordinates})"
        return f"{origin} → {destination} ({self.total_distance}km, ${self.total_cost})"