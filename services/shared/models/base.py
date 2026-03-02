"""Base models with tenant isolation and timestamp mixins."""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import text
from sqlmodel import Field, SQLModel


class TimestampMixin(SQLModel):
    """Mixin for created_at and updated_at timestamps."""

    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"server_default": text("now()")},
    )
    updated_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"server_default": text("now()"), "onupdate": datetime.utcnow},
    )


class BaseTenantModel(TimestampMixin, SQLModel):
    """Base model with tenant isolation and timestamps.
    
    All models that need tenant isolation should inherit from this class.
    The tenant_id field ensures data isolation between different tenants.
    """

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

    class Config:
        """SQLModel configuration."""
        arbitrary_types_allowed = True
