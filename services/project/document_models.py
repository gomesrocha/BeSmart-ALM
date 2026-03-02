"""Project document models."""
from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from sqlmodel import Field, SQLModel

from services.shared.models.base import BaseTenantModel


class DocumentType(str, Enum):
    """Document type enum."""

    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    URL = "url"
    OTHER = "other"


class DocumentCategory(str, Enum):
    """Document category enum."""

    REQUIREMENTS = "REQUIREMENTS"  # Match DB enum
    SPECIFICATION = "SPECIFICATION"  # Match DB enum
    ARCHITECTURE = "architecture"  # Match DB enum (lowercase)
    DESIGN = "DESIGN"  # Match DB enum
    TECHNICAL = "TECHNICAL"  # Match DB enum
    BUSINESS = "BUSINESS"  # Match DB enum
    GENERATED = "generated"  # Match DB enum (lowercase)
    RAG_SOURCE = "rag_source"  # Match DB enum (lowercase)
    OTHER = "OTHER"  # Match DB enum


class ProjectDocument(BaseTenantModel, table=True):
    """Project document model."""

    __tablename__ = "project_document"

    project_id: UUID = Field(foreign_key="project.id", index=True, nullable=False)
    name: str = Field(max_length=500, nullable=False)
    type: DocumentType = Field(nullable=False)
    category: DocumentCategory = Field(default=DocumentCategory.OTHER, nullable=False)
    url: Optional[str] = Field(default=None, max_length=2000)
    file_path: Optional[str] = Field(default=None, max_length=1000)
    file_size: Optional[int] = Field(default=None)
    content_hash: Optional[str] = Field(default=None, max_length=64)
    description: Optional[str] = Field(default=None)
    uploaded_by: UUID = Field(foreign_key="user.id", nullable=False)
    uploaded_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    
    # RAG metadata
    is_indexed: bool = Field(default=False, nullable=False)
    chunk_count: int = Field(default=0, nullable=False)
    indexed_at: Optional[datetime] = Field(default=None)
    
    # Generated document metadata
    is_generated: bool = Field(default=False, nullable=False)
    generated_from: Optional[str] = Field(default=None, max_length=50)  # 'specification', 'architecture', etc.
    is_editable: bool = Field(default=True, nullable=False)
    version: int = Field(default=1, nullable=False)
    content: Optional[str] = Field(default=None)  # For generated/editable documents
