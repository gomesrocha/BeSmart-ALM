"""Project document schemas."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ProjectDocumentCreate(BaseModel):
    """Project document creation schema."""

    name: str = Field(min_length=1, max_length=500)
    type: str
    category: str = "other"
    url: Optional[str] = None
    description: Optional[str] = None


class ProjectDocumentResponse(BaseModel):
    """Project document response schema."""

    id: UUID
    project_id: UUID
    name: str
    type: str
    category: str
    url: Optional[str]
    file_path: Optional[str]
    file_size: Optional[int]
    description: Optional[str]
    uploaded_by: UUID
    uploaded_at: datetime
    is_indexed: bool
    chunk_count: int
    indexed_at: Optional[datetime]
    is_generated: bool = False
    generated_from: Optional[str] = None
    is_editable: bool = True
    version: int = 1
    content: Optional[str] = None

    class Config:
        """Pydantic config."""

        from_attributes = True


class ProjectDocumentUpdate(BaseModel):
    """Project document update schema."""

    name: Optional[str] = Field(default=None, min_length=1, max_length=500)
    category: Optional[str] = None
    description: Optional[str] = None
