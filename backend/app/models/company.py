"""
Company model for transport companies.
"""
from sqlalchemy import Column, String, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid

from app.database import Base


class Company(Base):
    """
    Model for transport companies.
    
    Represents companies that use the route optimization system.
    Each company can have multiple users and vehicles.
    """
    __tablename__ = "companies"

    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4,
        index=True
    )
    name = Column(String(255), nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(50), nullable=True)
    address = Column(String(500), nullable=True)
    tax_id = Column(String(50), nullable=True, unique=True)  # CUIT/CUIL
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now()
    )

    # Relationships
    users = relationship("User", back_populates="company", cascade="all, delete-orphan")
    vehicles = relationship("Vehicle", back_populates="company", cascade="all, delete-orphan")
    calculated_routes = relationship("CalculatedRoute", back_populates="company")

    def __repr__(self):
        return f"<Company(id={self.id}, name='{self.name}', email='{self.email}')>"

    def __str__(self):
        return self.name