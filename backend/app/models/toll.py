"""
Toll model with PostGIS geometry for spatial queries.
"""
from sqlalchemy import Column, String, DateTime, Numeric, Boolean, Index, Integer, Float
from sqlalchemy.sql import func

from app.database import Base


class Toll(Base):
    """
    Model for toll stations with geographic location.
    
    Uses PostGIS geometry for spatial queries to determine
    which tolls are intersected by calculated routes.
    """
    __tablename__ = "tolls"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    road_name = Column(
        String(255), 
        nullable=False, 
        index=True,
        comment="Road name (e.g., RN12, RN14)"
    )
    latitude = Column(
        Float, 
        nullable=False,
        comment="Latitude coordinate"
    )
    longitude = Column(
        Float, 
        nullable=False,
        comment="Longitude coordinate"
    )
    tariff = Column(
        Numeric(10, 2), 
        nullable=False,
        comment="Toll tariff in ARS"
    )
    region = Column(
        String(100), 
        nullable=False,
        default="NEA",
        comment="Region code"
    )
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    updated_by = Column(String(50), nullable=True, comment="User ID who updated")

    # Create index for efficient geographic queries
    __table_args__ = (
        Index('idx_tolls_coordinates', 'latitude', 'longitude'),
        Index('idx_tolls_road_region', 'road_name', 'region'),
    )

    @property
    def coordinates(self) -> tuple:
        """Get (longitude, latitude) tuple."""
        return (self.longitude, self.latitude)

    @classmethod
    def find_tolls_in_region(cls, session, min_lat: float, max_lat: float, 
                           min_lon: float, max_lon: float):
        """
        Find tolls within a bounding box.
        
        Args:
            session: Database session
            min_lat, max_lat: Latitude bounds
            min_lon, max_lon: Longitude bounds
            
        Returns:
            List of Toll objects
        """
        return session.query(cls).filter(
            cls.is_active == True,
            cls.latitude.between(min_lat, max_lat),
            cls.longitude.between(min_lon, max_lon)
        ).all()

    def distance_to_point(self, longitude: float, latitude: float) -> float:
        """
        Calculate distance to a point in meters using Haversine formula.
        
        Args:
            longitude: Point longitude
            latitude: Point latitude
            
        Returns:
            Distance in meters
        """
        from geopy.distance import geodesic
        return geodesic(
            (self.latitude, self.longitude),
            (latitude, longitude)
        ).meters

    def __repr__(self):
        return f"<Toll(id={self.id}, name='{self.name}', road='{self.road_name}', tariff={self.tariff})>"

    def __str__(self):
        return f"{self.name} ({self.road_name}) - ${self.tariff}"