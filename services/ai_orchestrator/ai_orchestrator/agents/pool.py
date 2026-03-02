"""Agent pool manager."""

import logging
from typing import Dict, Any, Optional

from .base import CodeAgent
from .aider import AiderAgent

logger = logging.getLogger(__name__)


class AgentPool:
    """Manages pool of available coding agents."""
    
    def __init__(self, config: Dict[str, Any]):
        """Initialize agent pool.
        
        Args:
            config: Configuration for all agents
        """
        self.agents: Dict[str, CodeAgent] = {}
        self._initialize_agents(config)
    
    def _initialize_agents(self, config: Dict[str, Any]) -> None:
        """Initialize all configured agents.
        
        Args:
            config: Agent configuration
        """
        agents_config = config.get('agents', {})
        
        # Aider with Ollama (local)
        if agents_config.get('aider_ollama', {}).get('enabled', True):
            ollama_config = agents_config['aider_ollama']
            self.agents['aider_ollama'] = AiderAgent('aider_ollama', {
                'model': ollama_config.get('model', 'codellama:13b'),
                'base_url': ollama_config.get('base_url', 'http://localhost:11434')
            })
            logger.info("Initialized Aider with Ollama")
        
        # Aider with Grok
        if agents_config.get('aider_grok', {}).get('enabled', False):
            grok_config = agents_config['aider_grok']
            api_key = grok_config.get('api_key')
            if api_key:
                self.agents['aider_grok'] = AiderAgent('aider_grok', {
                    'model': grok_config.get('model', 'grok-beta'),
                    'api_key': api_key
                })
                logger.info("Initialized Aider with Grok")
            else:
                logger.warning("Aider Grok enabled but no API key provided")
        
        # Aider with Gemini
        if agents_config.get('aider_gemini', {}).get('enabled', False):
            gemini_config = agents_config['aider_gemini']
            api_key = gemini_config.get('api_key')
            if api_key:
                self.agents['aider_gemini'] = AiderAgent('aider_gemini', {
                    'model': gemini_config.get('model', 'gemini-pro'),
                    'api_key': api_key
                })
                logger.info("Initialized Aider with Gemini")
            else:
                logger.warning("Aider Gemini enabled but no API key provided")
        
        # OpenHands (future implementation)
        if agents_config.get('openhands', {}).get('enabled', False):
            logger.warning("OpenHands agent not yet implemented")
        
        logger.info(f"Agent pool initialized with {len(self.agents)} agents")
    
    def is_available(self, agent_name: str) -> bool:
        """Check if agent is available.
        
        Args:
            agent_name: Name of agent to check
            
        Returns:
            True if agent exists and is available
        """
        agent = self.agents.get(agent_name)
        return agent is not None and agent.is_available()
    
    def get_agent(self, agent_name: str) -> Optional[CodeAgent]:
        """Get agent by name.
        
        Args:
            agent_name: Name of agent
            
        Returns:
            Agent instance or None if not found
        """
        return self.agents.get(agent_name)
    
    def get_any_available(self) -> Optional[str]:
        """Get any available agent.
        
        Returns:
            Name of available agent or None if all busy
        """
        for name, agent in self.agents.items():
            if agent.is_available():
                return name
        return None
    
    async def health_check_all(self) -> Dict[str, bool]:
        """Check health of all agents.
        
        Returns:
            Dictionary mapping agent names to health status
        """
        results = {}
        for name, agent in self.agents.items():
            try:
                results[name] = await agent.health_check()
            except Exception as e:
                logger.error(f"Health check failed for {name}: {e}")
                results[name] = False
        
        return results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get agent pool statistics.
        
        Returns:
            Statistics about agent pool
        """
        total = len(self.agents)
        available = sum(1 for agent in self.agents.values() if agent.is_available())
        busy = total - available
        
        return {
            'total_agents': total,
            'available': available,
            'busy': busy,
            'agents': {
                name: {
                    'available': agent.is_available(),
                    'current_task': agent.current_task.id if agent.current_task else None
                }
                for name, agent in self.agents.items()
            }
        }
