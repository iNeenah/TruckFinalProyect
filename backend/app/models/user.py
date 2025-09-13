"""
User model for system authentication and authorization.
"""
from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum

from app.database import Base


class UserRole(str, enum.Enum):
    """User roles in the system."""
    ADMIN = "admin"
    OPERATOR = "operator"


class User(Base):
    """
    Model for system users.
    
    Users belong to companies and can have different roles.
    Admins can manage system data, operators can calculate routes.
    """
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid.uuid4,
        index=True
    )
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    role = Column(
        Enum(UserRole), 
        default=UserRole.OPERATOR, 
        nullable=False
    )
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    last_login = Column(DateTime(timezone=True), nullable=True)
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
    company = relationship("Company", back_populates="users")
    calculated_routes = relationship("CalculatedRoute", back_populates="user")
    fuel_price_updates = relationship("FuelPrice", back_populates="updated_by_user")

    @property
    def full_name(self) -> str:
        """Get user's full name."""
        return f"{self.first_name} {self.last_name}"

    @property
    def is_admin(self) -> bool:
        """Check if user is admin."""
        return self.role == UserRole.ADMIN

    @property
    def is_operator(self) -> bool:
        """Check if user is operator."""
        return self.role == UserRole.OPERATOR

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"

    def __str__(self):
        return f"{self.full_name} ({self.email})"