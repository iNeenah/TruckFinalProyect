"""
Permission system for role-based access control.
"""
from enum import Enum
from typing import List, Set
from app.models.user import UserRole


class Permission(str, Enum):
    """System permissions."""
    
    # User management
    CREATE_USER = "create_user"
    READ_USER = "read_user"
    UPDATE_USER = "update_user"
    DELETE_USER = "delete_user"
    
    # Company management
    CREATE_COMPANY = "create_company"
    READ_COMPANY = "read_company"
    UPDATE_COMPANY = "update_company"
    DELETE_COMPANY = "delete_company"
    
    # Vehicle management
    CREATE_VEHICLE = "create_vehicle"
    READ_VEHICLE = "read_vehicle"
    UPDATE_VEHICLE = "update_vehicle"
    DELETE_VEHICLE = "delete_vehicle"
    
    # Route calculation
    CALCULATE_ROUTE = "calculate_route"
    READ_ROUTE = "read_route"
    DELETE_ROUTE = "delete_route"
    
    # Fuel price management
    CREATE_FUEL_PRICE = "create_fuel_price"
    READ_FUEL_PRICE = "read_fuel_price"
    UPDATE_FUEL_PRICE = "update_fuel_price"
    DELETE_FUEL_PRICE = "delete_fuel_price"
    
    # Toll management
    CREATE_TOLL = "create_toll"
    READ_TOLL = "read_toll"
    UPDATE_TOLL = "update_toll"
    DELETE_TOLL = "delete_toll"
    
    # Report generation
    GENERATE_REPORT = "generate_report"
    
    # System administration
    ADMIN_PANEL = "admin_panel"
    VIEW_SYSTEM_STATS = "view_system_stats"
    MANAGE_SYSTEM_DATA = "manage_system_data"


# Role-based permissions mapping
ROLE_PERMISSIONS: dict[UserRole, Set[Permission]] = {
    UserRole.ADMIN: {
        # Admin has all permissions
        Permission.CREATE_USER,
        Permission.READ_USER,
        Permission.UPDATE_USER,
        Permission.DELETE_USER,
        Permission.CREATE_COMPANY,
        Permission.READ_COMPANY,
        Permission.UPDATE_COMPANY,
        Permission.DELETE_COMPANY,
        Permission.CREATE_VEHICLE,
        Permission.READ_VEHICLE,
        Permission.UPDATE_VEHICLE,
        Permission.DELETE_VEHICLE,
        Permission.CALCULATE_ROUTE,
        Permission.READ_ROUTE,
        Permission.DELETE_ROUTE,
        Permission.CREATE_FUEL_PRICE,
        Permission.READ_FUEL_PRICE,
        Permission.UPDATE_FUEL_PRICE,
        Permission.DELETE_FUEL_PRICE,
        Permission.CREATE_TOLL,
        Permission.READ_TOLL,
        Permission.UPDATE_TOLL,
        Permission.DELETE_TOLL,
        Permission.GENERATE_REPORT,
        Permission.ADMIN_PANEL,
        Permission.VIEW_SYSTEM_STATS,
        Permission.MANAGE_SYSTEM_DATA,
    },
    UserRole.OPERATOR: {
        # Operator has limited permissions
        Permission.READ_USER,  # Can read own user info
        Permission.UPDATE_USER,  # Can update own user info
        Permission.READ_COMPANY,  # Can read own company info
        Permission.CREATE_VEHICLE,  # Can manage company vehicles
        Permission.READ_VEHICLE,
        Permission.UPDATE_VEHICLE,
        Permission.DELETE_VEHICLE,
        Permission.CALCULATE_ROUTE,  # Main functionality
        Permission.READ_ROUTE,
        Permission.READ_FUEL_PRICE,  # Can view prices
        Permission.READ_TOLL,  # Can view tolls
        Permission.GENERATE_REPORT,  # Can generate reports
    }
}


def get_user_permissions(role: UserRole) -> Set[Permission]:
    """
    Get all permissions for a user role.
    
    Args:
        role: User role
        
    Returns:
        Set of permissions for the role
    """
    return ROLE_PERMISSIONS.get(role, set())


def has_permission(role: UserRole, permission: Permission) -> bool:
    """
    Check if a role has a specific permission.
    
    Args:
        role: User role
        permission: Permission to check
        
    Returns:
        True if role has permission, False otherwise
    """
    user_permissions = get_user_permissions(role)
    return permission in user_permissions


def has_any_permission(role: UserRole, permissions: List[Permission]) -> bool:
    """
    Check if a role has any of the specified permissions.
    
    Args:
        role: User role
        permissions: List of permissions to check
        
    Returns:
        True if role has any of the permissions, False otherwise
    """
    user_permissions = get_user_permissions(role)
    return any(permission in user_permissions for permission in permissions)


def has_all_permissions(role: UserRole, permissions: List[Permission]) -> bool:
    """
    Check if a role has all of the specified permissions.
    
    Args:
        role: User role
        permissions: List of permissions to check
        
    Returns:
        True if role has all permissions, False otherwise
    """
    user_permissions = get_user_permissions(role)
    return all(permission in user_permissions for permission in permissions)


def require_admin_role(user) -> None:
    """
    Require admin role for accessing endpoint.
    
    Args:
        user: Current user object
        
    Raises:
        HTTPException: If user is not admin
    """
    from fastapi import HTTPException, status
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    if not hasattr(user, 'role') or user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )


def require_permission(user, permission: Permission) -> None:
    """
    Require specific permission for accessing endpoint.
    
    Args:
        user: Current user object
        permission: Required permission
        
    Raises:
        HTTPException: If user doesn't have permission
    """
    from fastapi import HTTPException, status
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )
    
    if not hasattr(user, 'role') or not has_permission(user.role, permission):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission required: {permission.value}"
        )