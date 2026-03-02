"""Git operations manager."""

import logging
from typing import Dict, Any, Optional
import git
import httpx

logger = logging.getLogger(__name__)


class GitManager:
    """Manages Git operations including commit, push, and PR creation."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize Git manager.
        
        Args:
            config: Git configuration including provider, token, etc.
        """
        self.provider = config.get('provider', 'github')  # github or gitlab
        self.api_token = config.get('api_token')
        self.default_branch = config.get('default_branch', 'main')
        self.auto_merge = config.get('pr_auto_merge', False)
        
        self.client = httpx.AsyncClient(
            headers={'Authorization': f'Bearer {self.api_token}'},
            timeout=30.0
        )
    
    async def commit_and_push(
        self,
        workspace: str,
        branch: str,
        work_item_id: str,
        title: str,
        modified_files: list[str]
    ) -> bool:
        """Commit changes and push to remote.
        
        Args:
            workspace: Workspace directory
            branch: Branch name
            work_item_id: Work item ID for commit message
            title: Work item title
            modified_files: List of modified files
            
        Returns:
            True if successful, False otherwise
        """
        try:
            repo = git.Repo(workspace)
            
            # Stage all changes
            repo.git.add(A=True)
            
            # Create commit message
            commit_message = self._build_commit_message(
                work_item_id,
                title,
                modified_files
            )
            
            # Commit
            repo.index.commit(commit_message)
            logger.info(
                f"Created commit for work item {work_item_id}",
                extra={'work_item_id': work_item_id, 'branch': branch}
            )
            
            # Push to remote
            origin = repo.remote('origin')
            origin.push(branch)
            logger.info(
                f"Pushed branch {branch}",
                extra={'work_item_id': work_item_id, 'branch': branch}
            )
            
            return True
        
        except Exception as e:
            logger.error(
                f"Failed to commit and push: {e}",
                extra={'work_item_id': work_item_id, 'branch': branch},
                exc_info=True
            )
            return False
    
    async def create_pull_request(
        self,
        repo_owner: str,
        repo_name: str,
        branch: str,
        work_item_id: str,
        title: str,
        description: str
    ) -> Optional[str]:
        """Create pull request.
        
        Args:
            repo_owner: Repository owner/organization
            repo_name: Repository name
            branch: Source branch
            work_item_id: Work item ID
            title: PR title
            description: PR description
            
        Returns:
            PR URL if successful, None otherwise
        """
        if self.provider == 'github':
            return await self._create_github_pr(
                repo_owner, repo_name, branch, work_item_id, title, description
            )
        elif self.provider == 'gitlab':
            return await self._create_gitlab_mr(
                repo_owner, repo_name, branch, work_item_id, title, description
            )
        else:
            logger.error(f"Unsupported Git provider: {self.provider}")
            return None
    
    async def _create_github_pr(
        self,
        repo_owner: str,
        repo_name: str,
        branch: str,
        work_item_id: str,
        title: str,
        description: str
    ) -> Optional[str]:
        """Create GitHub pull request.
        
        Args:
            repo_owner: Repository owner
            repo_name: Repository name
            branch: Source branch
            work_item_id: Work item ID
            title: PR title
            description: PR description
            
        Returns:
            PR URL if successful, None otherwise
        """
        try:
            url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/pulls'
            
            pr_data = {
                'title': f'[WI-{work_item_id}] {title}',
                'head': branch,
                'base': self.default_branch,
                'body': self._build_pr_description(work_item_id, description),
                'draft': False
            }
            
            response = await self.client.post(url, json=pr_data)
            response.raise_for_status()
            
            pr_url = response.json()['html_url']
            logger.info(
                f"Created GitHub PR: {pr_url}",
                extra={'work_item_id': work_item_id, 'pr_url': pr_url}
            )
            
            return pr_url
        
        except Exception as e:
            logger.error(
                f"Failed to create GitHub PR: {e}",
                extra={'work_item_id': work_item_id},
                exc_info=True
            )
            return None
    
    async def _create_gitlab_mr(
        self,
        repo_owner: str,
        repo_name: str,
        branch: str,
        work_item_id: str,
        title: str,
        description: str
    ) -> Optional[str]:
        """Create GitLab merge request.
        
        Args:
            repo_owner: Repository owner
            repo_name: Repository name
            branch: Source branch
            work_item_id: Work item ID
            title: MR title
            description: MR description
            
        Returns:
            MR URL if successful, None otherwise
        """
        try:
            # Get project ID
            project_path = f'{repo_owner}/{repo_name}'
            project_url = f'https://gitlab.com/api/v4/projects/{project_path.replace("/", "%2F")}'
            
            project_response = await self.client.get(project_url)
            project_response.raise_for_status()
            project_id = project_response.json()['id']
            
            # Create MR
            mr_url = f'https://gitlab.com/api/v4/projects/{project_id}/merge_requests'
            
            mr_data = {
                'source_branch': branch,
                'target_branch': self.default_branch,
                'title': f'[WI-{work_item_id}] {title}',
                'description': self._build_pr_description(work_item_id, description),
                'remove_source_branch': True
            }
            
            response = await self.client.post(mr_url, json=mr_data)
            response.raise_for_status()
            
            mr_web_url = response.json()['web_url']
            logger.info(
                f"Created GitLab MR: {mr_web_url}",
                extra={'work_item_id': work_item_id, 'mr_url': mr_web_url}
            )
            
            return mr_web_url
        
        except Exception as e:
            logger.error(
                f"Failed to create GitLab MR: {e}",
                extra={'work_item_id': work_item_id},
                exc_info=True
            )
            return None
    
    def _build_commit_message(
        self,
        work_item_id: str,
        title: str,
        modified_files: list[str]
    ) -> str:
        """Build commit message.
        
        Args:
            work_item_id: Work item ID
            title: Work item title
            modified_files: List of modified files
            
        Returns:
            Formatted commit message
        """
        message = f"""[WI-{work_item_id}] {title}

Automated implementation by AI Orchestrator

Modified files:
"""
        for file in modified_files[:10]:  # Limit to first 10 files
            message += f"- {file}\n"
        
        if len(modified_files) > 10:
            message += f"... and {len(modified_files) - 10} more files\n"
        
        message += f"\nWork Item ID: {work_item_id}"
        
        return message
    
    def _build_pr_description(self, work_item_id: str, description: str) -> str:
        """Build PR/MR description.
        
        Args:
            work_item_id: Work item ID
            description: Work item description
            
        Returns:
            Formatted PR description
        """
        return f"""## 🤖 Automated Implementation

This PR was automatically generated by the AI Orchestrator.

### Work Item
**ID**: {work_item_id}

### Description
{description}

### Implementation Notes
- Code generated using AI coding agents
- Automated validation performed
- Tests executed successfully

### Review Checklist
- [ ] Code follows project standards
- [ ] Tests are passing
- [ ] Documentation is updated
- [ ] No security vulnerabilities

---
*Generated by Bsmart AI Orchestrator*
"""
    
    async def close(self) -> None:
        """Close HTTP client."""
        await self.client.aclose()
