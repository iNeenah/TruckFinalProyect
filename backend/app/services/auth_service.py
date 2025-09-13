"""
Authentication service for user login, registration, and token management.
"""
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.models.company import Company
from app.schemas.user import UserCreate, UserLogin
from app.auth.password_handler import hash_password, verify_password, is_password_strong
from app.auth.jwt_handler import create_user_token


class AuthService:
    """Service for authentication operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def register_user(self, user_data: UserCreate) -> Dict[str, Any]:
        """
        Register a new user.
        
        Args:
            user_data: User registration data
            
        Returns:
            User token data
            
        Raises:
            HTTPException: If registration fails
        """
        # Check if user already exists
        existing_user = self.db.query(User).filter(User.email == user_data.email).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Check if company exists
        company = self.db.query(Company).filter(Company.id == user_data.company_id).first()
        if not company:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Company not found"
            )
        
        if not company.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Company is not active"
            )
        
        # Validate password strength
        is_strong, issues = is_password_strong(user_data.password)
        if not is_strong:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Password requirements not met: {', '.join(issues)}"
            )
        
        # Create new user
        hashed_password = hash_password(user_data.password)
        db_user = User(
            email=user_data.email,
            hashed_password=hashed_password,
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            role=user_data.role,
            company_id=user_data.company_id,
            is_active=True,
            is_verified=False  # Email verification required
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        # Create token
        token_data = create_user_token(db_user)
        
        return {
            **token_data,
            "user": {
                "id": str(db_user.id),
                "email": db_user.email,
                "full_name": db_user.full_name,
                "role": db_user.role.value,
                "company_id": str(db_user.company_id),
                "is_verified": db_user.is_verified
            }
        }
    
    def login_user(self, login_data: UserLogin) -> Dict[str, Any]:
        """
        Authenticate user login.
        
        Args:
            login_data: User login credentials
            
        Returns:
            User token data
            
        Raises:
            HTTPException: If login fails
        """
        # Find user by email
        user = self.db.query(User).filter(User.email == login_data.email).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Verify password
        if not verify_password(login_data.password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Check if user is active
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User account is disabled"
            )
        
        # Check if company is active
        if not user.company.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Company account is disabled"
            )
        
        # Update last login
        user.last_login = datetime.utcnow()
        self.db.commit()
        
        # Create token
        token_data = create_user_token(user)
        
        return {
            **token_data,
            "user": {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value,
                "company_id": str(user.company_id),
                "company_name": user.company.name,
                "is_verified": user.is_verified,
                "last_login": user.last_login.isoformat() if user.last_login else None
            }
        }
    
    def change_password(self, user: User, current_password: str, new_password: str) -> bool:
        """
        Change user password.
        
        Args:
            user: User object
            current_password: Current password
            new_password: New password
            
        Returns:
            True if password changed successfully
            
        Raises:
            HTTPException: If password change fails
        """
        # Verify current password
        if not verify_password(current_password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Validate new password strength
        is_strong, issues = is_password_strong(new_password)
        if not is_strong:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"New password requirements not met: {', '.join(issues)}"
            )
        
        # Update password
        user.hashed_password = hash_password(new_password)
        self.db.commit()
        
        return True
    
    def verify_email(self, user: User) -> bool:
        """
        Mark user email as verified.
        
        Args:
            user: User object
            
        Returns:
            True if email verified successfully
        """
        user.is_verified = True
        self.db.commit()
        return True
    
    def deactivate_user(self, user: User) -> bool:
        """
        Deactivate user account.
        
        Args:
            user: User object
            
        Returns:
            True if user deactivated successfully
        """
        user.is_active = False
        self.db.commit()
        return True
    
    def reactivate_user(self, user: User) -> bool:
        """
        Reactivate user account.
        
        Args:
            user: User object
            
        Returns:
            True if user reactivated successfully
        """
        user.is_active = True
        self.db.commit()
        return True