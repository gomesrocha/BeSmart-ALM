"""Web UI for AI Orchestrator."""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from ai_orchestrator.api import BsmartClient
from ai_orchestrator.core import QueueManager, Task, TaskStatus, TaskComplexity
from ai_orchestrator.agents import AgentPool
from ai_orchestrator.core.task_router import TaskRouter

app = FastAPI(title="AI Orchestrator", description="Web interface for AI Orchestrator")

# Global state (in production, use proper state management)
state = {
    'client': None,
    'queue': None,
    'agent_pool': None,
    'router': None,
    'authenticated': False,
    'selected_project': None,
    'processing': False,
    'repo_path': None  # Repository base path
}

# WebSocket connections for real-time updates
connections: List[WebSocket] = []

# Pydantic models
class LoginRequest(BaseModel):
    api_url: str
    email: str
    password: str
    repo_path: str = "~/bsmart-repos"  # Default path

class ProjectSelection(BaseModel):
    project_id: str

class WorkItemDict(BaseModel):
    id: str
    title: str
    description: str

class WorkItemAction(BaseModel):
    work_items: List[WorkItemDict]
    task_type: str

# API Routes
@app.get("/")
async def root():
    """Serve main page."""
    html_path = Path(__file__).parent / "static" / "index.html"
    if html_path.exists():
        return HTMLResponse(html_path.read_text())
    return HTMLResponse("<h1>AI Orchestrator</h1><p>Static files not found</p>")

