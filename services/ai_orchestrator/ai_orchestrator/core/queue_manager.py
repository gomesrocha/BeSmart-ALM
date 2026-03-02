"""Queue manager for task orchestration."""

import asyncio
import logging
from typing import List, Optional
from datetime import datetime

from .models import Task, TaskStatus, OrchestratorStats

logger = logging.getLogger(__name__)


class QueueManager:
    """Manages task queue with priority ordering and concurrency control."""
    
    def __init__(self, max_concurrent_tasks: int = 3):
        """Initialize queue manager.
        
        Args:
            max_concurrent_tasks: Maximum number of concurrent tasks
        """
        self.pending_queue: List[Task] = []
        self.in_progress: List[Task] = []
        self.completed: List[Task] = []
        self.failed: List[Task] = []
        self.max_concurrent = max_concurrent_tasks
        self.semaphore = asyncio.Semaphore(max_concurrent_tasks)
        self._lock = asyncio.Lock()
    
    async def add_task(self, task: Task) -> None:
        """Add task to queue with priority ordering.
        
        Args:
            task: Task to add to queue
        """
        async with self._lock:
            # Insert task in priority order (higher priority first)
            inserted = False
            for i, existing_task in enumerate(self.pending_queue):
                if task.priority > existing_task.priority:
                    self.pending_queue.insert(i, task)
                    inserted = True
                    break
            
            if not inserted:
                self.pending_queue.append(task)
            
            logger.info(
                f"Task {task.id} added to queue",
                extra={
                    'task_id': task.id,
                    'work_item_id': task.work_item_id,
                    'priority': task.priority,
                    'queue_size': len(self.pending_queue)
                }
            )
    
    async def get_next_task(self) -> Optional[Task]:
        """Get next task from queue if capacity allows.
        
        Returns:
            Next task or None if queue is empty or at capacity
        """
        async with self._lock:
            if not self.pending_queue or len(self.in_progress) >= self.max_concurrent:
                return None
            
            task = self.pending_queue.pop(0)
            task.status = TaskStatus.IN_PROGRESS
            task.started_at = datetime.now()
            self.in_progress.append(task)
            
            logger.info(
                f"Task {task.id} started",
                extra={
                    'task_id': task.id,
                    'work_item_id': task.work_item_id,
                    'agent': task.assigned_agent,
                    'in_progress_count': len(self.in_progress)
                }
            )
            
            return task
    
    async def complete_task(
        self,
        task_id: str,
        success: bool,
        error: Optional[str] = None
    ) -> None:
        """Mark task as completed or failed.
        
        Args:
            task_id: ID of task to complete
            success: Whether task completed successfully
            error: Error message if task failed
        """
        async with self._lock:
            task = self._find_task_in_progress(task_id)
            if not task:
                logger.warning(f"Task {task_id} not found in progress")
                return
            
            self.in_progress.remove(task)
            task.completed_at = datetime.now()
            
            if success:
                task.status = TaskStatus.COMPLETED
                self.completed.append(task)
                logger.info(
                    f"Task {task_id} completed successfully",
                    extra={
                        'task_id': task_id,
                        'work_item_id': task.work_item_id,
                        'execution_time': (task.completed_at - task.started_at).total_seconds()
                    }
                )
            else:
                task.retry_count += 1
                task.error_message = error
                
                if task.retry_count < task.max_retries:
                    task.status = TaskStatus.PENDING
                    await self.add_task(task)
                    logger.warning(
                        f"Task {task_id} failed, retrying",
                        extra={
                            'task_id': task_id,
                            'retry_count': task.retry_count,
                            'max_retries': task.max_retries,
                            'error': error
                        }
                    )
                else:
                    task.status = TaskStatus.FAILED
                    self.failed.append(task)
                    logger.error(
                        f"Task {task_id} failed permanently",
                        extra={
                            'task_id': task_id,
                            'work_item_id': task.work_item_id,
                            'error': error
                        }
                    )
    
    def _find_task_in_progress(self, task_id: str) -> Optional[Task]:
        """Find task in progress list.
        
        Args:
            task_id: ID of task to find
            
        Returns:
            Task if found, None otherwise
        """
        for task in self.in_progress:
            if task.id == task_id:
                return task
        return None
    
    def get_stats(self) -> OrchestratorStats:
        """Get queue statistics.
        
        Returns:
            Statistics about queue state
        """
        total = len(self.pending_queue) + len(self.in_progress) + len(self.completed) + len(self.failed)
        success_rate = (len(self.completed) / total * 100) if total > 0 else 0.0
        
        # Calculate average execution time
        execution_times = [
            (task.completed_at - task.started_at).total_seconds()
            for task in self.completed
            if task.started_at and task.completed_at
        ]
        avg_time = sum(execution_times) / len(execution_times) if execution_times else 0.0
        
        return OrchestratorStats(
            pending_tasks=len(self.pending_queue),
            in_progress_tasks=len(self.in_progress),
            completed_tasks=len(self.completed),
            failed_tasks=len(self.failed),
            total_tasks=total,
            success_rate=success_rate,
            average_execution_time=avg_time
        )
    
    async def clear_completed(self) -> int:
        """Clear completed tasks from memory.
        
        Returns:
            Number of tasks cleared
        """
        async with self._lock:
            count = len(self.completed)
            self.completed.clear()
            logger.info(f"Cleared {count} completed tasks")
            return count
