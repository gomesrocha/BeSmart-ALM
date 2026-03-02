# Design Document - AI Coding Orchestrator

## Overview

Orquestrador autônomo que consome work items do Bsmart-ALM, distribui para agentes de coding AI (Aider com múltiplos modelos, OpenHands), executa validações de qualidade (Continue, AI Security Checks, testes automatizados), e entrega código via Git com pull requests automáticos.

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI ORCHESTRATOR                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐ │
│  │  ORCHESTRATOR   │    │   AGENT POOL    │    │  VALIDATOR  │ │
│  │    ENGINE       │    │                 │    │   PIPELINE  │ │
│  │                 │    │ ┌─────────────┐ │    │             │ │
│  │ - Queue Manager │◄──►│ │    Aider    │ │◄──►│ - Continue  │ │
│  │ - Task Router   │    │ │  + Ollama   │ │    │ - Security  │ │
│  │ - Status Mgr    │    │ │  + Grok     │ │    │ - Tests     │ │
│  │ - Scheduler     │    │ │  + Gemini   │ │    │ - Linting   │ │
│  │                 │    │ └─────────────┘ │    │             │ │
│  └─────────────────┘    │ ┌─────────────┐ │    └─────────────┘ │
│                         │ │ OpenHands   │ │                    │
│                         │ │  + Docker   │ │                    │
│                         │ │  + Multi    │ │                    │
│                         │ │    Models   │ │                    │
│                         │ └─────────────┘ │                    │
│                         └─────────────────┘                    │
├─────────────────────────────────────────────────────────────────┤
│                    EXTERNAL INTEGRATIONS                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐ │
│  │ Bsmart-ALM  │  │    Git      │  │   Models    │  │ Monitor │ │
│  │    API      │  │ Repository  │  │             │  │ & Logs  │ │
│  │             │  │             │  │ - Ollama    │  │         │ │
│  │ - WorkItems │  │ - Clone     │  │ - Grok API  │  │ - Logs  │ │
│  │ - Projects  │  │ - Branch    │  │ - Gemini    │  │ - Metrics│ │
│  │ - Status    │  │ - Commit    │  │ - Claude    │  │ - Alerts│ │
│  │ - Comments  │  │ - Push      │  │ - GPT-4     │  │         │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Orchestrator Engine

#### Queue Manager
Gerencia fila de tarefas com priorização e retry logic.

```python
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional
import asyncio
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"

@dataclass
class Task:
    id: str
    work_item_id: str
    project_id: str
    title: str
    description: str
    priority: int
    complexity: str  # 'simple', 'medium', 'complex'
    status: TaskStatus
    assigned_agent: Optional[str] = None
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    error_message: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()

class QueueManager:
    def __init__(self, max_concurrent_tasks: int = 3):
        self.pending_queue: List[Task] = []
        self.in_progress: List[Task] = []
        self.completed: List[Task] = []
        self.failed: List[Task] = []
        self.max_concurrent = max_concurrent_tasks
        self.semaphore = asyncio.Semaphore(max_concurrent_tasks)
    
    async def add_task(self, task: Task) -> None:
        """Add task to queue with priority ordering"""
        inserted = False
        for i, existing_task in enumerate(self.pending_queue):
            if task.priority > existing_task.priority:
                self.pending_queue.insert(i, task)
                inserted = True
                break
        
        if not inserted:
            self.pending_queue.append(task)
        
        logger.info(f"Task {task.id} added to queue (priority: {task.priority})")
    
    async def get_next_task(self) -> Optional[Task]:
        """Get next task from queue if capacity allows"""
        if not self.pending_queue or len(self.in_progress) >= self.max_concurrent:
            return None
        
        task = self.pending_queue.pop(0)
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.now()
        self.in_progress.append(task)
        
        return task
    
    async def complete_task(self, task_id: str, success: bool, error: str = None) -> None:
        """Mark task as completed or failed"""
        task = self.find_task_in_progress(task_id)
        if not task:
            return
        
        self.in_progress.remove(task)
        task.completed_at = datetime.now()
        
        if success:
            task.status = TaskStatus.COMPLETED
            self.completed.append(task)
            logger.info(f"Task {task_id} completed successfully")
        else:
            task.retry_count += 1
            task.error_message = error
            
            if task.retry_count < task.max_retries:
                task.status = TaskStatus.PENDING
                await self.add_task(task)
                logger.warning(f"Task {task_id} failed, retrying ({task.retry_count}/{task.max_retries})")
            else:
                task.status = TaskStatus.FAILED
                self.failed.append(task)
                logger.error(f"Task {task_id} failed permanently: {error}")
    
    def find_task_in_progress(self, task_id: str) -> Optional[Task]:
        """Find task in progress list"""
        for task in self.in_progress:
            if task.id == task_id:
                return task
        return None
    
    def get_stats(self) -> dict:
        """Get queue statistics"""
        return {
            'pending': len(self.pending_queue),
            'in_progress': len(self.in_progress),
            'completed': len(self.completed),
            'failed': len(self.failed),
            'total': len(self.pending_queue) + len(self.in_progress) + len(self.completed) + len(self.failed)
        }
```

#### Task Router
Seleciona o melhor agente para cada tarefa baseado em complexidade.

