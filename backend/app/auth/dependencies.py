"""
Authentication dependencies for FastAPI endpoints.
"""
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session

from app.models.user import User, UserRole
from app.auth.jwt_handler import get_current_user
from app.database import get_db


def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Get current active user.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Active user object
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user


def get_current_admin_user(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Get current admin user.
    
    Args:
        current_user: Current active user
        
    Returns:
        Admin user object
        
    Raises:
        HTTPException: If user is not admin
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin role required."
        )
    return current_user


def get_current_verified_user(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Get current verified user.
    
    Args:
        current_user: Current active user
        
    Returns:
        Verified user object
        
    Raises:
        HTTPException: If user is not verified
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User email not verified"
        )
    return current_user


def check_company_access(
    company_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> User:
    """
    Check if current user has access to a specific company.
    
    Args:
        company_id: Company ID to check access for
        current_user: Current active user
        db: Database session
        
    Returns:
        User object if access is granted
        
    Raises:
        HTTPException: If user doesn't have access to company
    """
    # Admin users have access to all companies
    if current_user.role == UserRole.ADMIN:
        return current_user
    
    # Regular users can only access their own company
    if str(current_user.company_id) != company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this company's data"
        )
    
    return current_user


def check_vehicle_access(
    vehicle_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
) -> User:
    """
    Check if current user has access to a specific vehicle.
    
    Args:
        vehicle_id: Vehicle ID to check access for
        current_user: Current active user
        db: Database session
        
    Returns:
        User object if access is granted
        
    Raises:
        HTTPException: If user doesn't have access to vehicle
    """
    from app.models.vehicle import Vehicle
    
    # Admin users have access to all vehicles
    if current_user.role == UserRole.ADMIN:
        return current_user
    
    # Check if vehicle belongs to user's company
    vehicle = db.query(Vehicle).filter(Vehicle.id == vehicle_id).first()
    if not vehicle:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found"
        )
    
    if vehicle.company_id != current_user.company_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions to access this vehicle"
        )
    
    return current_user