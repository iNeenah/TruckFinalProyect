"""
Authentication middleware for request processing.
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import logging

from app.auth.jwt_handler import verify_token

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle authentication for protected routes.
    
    This middleware runs before route handlers and can:
    - Log authentication attempts
    - Add user context to requests
    - Handle authentication errors globally
    """
    
    def __init__(self, app, excluded_paths: list = None):
        super().__init__(app)
        self.excluded_paths = excluded_paths or [
            "/docs",
            "/redoc",
            "/openapi.json",
            "/health",
            "/auth/login",
            "/auth/register",
            "/auth/health"
        ]
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process request through authentication middleware.
        
        Args:
            request: HTTP request
            call_next: Next middleware/handler in chain
            
        Returns:
            HTTP response
        """
        # Skip authentication for excluded paths
        if any(request.url.path.startswith(path) for path in self.excluded_paths):
            return await call_next(request)
        
        # Extract authorization header
        authorization = request.headers.get("Authorization")
        
        if authorization:
            try:
                # Extract token from "Bearer <token>" format
                scheme, token = authorization.split()
                if scheme.lower() != "bearer":
                    logger.warning(f"Invalid authorization scheme: {scheme}")
                else:
                    # Verify token and add user info to request state
                    payload = verify_token(token)
                    request.state.user_id = payload.get("sub")
                    request.state.user_email = payload.get("email")
                    request.state.user_role = payload.get("role")
                    
                    logger.info(f"Authenticated request from user: {request.state.user_email}")
                    
            except ValueError:
                logger.warning("Invalid authorization header format")
            except Exception as e:
                logger.warning(f"Token verification failed: {e}")
        
        # Continue to next middleware/handler
        try:
            response = await call_next(request)
            return response
        except HTTPException as e:
            # Handle HTTP exceptions
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail}
            )
        except Exception as e:
            # Handle unexpected errors
            logger.error(f"Unexpected error in auth middleware: {e}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Internal server error"}
            )