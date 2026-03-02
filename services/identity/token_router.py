"""API Token management router."""
from datetime import datetime, timedelta
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from services.identity.dependencies import get_current_user, get_tenant_id
from services.identity.models import APIToken, User
from services.identity.schemas import APITokenCreate, APITokenInfo, APITokenResponse
from services.identity.security import generate_api_token, hash_api_token
from services.shared.database import get_session

router = APIRouter(prefix="/api-tokens", tags=["API Tokens"])


@router.get("", response_model=list[APITokenInfo])
async def list_api_tokens(
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
) -> list[APITokenInfo]:
    """List all API tokens for current user.

    Args:
        session: Database session
        current_user: Current authenticated user
        tenant_id: Tenant ID

    Returns:
        List of API tokens (without token values)
    """
    result = await session.execute(
        select(APIToken)
        .where(
            APIToken.tenant_id == tenant_id,
            APIToken.user_id == current_user.id,
        )
        .order_by(APIToken.created_at.desc())
    )
    tokens = result.scalars().all()
    return [APITokenInfo.model_validate(token) for token in tokens]


@router.post("", response_model=APITokenResponse, status_code=status.HTTP_201_CREATED)
async def create_api_token(
    token_data: APITokenCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
) -> APITokenResponse:
    """Create new API token.

    Args:
        token_data: Token creation data
        session: Database session
        current_user: Current authenticated user
        tenant_id: Tenant ID

    Returns:
        Created API token (with token value - only shown once!)
    """
    # Generate token
    plain_token = generate_api_token()
    token_hash = hash_api_token(plain_token)

    # Calculate expiration
    expires_at = None
    if token_data.expires_in_days:
        expires_at = datetime.utcnow() + timedelta(days=token_data.expires_in_days)

    # Create token record
    api_token = APIToken(
        tenant_id=tenant_id,
        user_id=current_user.id,
        name=token_data.name,
        token_hash=token_hash,
        scopes=token_data.scopes,
        expires_at=expires_at,
        is_active=True,
    )

    session.add(api_token)
    await session.commit()
    await session.refresh(api_token)

    # Return response with plain token (only time it's shown)
    return APITokenResponse(
        id=api_token.id,
        name=api_token.name,
        token=plain_token,
        scopes=api_token.scopes,
        expires_at=api_token.expires_at,
        created_at=api_token.created_at,
    )


@router.get("/{token_id}", response_model=APITokenInfo)
async def get_api_token(
    token_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
) -> APITokenInfo:
    """Get API token by ID.

    Args:
        token_id: Token ID
        session: Database session
        current_user: Current authenticated user
        tenant_id: Tenant ID

    Returns:
        API token info (without token value)

    Raises:
        HTTPException: If token not found
    """
    result = await session.execute(
        select(APIToken).where(
            APIToken.id == token_id,
            APIToken.tenant_id == tenant_id,
            APIToken.user_id == current_user.id,
        )
    )
    token = result.scalar_one_or_none()

    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API token not found",
        )

    return APITokenInfo.model_validate(token)


@router.patch("/{token_id}/revoke", response_model=APITokenInfo)
async def revoke_api_token(
    token_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
) -> APITokenInfo:
    """Revoke API token.

    Args:
        token_id: Token ID
        session: Database session
        current_user: Current authenticated user
        tenant_id: Tenant ID

    Returns:
        Revoked API token info

    Raises:
        HTTPException: If token not found
    """
    result = await session.execute(
        select(APIToken).where(
            APIToken.id == token_id,
            APIToken.tenant_id == tenant_id,
            APIToken.user_id == current_user.id,
        )
    )
    token = result.scalar_one_or_none()

    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API token not found",
        )

    # Revoke token
    token.is_active = False
    session.add(token)
    await session.commit()
    await session.refresh(token)

    return APITokenInfo.model_validate(token)


@router.delete("/{token_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_api_token(
    token_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
    tenant_id: Annotated[UUID, Depends(get_tenant_id)],
) -> None:
    """Delete API token.

    Args:
        token_id: Token ID
        session: Database session
        current_user: Current authenticated user
        tenant_id: Tenant ID

    Raises:
        HTTPException: If token not found
    """
    result = await session.execute(
        select(APIToken).where(
            APIToken.id == token_id,
            APIToken.tenant_id == tenant_id,
            APIToken.user_id == current_user.id,
        )
    )
    token = result.scalar_one_or_none()

    if not token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="API token not found",
        )

    await session.delete(token)
    await session.commit()