@app.post("/api/login")
async def login(request: LoginRequest):
    """Login to Bsmart-ALM."""
    try:
        import httpx
        from pathlib import Path
        import os
        
        # Expand and validate repo path
        repo_path = os.path.expanduser(request.repo_path)
        repo_path = Path(repo_path)
        
        # Create directory if it doesn't exist
        repo_path.mkdir(parents=True, exist_ok=True)
        
        logging.info(f"📂 Repository path: {repo_path}")
        
        # Try to authenticate with real API
        async with httpx.AsyncClient() as client:
            try:
                login_url = f"{request.api_url}/auth/login"
                logging.info(f"🔐 Attempting login to: {login_url}")
                logging.info(f"📧 Email: {request.email}")
                logging.info(f"🔑 Password length: {len(request.password)} chars")
                
                login_payload = {"email": request.email, "password": request.password}
                logging.info(f"📦 Payload: {login_payload}")
                
                response = await client.post(
                    login_url,
                    json=login_payload,
                    timeout=10.0
                )
                
                logging.info(f"📡 Login response status: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    token = data.get('access_token')
                    if not token:
                        raise HTTPException(status_code=500, detail="No access token in response")
                    logging.info(f"✅ Real authentication successful")
                    logging.info(f"🔑 Token: {token[:20]}...")
                else:
                    # Login failed - return error to user
                    error_detail = response.text
                    logging.error(f"❌ API login failed (status {response.status_code}): {error_detail}")
                    raise HTTPException(status_code=response.status_code, detail=f"Login failed: {error_detail}")
                    
            except HTTPException:
                raise  # Re-raise HTTP exceptions
            except Exception as api_error:
                # Connection error
                logging.error(f"❌ API connection failed: {type(api_error).__name__}: {api_error}")
                raise HTTPException(status_code=503, detail=f"Cannot connect to API: {str(api_error)}")
        
        # Create client with token
        state['client'] = BsmartClient(request.api_url, token)
        state['authenticated'] = True
        state['repo_path'] = str(repo_path)  # Store repo path
        
        # Initialize components
        state['queue'] = QueueManager(max_concurrent_tasks=3)
        
        agent_config = {
            'agents': {
                'aider_ollama': {
                    'enabled': True,
                    'model': 'deepseek-coder-v2:latest'
                }
            }
        }
        state['agent_pool'] = AgentPool(agent_config)
        state['router'] = TaskRouter(state['agent_pool'])
        
        logging.info(f"🎉 BeeSmart: AI Orchestrator initialized successfully")
        
        await broadcast_update({'type': 'login_success', 'authenticated': True})
        
        return {"success": True, "message": "Login successful", "repo_path": str(repo_path)}
        
    except Exception as e:
        logging.error(f"❌ Login failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/api/logout")
async def logout():
    """Logout and clear session."""
    try:
        # Stop processing if running
        if state.get('processing'):
            state['processing'] = False
            logging.info("⏹️ Stopped processing")
        
        # Clear state
        state['authenticated'] = False
        state['client'] = None
        state['selected_project'] = None
        state['queue'] = None
        state['agent_pool'] = None
        state['router'] = None
        state['repo_path'] = None
        
        logging.info("🚪 Logged out successfully")
        
        await broadcast_update({'type': 'logout_success', 'authenticated': False})
        
        return {"success": True, "message": "Logged out successfully"}
        
    except Exception as e:
        logging.error(f"❌ Logout failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/projects")
async def get_projects():
    """Get available projects."""
    logging.info("🔍 GET /api/projects called")
    logging.info(f"   Authenticated: {state.get('authenticated')}")
    logging.info(f"   Has client: {state.get('client') is not None}")
    
    if not state['authenticated']:
        logging.error("❌ Not authenticated")
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        # Try to get real projects from API
        if state.get('client'):
            logging.info("🌐 Attempting to fetch real projects from API...")
            projects = await state['client']._get_projects()
            logging.info(f"✅ Loaded {len(projects)} real projects from API")
            return {"projects": projects}
        else:
            logging.warning("⚠️ No client available")
    except Exception as e:
        logging.error(f"❌ Failed to get real projects: {type(e).__name__}: {e}")
        import traceback
        logging.error(f"   Traceback: {traceback.format_exc()}")
    
    # Fallback to mock data
    logging.info("📁 Using mock projects (fallback)")
    projects = [
        {"id": "1", "name": "Sistema de Vendas", "description": "Sistema principal"},
        {"id": "2", "name": "Portal Cliente", "description": "Portal web"},
        {"id": "3", "name": "API Gateway", "description": "Gateway de APIs"}
    ]
    return {"projects": projects}

@app.post("/api/select-project")
async def select_project(request: ProjectSelection):
    """Select project."""
    logging.info(f"📌 POST /api/select-project called")
    logging.info(f"   Project ID: {request.project_id}")
    logging.info(f"   Authenticated: {state.get('authenticated')}")
    
    if not state['authenticated']:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Get real projects from API
    try:
        if state.get('client'):
            logging.info("🌐 Fetching projects to find selected one...")
            projects = await state['client']._get_projects()
            
            # Find the selected project
            selected = None
            for project in projects:
                if str(project.get('id')) == str(request.project_id):
                    selected = project
                    break
            
            if not selected:
                logging.error(f"❌ Project not found: {request.project_id}")
                logging.error(f"   Available projects: {[p.get('id') for p in projects]}")
                raise HTTPException(status_code=404, detail="Project not found")
            
            state['selected_project'] = selected
            logging.info(f"✅ Project selected: {selected.get('name')}")
            
            await broadcast_update({
                'type': 'project_selected',
                'project': state['selected_project']
            })
            
            return {"success": True, "project": state['selected_project']}
        else:
            logging.error("❌ No client available")
            raise HTTPException(status_code=500, detail="Client not initialized")
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"❌ Error selecting project: {type(e).__name__}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/work-items")
async def get_work_items():
    """Get work items for selected project."""
    logging.info("🔍 GET /api/work-items called")
    logging.info(f"   Selected project: {state.get('selected_project')}")
    logging.info(f"   Has client: {state.get('client') is not None}")
    
    if not state['selected_project']:
        raise HTTPException(status_code=400, detail="No project selected")
    
    # Try to get real work items from API
    try:
        if state.get('client'):
            project_id = state['selected_project']['id']
            logging.info(f"🌐 Attempting to fetch work items for project {project_id}...")
            
            work_items = await state['client']._get_project_work_items(project_id)
            logging.info(f"✅ Loaded {len(work_items)} real work items from API")
            return {"work_items": work_items}
        else:
            logging.warning("⚠️ No client available")
    except Exception as e:
        logging.error(f"❌ Failed to get real work items: {type(e).__name__}: {e}")
        import traceback
        logging.error(f"   Traceback: {traceback.format_exc()}")
    
    # Fallback to mock data
    logging.info("📁 Using mock work items (fallback)")
    work_items = [
        {
            "id": "WI-1",
            "title": "Implementar autenticação",
            "description": "Implementar sistema de autenticação JWT",
            "status": "ready",
            "priority": "high",
            "complexity": "medium",
            "acceptance_criteria": [
                "Login com email/senha",
                "JWT token válido",
                "Logout funcional"
            ]
        },
        {
            "id": "WI-2",
            "title": "Corrigir bug no login",
            "description": "Corrigir erro de validação no formulário de login",
            "status": "ready",
            "priority": "critical",
            "complexity": "simple",
            "acceptance_criteria": [
                "Validação de email funciona",
                "Mensagens de erro claras"
            ]
        },
        {
            "id": "WI-3",
            "title": "Refatorar arquitetura",
            "description": "Refatorar arquitetura para microserviços",
            "status": "backlog",
            "priority": "medium",
            "complexity": "complex",
            "acceptance_criteria": [
                "Separar em microserviços",
                "API Gateway implementado",
                "Testes passando"
            ]
        }
    ]
    
    return {"work_items": work_items}

