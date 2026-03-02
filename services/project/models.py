"""Project models."""
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import JSON, Column
from sqlmodel import Field, Relationship, SQLModel

from services.shared.models.base import BaseTenantModel


class ProjectStatus(str, Enum):
    """Project status enum."""

    ACTIVE = "active"
    ARCHIVED = "archived"
    ON_HOLD = "on_hold"


class ProjectSettings(SQLModel):
    """Project settings schema."""

    target_cloud: str = "AWS"  # AWS, Azure, GCP, OCI
    mps_br_level: str = "G"  # G, F, E, D, C, B, A
    code_standards: dict = Field(default_factory=dict)
    allowed_sources: list[str] = Field(default_factory=list)  # whitelist URLs
    default_policies: dict = Field(default_factory=dict)


class Project(BaseTenantModel, table=True):
    """Project model."""

    __tablename__ = "project"

    name: str = Field(max_length=255, nullable=False, index=True)
    description: Optional[str] = Field(default=None, max_length=2000)
    status: ProjectStatus = Field(default=ProjectStatus.ACTIVE, nullable=False)
    settings: dict = Field(default_factory=dict, sa_column=Column(JSON))
    created_by: UUID = Field(foreign_key="user.id", nullable=False)

    # Relationships
    members: list["ProjectMember"] = Relationship(back_populates="project")


class ProjectMemberRole(str, Enum):
    """Project member role enum."""

    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class ProjectMember(BaseTenantModel, table=True):
    """Project member association."""

    __tablename__ = "project_member"

    project_id: UUID = Field(
        foreign_key="project.id",
        index=True,
        nullable=False,
    )
    user_id: UUID = Field(
        foreign_key="user.id",
        index=True,
        nullable=False,
    )
    role_id: Optional[UUID] = Field(
        default=None,
        foreign_key="role.id",
        index=True,
        nullable=True,
    )
    member_role: ProjectMemberRole = Field(
        default=ProjectMemberRole.MEMBER,
        nullable=False,
    )
    joined_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

    # Relationships
    project: Project = Relationship(back_populates="members")