```python
class TaskRouter:
    def __init__(self, agent_pool: 'AgentPool'):
        self.agent_pool = agent_pool
        self.complexity_thresholds = {
            'simple': {'max_files': 3, 'max_lines': 200},
            'medium': {'max_files': 10, 'max_lines': 1000},
            'complex': {'max_files': float('inf'), 'max_lines': float('inf')}
        }
    
    def analyze_complexity(self, work_item: dict) -> str:
        """Analyze work item complexity"""
        description = work_item.get('description', '')
        specifications = work_item.get('specifications', '')
        
        # Simple heuristics for complexity
        total_text = len(description) + len(specifications or '')
        
        # Check for keywords indicating complexity
        complex_keywords = ['refactor', 'architecture', 'migration', 'multiple files']
        medium_keywords = ['implement', 'add feature', 'integrate']
        
        description_lower = description.lower()
        
        if any(keyword in description_lower for keyword in complex_keywords):
            return 'complex'
        elif any(keyword in description_lower for keyword in medium_keywords):
            return 'medium'
        elif total_text < 500:
            return 'simple'
        elif total_text < 2000:
            return 'medium'
        else:
            return 'complex'
    
    def select_agent(self, task: Task) -> str:
        """Select best agent for task based on complexity and availability"""
        if task.complexity == 'simple':
            # Prefer local/free agents for simple tasks
            if self.agent_pool.is_available('aider_ollama'):
                return 'aider_ollama'
            elif self.agent_pool.is_available('aider_gemini'):
                return 'aider_gemini'
        
        elif task.complexity == 'medium':
            # Use API-based agents for medium complexity
            if self.agent_pool.is_available('aider_grok'):
                return 'aider_grok'
            elif self.agent_pool.is_available('aider_gemini'):
                return 'aider_gemini'
        
        else:  # complex
            # Use OpenHands for complex multi-file tasks
            if self.agent_pool.is_available('openhands'):
                return 'openhands'
            elif self.agent_pool.is_available('aider_grok'):
                return 'aider_grok'
        
        # Fallback to any available agent
        return self.agent_pool.get_any_available()
```

### 2. Agent Pool

#### Base Agent Interface
Interface abstrata para todos os agentes de coding.

```python
from abc import ABC, abstractmethod
from typing import Dict, Any
import asyncio

class CodeAgent(ABC):
    def __init__(self, name: str, config: Dict[str, Any]):
        self.name = name
        self.config = config
        self.is_busy = False
        self.current_task = None
    
    @abstractmethod
    async def execute_task(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute coding task and return results"""
        pass
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if agent is healthy and ready"""
        pass
    
    def is_available(self) -> bool:
        return not self.is_busy
    
    async def acquire(self, task: Task) -> bool:
        if self.is_busy:
            return False
        self.is_busy = True
        self.current_task = task
        return True
    
    async def release(self) -> None:
        self.is_busy = False
        self.current_task = None
```

#### Aider Agent Implementation
Implementação do agente Aider com suporte a múltiplos modelos.

```python
import subprocess
import tempfile
import os
from pathlib import Path
import git

class AiderAgent(CodeAgent):
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.model = config.get('model', 'gpt-4')
        self.api_key = config.get('api_key')
        self.base_url = config.get('base_url')  # For Ollama
    
    async def execute_task(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task using Aider"""
        try:
            # Create temporary workspace
            with tempfile.TemporaryDirectory() as workspace:
                # Clone repository
                repo_url = context['repository_url']
                await self._clone_repository(repo_url, workspace)
                
                # Create branch for this work item
                branch_name = f"wi-{task.work_item_id}"
                await self._create_branch(workspace, branch_name)
                
                # Prepare Aider prompt
                prompt = self._build_prompt(task, context)
                
                # Execute Aider
                result = await self._run_aider(workspace, prompt)
                
                # Get modified files
                modified_files = await self._get_modified_files(workspace)
                
                return {
                    'success': True,
                    'modified_files': modified_files,
                    'workspace': workspace,
                    'branch': branch_name,
                    'output': result.stdout if result else '',
                    'agent': self.name
                }
        
        except Exception as e:
            logger.error(f"Aider execution failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'agent': self.name
            }
    
    async def _clone_repository(self, repo_url: str, workspace: str) -> None:
        """Clone repository to workspace"""
        git.Repo.clone_from(repo_url, workspace)
    
    async def _create_branch(self, workspace: str, branch_name: str) -> None:
        """Create and checkout new branch"""
        repo = git.Repo(workspace)
        repo.git.checkout('-b', branch_name)
    
    async def _run_aider(self, workspace: str, prompt: str) -> subprocess.CompletedProcess:
        """Run Aider command"""
        cmd = [
            'aider',
            '--model', self.model,
            '--message', prompt,
            '--yes',  # Auto-confirm changes
            '--no-git',  # We handle git ourselves
        ]
        
        # Add API configuration
        env = os.environ.copy()
        if self.api_key:
            if 'grok' in self.model:
                env['XAI_API_KEY'] = self.api_key
            elif 'gemini' in self.model:
                env['GOOGLE_API_KEY'] = self.api_key
            elif 'claude' in self.model:
                env['ANTHROPIC_API_KEY'] = self.api_key
            else:
                env['OPENAI_API_KEY'] = self.api_key
        
        if self.base_url:  # Ollama
            env['OLLAMA_BASE_URL'] = self.base_url
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=workspace,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        return subprocess.CompletedProcess(
            args=cmd,
            returncode=process.returncode,
            stdout=stdout.decode(),
            stderr=stderr.decode()
        )
    
    async def _get_modified_files(self, workspace: str) -> List[str]:
        """Get list of modified files"""
        repo = git.Repo(workspace)
        return [item.a_path for item in repo.index.diff(None)]
    
    def _build_prompt(self, task: Task, context: Dict[str, Any]) -> str:
        """Build comprehensive prompt for Aider"""
        return f"""Implement the following work item:

Title: {task.title}

Description:
{task.description}

Acceptance Criteria:
{context.get('acceptance_criteria', 'None specified')}

Technical Specifications:
{context.get('specifications', 'None specified')}

Related Files:
{', '.join(context.get('related_files', []))}

Please implement this feature following best practices:
1. Write clean, maintainable code
2. Add appropriate error handling
3. Include unit tests if applicable
4. Follow the existing code style
5. Add comments for complex logic

Focus on implementing exactly what's described in the acceptance criteria.
"""
    
    async def health_check(self) -> bool:
        """Check if Aider is available"""
        try:
            process = await asyncio.create_subprocess_exec(
                'aider', '--version',
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            await process.communicate()
            return process.returncode == 0
        except Exception:
            return False
```


