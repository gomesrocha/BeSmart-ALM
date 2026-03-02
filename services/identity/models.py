"""Identity and Tenant models."""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import JSON, Column
from sqlmodel import Field, Relationship, SQLModel

from services.shared.models.base import TimestampMixin


class Tenant(TimestampMixin, SQLModel, table=True):
    """Tenant model for multi-tenancy support."""

    __tablename__ = "tenant"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    name: str = Field(max_length=255, nullable=False)
    slug: str = Field(max_length=100, unique=True, index=True, nullable=False)
    settings: dict = Field(default_factory=dict, sa_column=Column(JSON))
    is_active: bool = Field(default=True, nullable=False)

    # Relationships
    users: list["User"] = Relationship(back_populates="tenant")
    roles: list["Role"] = Relationship(back_populates="tenant")


class User(TimestampMixin, SQLModel, table=True):
    """User model."""

    __tablename__ = "user"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    tenant_id: UUID = Field(
        foreign_key="tenant.id",
        index=True,
        nullable=False,
    )
    email: str = Field(max_length=255, unique=True, index=True, nullable=False)
    hashed_password: str = Field(max_length=255, nullable=False)
    full_name: str = Field(max_length=255, nullable=False)
    is_active: bool = Field(default=True, nullable=False)
    is_superuser: bool = Field(default=False, nullable=False)
    last_login: Optional[datetime] = Field(default=None, nullable=True)

    # Relationships
    tenant: Tenant = Relationship(back_populates="users")
    user_roles: list["UserRole"] = Relationship(back_populates="user")


class Role(TimestampMixin, SQLModel, table=True):
    """Role model for RBAC."""

    __tablename__ = "role"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    tenant_id: UUID = Field(
        foreign_key="tenant.id",
        index=True,
        nullable=False,
    )
    name: str = Field(max_length=100, nullable=False)
    description: Optional[str] = Field(default=None, max_length=500)
    permissions: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    is_system: bool = Field(
        default=False,
        nullable=False,
        description="System roles cannot be deleted",
    )

    # Relationships
    tenant: Tenant = Relationship(back_populates="roles")
    user_roles: list["UserRole"] = Relationship(back_populates="role")


class UserRole(TimestampMixin, SQLModel, table=True):
    """User-Role association with optional project scope."""

    __tablename__ = "user_role"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    user_id: UUID = Field(
        foreign_key="user.id",
        index=True,
        nullable=False,
    )
    role_id: UUID = Field(
        foreign_key="role.id",
        index=True,
        nullable=False,
    )
    project_id: Optional[UUID] = Field(
        default=None,
        index=True,
        nullable=True,
        description="If set, role applies only to this project",
    )

    # Relationships
    user: User = Relationship(back_populates="user_roles")
    role: Role = Relationship(back_populates="user_roles")


class APIToken(TimestampMixin, SQLModel, table=True):
    """API Token for integrations."""

    __tablename__ = "api_token"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    tenant_id: UUID = Field(
        foreign_key="tenant.id",
        index=True,
        nullable=False,
    )
    user_id: UUID = Field(
        foreign_key="user.id",
        index=True,
        nullable=False,
    )
    name: str = Field(max_length=255, nullable=False)
    token_hash: str = Field(max_length=255, unique=True, index=True, nullable=False)
    scopes: list[str] = Field(default_factory=list, sa_column=Column(JSON))
    expires_at: Optional[datetime] = Field(default=None, nullable=True)
    last_used_at: Optional[datetime] = Field(default=None, nullable=True)
    is_active: bool = Field(default=True, nullable=False)


class AuditLog(TimestampMixin, SQLModel, table=True):
    """Audit log for tracking user actions."""

    __tablename__ = "audit_log"

    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )
    tenant_id: UUID = Field(
        foreign_key="tenant.id",
        index=True,
        nullable=False,
    )
    user_id: Optional[UUID] = Field(
        foreign_key="user.id",
        index=True,
        nullable=True,
    )
    action: str = Field(max_length=100, index=True, nullable=False)
    resource_type: str = Field(max_length=100, index=True, nullable=False)
    resource_id: Optional[UUID] = Field(default=None, index=True, nullable=True)
    details: dict = Field(default_factory=dict, sa_column=Column(JSON))
    ip_address: Optional[str] = Field(default=None, max_length=45, nullable=True)
    user_agent: Optional[str] = Field(default=None, max_length=500, nullable=True)
