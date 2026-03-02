"""Core data models for AI Orchestrator."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict, Any
from uuid import UUID, uuid4


class TaskStatus(Enum):
    """Task execution status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


class TaskComplexity(Enum):
    """Task complexity level."""
    SIMPLE = "simple"
    MEDIUM = "medium"
    COMPLEX = "complex"


@dataclass
class Task:
    """Represents a coding task to be executed by an agent."""
    
    id: str
    work_item_id: str
    project_id: str
    title: str
    description: str
    priority: int
    complexity: TaskComplexity
    status: TaskStatus = TaskStatus.PENDING
    assigned_agent: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    error_message: Optional[str] = None
    acceptance_criteria: List[str] = field(default_factory=list)
    specifications: Optional[str] = None
    related_files: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary."""
        return {
            'id': self.id,
            'work_item_id': self.work_item_id,
            'project_id': self.project_id,
            'title': self.title,
            'description': self.description,
            'priority': self.priority,
            'complexity': self.complexity.value,
            'status': self.status.value,
            'assigned_agent': self.assigned_agent,
            'created_at': self.created_at.isoformat(),
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'retry_count': self.retry_count,
            'max_retries': self.max_retries,
            'error_message': self.error_message,
            'acceptance_criteria': self.acceptance_criteria,
            'specifications': self.specifications,
            'related_files': self.related_files
        }


@dataclass
class AgentResult:
    """Result from agent execution."""
    
    success: bool
    agent_name: str
    modified_files: List[str] = field(default_factory=list)
    workspace: Optional[str] = None
    branch: Optional[str] = None
    output: str = ""
    error: Optional[str] = None
    execution_time: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            'success': self.success,
            'agent_name': self.agent_name,
            'modified_files': self.modified_files,
            'workspace': self.workspace,
            'branch': self.branch,
            'output': self.output,
            'error': self.error,
            'execution_time': self.execution_time
        }


@dataclass
class ValidationResult:
    """Result from validation pipeline."""
    
    passed: bool
    validator_name: str
    issues: List[Dict[str, Any]] = field(default_factory=list)
    error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            'passed': self.passed,
            'validator_name': self.validator_name,
            'issues': self.issues,
            'error': self.error
        }


@dataclass
class OrchestratorStats:
    """Statistics for orchestrator execution."""
    
    pending_tasks: int = 0
    in_progress_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    total_tasks: int = 0
    success_rate: float = 0.0
    average_execution_time: float = 0.0
    total_cost: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert stats to dictionary."""
        return {
            'pending_tasks': self.pending_tasks,
            'in_progress_tasks': self.in_progress_tasks,
            'completed_tasks': self.completed_tasks,
            'failed_tasks': self.failed_tasks,
            'total_tasks': self.total_tasks,
            'success_rate': self.success_rate,
            'average_execution_time': self.average_execution_time,
            'total_cost': self.total_cost
        }