#### OpenHands Agent Implementation
Implementação do agente OpenHands com Docker.

```python
import docker
import json
from typing import Dict, Any

class OpenHandsAgent(CodeAgent):
    def __init__(self, name: str, config: Dict[str, Any]):
        super().__init__(name, config)
        self.docker_client = docker.from_env()
        self.image = config.get('image', 'ghcr.io/all-hands-ai/openhands:latest')
        self.model = config.get('model', 'gpt-4')
    
    async def execute_task(self, task: Task, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute task using OpenHands in Docker"""
        container = None
        try:
            # Create workspace directory
            workspace = tempfile.mkdtemp()
            
            # Clone repository
            repo_url = context['repository_url']
            git.Repo.clone_from(repo_url, workspace)
            
            # Create OpenHands container
            container = self._create_container(workspace, task, context)
            
            # Start container
            container.start()
            
            # Wait for OpenHands to be ready
            await self._wait_for_ready(container)
            
            # Send task to OpenHands via API
            result = await self._send_task(container, task, context)
            
            # Wait for completion
            await self._wait_for_completion(container, timeout=1800)  # 30 min
            
            # Extract results
            modified_files = await self._extract_results(workspace)
            
            return {
                'success': True,
                'modified_files': modified_files,
                'workspace': workspace,
                'container_id': container.id,
                'agent': self.name
            }
        
        except Exception as e:
            logger.error(f"OpenHands execution failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'agent': self.name
            }
        
        finally:
            if container:
                try:
                    container.stop()
                    container.remove()
                except Exception as e:
                    logger.warning(f"Failed to cleanup container: {e}")
    
    def _create_container(self, workspace: str, task: Task, context: Dict[str, Any]):
        """Create OpenHands container with proper configuration"""
        return self.docker_client.containers.create(
            self.image,
            environment={
                'OPENAI_API_KEY': self.config.get('api_key'),
                'MODEL': self.model,
                'WORKSPACE': '/workspace'
            },
            volumes={
                workspace: {'bind': '/workspace', 'mode': 'rw'}
            },
            ports={'3000/tcp': None},
            detach=True
        )
    
    async def _wait_for_ready(self, container, timeout: int = 60) -> None:
        """Wait for OpenHands to be ready"""
        import time
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                # Check if container is running
                container.reload()
                if container.status == 'running':
                    # Try to connect to API
                    port = container.attrs['NetworkSettings']['Ports']['3000/tcp'][0]['HostPort']
                    response = await asyncio.get_event_loop().run_in_executor(
                        None,
                        lambda: requests.get(f'http://localhost:{port}/health')
                    )
                    if response.status_code == 200:
                        return
            except Exception:
                pass
            
            await asyncio.sleep(2)
        
        raise TimeoutError("OpenHands failed to start")
    
    async def _send_task(self, container, task: Task, context: Dict[str, Any]) -> dict:
        """Send task to OpenHands via API"""
        port = container.attrs['NetworkSettings']['Ports']['3000/tcp'][0]['HostPort']
        
        task_data = {
            'task': self._build_prompt(task, context),
            'workspace': '/workspace'
        }
        
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: requests.post(
                f'http://localhost:{port}/api/execute',
                json=task_data
            )
        )
        
        return response.json()
    
    async def _wait_for_completion(self, container, timeout: int = 1800) -> None:
        """Wait for OpenHands to complete task"""
        import time
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            container.reload()
            if container.status != 'running':
                break
            
            # Check if task is complete via API
            port = container.attrs['NetworkSettings']['Ports']['3000/tcp'][0]['HostPort']
            try:
                response = await asyncio.get_event_loop().run_in_executor(
                    None,
                    lambda: requests.get(f'http://localhost:{port}/api/status')
                )
                status = response.json()
                if status.get('state') in ['completed', 'failed']:
                    break
            except Exception:
                pass
            
            await asyncio.sleep(10)
    
    async def _extract_results(self, workspace: str) -> List[str]:
        """Extract modified files from workspace"""
        repo = git.Repo(workspace)
        return [item.a_path for item in repo.index.diff(None)]
    
    def _build_prompt(self, task: Task, context: Dict[str, Any]) -> str:
        """Build prompt for OpenHands"""
        return f"""Implement the following work item:

Title: {task.title}

Description:
{task.description}

Acceptance Criteria:
{context.get('acceptance_criteria', 'None specified')}

Technical Specifications:
{context.get('specifications', 'None specified')}

Please implement this feature following best practices.
"""
    
    async def health_check(self) -> bool:
        """Check if Docker and OpenHands image are available"""
        try:
            self.docker_client.ping()
            self.docker_client.images.get(self.image)
            return True
        except Exception:
            return False
```

#### Agent Pool Manager
Gerencia pool de agentes disponíveis.

