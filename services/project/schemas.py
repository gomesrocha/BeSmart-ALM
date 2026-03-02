"""Project schemas."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from services.project.models import ProjectMemberRole, ProjectSettings, ProjectStatus


# Project schemas
class ProjectBase(BaseModel):
    """Base project schema."""

    name: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=2000)


class ProjectCreate(ProjectBase):
    """Project creation schema."""

    settings: ProjectSettings = Field(default_factory=ProjectSettings)


class ProjectUpdate(BaseModel):
    """Project update schema."""

    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[ProjectStatus] = None
    settings: Optional[dict] = None


class ProjectResponse(ProjectBase):
    """Project response schema."""

    id: UUID
    tenant_id: UUID
    status: ProjectStatus
    settings: dict
    created_by: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


# Project member schemas
class ProjectMemberAdd(BaseModel):
    """Add member to project schema."""

    user_id: UUID
    role_id: Optional[UUID] = None
    member_role: ProjectMemberRole = ProjectMemberRole.MEMBER


class ProjectMemberUpdate(BaseModel):
    """Update project member schema."""

    role_id: Optional[UUID] = None
    member_role: Optional[ProjectMemberRole] = None


class ProjectMemberResponse(BaseModel):
    """Project member response schema."""

    id: UUID
    project_id: UUID
    user_id: UUID
    role_id: Optional[UUID]
    member_role: ProjectMemberRole
    joined_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True



# Project settings schemas
class ProjectSettingsUpdate(BaseModel):
    """Project settings update schema."""

    target_cloud: Optional[str] = None
    mps_br_level: Optional[str] = None
    code_standards: Optional[dict] = None
    allowed_sources: Optional[list[str]] = None
    default_policies: Optional[dict] = None


class WhitelistSourceAdd(BaseModel):
    """Add URL to whitelist schema."""

    url: str = Field(min_length=1, max_length=500)


class WhitelistSourcesResponse(BaseModel):
    """Whitelist sources response schema."""

    allowed_sources: list[str]
