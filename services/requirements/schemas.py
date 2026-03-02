"""Schemas for requirements generation."""
from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel


class GenerateRequirementsRequest(BaseModel):
    """Request to generate requirements from project description."""
    project_id: str
    description: str


class UserStory(BaseModel):
    """Structured user story."""
    as_a: str
    i_want: str
    so_that: str


class GherkinScenario(BaseModel):
    """Gherkin scenario with Given-When-Then format."""
    scenario: str
    given: str
    when: str
    then: str
    and_: List[str] = []
    
    class Config:
        fields = {'and_': 'and'}


class RequirementItem(BaseModel):
    """A single generated requirement with Gherkin format support."""
    title: str
    user_story: Union[str, UserStory]  # Support both old and new format
    acceptance_criteria: Union[List[str], List[GherkinScenario]]  # Support both formats
    business_context: Optional[str] = None
    type: str = "requirement"
    priority: str = "medium"


class GenerateRequirementsResponse(BaseModel):
    """Response with generated requirements."""
    requirements: List[RequirementItem]
    project_id: str


class ApproveRequirementsRequest(BaseModel):
    """Request to approve and create work items from requirements."""
    project_id: str
    requirements: List[RequirementItem]