```python
class AgentPool:
    def __init__(self, config: Dict[str, Any]):
        self.agents: Dict[str, CodeAgent] = {}
        self._initialize_agents(config)
    
    def _initialize_agents(self, config: Dict[str, Any]) -> None:
        """Initialize all configured agents"""
        agents_config = config.get('agents', {})
        
        # Aider with Ollama (local)
        if agents_config.get('aider_ollama', {}).get('enabled', True):
            self.agents['aider_ollama'] = AiderAgent('aider_ollama', {
                'model': 'codellama:13b',
                'base_url': 'http://localhost:11434'
            })
        
        # Aider with Grok
        if agents_config.get('aider_grok', {}).get('enabled', False):
            self.agents['aider_grok'] = AiderAgent('aider_grok', {
                'model': 'grok-beta',
                'api_key': agents_config['aider_grok'].get('api_key')
            })
        
        # Aider with Gemini
        if agents_config.get('aider_gemini', {}).get('enabled', False):
            self.agents['aider_gemini'] = AiderAgent('aider_gemini', {
                'model': 'gemini-pro',
                'api_key': agents_config['aider_gemini'].get('api_key')
            })
        
        # OpenHands
        if agents_config.get('openhands', {}).get('enabled', False):
            self.agents['openhands'] = OpenHandsAgent('openhands', {
                'image': 'ghcr.io/all-hands-ai/openhands:latest',
                'model': 'gpt-4',
                'api_key': agents_config['openhands'].get('api_key')
            })
    
    def is_available(self, agent_name: str) -> bool:
        """Check if agent is available"""
        agent = self.agents.get(agent_name)
        return agent is not None and agent.is_available()
    
    def get_any_available(self) -> Optional[str]:
        """Get any available agent"""
        for name, agent in self.agents.items():
            if agent.is_available():
                return name
        return None
    
    async def health_check_all(self) -> Dict[str, bool]:
        """Check health of all agents"""
        results = {}
        for name, agent in self.agents.items():
            results[name] = await agent.health_check()
        return results
```

### 3. Validation Pipeline

#### Continue Validator
Valida código usando Continue.

```python
class ContinueValidator:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_key = config.get('api_key')
    
    async def validate_code(self, workspace: str, modified_files: List[str]) -> Dict[str, Any]:
        """Validate code using Continue"""
        try:
            issues = []
            
            for file_path in modified_files:
                file_issues = await self._review_file(workspace, file_path)
                issues.extend(file_issues)
            
            return {
                'success': True,
                'issues': issues,
                'passed': len([i for i in issues if i['severity'] == 'error']) == 0
            }
        
        except Exception as e:
            logger.error(f"Continue validation failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _review_file(self, workspace: str, file_path: str) -> List[Dict[str, Any]]:
        """Review individual file with AI"""
        full_path = os.path.join(workspace, file_path)
        
        with open(full_path, 'r') as f:
            content = f.read()
        
        # Use AI to review code
        prompt = f"""Review this code for issues:

File: {file_path}

```
{content}
```

Look for:
1. Bugs and logic errors
2. Security vulnerabilities
3. Performance issues
4. Code style violations
5. Best practice violations

Return findings in JSON format:
{{
  "issues": [
    {{
      "line": 42,
      "severity": "error|warning|info",
      "message": "Description of issue",
      "suggestion": "How to fix it"
    }}
  ]
}}
"""
        
        # Call AI model
        response = await self._call_ai_model(prompt)
        
        try:
            result = json.loads(response)
            return [
                {
                    'file': file_path,
                    'line': issue['line'],
                    'severity': issue['severity'],
                    'message': issue['message'],
                    'suggestion': issue.get('suggestion', '')
                }
                for issue in result.get('issues', [])
            ]
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse AI review response for {file_path}")
            return []
    
    async def _call_ai_model(self, prompt: str) -> str:
        """Call AI model for code review"""
        import openai
        
        client = openai.AsyncOpenAI(api_key=self.api_key)
        
        response = await client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a code reviewer. Provide detailed, actionable feedback."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        return response.choices[0].message.content
```

#### AI Security Checker
Executa verificações de segurança com IA.

```python
class AISecurityChecker:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.api_key = config.get('api_key')
    
    async def check_security(self, workspace: str, modified_files: List[str]) -> Dict[str, Any]:
        """Run AI-powered security checks"""
        try:
            vulnerabilities = []
            
            for file_path in modified_files:
                file_vulns = await self._check_file_security(workspace, file_path)
                vulnerabilities.extend(file_vulns)
            
            return {
                'success': True,
                'vulnerabilities': vulnerabilities,
                'passed': len([v for v in vulnerabilities if v['severity'] == 'high']) == 0
            }
        
        except Exception as e:
            logger.error(f"Security check failed: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _check_file_security(self, workspace: str, file_path: str) -> List[Dict[str, Any]]:
        """Check individual file for security issues"""
        full_path = os.path.join(workspace, file_path)
        
        with open(full_path, 'r') as f:
            content = f.read()
        
        prompt = f"""Analyze this code for security vulnerabilities:

File: {file_path}

```
{content}
```

Look for:
1. SQL injection vulnerabilities
2. XSS vulnerabilities
3. Authentication/authorization issues
4. Input validation problems
5. Sensitive data exposure
6. Insecure dependencies
7. CSRF vulnerabilities
8. Command injection

Return findings in JSON format:
{{
  "vulnerabilities": [
    {{
      "type": "sql_injection",
      "severity": "high|medium|low",
      "line": 42,
      "description": "Detailed description",
      "recommendation": "How to fix it"
    }}
  ]
}}
"""
        
        response = await self._call_ai_model(prompt)
        
        try:
            result = json.loads(response)
            return [
                {
                    'file': file_path,
                    'type': vuln['type'],
                    'severity': vuln['severity'],
                    'line': vuln['line'],
                    'description': vuln['description'],
                    'recommendation': vuln['recommendation']
                }
                for vuln in result.get('vulnerabilities', [])
            ]
        except json.JSONDecodeError:
            logger.warning(f"Failed to parse security response for {file_path}")
            return []
    
    async def _call_ai_model(self, prompt: str) -> str:
        """Call AI model for security analysis"""
        import openai
        
        client = openai.AsyncOpenAI(api_key=self.api_key)
        
        response = await client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a security expert. Analyze code for vulnerabilities."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        
        return response.choices[0].message.content
```

