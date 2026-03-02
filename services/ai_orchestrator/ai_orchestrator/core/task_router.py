"""Task router for agent selection based on complexity."""

import logging
from typing import Optional

from .models import Task, TaskComplexity

logger = logging.getLogger(__name__)


class TaskRouter:
    """Routes tasks to appropriate agents based on complexity and availability."""
    
    def __init__(self, agent_pool: 'AgentPool'):
        """Initialize task router.
        
        Args:
            agent_pool: Pool of available agents
        """
        self.agent_pool = agent_pool
        self.complexity_keywords = {
            'complex': [
                'refactor', 'architecture', 'migration', 'multiple files',
                'redesign', 'restructure', 'major change', 'breaking change'
            ],
            'medium': [
                'implement', 'add feature', 'integrate', 'extend',
                'enhance', 'improve', 'modify', 'update'
            ],
            'simple': [
                'fix', 'bug', 'typo', 'update text', 'change color',
                'adjust', 'tweak', 'small change'
            ]
        }
    
    def analyze_complexity(self, work_item: dict) -> TaskComplexity:
        """Analyze work item complexity.
        
        Args:
            work_item: Work item data from Bsmart-ALM
            
        Returns:
            Complexity level (SIMPLE, MEDIUM, or COMPLEX)
        """
        description = work_item.get('description', '').lower()
        specifications = work_item.get('specifications', '').lower()
        title = work_item.get('title', '').lower()
        
        full_text = f"{title} {description} {specifications}"
        
        # Check for complexity keywords
        complex_score = sum(
            1 for keyword in self.complexity_keywords['complex']
            if keyword in full_text
        )
        medium_score = sum(
            1 for keyword in self.complexity_keywords['medium']
            if keyword in full_text
        )
        simple_score = sum(
            1 for keyword in self.complexity_keywords['simple']
            if keyword in full_text
        )
        
        # Determine complexity based on scores and text length
        text_length = len(full_text)
        
        if complex_score > 0 or text_length > 2000:
            complexity = TaskComplexity.COMPLEX
        elif medium_score > 0 or text_length > 500:
            complexity = TaskComplexity.MEDIUM
        elif simple_score > 0 or text_length < 200:
            complexity = TaskComplexity.SIMPLE
        else:
            # Default to medium for ambiguous cases
            complexity = TaskComplexity.MEDIUM
        
        logger.info(
            f"Analyzed complexity: {complexity.value}",
            extra={
                'work_item_id': work_item.get('id'),
                'text_length': text_length,
                'complex_score': complex_score,
                'medium_score': medium_score,
                'simple_score': simple_score
            }
        )
        
        return complexity
    
    def select_agent(self, task: Task) -> Optional[str]:
        """Select best agent for task based on complexity and availability.
        
        Args:
            task: Task to assign
            
        Returns:
            Agent name or None if no agent available
        """
        # Priority order based on complexity
        if task.complexity == TaskComplexity.SIMPLE:
            # Prefer local/free agents for simple tasks
            agent_priority = ['aider_ollama', 'aider_gemini', 'aider_grok']
        elif task.complexity == TaskComplexity.MEDIUM:
            # Use API-based agents for medium complexity
            agent_priority = ['aider_grok', 'aider_gemini', 'aider_ollama']
        else:  # COMPLEX
            # Use OpenHands or powerful agents for complex tasks
            agent_priority = ['openhands', 'aider_grok', 'aider_gemini']
        
        # Try agents in priority order
        for agent_name in agent_priority:
            if self.agent_pool.is_available(agent_name):
                logger.info(
                    f"Selected agent {agent_name} for task",
                    extra={
                        'task_id': task.id,
                        'complexity': task.complexity.value,
                        'agent': agent_name
                    }
                )
                return agent_name
        
        # Fallback to any available agent
        fallback = self.agent_pool.get_any_available()
        if fallback:
            logger.warning(
                f"Using fallback agent {fallback}",
                extra={
                    'task_id': task.id,
                    'complexity': task.complexity.value
                }
            )
        else:
            logger.error(
                "No agents available",
                extra={'task_id': task.id}
            )
        
        return fallback
