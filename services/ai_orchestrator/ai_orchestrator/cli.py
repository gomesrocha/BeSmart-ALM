"""CLI interface for AI Orchestrator."""

import asyncio
import logging
import sys
from typing import Optional
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt, Confirm

from ai_orchestrator.api import BsmartClient
from ai_orchestrator.core import QueueManager, Task, TaskStatus, TaskComplexity
from ai_orchestrator.agents import AgentPool
from ai_orchestrator.core.task_router import TaskRouter

console = Console()

class OrchestratorCLI:
    """Interactive CLI for AI Orchestrator."""
    
    def __init__(self):
        self.client: Optional[BsmartClient] = None
        self.queue: Optional[QueueManager] = None
        self.agent_pool: Optional[AgentPool] = None
        self.router: Optional[TaskRouter] = None
        self.authenticated = False
        self.selected_project = None
        
    async def start(self):
        """Start interactive CLI."""
        console.print(Panel.fit(
            "[bold blue]🤖 Bsmart AI Orchestrator[/bold blue]\n"
            "Autonomous coding agent orchestration system",
            border_style="blue"
        ))
        
        await self.main_menu()
    
    async def main_menu(self):
        """Main menu loop."""
        while True:
            console.print("\n" + "="*60)
            
            # Status
            status_text = "[red]❌ Not authenticated[/red]"
            if self.authenticated:
                status_text = "[green]✅ Authenticated[/green]"
                if self.selected_project:
                    status_text += f" | Project: [cyan]{self.selected_project['name']}[/cyan]"
            
            console.print(f"Status: {status_text}")
            
            # Menu options
            options = [
                "1. 🔑 Login to Bsmart-ALM",
                "2. 📁 Select Project",
                "3. 🔍 View Work Items",
                "4. 🤖 View Agents Status",
                "5. ▶️  Start Processing",
                "6. 📊 View Queue Status",
                "7. ⚙️  Configuration",
                "8. 🚪 Exit"
            ]
            
            for option in options:
                console.print(f"  {option}")
            
            choice = Prompt.ask("\nChoose an option", choices=["1", "2", "3", "4", "5", "6", "7", "8"])
            
            if choice == "1":
                await self.login()
            elif choice == "2":
                await self.select_project()
            elif choice == "3":
                await self.view_work_items()
            elif choice == "4":
                await self.view_agents()
            elif choice == "5":
                await self.start_processing()
            elif choice == "6":
                await self.view_queue()
            elif choice == "7":
                await self.configuration()
            elif choice == "8":
                console.print("[yellow]👋 Goodbye![/yellow]")
                break
    
    async def login(self):
        """Login to Bsmart-ALM."""
        console.print("\n[bold]🔑 Login to Bsmart-ALM[/bold]")
        
        api_url = Prompt.ask("API URL", default="http://localhost:8086/api/v1")
        email = Prompt.ask("Email")
        password = Prompt.ask("Password", password=True)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Authenticating...", total=None)
            
            try:
                # Create client
                self.client = BsmartClient(api_url, "temp-key")
                
                # TODO: Implement actual login
                # For now, simulate login
                await asyncio.sleep(1)
                
                self.authenticated = True
                console.print("[green]✅ Login successful![/green]")
                
                # Initialize components
                self.queue = QueueManager(max_concurrent_tasks=3)
                
                # Load agent config (simplified)
                agent_config = {
                    'agents': {
                        'aider_ollama': {
                            'enabled': True,
                            'model': 'codellama:13b'
                        }
                    }
                }
                self.agent_pool = AgentPool(agent_config)
                self.router = TaskRouter(self.agent_pool)
                
            except Exception as e:
                console.print(f"[red]❌ Login failed: {e}[/red]")
    
    async def select_project(self):
        """Select project."""
        if not self.authenticated:
            console.print("[red]❌ Please login first[/red]")
            return
        
        console.print("\n[bold]📁 Select Project[/bold]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Loading projects...", total=None)
            
            try:
                # TODO: Get real projects from API
                # For now, simulate
                await asyncio.sleep(1)
                
                projects = [
                    {"id": "1", "name": "Sistema de Vendas", "description": "Sistema principal"},
                    {"id": "2", "name": "Portal Cliente", "description": "Portal web"},
                    {"id": "3", "name": "API Gateway", "description": "Gateway de APIs"}
                ]
                
                # Show projects table
                table = Table(title="Available Projects")
                table.add_column("ID", style="cyan")
                table.add_column("Name", style="green")
                table.add_column("Description")
                
                for proj in projects:
                    table.add_row(proj["id"], proj["name"], proj["description"])
                
                console.print(table)
                
                project_id = Prompt.ask("Select project ID", choices=[p["id"] for p in projects])
                self.selected_project = next(p for p in projects if p["id"] == project_id)
                
                console.print(f"[green]✅ Selected: {self.selected_project['name']}[/green]")
                
            except Exception as e:
                console.print(f"[red]❌ Failed to load projects: {e}[/red]")
    
    async def view_work_items(self):
        """View work items."""
        if not self.selected_project:
            console.print("[red]❌ Please select a project first[/red]")
            return
        
        console.print("\n[bold]🔍 Work Items[/bold]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Loading work items...", total=None)
            
            try:
                # TODO: Get real work items from API
                await asyncio.sleep(1)
                
                work_items = [
                    {
                        "id": "WI-1",
                        "title": "Implementar autenticação",
                        "status": "ready",
                        "priority": "high",
                        "complexity": "medium"
                    },
                    {
                        "id": "WI-2",
                        "title": "Corrigir bug no login",
                        "status": "ready",
                        "priority": "critical",
                        "complexity": "simple"
                    },
                    {
                        "id": "WI-3",
                        "title": "Refatorar arquitetura",
                        "status": "backlog",
                        "priority": "medium",
                        "complexity": "complex"
                    }
                ]
                
                # Filter ready items
                ready_items = [wi for wi in work_items if wi["status"] == "ready"]
                
                if not ready_items:
                    console.print("[yellow]⚠️  No work items ready for processing[/yellow]")
                    return
                
                # Show work items table
                table = Table(title=f"Work Items - {self.selected_project['name']}")
                table.add_column("ID", style="cyan")
                table.add_column("Title", style="green")
                table.add_column("Status")
                table.add_column("Priority")
                table.add_column("Complexity")
                
                for wi in ready_items:
                    status_color = "green" if wi["status"] == "ready" else "yellow"
                    priority_color = "red" if wi["priority"] == "critical" else "orange" if wi["priority"] == "high" else "blue"
                    
                    table.add_row(
                        wi["id"],
                        wi["title"],
                        f"[{status_color}]{wi['status']}[/{status_color}]",
                        f"[{priority_color}]{wi['priority']}[/{priority_color}]",
                        wi["complexity"]
                    )
                
                console.print(table)
                
                # Ask if user wants to add to queue
                if Confirm.ask("\nAdd ready items to processing queue?"):
                    await self.add_to_queue(ready_items)
                
            except Exception as e:
                console.print(f"[red]❌ Failed to load work items: {e}[/red]")
    
    async def add_to_queue(self, work_items):
        """Add work items to processing queue."""
        for wi in work_items:
            complexity_map = {
                "simple": TaskComplexity.SIMPLE,
                "medium": TaskComplexity.MEDIUM,
                "complex": TaskComplexity.COMPLEX
            }
            
            priority_map = {
                "low": 1,
                "medium": 3,
                "high": 5,
                "critical": 10
            }
            
            task = Task(
                id=f"task-{wi['id']}",
                work_item_id=wi["id"],
                project_id=self.selected_project["id"],
                title=wi["title"],
                description=wi["title"],  # Simplified
                priority=priority_map.get(wi["priority"], 3),
                complexity=complexity_map.get(wi["complexity"], TaskComplexity.MEDIUM)
            )
            
            await self.queue.add_task(task)
        
        console.print(f"[green]✅ Added {len(work_items)} items to queue[/green]")
    
    async def view_agents(self):
        """View agents status."""
        if not self.agent_pool:
            console.print("[red]❌ Please login first[/red]")
            return
        
        console.print("\n[bold]🤖 Agents Status[/bold]")
        
        stats = self.agent_pool.get_stats()
        
        # Summary
        console.print(f"Total agents: [cyan]{stats['total_agents']}[/cyan]")
        console.print(f"Available: [green]{stats['available']}[/green]")
        console.print(f"Busy: [yellow]{stats['busy']}[/yellow]")
        
        # Agents table
        table = Table(title="Agent Details")
        table.add_column("Agent", style="cyan")
        table.add_column("Status")
        table.add_column("Current Task")
        
        for name, info in stats['agents'].items():
            status = "[green]Available[/green]" if info['available'] else "[yellow]Busy[/yellow]"
            current_task = info['current_task'] or "None"
            table.add_row(name, status, current_task)
        
        console.print(table)
        
        # Health check
        if Confirm.ask("\nRun health check?"):
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Checking agent health...", total=None)
                
                health = await self.agent_pool.health_check_all()
                
                console.print("\n[bold]Health Check Results:[/bold]")
                for name, is_healthy in health.items():
                    status = "[green]✅ Healthy[/green]" if is_healthy else "[red]❌ Unhealthy[/red]"
                    console.print(f"  {name}: {status}")
    
    async def view_queue(self):
        """View queue status."""
        if not self.queue:
            console.print("[red]❌ Please login first[/red]")
            return
        
        console.print("\n[bold]📊 Queue Status[/bold]")
        
        stats = self.queue.get_stats()
        
        # Summary panel
        summary = f"""
[cyan]Pending:[/cyan] {stats['pending_tasks']}
[yellow]In Progress:[/yellow] {stats['in_progress_tasks']}
[green]Completed:[/green] {stats['completed_tasks']}
[red]Failed:[/red] {stats['failed_tasks']}
[blue]Total:[/blue] {stats['total_tasks']}
[magenta]Success Rate:[/magenta] {stats['success_rate']:.1f}%
        """
        
        console.print(Panel(summary, title="Queue Statistics", border_style="blue"))
    
    async def start_processing(self):
        """Start processing work items."""
        if not all([self.authenticated, self.selected_project, self.queue, self.agent_pool]):
            console.print("[red]❌ Please complete setup first (login, select project, add work items)[/red]")
            return
        
        stats = self.queue.get_stats()
        if stats['pending_tasks'] == 0:
            console.print("[yellow]⚠️  No tasks in queue. Add work items first.[/yellow]")
            return
        
        console.print("\n[bold]▶️  Starting Processing[/bold]")
        
        if not Confirm.ask(f"Process {stats['pending_tasks']} pending tasks?"):
            return
        
        # TODO: Implement actual processing loop
        console.print("[yellow]⚠️  Processing loop not yet implemented[/yellow]")
        console.print("This will be implemented in the main orchestrator component.")
    
    async def configuration(self):
        """Configuration menu."""
        console.print("\n[bold]⚙️  Configuration[/bold]")
        
        config_options = [
            "1. View current config",
            "2. Edit API settings",
            "3. Edit agent settings",
            "4. Back to main menu"
        ]
        
        for option in config_options:
            console.print(f"  {option}")
        
        choice = Prompt.ask("Choose option", choices=["1", "2", "3", "4"])
        
        if choice == "1":
            console.print("[yellow]⚠️  Config viewer not yet implemented[/yellow]")
        elif choice == "2":
            console.print("[yellow]⚠️  API settings editor not yet implemented[/yellow]")
        elif choice == "3":
            console.print("[yellow]⚠️  Agent settings editor not yet implemented[/yellow]")


@click.command()
@click.option('--config', '-c', default='config.yaml', help='Configuration file path')
def main(config):
    """Start AI Orchestrator CLI."""
    try:
        cli = OrchestratorCLI()
        asyncio.run(cli.start())
    except KeyboardInterrupt:
        console.print("\n[yellow]👋 Interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        sys.exit(1)


if __name__ == '__main__':
    main()
