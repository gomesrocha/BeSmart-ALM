"""Tenant middleware for multi-tenant isolation."""
from typing import Callable
from uuid import UUID

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from services.identity.security import decode_token


class TenantMiddleware(BaseHTTPMiddleware):
    """Middleware to extract and inject tenant_id from JWT token into request state.
    
    This middleware:
    1. Extracts the JWT token from the Authorization header
    2. Decodes the token to get tenant_id and is_super_admin
    3. Injects these values into request.state for easy access in route handlers
    
    This enables automatic tenant isolation without manually extracting
    tenant_id in every endpoint.
    """

    def __init__(self, app: ASGIApp):
        """Initialize the middleware.
        
        Args:
            app: The ASGI application
        """
        super().__init__(app)

    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        """Process the request and inject tenant information.
        
        Args:
            request: The incoming request
            call_next: The next middleware or route handler
            
        Returns:
            The response from the next handler
        """
        # Initialize tenant_id and is_super_admin as None
        request.state.tenant_id = None
        request.state.is_super_admin = False

        # Try to extract tenant info from JWT token
        auth_header = request.headers.get("Authorization")
        
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
            
            try:
                # Decode token to get tenant_id and is_super_admin
                payload = decode_token(token)
                
                # Extract tenant_id
                tenant_id_str = payload.get("tenant_id")
                if tenant_id_str:
                    request.state.tenant_id = UUID(tenant_id_str)
                
                # Extract is_super_admin flag
                request.state.is_super_admin = payload.get("is_super_admin", False)
                
            except Exception:
                # If token is invalid, leave tenant_id as None
                # The authentication will be handled by the auth dependency
                pass

        # Continue processing the request
        response = await call_next(request)
        return response
