"""Authentication router."""
from datetime import datetime, timedelta
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from services.identity.dependencies import get_current_user
from services.identity.models import User
from services.identity.schemas import (
    LoginRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserResponse,
)
from services.identity.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from services.shared.config import settings
from services.shared.database import get_session

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: LoginRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> TokenResponse:
    """Login endpoint.
    
    Authenticates user and returns JWT tokens.
    
    Args:
        credentials: Login credentials (email and password)
        session: Database session
        
    Returns:
        Access and refresh tokens
        
    Raises:
        HTTPException: If credentials are invalid
    """
    # Find user by email
    result = await session.execute(
        select(User).where(User.email == credentials.email)
    )
    user = result.scalar_one_or_none()
    
    # Verify user exists and password is correct
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    session.add(user)
    await session.commit()
    
    # Create tokens com tenant_id e is_superuser
    token_data = {
        "sub": str(user.id),
        "tenant_id": str(user.tenant_id),
        "email": user.email,
    }
    
    # Verificar se é superuser
    is_superuser = getattr(user, "is_superuser", False)
    
    access_token = create_access_token(
        token_data,
        tenant_id=user.tenant_id,
        is_super_admin=is_superuser,
    )
    refresh_token = create_refresh_token(token_data)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.jwt_access_token_expire_minutes * 60,
    )


@router.post("/token/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> TokenResponse:
    """Refresh access token.
    
    Uses refresh token to generate new access token.
    
    Args:
        request: Refresh token request
        session: Database session
        
    Returns:
        New access and refresh tokens
        
    Raises:
        HTTPException: If refresh token is invalid
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = decode_token(request.refresh_token)
        
        # Validate token type
        if payload.get("type") != "refresh":
            raise credentials_exception
        
        # Extract user info
        user_id: UUID = UUID(payload.get("sub"))
        if user_id is None:
            raise credentials_exception
            
    except Exception:
        raise credentials_exception
    
    # Get user from database
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if user is None or not user.is_active:
        raise credentials_exception
    
    # Create new tokens com tenant_id e is_super_admin
    token_data = {
        "sub": str(user.id),
        "tenant_id": str(user.tenant_id),
        "email": user.email,
    }
    
    # Verificar se é super admin
    is_super_admin = getattr(user, "is_superuser", False)
    
    access_token = create_access_token(
        token_data,
        tenant_id=user.tenant_id,
        is_super_admin=is_super_admin,
    )
    refresh_token = create_refresh_token(token_data)
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
        expires_in=settings.jwt_access_token_expire_minutes * 60,
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserResponse:
    """Get current user information.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User information
    """
    return UserResponse.model_validate(current_user)


@router.post("/logout")
async def logout(
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict[str, str]:
    """Logout endpoint.
    
    Note: With JWT, logout is handled client-side by removing the token.
    This endpoint is provided for consistency and can be extended for
    token blacklisting if needed.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Success message
    """
    return {"message": "Successfully logged out"}


@router.get("/permissions", response_model=dict)
async def get_user_permissions(
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> dict:
    """Get current user's permissions.

    Args:
        session: Database session
        current_user: Current authenticated user

    Returns:
        Dictionary with user permissions and roles
    """
    try:
        from services.identity.permission_service import PermissionService

        # Obter permissões do usuário
        permissions = await PermissionService.get_user_permissions(
            user=current_user, session=session, use_cache=True
        )

        # Obter roles do usuário
        roles = await PermissionService.get_user_roles(
            user=current_user, session=session
        )

        # Montar resposta
        return {
            "user_id": str(current_user.id),
            "email": current_user.email,
            "tenant_id": str(current_user.tenant_id),
            "is_super_admin": getattr(current_user, "is_superuser", False),
            "permissions": permissions,
            "roles": [
                {
                    "id": str(role.id),
                    "name": role.name,
                    "display_name": getattr(role, "display_name", role.name),
                    "description": role.description,
                }
                for role in roles
            ],
        }
    except Exception as e:
        import traceback
        print(f"❌ Error in get_user_permissions: {e}")
        print(traceback.format_exc())
        # Retornar resposta vazia em caso de erro
        return {
            "user_id": str(current_user.id),
            "email": current_user.email,
            "tenant_id": str(current_user.tenant_id),
            "is_super_admin": False,
            "permissions": [],
            "roles": [],
            "error": str(e)
        }
