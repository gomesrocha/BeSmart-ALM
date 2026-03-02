"""Dependencies for Identity service."""
from functools import wraps
from typing import Annotated, Callable, Optional
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from services.identity.models import User
from services.identity.permissions import Permission, check_permission
from services.identity.schemas import TokenPayload
from services.identity.security import decode_token
from services.shared.database import get_session

# Security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> User:
    """Get current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer credentials
        session: Database session
        
    Returns:
        Current user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = decode_token(token)
        
        # Validate token type
        if payload.get("type") != "access":
            raise credentials_exception
        
        # Extract user info
        user_id: UUID = UUID(payload.get("sub"))
        if user_id is None:
            raise credentials_exception
        
        # Extrair tenant_id e is_super_admin do token
        tenant_id_str = payload.get("tenant_id")
        is_super_admin = payload.get("is_super_admin", False)
            
    except (JWTError, ValueError):
        raise credentials_exception
    
    # Get user from database
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Get current active user.
    
    Args:
        current_user: Current user from token
        
    Returns:
        Current active user
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    return current_user


async def get_current_superuser(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Get current superuser.
    
    Args:
        current_user: Current user from token
        
    Returns:
        Current superuser
        
    Raises:
        HTTPException: If user is not a superuser
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return current_user


def get_tenant_id(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UUID:
    """Get tenant ID from current user.
    
    Args:
        current_user: Current user from token
        
    Returns:
        Tenant ID
    """
    return current_user.tenant_id


def get_tenant_id_from_request(request: Request) -> Optional[UUID]:
    """Get tenant ID from request state (injected by TenantMiddleware).
    
    This is useful for accessing tenant_id without requiring authentication.
    
    Args:
        request: FastAPI request object
        
    Returns:
        Tenant ID if available, None otherwise
    """
    return getattr(request.state, "tenant_id", None)


def is_super_admin_from_request(request: Request) -> bool:
    """Check if current user is super admin from request state.
    
    Args:
        request: FastAPI request object
        
    Returns:
        True if user is super admin, False otherwise
    """
    return getattr(request.state, "is_super_admin", False)



class PermissionChecker:
    """Dependency to check user permissions."""

    def __init__(
        self,
        required_permission: Permission | str,
        project_id_param: Optional[str] = None,
    ):
        """Initialize permission checker.

        Args:
            required_permission: Permission required
            project_id_param: Optional parameter name for project_id in path/query
        """
        self.required_permission = required_permission
        self.project_id_param = project_id_param

    async def __call__(
        self,
        current_user: Annotated[User, Depends(get_current_user)],
        session: Annotated[AsyncSession, Depends(get_session)],
    ) -> User:
        """Check if user has required permission.

        Args:
            current_user: Current authenticated user
            session: Database session

        Returns:
            Current user if has permission

        Raises:
            HTTPException: If user doesn't have permission
        """
        # Superusers bypass permission checks
        if current_user.is_superuser:
            return current_user

        # Check permission
        has_permission = await check_permission(
            current_user,
            self.required_permission,
            session,
        )

        if not has_permission:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {self.required_permission}",
            )

        return current_user


def require_permissions(*permissions: Permission | str) -> Callable:
    """Decorator to require specific permissions.

    Args:
        *permissions: Permissions required

    Returns:
        Decorator function
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract user and session from kwargs
            current_user = kwargs.get("current_user")
            session = kwargs.get("session")

            if not current_user or not session:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Missing user or session in request context",
                )

            # Superusers bypass checks
            if current_user.is_superuser:
                return await func(*args, **kwargs)

            # Check all required permissions
            for permission in permissions:
                has_permission = await check_permission(
                    current_user,
                    permission,
                    session,
                )
                if not has_permission:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"Permission denied: {permission}",
                    )

            return await func(*args, **kwargs)

        return wrapper

    return decorator



async def get_user_from_api_token(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    session: Annotated[AsyncSession, Depends(get_session)],
) -> User:
    """Get user from API token.

    Args:
        credentials: HTTP Bearer credentials
        session: Database session

    Returns:
        User associated with API token

    Raises:
        HTTPException: If token is invalid
    """
    from services.identity.models import APIToken
    from services.identity.security import verify_api_token

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials

    # Try to find token in database
    result = await session.execute(
        select(APIToken).where(APIToken.is_active == True)  # noqa: E712
    )
    api_tokens = result.scalars().all()

    # Check each active token
    matching_token = None
    for api_token in api_tokens:
        if verify_api_token(token, api_token.token_hash):
            matching_token = api_token
            break

    if not matching_token:
        raise credentials_exception

    # Check expiration
    if matching_token.expires_at and matching_token.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API token expired",
        )

    # Update last used timestamp
    matching_token.last_used_at = datetime.utcnow()
    session.add(matching_token)
    await session.commit()

    # Get user
    result = await session.execute(
        select(User).where(User.id == matching_token.user_id)
    )
    user = result.scalar_one_or_none()

    if not user or not user.is_active:
        raise credentials_exception

    return user