#### Test Runner
Executa testes automatizados.

```python
class TestRunner:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.timeout = config.get('timeout', 300)
        self.frameworks = config.get('frameworks', ['pytest', 'jest', 'junit'])
    
    async def run_tests(self, workspace: str) -> Dict[str, Any]:
        """Run automated tests"""
        try:
            results = []
            
            # Detect test framework
            framework = self._detect_framework(workspace)
            
            if framework:
                test_result = await self._run_framework_tests(workspace, framework)
                results.append(test_result)
            
            # Aggregate results
            all_passed = all(r['passed'] for r in results)
            
            return {
                'success': True,
                'passed': all_passed,
                'results': results
            }
        
        except Exception as e:
            logger.error(f"Test execution failed: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'passed': False
            }
    
    def _detect_framework(self, workspace: str) -> Optional[str]:
        """Detect test framework used in project"""
        if os.path.exists(os.path.join(workspace, 'pytest.ini')) or \
           os.path.exists(os.path.join(workspace, 'setup.py')):
            return 'pytest'
        elif os.path.exists(os.path.join(workspace, 'package.json')):
            return 'jest'
        elif os.path.exists(os.path.join(workspace, 'pom.xml')):
            return 'junit'
        return None
    
    async def _run_framework_tests(self, workspace: str, framework: str) -> Dict[str, Any]:
        """Run tests for specific framework"""
        if framework == 'pytest':
            cmd = ['pytest', '--tb=short', '-v']
        elif framework == 'jest':
            cmd = ['npm', 'test', '--', '--ci']
        elif framework == 'junit':
            cmd = ['mvn', 'test']
        else:
            return {'passed': True, 'framework': 'unknown'}
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=workspace,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=self.timeout
            )
            
            return {
                'framework': framework,
                'passed': process.returncode == 0,
                'output': stdout.decode(),
                'errors': stderr.decode()
            }
        
        except asyncio.TimeoutError:
            process.kill()
            return {
                'framework': framework,
                'passed': False,
                'error': 'Test execution timed out'
            }
```

### 4. Git Integration

```python
import git
from typing import Dict, List, Any
import requests

class GitManager:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.github_token = config.get('github_token')
        self.gitlab_token = config.get('gitlab_token')
    
    async def commit_changes(self, workspace: str, work_item_id: str, title: str) -> str:
        """Commit all changes with proper message"""
        repo = git.Repo(workspace)
        
        # Stage all changes
        repo.git.add('.')
        
        # Create commit message
        commit_message = f"[WI-{work_item_id}] {title}\n\nImplemented by AI Orchestrator"
        
        # Commit
        commit = repo.index.commit(commit_message)
        return commit.hexsha
    
    async def push_branch(self, workspace: str, branch_name: str) -> None:
        """Push branch to remote"""
        repo = git.Repo(workspace)
        origin = repo.remote('origin')
        origin.push(branch_name)
    
    async def create_pull_request(self, repo_info: Dict[str, Any], branch_name: str,
                                 work_item: Dict[str, Any]) -> Dict[str, Any]:
        """Create pull request"""
        if 'github.com' in repo_info['url']:
            return await self._create_github_pr(repo_info, branch_name, work_item)
        elif 'gitlab.com' in repo_info['url']:
            return await self._create_gitlab_pr(repo_info, branch_name, work_item)
        else:
            raise ValueError(f"Unsupported git provider: {repo_info['url']}")
    
    async def _create_github_pr(self, repo_info: Dict[str, Any], branch_name: str,
                               work_item: Dict[str, Any]) -> Dict[str, Any]:
        """Create GitHub pull request"""
        headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        pr_data = {
            'title': f"[WI-{work_item['id']}] {work_item['title']}",
            'body': f"""## Work Item: {work_item['title']}

### Description
{work_item['description']}

### Acceptance Criteria
{work_item.get('acceptance_criteria', 'None specified')}

### Implementation Notes
- Implemented by AI Orchestrator
- Agent: {work_item.get('agent', 'Unknown')}
- Validation: Passed all checks

### Related Work Item
- ID: {work_item['id']}
- Project: {work_item['project_id']}
""",
            'head': branch_name,
            'base': 'main'
        }
        
        url = f"https://api.github.com/repos/{repo_info['owner']}/{repo_info['repo']}/pulls"
        
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: requests.post(url, json=pr_data, headers=headers)
        )
        
        if response.status_code == 201:
            pr_data = response.json()
            return {
                'success': True,
                'pr_url': pr_data['html_url'],
                'pr_number': pr_data['number']
            }
        else:
            raise Exception(f"Failed to create PR: {response.text}")
    
    async def _create_gitlab_pr(self, repo_info: Dict[str, Any], branch_name: str,
                               work_item: Dict[str, Any]) -> Dict[str, Any]:
        """Create GitLab merge request"""
        headers = {
            'PRIVATE-TOKEN': self.gitlab_token,
            'Content-Type': 'application/json'
        }
        
        mr_data = {
            'source_branch': branch_name,
            'target_branch': 'main',
            'title': f"[WI-{work_item['id']}] {work_item['title']}",
            'description': f"""## Work Item: {work_item['title']}

### Description
{work_item['description']}

### Implementation Notes
- Implemented by AI Orchestrator
- Agent: {work_item.get('agent', 'Unknown')}
"""
        }
        
        url = f"https://gitlab.com/api/v4/projects/{repo_info['project_id']}/merge_requests"
        
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: requests.post(url, json=mr_data, headers=headers)
        )
        
        if response.status_code == 201:
            mr_data = response.json()
            return {
                'success': True,
                'pr_url': mr_data['web_url'],
                'pr_number': mr_data['iid']
            }
        else:
            raise Exception(f"Failed to create MR: {response.text}")
```


