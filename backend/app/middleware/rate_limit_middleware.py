"""
Rate limiting middleware.
"""
import time
from collections import defaultdict, deque
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import logging

from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using sliding window algorithm.
    
    Limits requests per IP address and per authenticated user.
    """
    
    def __init__(self, app, requests_per_minute: int = None):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute or settings.rate_limit_per_minute
        self.window_size = 60  # 1 minute in seconds
        
        # Storage for request timestamps
        self.ip_requests = defaultdict(deque)
        self.user_requests = defaultdict(deque)
        
        # Excluded paths that don't count towards rate limit
        self.excluded_paths = [
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json"
        ]
    
    def _clean_old_requests(self, request_queue: deque, current_time: float):
        """
        Remove requests older than the window size.
        
        Args:
            request_queue: Deque of request timestamps
            current_time: Current timestamp
        """
        while request_queue and current_time - request_queue[0] > self.window_size:
            request_queue.popleft()
    
    def _is_rate_limited(self, identifier: str, request_queue: deque, current_time: float) -> bool:
        """
        Check if identifier is rate limited.
        
        Args:
            identifier: IP address or user ID
            request_queue: Deque of request timestamps for this identifier
            current_time: Current timestamp
            
        Returns:
            True if rate limited, False otherwise
        """
        # Clean old requests
        self._clean_old_requests(request_queue, current_time)
        
        # Check if limit exceeded
        if len(request_queue) >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for {identifier}")
            return True
        
        # Add current request
        request_queue.append(current_time)
        return False
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """
        Process request through rate limiting middleware.
        
        Args:
            request: HTTP request
            call_next: Next middleware/handler in chain
            
        Returns:
            HTTP response
        """
        # Skip rate limiting for excluded paths
        if any(request.url.path.startswith(path) for path in self.excluded_paths):
            return await call_next(request)
        
        current_time = time.time()
        client_ip = request.client.host
        
        # Check IP-based rate limiting
        if self._is_rate_limited(f"ip:{client_ip}", self.ip_requests[client_ip], current_time):
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "detail": "Too many requests. Please try again later.",
                    "retry_after": 60
                },
                headers={"Retry-After": "60"}
            )
        
        # Check user-based rate limiting if authenticated
        user_id = getattr(request.state, 'user_id', None)
        if user_id:
            if self._is_rate_limited(f"user:{user_id}", self.user_requests[user_id], current_time):
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "detail": "Too many requests for this user. Please try again later.",
                        "retry_after": 60
                    },
                    headers={"Retry-After": "60"}
                )
        
        # Continue to next middleware/handler
        response = await call_next(request)
        
        # Add rate limit headers to response
        remaining_requests = max(0, self.requests_per_minute - len(self.ip_requests[client_ip]))
        response.headers["X-RateLimit-Limit"] = str(self.requests_per_minute)
        response.headers["X-RateLimit-Remaining"] = str(remaining_requests)
        response.headers["X-RateLimit-Reset"] = str(int(current_time + self.window_size))
        
        return response