"""Pydantic schemas for Identity service."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


# Auth schemas
class LoginRequest(BaseModel):
    """Login request schema."""

    email: EmailStr
    password: str = Field(min_length=8)


class TokenResponse(BaseModel):
    """Token response schema."""

    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds


class RefreshTokenRequest(BaseModel):
    """Refresh token request schema."""

    refresh_token: str


class TokenPayload(BaseModel):
    """JWT token payload schema."""

    sub: UUID  # user_id
    tenant_id: UUID
    email: str
    exp: datetime
    type: str  # access or refresh


# User schemas
class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    full_name: str


class UserCreate(UserBase):
    """User creation schema."""

    password: str = Field(min_length=8)
    tenant_id: UUID


class UserUpdate(BaseModel):
    """User update schema."""

    full_name: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """User response schema."""

    id: UUID
    tenant_id: UUID
    is_active: bool
    is_superuser: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        """Pydantic config."""
        from_attributes = True


# Tenant schemas
class TenantBase(BaseModel):
    """Base tenant schema."""

    name: str
    slug: str


class TenantCreate(TenantBase):
    """Tenant creation schema."""

    settings: dict = Field(default_factory=dict)


class TenantUpdate(BaseModel):
    """Tenant update schema."""

    name: Optional[str] = None
    settings: Optional[dict] = None
    is_active: Optional[bool] = None


class TenantResponse(TenantBase):
    """Tenant response schema."""

    id: UUID
    settings: dict
    is_active: bool
    created_at: datetime

    class Config:
        """Pydantic config."""
        from_attributes = True


# Role schemas
class RoleBase(BaseModel):
    """Base role schema."""

    name: str
    description: Optional[str] = None
    permissions: list[str] = Field(default_factory=list)


class RoleCreate(RoleBase):
    """Role creation schema."""

    tenant_id: UUID


class RoleUpdate(BaseModel):
    """Role update schema."""

    name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[list[str]] = None


class RoleResponse(RoleBase):
    """Role response schema."""

    id: UUID
    tenant_id: UUID
    is_system: bool
    created_at: datetime

    class Config:
        """Pydantic config."""
        from_attributes = True



# API Token schemas
class APITokenCreate(BaseModel):
    """API token creation schema."""

    name: str
    scopes: list[str] = Field(default_factory=list)
    expires_in_days: int | None = Field(default=None, ge=1, le=365)


class APITokenResponse(BaseModel):
    """API token response schema."""

    id: UUID
    name: str
    token: str  # Only returned on creation
    scopes: list[str]
    expires_at: datetime | None
    created_at: datetime

    class Config:
        """Pydantic config."""
        from_attributes = True


class APITokenInfo(BaseModel):
    """API token info schema (without token value)."""

    id: UUID
    name: str
    scopes: list[str]
    expires_at: datetime | None
    last_used_at: datetime | None
    is_active: bool
    created_at: datetime

    class Config:
        """Pydantic config."""
        from_attributes = True
