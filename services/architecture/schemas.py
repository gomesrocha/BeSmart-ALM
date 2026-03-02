"""Schemas for architecture generation."""
from typing import Optional, List
from pydantic import BaseModel


class GenerateArchitectureRequest(BaseModel):
    """Request to generate architecture from requirements."""
    project_id: str


class ArchitectureResponse(BaseModel):
    """Response with generated architecture."""
    project_id: str
    architecture: str  # Markdown content with Mermaid diagrams
    diagrams: List[str]  # List of Mermaid diagram codes
    version: int
    document_id: Optional[str] = None  # ID of the saved document


class UpdateArchitectureRequest(BaseModel):
    """Request to update architecture."""
    project_id: str
    content: str
    version: int
