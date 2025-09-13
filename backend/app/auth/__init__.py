"""
Authentication module for JWT token management and user authentication.
"""

from .jwt_handler import create_access_token, verify_token, get_current_user
from .password_handler import hash_password, verify_password
from .dependencies import get_current_active_user, get_current_admin_user
from .permissions import Permission, has_permission, get_user_permissions
from .decorators import (
    require_permission, 
    require_admin, 
    require_vehicle_access,
    require_route_access,
    require_fuel_price_management,
    require_toll_management
)

__all__ = [
    "create_access_token",
    "verify_token", 
    "get_current_user",
    "hash_password",
    "verify_password",
    "get_current_active_user",
    "get_current_admin_user",
    "Permission",
    "has_permission",
    "get_user_permissions",
    "require_permission",
    "require_admin",
    "require_vehicle_access",
    "require_route_access",
    "require_fuel_price_management",
    "require_toll_management"
]