"""Work item schemas."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from services.work_item.models import WorkItemStatus, WorkItemType


class WorkItemBase(BaseModel):
    """Base work item schema."""

    title: str = Field(min_length=1, max_length=500)
    description: Optional[str] = None
    type: WorkItemType


class WorkItemCreate(WorkItemBase):
    """Work item creation schema."""

    project_id: UUID
    priority: Optional[str] = "medium"
    assigned_to: Optional[UUID] = None


class WorkItemUpdate(BaseModel):
    """Work item update schema."""

    title: Optional[str] = Field(default=None, min_length=1, max_length=500)
    description: Optional[str] = None
    priority: Optional[str] = None
    assigned_to: Optional[UUID] = None


class WorkItemResponse(WorkItemBase):
    """Work item response schema."""

    id: UUID
    tenant_id: UUID
    project_id: UUID
    status: WorkItemStatus
    priority: str
    version: int
    created_by: UUID
    assigned_to: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True


class WorkItemStatusTransition(BaseModel):
    """Work item status transition schema."""

    new_status: WorkItemStatus


class WorkItemApprovalRequest(BaseModel):
    """Work item approval request schema."""

    decision: str = Field(pattern="^(APPROVED|REJECTED)$")
    comments: Optional[str] = None


class WorkItemLinkCreate(BaseModel):
    """Work item link creation schema."""

    target_id: UUID
    link_type: str = Field(min_length=1, max_length=50)


class WorkItemCommentCreate(BaseModel):
    """Work item comment creation schema."""

    content: str = Field(min_length=1)


class WorkItemCommentResponse(BaseModel):
    """Work item comment response schema."""

    id: UUID
    work_item_id: UUID
    content: str
    created_by: UUID
    created_at: datetime

    class Config:
        """Pydantic config."""

        from_attributes = True
