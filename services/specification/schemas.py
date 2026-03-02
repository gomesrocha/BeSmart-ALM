"""Schemas for specification generation."""
from typing import Optional
from pydantic import BaseModel


class GenerateSpecificationRequest(BaseModel):
    """Request to generate specification from requirements."""
    project_id: str


class SpecificationResponse(BaseModel):
    """Response with generated specification."""
    project_id: str
    specification: str  # Markdown content
    version: int
    document_id: Optional[str] = None  # ID of the saved document


class UpdateSpecificationRequest(BaseModel):
    """Request to update specification."""
    project_id: str
    content: str
    version: int
