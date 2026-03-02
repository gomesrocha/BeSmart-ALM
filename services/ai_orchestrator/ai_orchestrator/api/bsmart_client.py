"""Client for Bsmart-ALM API integration."""

import logging
from typing import List, Dict, Any, Optional
import httpx
from datetime import datetime

logger = logging.getLogger(__name__)


class BsmartClient:
    """Client for interacting with Bsmart-ALM API."""
    
    def __init__(self, api_url: str, api_key: str):
        """Initialize Bsmart client.
        
        Args:
            api_url: Base URL for Bsmart-ALM API
            api_key: API key for authentication
        """
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.client = httpx.AsyncClient(
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            },
            timeout=30.0
        )
    
    async def get_ready_work_items(
        self,
        project_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get work items with status 'ready'.
        
        Args:
            project_id: Optional project ID to filter by
            
        Returns:
            List of work items ready for processing
        """
        try:
            # Get all projects if no project_id specified
            if not project_id:
                projects = await self._get_projects()
                work_items = []
                for project in projects:
                    items = await self._get_project_work_items(
                        project['id'],
                        status='ready'
                    )
                    work_items.extend(items)
                return work_items
            else:
                return await self._get_project_work_items(project_id, status='ready')
        
        except Exception as e:
            logger.error(f"Failed to get ready work items: {e}")
            return []
    
    async def _get_projects(self) -> List[Dict[str, Any]]:
        """Get all projects."""
        try:
            url = f'{self.api_url}/api/v1/projects'
            logger.info(f"🔍 Fetching projects from: {url}")
            logger.info(f"🔑 Using token: {self.api_key[:20]}...")
            
            response = await self.client.get(url)
            logger.info(f"📡 Response status: {response.status_code}")
            logger.info(f"📄 Response headers: {dict(response.headers)}")
            
            response.raise_for_status()
            data = response.json()
            logger.info(f"📦 Response data type: {type(data)}")
            logger.info(f"📦 Response data: {data}")
            
            # API retorna lista diretamente
            if isinstance(data, list):
                logger.info(f"✅ Got {len(data)} projects (list format)")
                return data
            # Ou pode retornar objeto com 'data' ou 'projects'
            elif isinstance(data, dict):
                projects = data.get('data', data.get('projects', []))
                logger.info(f"✅ Got {len(projects)} projects (dict format)")
                return projects
            
            logger.warning("⚠️ Unexpected data format, returning empty list")
            return []
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ HTTP error getting projects: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"❌ Failed to get projects: {type(e).__name__}: {e}")
            raise
    
    async def _get_project_work_items(
        self,
        project_id: str,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get work items for a project."""
        try:
            url = f'{self.api_url}/projects/{project_id}/work-items'
            params = {'status': status} if status else {}
            
            response = await self.client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            # API retorna lista diretamente
            if isinstance(data, list):
                return data
            # Ou pode retornar objeto com 'data' ou 'work_items'
            elif isinstance(data, dict):
                return data.get('data', data.get('work_items', []))
            
            return []
        except Exception as e:
            logger.error(f"Failed to get work items for project {project_id}: {e}")
            return []
    
    async def get_work_item_context(self, work_item_id: str) -> Dict[str, Any]:
        """Get full context for a work item.
        
        Args:
            work_item_id: ID of work item
            
        Returns:
            Work item with full context including acceptance criteria, specs, etc.
        """
        try:
            response = await self.client.get(
                f'{self.api_url}/work-items/{work_item_id}'
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Failed to get work item context: {e}")
            return {}
    
    async def update_work_item_status(
        self,
        work_item_id: str,
        status: str
    ) -> bool:
        """Update work item status.
        
        Args:
            work_item_id: ID of work item
            status: New status (in_progress, in_review, done, blocked)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = await self.client.patch(
                f'{self.api_url}/work-items/{work_item_id}',
                json={'status': status}
            )
            response.raise_for_status()
            
            logger.info(
                f"Updated work item status to {status}",
                extra={'work_item_id': work_item_id, 'status': status}
            )
            return True
        
        except Exception as e:
            logger.error(
                f"Failed to update work item status: {e}",
                extra={'work_item_id': work_item_id, 'status': status}
            )
            return False
    
    async def add_work_item_comment(
        self,
        work_item_id: str,
        comment: str
    ) -> bool:
        """Add comment to work item.
        
        Args:
            work_item_id: ID of work item
            comment: Comment text
            
        Returns:
            True if successful, False otherwise
        """
        try:
            response = await self.client.post(
                f'{self.api_url}/work-items/{work_item_id}/comments',
                json={'content': comment}
            )
            response.raise_for_status()
            
            logger.info(
                "Added comment to work item",
                extra={'work_item_id': work_item_id}
            )
            return True
        
        except Exception as e:
            logger.error(
                f"Failed to add comment: {e}",
                extra={'work_item_id': work_item_id}
            )
            return False
    
    async def add_pr_link(
        self,
        work_item_id: str,
        pr_url: str
    ) -> bool:
        """Add pull request link to work item.
        
        Args:
            work_item_id: ID of work item
            pr_url: URL of pull request
            
        Returns:
            True if successful, False otherwise
        """
        comment = f"🔗 Pull Request created: {pr_url}"
        return await self.add_work_item_comment(work_item_id, comment)
    
    async def report_error(
        self,
        work_item_id: str,
        error: str,
        agent: str
    ) -> bool:
        """Report error to work item.
        
        Args:
            work_item_id: ID of work item
            error: Error message
            agent: Agent that encountered the error
            
        Returns:
            True if successful, False otherwise
        """
        comment = f"""❌ Error during automated implementation:

**Agent**: {agent}
**Error**: {error}
**Time**: {datetime.now().isoformat()}

The work item has been marked as blocked. Please review and resolve the issue."""
        
        # Add comment and update status
        await self.add_work_item_comment(work_item_id, comment)
        return await self.update_work_item_status(work_item_id, 'blocked')
    
    async def close(self) -> None:
        """Close HTTP client."""
        await self.client.aclose()