### 5. Bsmart-ALM Client

```python
class BsmartClient:
    def __init__(self, config: Dict[str, Any]):
        self.base_url = config.get('base_url', 'http://localhost:8086')
        self.api_key = config.get('api_key')
    
    async def get_ready_work_items(self) -> List[Dict[str, Any]]:
        """Get work items with status 'ready'"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: requests.get(
                f'{self.base_url}/api/v1/work-items?status=ready',
                headers=headers
            )
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch work items: {response.text}")
    
    async def get_work_item_context(self, work_item_id: str) -> Dict[str, Any]:
        """Get full context for work item"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: requests.get(
                f'{self.base_url}/api/v1/work-items/{work_item_id}',
                headers=headers
            )
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Failed to fetch work item context: {response.text}")
    
    async def update_work_item_status(self, work_item_id: str, status: str) -> None:
        """Update work item status"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: requests.patch(
                f'{self.base_url}/api/v1/work-items/{work_item_id}',
                json={'status': status},
                headers=headers
            )
        )
        
        if response.status_code != 200:
            raise Exception(f"Failed to update work item status: {response.text}")
    
    async def add_work_item_comment(self, work_item_id: str, comment: str) -> None:
        """Add comment to work item"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: requests.post(
                f'{self.base_url}/api/v1/work-items/{work_item_id}/comments',
                json={'content': comment},
                headers=headers
            )
        )
        
        if response.status_code != 201:
            raise Exception(f"Failed to add comment: {response.text}")
```

### 6. Main Orchestrator

