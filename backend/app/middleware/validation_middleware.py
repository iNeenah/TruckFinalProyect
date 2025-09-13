"""
Validation middleware for handling validation errors.
"""
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)


class ValidationMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle validation errors and provide user-friendly responses.
    """
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process request through validation middleware.
        
        Args:
            request: HTTP request
            call_next: Next middleware/handler in chain
            
        Returns:
            HTTP response
        """
        try:
            response = await call_next(request)
            return response
            
        except ValidationError as e:
            # Handle Pydantic validation errors
            logger.warning(f"Validation error: {e}")
            
            errors = []
            for error in e.errors():
                field = " -> ".join(str(loc) for loc in error["loc"])
                message = error["msg"]
                errors.append({
                    "field": field,
                    "message": message,
                    "type": error["type"]
                })
            
            return JSONResponse(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                content={
                    "detail": "Validation error",
                    "errors": errors
                }
            )
            
        except HTTPException as e:
            # Handle HTTP exceptions (including our custom validation errors)
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail}
            )
            
        except Exception as e:
            # Handle unexpected errors
            logger.error(f"Unexpected error in validation middleware: {e}")
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"detail": "Internal server error"}
            )