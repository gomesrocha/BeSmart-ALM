"""Aider agent implementation."""

import asyncio
import logging
import os
import tempfile
import time
from pathlib import Path
from typing import Dict, Any, List
import git

from .base import CodeAgent
from ..core.models import Task, AgentResult

logger = logging.getLogger(__name__)


class AiderAgent(CodeAgent):
    """Agent that uses Aider CLI for code generation."""
    
    def __init__(self, name: str, config: Dict[str, Any]):
        """Initialize Aider agent.
        
        Args:
            name: Agent name (e.g., 'aider_ollama', 'aider_grok')
            config: Configuration including model, api_key, base_url
        """
        super().__init__(name, config)
        self.model = config.get('model', 'gpt-4')
        self.api_key = config.get('api_key')
        self.base_url = config.get('base_url')  # For Ollama
    
    async def execute_task(self, task: Task, context: Dict[str, Any]) -> AgentResult:
        """Execute task using Aider.
        
        Args:
            task: Task to execute
            context: Context including repository_url, branch, etc.
            
        Returns:
            Agent execution result
        """
        start_time = time.time()
        workspace = None
        
        try:
            # Create temporary workspace
            workspace = tempfile.mkdtemp(prefix=f"aider_{task.id}_")
            logger.info(
                f"Created workspace for task",
                extra={'task_id': task.id, 'workspace': workspace}
            )
            
            # Clone repository
            repo_url = context.get('repository_url')
            if not repo_url:
                raise ValueError("repository_url not provided in context")
            
            await self._clone_repository(repo_url, workspace)
            
            # Create branch for this work item
            branch_name = f"wi-{task.work_item_id}"
            await self._create_branch(workspace, branch_name)
            
            # Prepare Aider prompt
            prompt = self._build_prompt(task, context)
            
            # Execute Aider
            output = await self._run_aider(workspace, prompt)
            
            # Get modified files
            modified_files = await self._get_modified_files(workspace)
            
            execution_time = time.time() - start_time
            
            return AgentResult(
                success=True,
                agent_name=self.name,
                modified_files=modified_files,
                workspace=workspace,
                branch=branch_name,
                output=output,
                execution_time=execution_time
            )
        
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(
                f"Aider execution failed: {str(e)}",
                extra={'task_id': task.id, 'agent': self.name},
                exc_info=True
            )
            return AgentResult(
                success=False,
                agent_name=self.name,
                error=str(e),
                execution_time=execution_time
            )
    
    async def _clone_repository(self, repo_url: str, workspace: str) -> None:
        """Clone repository to workspace.
        
        Args:
            repo_url: Git repository URL
            workspace: Workspace directory
        """
        logger.info(f"Cloning repository: {repo_url}")
        await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: git.Repo.clone_from(repo_url, workspace)
        )
    
    async def _create_branch(self, workspace: str, branch_name: str) -> None:
        """Create and checkout new branch.
        
        Args:
            workspace: Workspace directory
            branch_name: Name of branch to create
        """
        repo = git.Repo(workspace)
        await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: repo.git.checkout('-b', branch_name)
        )
        logger.info(f"Created branch: {branch_name}")
    
    async def _run_aider(self, workspace: str, prompt: str) -> str:
        """Run Aider command.
        
        Args:
            workspace: Workspace directory
            prompt: Prompt for Aider
            
        Returns:
            Aider output
        """
        cmd = [
            'aider',
            '--model', self.model,
            '--message', prompt,
            '--yes',  # Auto-confirm changes
            '--no-git',  # We handle git ourselves
        ]
        
        # Setup environment variables
        env = os.environ.copy()
        
        if self.api_key:
            # Set appropriate API key based on model
            if 'grok' in self.model.lower():
                env['XAI_API_KEY'] = self.api_key
            elif 'gemini' in self.model.lower():
                env['GOOGLE_API_KEY'] = self.api_key
            elif 'claude' in self.model.lower():
                env['ANTHROPIC_API_KEY'] = self.api_key
            else:
                env['OPENAI_API_KEY'] = self.api_key
        
        if self.base_url:  # Ollama
            env['OLLAMA_BASE_URL'] = self.base_url
        
        logger.info(
            f"Running Aider with model {self.model}",
            extra={'model': self.model, 'workspace': workspace}
        )
        
        # Run Aider
        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=workspace,
            env=env,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            error_msg = stderr.decode() if stderr else "Unknown error"
            raise RuntimeError(f"Aider failed: {error_msg}")
        
        return stdout.decode()
    
    async def _get_modified_files(self, workspace: str) -> List[str]:
        """Get list of modified files.
        
        Args:
            workspace: Workspace directory
            
        Returns:
            List of modified file paths
        """
        repo = git.Repo(workspace)
        
        # Get both staged and unstaged changes
        modified = []
        
        # Staged changes
        for item in repo.index.diff("HEAD"):
            modified.append(item.a_path)
        
        # Unstaged changes
        for item in repo.index.diff(None):
            modified.append(item.a_path)
        
        # Untracked files
        modified.extend(repo.untracked_files)
        
        return list(set(modified))  # Remove duplicates
    
    def _build_prompt(self, task: Task, context: Dict[str, Any]) -> str:
        """Build comprehensive prompt for Aider.
        
        Args:
            task: Task to execute
            context: Additional context
            
        Returns:
            Formatted prompt
        """
        acceptance_criteria = "\n".join(
            f"- {criterion}" for criterion in task.acceptance_criteria
        ) if task.acceptance_criteria else "None specified"
        
        related_files = ", ".join(task.related_files) if task.related_files else "None specified"
        
        prompt = f"""Implement the following work item:

Title: {task.title}

Description:
{task.description}

Acceptance Criteria:
{acceptance_criteria}

Technical Specifications:
{task.specifications or 'None specified'}

Related Files:
{related_files}

Please implement this feature following best practices:
1. Write clean, maintainable code
2. Add appropriate error handling
3. Include docstrings and comments for complex logic
4. Follow the existing code style and patterns
5. Ensure the code is production-ready

Focus on implementing exactly what's described in the acceptance criteria.
Do not add unnecessary features or make unrelated changes.
"""
        return prompt
    
    async def health_check(self) -> bool:
        """Check if Aider is available.
        
        Returns:
            True if Aider is installed and working
        """
        try:
            process = await asyncio.create_subprocess_exec(
                'aider', '--version',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            await process.communicate()
            return process.returncode == 0
        except FileNotFoundError:
            logger.error("Aider not found. Please install: pip install aider-chat")
            return False
        except Exception as e:
            logger.error(f"Aider health check failed: {e}")
            return False