```python
import asyncio
from typing import Dict, Any, List
import logging
import yaml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AIOrchestrator:
    def __init__(self, config_path: str):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.queue_manager = QueueManager(
            self.config.get('orchestrator', {}).get('max_concurrent_tasks', 3)
        )
        self.agent_pool = AgentPool(self.config)
        self.task_router = TaskRouter(self.agent_pool)
        self.validators = self._initialize_validators()
        self.git_manager = GitManager(self.config.get('git', {}))
        self.bsmart_client = BsmartClient(self.config.get('bsmart', {}))
        self.running = False
    
    def _initialize_validators(self) -> Dict[str, Any]:
        """Initialize validation pipeline"""
        validation_config = self.config.get('validation', {})
        
        validators = {}
        
        if validation_config.get('continue', {}).get('enabled', True):
            validators['continue'] = ContinueValidator(validation_config.get('continue', {}))
        
        if validation_config.get('security', {}).get('enabled', True):
            validators['security'] = AISecurityChecker(validation_config.get('security', {}))
        
        if validation_config.get('tests', {}).get('enabled', True):
            validators['tests'] = TestRunner(validation_config.get('tests', {}))
        
        return validators
    
    async def start(self) -> None:
        """Start the orchestrator"""
        self.running = True
        logger.info("AI Orchestrator started")
        
        # Start main processing loops
        await asyncio.gather(
            self._work_item_poller(),
            self._task_processor(),
            self._health_monitor()
        )
    
    async def stop(self) -> None:
        """Stop the orchestrator"""
        self.running = False
        logger.info("AI Orchestrator stopped")
    
    async def _work_item_poller(self) -> None:
        """Poll Bsmart-ALM for new work items"""
        poll_interval = self.config.get('orchestrator', {}).get('poll_interval', 30)
        
        while self.running:
            try:
                # Get work items with status 'ready'
                work_items = await self.bsmart_client.get_ready_work_items()
                
                for work_item in work_items:
                    # Convert to task
                    task = self._create_task_from_work_item(work_item)
                    
                    # Add to queue
                    await self.queue_manager.add_task(task)
                    
                    # Update status in Bsmart-ALM
                    await self.bsmart_client.update_work_item_status(
                        work_item['id'], 'in_progress'
                    )
                
                # Wait before next poll
                await asyncio.sleep(poll_interval)
                
            except Exception as e:
                logger.error(f"Error polling work items: {str(e)}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _task_processor(self) -> None:
        """Process tasks from queue"""
        while self.running:
            try:
                # Get next task
                task = await self.queue_manager.get_next_task()
                if not task:
                    await asyncio.sleep(5)
                    continue
                
                # Process task in background
                asyncio.create_task(self._process_task(task))
                
            except Exception as e:
                logger.error(f"Error in task processor: {str(e)}")
                await asyncio.sleep(10)
    
    async def _process_task(self, task: Task) -> None:
        """Process individual task"""
        try:
            logger.info(f"Processing task {task.id}")
            
            # Select agent
            agent_name = self.task_router.select_agent(task)
            agent = self.agent_pool.agents[agent_name]
            
            # Acquire agent
            if not await agent.acquire(task):
                # Agent busy, re-queue task
                await self.queue_manager.add_task(task)
                return
            
            try:
                # Get work item context
                context = await self.bsmart_client.get_work_item_context(task.work_item_id)
                
                # Execute task
                result = await agent.execute_task(task, context)
                
                if result['success']:
                    # Validate code
                    validation_result = await self._validate_code(
                        result['workspace'], result['modified_files']
                    )
                    
                    if validation_result['passed']:
                        # Commit and push
                        await self._commit_and_push(task, result, context)
                        
                        # Mark as completed
                        await self.queue_manager.complete_task(task.id, True)
                        
                        # Update Bsmart-ALM
                        await self.bsmart_client.update_work_item_status(
                            task.work_item_id, 'in_review'
                        )
                        
                        logger.info(f"Task {task.id} completed successfully")
                    else:
                        # Validation failed
                        await self._handle_validation_failure(task, validation_result)
                else:
                    # Execution failed
                    await self.queue_manager.complete_task(
                        task.id, False, result.get('error')
                    )
                    
                    # Update Bsmart-ALM
                    await self.bsmart_client.update_work_item_status(
                        task.work_item_id, 'blocked'
                    )
                    await self.bsmart_client.add_work_item_comment(
                        task.work_item_id,
                        f"Task failed: {result.get('error')}"
                    )
            
            finally:
                await agent.release()
        
        except Exception as e:
            logger.error(f"Error processing task {task.id}: {str(e)}")
            await self.queue_manager.complete_task(task.id, False, str(e))
    
    async def _validate_code(self, workspace: str, modified_files: List[str]) -> Dict[str, Any]:
        """Run validation pipeline"""
        results = {}
        
        # Continue validation
        if 'continue' in self.validators:
            continue_result = await self.validators['continue'].validate_code(
                workspace, modified_files
            )
            results['continue'] = continue_result
        
        # Security checks
        if 'security' in self.validators:
            security_result = await self.validators['security'].check_security(
                workspace, modified_files
            )
            results['security'] = security_result
        
        # Run tests
        if 'tests' in self.validators:
            test_result = await self.validators['tests'].run_tests(workspace)
            results['tests'] = test_result
        
        # Overall pass/fail
        passed = all([
            results.get('continue', {}).get('passed', True),
            results.get('security', {}).get('passed', True),
            results.get('tests', {}).get('passed', True)
        ])
        
        return {
            'passed': passed,
            'results': results
        }
    
    async def _commit_and_push(self, task: Task, result: Dict[str, Any],
                              context: Dict[str, Any]) -> None:
        """Commit changes and create PR"""
        workspace = result['workspace']
        branch_name = result['branch']
        
        # Commit changes
        commit_hash = await self.git_manager.commit_changes(
            workspace, task.work_item_id, task.title
        )
        
        # Push branch
        await self.git_manager.push_branch(workspace, branch_name)
        
        # Create pull request
        pr_result = await self.git_manager.create_pull_request(
            context['repository'], branch_name, {
                'id': task.work_item_id,
                'title': task.title,
                'description': task.description,
                'project_id': task.project_id,
                'agent': result['agent']
            }
        )
        
        # Add PR link to work item
        await self.bsmart_client.add_work_item_comment(
            task.work_item_id,
            f"Pull Request created: {pr_result['pr_url']}"
        )
    
    async def _handle_validation_failure(self, task: Task, validation_result: Dict[str, Any]) -> None:
        """Handle validation failure"""
        # Add validation issues as comment
        issues_summary = self._format_validation_issues(validation_result)
        
        await self.bsmart_client.add_work_item_comment(
            task.work_item_id,
            f"Validation failed:\n\n{issues_summary}"
        )
        
        # Mark as blocked
        await self.queue_manager.complete_task(task.id, False, "Validation failed")
        await self.bsmart_client.update_work_item_status(task.work_item_id, 'blocked')
    
    def _format_validation_issues(self, validation_result: Dict[str, Any]) -> str:
        """Format validation issues for comment"""
        summary = []
        
        for validator_name, result in validation_result.get('results', {}).items():
            if not result.get('passed', True):
                summary.append(f"### {validator_name.title()} Issues:")
                
                if validator_name == 'continue':
                    for issue in result.get('issues', []):
                        summary.append(f"- {issue['file']}:{issue['line']} - {issue['message']}")
                
                elif validator_name == 'security':
                    for vuln in result.get('vulnerabilities', []):
                        summary.append(f"- [{vuln['severity']}] {vuln['file']}:{vuln['line']} - {vuln['description']}")
                
                elif validator_name == 'tests':
                    summary.append(f"- Tests failed: {result.get('error', 'Unknown error')}")
        
        return '\n'.join(summary)
    
    def _create_task_from_work_item(self, work_item: Dict[str, Any]) -> Task:
        """Convert work item to task"""
        complexity = self.task_router.analyze_complexity(work_item)
        
        return Task(
            id=f"task-{work_item['id']}",
            work_item_id=work_item['id'],
            project_id=work_item['project_id'],
            title=work_item['title'],
            description=work_item['description'],
            priority=self._map_priority(work_item.get('priority', 'medium')),
            complexity=complexity,
            status=TaskStatus.PENDING
        )
    
    def _map_priority(self, priority: str) -> int:
        """Map priority string to numeric value"""
        priority_map = {
            'critical': 4,
            'high': 3,
            'medium': 2,
            'low': 1
        }
        return priority_map.get(priority, 2)
    
    async def _health_monitor(self) -> None:
        """Monitor health of agents and system"""
        check_interval = self.config.get('orchestrator', {}).get('health_check_interval', 60)
        
        while self.running:
            try:
                # Check agent health
                health_status = await self.agent_pool.health_check_all()
                
                for agent_name, is_healthy in health_status.items():
                    if not is_healthy:
                        logger.warning(f"Agent {agent_name} is unhealthy")
                
                # Log queue stats
                stats = self.queue_manager.get_stats()
                logger.info(f"Queue stats: {stats}")
                
                await asyncio.sleep(check_interval)
                
            except Exception as e:
                logger.error(f"Error in health monitor: {str(e)}")
                await asyncio.sleep(check_interval)
```

