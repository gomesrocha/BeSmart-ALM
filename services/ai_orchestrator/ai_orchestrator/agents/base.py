"""Base agent interface for coding agents."""

from abc import ABC, abstractmethod
from typing import Dict, Any
import asyncio
import logging

from ..core.models import Task, AgentResult

logger = logging.getLogger(__name__)


class CodeAgent(ABC):
    """Abstract base class for all coding agents."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        """Initialize code agent.
        
        Args:
            name: Agent name
            config: Agent configuration
        """
        self.name = name
        self.config = config
        self.is_busy = False
        self.current_task: Task | None = None
        self._lock = asyncio.Lock()
    
    @abstractmethod
    async def execute_task(self, task: Task, context: Dict[str, Any]) -> AgentResult:
        """Execute coding task and return results.
        
        Args:
            task: Task to execute
            context: Additional context (repository_url, etc.)
            
        Returns:
            Result of agent execution
        """
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if agent is healthy and ready.
        
        Returns:
            True if agent is healthy, False otherwise
        """
        pass
    
    def is_available(self) -> bool:
        """Check if agent is available for work.
        
        Returns:
            True if agent is not busy
        """
        return not self.is_busy
    
    async def acquire(self, task: Task) -> bool:
        """Acquire agent for task execution.
        
        Args:
            task: Task to acquire agent for
            
        Returns:
            True if agent was acquired, False if already busy
        """
        async with self._lock:
            if self.is_busy:
                return False
            self.is_busy = True
            self.current_task = task
            logger.info(
                f"Agent {self.name} acquired",
                extra={'agent': self.name, 'task_id': task.id}
            )
            return True
    
    async def release(self) -> None:
        """Release agent after task completion."""
        async with self._lock:
            task_id = self.current_task.id if self.current_task else None
            self.is_busy = False
            self.current_task = None
            logger.info(
                f"Agent {self.name} released",
                extra={'agent': self.name, 'task_id': task_id}
            )
