"""Models for specification and architecture."""
from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4
from sqlmodel import Field, SQLModel


class ProjectSpecification(SQLModel, table=True):
    """Project specification document."""
    __tablename__ = "project_specifications"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    tenant_id: UUID = Field(foreign_key="tenant.id", index=True)
    project_id: UUID = Field(foreign_key="project.id", index=True)
    content: str  # Markdown content
    version: int = Field(default=1)
    created_by: UUID = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class ProjectArchitecture(SQLModel, table=True):
    """Project architecture document."""
    __tablename__ = "project_architectures"
    
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    tenant_id: UUID = Field(foreign_key="tenant.id", index=True)
    project_id: UUID = Field(foreign_key="project.id", index=True)
    content: str  # Markdown content with Mermaid diagrams
    version: int = Field(default=1)
    created_by: UUID = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