## Configuration

### config.yaml
```yaml
orchestrator:
  max_concurrent_tasks: 3
  poll_interval: 30
  health_check_interval: 60

bsmart:
  base_url: "http://localhost:8086"
  api_key: "your-api-key"

git:
  github_token: "your-github-token"
  gitlab_token: "your-gitlab-token"

agents:
  aider_ollama:
    enabled: true
    model: "codellama:13b"
    base_url: "http://localhost:11434"
  
  aider_grok:
    enabled: true
    model: "grok-beta"
    api_key: "your-grok-key"
  
  aider_gemini:
    enabled: true
    model: "gemini-pro"
    api_key: "your-gemini-key"
  
  openhands:
    enabled: false
    image: "ghcr.io/all-hands-ai/openhands:latest"
    model: "gpt-4"
    api_key: "your-openai-key"

validation:
  continue:
    enabled: true
    api_key: "your-openai-key"
  
  security:
    enabled: true
    api_key: "your-openai-key"
  
  tests:
    enabled: true
    timeout: 300
    frameworks:
      - pytest
      - jest
      - junit

logging:
  level: INFO
  file: "orchestrator.log"
  max_size: "100MB"
  backup_count: 5

monitoring:
  metrics_port: 9090
  health_port: 8080
```

## Data Models

```python
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime
from enum import Enum

class TaskStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"

@dataclass
class Task:
    id: str
    work_item_id: str
    project_id: str
    title: str
    description: str
    priority: int
    complexity: str
    status: TaskStatus
    assigned_agent: Optional[str] = None
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    error_message: Optional[str] = None
```

## Error Handling

```python
class OrchestratorError(Exception):
    """Base exception for orchestrator errors"""
    pass

class AgentError(OrchestratorError):
    """Agent execution error"""
    pass

class ValidationError(OrchestratorError):
    """Validation pipeline error"""
    pass

class GitError(OrchestratorError):
    """Git operation error"""
    pass

class BsmartAPIError(OrchestratorError):
    """Bsmart-ALM API error"""
    pass
```

## Testing Strategy

### Unit Tests
- Test individual components (QueueManager, TaskRouter, Agents)
- Mock external dependencies
- Test error handling scenarios

### Integration Tests
- Test agent execution with real models
- Test validation pipeline
- Test Git operations

### E2E Tests
- Test complete workflow from work item to PR
- Test retry logic
- Test validation failures

## Performance Considerations

1. **Parallel Processing**: Process multiple tasks concurrently
2. **Resource Management**: Limit concurrent agents to prevent resource exhaustion
3. **Caching**: Cache work item context to reduce API calls
4. **Timeout Handling**: Set appropriate timeouts for long-running operations

## Security Considerations

1. **API Keys**: Store API keys securely in environment variables
2. **Token Management**: Rotate tokens regularly
3. **Code Isolation**: Run agents in isolated environments
4. **Input Validation**: Validate all inputs from Bsmart-ALM API

## Deployment

### Docker Compose
```yaml
version: '3.8'

services:
  orchestrator:
    build: .
    volumes:
      - ./config.yaml:/app/config.yaml
      - ./logs:/app/logs
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      - CONFIG_PATH=/app/config.yaml
    ports:
      - "8080:8080"  # Health check
      - "9090:9090"  # Metrics
    depends_on:
      - ollama
  
  ollama:
    image: ollama/ollama:latest
    volumes:
      - ollama_data:/root/.ollama
    ports:
      - "11434:11434"

volumes:
  ollama_data:
```

### Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    docker.io \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Install Aider
RUN pip install aider-chat

# Copy application code
COPY . .

# Run orchestrator
CMD ["python", "main.py"]
```

### requirements.txt
```
asyncio
pyyaml
gitpython
docker
requests
openai
```

### Main Entry Point
```python
# main.py
import asyncio
import sys
import signal

async def main():
    config_path = sys.argv[1] if len(sys.argv) > 1 else 'config.yaml'
    
    orchestrator = AIOrchestrator(config_path)
    
    # Handle shutdown gracefully
    def signal_handler(sig, frame):
        asyncio.create_task(orchestrator.stop())
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start orchestrator
    await orchestrator.start()

if __name__ == '__main__':
    asyncio.run(main())
```

## Monitoring and Observability

### Metrics
- Tasks processed per hour
- Success/failure rate
- Average processing time
- Agent utilization
- API costs

### Logging
- Structured logging with JSON format
- Log levels: DEBUG, INFO, WARNING, ERROR
- Centralized log aggregation

### Alerts
- Agent failures
- High error rate
- API quota exceeded
- Long-running tasks

## Future Enhancements

1. **Cost Optimization**: Implement cost tracking and budget limits
2. **Learning System**: Learn from successful/failed tasks to improve agent selection
3. **Human-in-the-Loop**: Allow human review before PR creation
4. **Multi-Repository**: Support multiple repositories per project
5. **Advanced Validation**: Add more validation steps (performance, accessibility)
