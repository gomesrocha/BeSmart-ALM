"""Work Item models."""
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import JSON, Column
from sqlmodel import Field, Relationship, SQLModel

from services.shared.models.base import BaseTenantModel


class WorkItemType(str, Enum):
    """Work item type enum."""

    REQUIREMENT = "requirement"
    USER_STORY = "user_story"
    ACCEPTANCE_CRITERIA = "acceptance_criteria"
    TASK = "task"
    DEFECT = "defect"
    NFR = "nfr"


class WorkItemStatus(str, Enum):
    """Work item status enum."""

    DRAFT = "draft"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class WorkItemPriority(str, Enum):
    """Work item priority enum."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class WorkItem(BaseTenantModel, table=True):
    """Work item model."""

    __tablename__ = "work_item"

    project_id: UUID = Field(foreign_key="project.id", index=True, nullable=False)
    type: WorkItemType = Field(nullable=False)
    title: str = Field(max_length=500, nullable=False, index=True)
    description: Optional[str] = Field(default=None)
    status: WorkItemStatus = Field(default=WorkItemStatus.DRAFT, nullable=False)
    priority: WorkItemPriority = Field(default=WorkItemPriority.MEDIUM, nullable=False)
    version: int = Field(default=1, nullable=False)
    created_by: UUID = Field(foreign_key="user.id", nullable=False)
    assigned_to: Optional[UUID] = Field(default=None, foreign_key="user.id")

    # Relationships
    links: list["WorkItemLink"] = Relationship(
        back_populates="source",
        sa_relationship_kwargs={"foreign_keys": "WorkItemLink.source_id"},
    )
    history: list["WorkItemHistory"] = Relationship(back_populates="work_item")
    approvals: list["WorkItemApproval"] = Relationship(back_populates="work_item")


class WorkItemLink(BaseTenantModel, table=True):
    """Work item link model."""

    __tablename__ = "work_item_link"

    source_id: UUID = Field(foreign_key="work_item.id", index=True, nullable=False)
    target_id: UUID = Field(foreign_key="work_item.id", index=True, nullable=False)
    link_type: str = Field(
        max_length=50, nullable=False
    )  # implements, tests, blocks, relates

    # Relationships
    source: WorkItem = Relationship(
        back_populates="links",
        sa_relationship_kwargs={"foreign_keys": "[WorkItemLink.source_id]"},
    )


class WorkItemHistory(BaseTenantModel, table=True):
    """Work item history model."""

    __tablename__ = "work_item_history"

    work_item_id: UUID = Field(foreign_key="work_item.id", index=True, nullable=False)
    version: int = Field(nullable=False)
    changed_by: UUID = Field(foreign_key="user.id", nullable=False)
    changed_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    changes: dict = Field(default_factory=dict, sa_column=Column(JSON))
    snapshot: dict = Field(default_factory=dict, sa_column=Column(JSON))

    # Relationships
    work_item: WorkItem = Relationship(back_populates="history")


class WorkItemApproval(BaseTenantModel, table=True):
    """Work item approval model."""

    __tablename__ = "work_item_approval"

    work_item_id: UUID = Field(foreign_key="work_item.id", index=True, nullable=False)
    version: int = Field(nullable=False)
    approved_by: UUID = Field(foreign_key="user.id", nullable=False)
    approved_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    decision: str = Field(max_length=20, nullable=False)  # APPROVED, REJECTED
    comments: Optional[str] = Field(default=None)

    # Relationships
    work_item: WorkItem = Relationship(back_populates="approvals")


class WorkItemComment(BaseTenantModel, table=True):
    """Work item comment model."""

    __tablename__ = "work_item_comment"

    work_item_id: UUID = Field(foreign_key="work_item.id", index=True, nullable=False)
    content: str = Field(nullable=False)
    created_by: UUID = Field(foreign_key="user.id", nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)