@app.post("/api/add-to-queue")
async def add_to_queue(request: WorkItemAction):
    """Add work items to processing queue."""
    if not state['queue']:
        raise HTTPException(status_code=400, detail="Queue not initialized")
    
    # Get work items (simplified)
    work_items = await get_work_items()
    requested_ids = [wi.id for wi in request.work_items]
    selected_items = [wi for wi in work_items['work_items'] if wi['id'] in requested_ids]
    
    added_count = 0
    for wi in selected_items:
        status = wi.get('status', '').lower()
        if status in ['done', 'completed', 'closed', 'resolved', 'pronto', 'concluído', 'concluido']:
            continue
            
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
            project_id=state['selected_project']["id"],
            title=wi["title"],
            description=wi["description"],
            priority=priority_map.get(wi["priority"], 3),
            complexity=complexity_map.get(wi["complexity"], TaskComplexity.MEDIUM),
            acceptance_criteria=wi.get("acceptance_criteria", [])
        )
        
        await state['queue'].add_task(task)
        added_count += 1
    
    await broadcast_update({
        'type': 'queue_updated',
        'stats': state['queue'].get_stats().to_dict()
    })
    
    return {"success": True, "added": added_count}

@app.get("/api/queue-status")
async def get_queue_status():
    """Get queue status."""
    if not state['queue']:
        return {"stats": None}
    
    stats = state['queue'].get_stats()
    return {"stats": stats.to_dict()}

@app.get("/api/agents-status")
async def get_agents_status():
    """Get agents status."""
    if not state['agent_pool']:
        return {"stats": None}
    
    stats = state['agent_pool'].get_stats()
    health = await state['agent_pool'].health_check_all()
    
    return {"stats": stats, "health": health}

@app.post("/api/start-processing")
async def start_processing():
    """Start processing work items."""
    if state['processing']:
        raise HTTPException(status_code=400, detail="Already processing")
    
    if not state['queue']:
        raise HTTPException(status_code=400, detail="Queue not initialized")
    
    stats = state['queue'].get_stats()
    if stats.pending_tasks == 0:
        raise HTTPException(status_code=400, detail="No tasks in queue")
    
    # TODO: Implement actual processing loop
    state['processing'] = True
    
    await broadcast_update({
        'type': 'processing_started',
        'processing': True
    })
    
    # Simulate processing (remove when real implementation is done)
    asyncio.create_task(simulate_processing())
    
    return {"success": True, "message": "Processing started"}

@app.post("/api/stop-processing")
async def stop_processing():
    """Stop processing."""
    state['processing'] = False
    
    await broadcast_update({
        'type': 'processing_stopped',
        'processing': False
    })
    
    return {"success": True, "message": "Processing stopped"}

# WebSocket for real-time updates
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connections.append(websocket)
    
    try:
        # Send initial state
        await websocket.send_json({
            'type': 'initial_state',
            'authenticated': state['authenticated'],
            'selected_project': state['selected_project'],
            'processing': state['processing']
        })
        
        while True:
            # Keep connection alive
            await websocket.receive_text()
            
    except WebSocketDisconnect:
        connections.remove(websocket)

async def broadcast_update(message: Dict[str, Any]):
    """Broadcast update to all connected clients."""
    if connections:
        for connection in connections.copy():
            try:
                await connection.send_json(message)
            except:
                connections.remove(connection)

async def simulate_processing():
    """Simulate processing for demo purposes."""
    while state['processing'] and state['queue']:
        stats = state['queue'].get_stats()
        if stats.pending_tasks == 0:
            state['processing'] = False
            await broadcast_update({
                'type': 'processing_completed',
                'processing': False
            })
            break
        
        # Simulate work
        await asyncio.sleep(5)
        
        # Update queue (simulate completion)
        await broadcast_update({
            'type': 'queue_updated',
            'stats': state['queue'].get_stats().to_dict()
        })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
