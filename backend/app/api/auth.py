"""
Authentication API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import UserCreate, UserLogin, TokenResponse, PasswordChange
from app.services.auth_service import AuthService
from app.auth.dependencies import get_current_active_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user.
    
    Creates a new user account and returns authentication token.
    """
    auth_service = AuthService(db)
    result = auth_service.register_user(user_data)
    
    return TokenResponse(
        access_token=result["access_token"],
        token_type=result["token_type"],
        expires_in=result["expires_in"],
        user=result["user"]
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: UserLogin,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return access token.
    
    Validates user credentials and returns JWT token for API access.
    """
    auth_service = AuthService(db)
    result = auth_service.login_user(login_data)
    
    return TokenResponse(
        access_token=result["access_token"],
        token_type=result["token_type"],
        expires_in=result["expires_in"],
        user=result["user"]
    )


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    password_data: PasswordChange,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Change user password.
    
    Requires current password for verification.
    """
    auth_service = AuthService(db)
    auth_service.change_password(
        current_user,
        password_data.current_password,
        password_data.new_password
    )
    
    return {"message": "Password changed successfully"}


@router.post("/verify-email", status_code=status.HTTP_200_OK)
async def verify_email(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Verify user email address.
    
    Marks the current user's email as verified.
    """
    auth_service = AuthService(db)
    auth_service.verify_email(current_user)
    
    return {"message": "Email verified successfully"}


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    current_user: User = Depends(get_current_active_user)
):
    """
    Logout user.
    
    Note: JWT tokens are stateless, so logout is handled client-side
    by removing the token. This endpoint is for consistency.
    """
    return {"message": "Logged out successfully"}


@router.get("/me")
async def get_current_user_info(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current user information.
    
    Returns detailed information about the authenticated user.
    """
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "first_name": current_user.first_name,
        "last_name": current_user.last_name,
        "role": current_user.role.value,
        "is_active": current_user.is_active,
        "is_verified": current_user.is_verified,
        "company_id": str(current_user.company_id),
        "company_name": current_user.company.name,
        "last_login": current_user.last_login.isoformat() if current_user.last_login else None,
        "created_at": current_user.created_at.isoformat(),
        "updated_at": current_user.updated_at.isoformat()
    }


@router.get("/health")
async def auth_health_check():
    """
    Health check endpoint for authentication service.
    """
    return {"status": "healthy", "service": "authentication"}