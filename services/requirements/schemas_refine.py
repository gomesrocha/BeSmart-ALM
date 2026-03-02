"""Schemas for iterative requirements refinement."""
from typing import List
from pydantic import BaseModel
from services.requirements.schemas import RequirementItem


class RefineRequirementsRequest(BaseModel):
    """Request to refine existing requirements."""
    project_id: str
    existing_requirements: List[RequirementItem]
    feedback: str
    operation: str = "refine"  # refine, add_more, improve


class RefineRequirementsResponse(BaseModel):
    """Response with refined requirements."""
    requirements: List[RequirementItem]
    project_id: str
    iteration: int
