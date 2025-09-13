"""
Authorization decorators for FastAPI endpoints.
"""
from functools import wraps
from typing import List, Callable, Any
from fastapi import HTTPException, status, Depends

from app.models.user import User
from app.auth.dependencies import get_current_active_user
from app.auth.permissions import Permission, has_permission, has_any_permission, has_all_permissions


def require_permission(permission: Permission):
    """
    Decorator to require a specific permission.
    
    Args:
        permission: Required permission
        
    Returns:
        Dependency function
    """
    def permission_dependency(current_user: User = Depends(get_current_active_user)) -> User:
        if not has_permission(current_user.role, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission required: {permission.value}"
            )
        return current_user
    
    return permission_dependency


def require_any_permission(permissions: List[Permission]):
    """
    Decorator to require any of the specified permissions.
    
    Args:
        permissions: List of permissions (user needs at least one)
        
    Returns:
        Dependency function
    """
    def permission_dependency(current_user: User = Depends(get_current_active_user)) -> User:
        if not has_any_permission(current_user.role, permissions):
            permission_names = [p.value for p in permissions]
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"One of these permissions required: {', '.join(permission_names)}"
            )
        return current_user
    
    return permission_dependency


def require_all_permissions(permissions: List[Permission]):
    """
    Decorator to require all of the specified permissions.
    
    Args:
        permissions: List of permissions (user needs all of them)
        
    Returns:
        Dependency function
    """
    def permission_dependency(current_user: User = Depends(get_current_active_user)) -> User:
        if not has_all_permissions(current_user.role, permissions):
            permission_names = [p.value for p in permissions]
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"All of these permissions required: {', '.join(permission_names)}"
            )
        return current_user
    
    return permission_dependency


# Convenience decorators for common permission checks
def require_admin():
    """Require admin role."""
    return require_permission(Permission.ADMIN_PANEL)


def require_vehicle_access():
    """Require vehicle management permissions."""
    return require_any_permission([
        Permission.CREATE_VEHICLE,
        Permission.READ_VEHICLE,
        Permission.UPDATE_VEHICLE,
        Permission.DELETE_VEHICLE
    ])


def require_route_access():
    """Require route calculation permissions."""
    return require_any_permission([
        Permission.CALCULATE_ROUTE,
        Permission.READ_ROUTE
    ])


def require_fuel_price_management():
    """Require fuel price management permissions."""
    return require_any_permission([
        Permission.CREATE_FUEL_PRICE,
        Permission.UPDATE_FUEL_PRICE,
        Permission.DELETE_FUEL_PRICE
    ])


def require_toll_management():
    """Require toll management permissions."""
    return require_any_permission([
        Permission.CREATE_TOLL,
        Permission.UPDATE_TOLL,
        Permission.DELETE_TOLL
    ])


def require_system_management():
    """Require system management permissions."""
    return require_permission(Permission.MANAGE_SYSTEM_DATA)