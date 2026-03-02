# 🎯 Próximos Passos - AI Orchestrator

## ✅ O Que Está Funcionando

1. **Infraestrutura Completa**
   - ✅ Estrutura de pacote Python correta
   - ✅ Servidor FastAPI rodando (porta 5010)
   - ✅ Interface web HTML completa
   - ✅ WebSocket para tempo real
   - ✅ API REST endpoints

2. **Interface Web**
   - ✅ Formulário de login
   - ✅ Seleção de projeto
   - ✅ Lista de work items
   - ✅ Dashboard com estatísticas
   - ✅ Controles de processamento

## 🔧 O Que Precisa Ser Implementado

### 1. Integração Real com Bsmart-ALM API

**Problema Atual:** Os dados de projetos e work items estão mockados no código.

**Solução Necessária:**

#### A. Atualizar endpoint `/api/login`

```python
@app.post("/api/login")
async def login(request: LoginRequest):
    try:
        # Criar cliente com credenciais reais
        state['client'] = BsmartClient(request.api_url, "temp-key")
        
        # TODO: Implementar autenticação real
        # Fazer login na API do Bsmart-ALM
        # Obter token de autenticação
        # Armazenar token no cliente
        
        state['authenticated'] = True
        # ... resto do código
```

#### B. Atualizar endpoint `/api/projects`

```python
@app.get("/api/projects")
async def get_projects():
    if not state['authenticated'] or not state['client']:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Buscar projetos reais da API
    projects = await state['client']._get_projects()
    
    return {"projects": projects}
```

#### C. Atualizar endpoint `/api/work-items`

```python
@app.get("/api/work-items")
async def get_work_items():
    if not state['selected_project'] or not state['client']:
        raise HTTPException(status_code=400, detail="No project selected")
    
    # Buscar work items reais da API
    work_items = await state['client']._get_project_work_items(
        state['selected_project']['id'],
        status='ready'
    )
    
    return {"work_items": work_items}
```

### 2. Adicionar Seleção de Tarefa Específica

**Requisito:** Ao selecionar um projeto, permitir selecionar uma tarefa específica para que seu texto entre no prompt.

**Implementação:**

#### A. Adicionar novo endpoint para buscar tarefa específica

```python
@app.get("/api/work-items/{work_item_id}")
async def get_work_item_detail(work_item_id: str):
    if not state['client']:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    # Buscar detalhes completos da tarefa
    work_item = await state['client'].get_work_item_context(work_item_id)
    
    return {"work_item": work_item}
```

#### B. Atualizar HTML para adicionar seleção de tarefa

Adicionar após a seleção de projeto:

```html
<!-- Task Selection -->
<div class="card hidden" id="taskSelectionSection">
    <h2>📝 Select Task</h2>
    <div class="form-group">
        <label>Select Task:</label>
        <select id="taskSelect" onchange="selectTask()">
            <option value="">-- Select Task --</option>
        </select>
    </div>
    <div id="selectedTask" class="hidden">
        <h3 id="taskTitle"></h3>
        <p id="taskDescription"></p>
        <div id="taskAcceptanceCriteria"></div>
    </div>
</div>
```

#### C. Adicionar JavaScript para carregar tarefas

```javascript
async function loadTasks() {
    try {
        const response = await fetch('/api/work-items');
        const data = await response.json();
        
        const select = document.getElementById('taskSelect');
        select.innerHTML = '<option value="">-- Select Task --</option>';
        
        data.work_items.forEach(task => {
            const option = document.createElement('option');
            option.value = task.id;
            option.textContent = task.title;
            select.appendChild(option);
        });
        
        document.getElementById('taskSelectionSection').classList.remove('hidden');
    } catch (error) {
        console.error('Failed to load tasks:', error);
    }
}

async function selectTask() {
    const taskId = document.getElementById('taskSelect').value;
    if (!taskId) return;
    
    try {
        const response = await fetch(`/api/work-items/${taskId}`);
        const data = await response.json();
        
        document.getElementById('selectedTask').classList.remove('hidden');
        document.getElementById('taskTitle').textContent = data.work_item.title;
        document.getElementById('taskDescription').textContent = data.work_item.description;
        
        // Mostrar acceptance criteria
        const criteriaDiv = document.getElementById('taskAcceptanceCriteria');
        criteriaDiv.innerHTML = '<h4>Acceptance Criteria:</h4><ul>';
        data.work_item.acceptance_criteria.forEach(criteria => {
            criteriaDiv.innerHTML += `<li>${criteria}</li>`;
        });
        criteriaDiv.innerHTML += '</ul>';
        
        // Armazenar tarefa selecionada
        selectedTask = data.work_item;
    } catch (error) {
        alert('Failed to select task: ' + error.message);
    }
}
```

### 3. Incluir Texto da Tarefa no Prompt

**Implementação:**

#### A. Atualizar Task model para incluir contexto completo

```python
# Em core/models.py
@dataclass
class Task:
    id: str
    work_item_id: str
    project_id: str
    title: str
    description: str
    priority: int
    complexity: TaskComplexity
    acceptance_criteria: List[str] = field(default_factory=list)
    specifications: Optional[str] = None  # Specs do projeto
    architecture: Optional[str] = None    # Arquitetura do projeto
    
    def get_prompt_context(self) -> str:
        """Generate context for AI prompt."""
        context = f"""
# Task: {self.title}

## Description
{self.description}

## Acceptance Criteria
"""
        for i, criteria in enumerate(self.acceptance_criteria, 1):
            context += f"{i}. {criteria}\n"
        
        if self.specifications:
            context += f"\n## Project Specifications\n{self.specifications}\n"
        
        if self.architecture:
            context += f"\n## Architecture\n{self.architecture}\n"
        
        return context
```

#### B. Usar contexto ao criar tarefa

```python
@app.post("/api/add-to-queue")
async def add_to_queue(request: WorkItemAction):
    # ... código existente ...
    
    for wi in selected_items:
        # Buscar contexto completo da tarefa
        full_context = await state['client'].get_work_item_context(wi['id'])
        
        task = Task(
            id=f"task-{wi['id']}",
            work_item_id=wi["id"],
            project_id=state['selected_project']["id"],
            title=wi["title"],
            description=wi["description"],
            priority=priority_map.get(wi["priority"], 3),
            complexity=complexity_map.get(wi["complexity"], TaskComplexity.MEDIUM),
            acceptance_criteria=full_context.get("acceptance_criteria", []),
            specifications=full_context.get("specifications"),
            architecture=full_context.get("architecture")
        )
        
        await state['queue'].add_task(task)
```

### 4. Implementar Loop de Processamento Real

**Implementação:**

```python
async def process_tasks():
    """Process tasks from queue using agents."""
    while state['processing'] and state['queue']:
        # Get next task
        task = await state['queue'].get_next_task()
        if not task:
            await asyncio.sleep(1)
            continue
        
        try:
            # Route task to appropriate agent
            agent = state['router'].route_task(task)
            
            # Get prompt context
            prompt = task.get_prompt_context()
            
            # Execute task with agent
            result = await agent.execute_task(task, prompt)
            
            # Update work item status
            if result.success:
                await state['client'].update_work_item_status(
                    task.work_item_id,
                    'in_review'
                )
                if result.pr_url:
                    await state['client'].add_pr_link(
                        task.work_item_id,
                        result.pr_url
                    )
            else:
                await state['client'].report_error(
                    task.work_item_id,
                    result.error,
                    agent.name
                )
            
            # Mark task as complete
            await state['queue'].complete_task(task.id, result)
            
        except Exception as e:
            logger.error(f"Error processing task: {e}")
            await state['queue'].fail_task(task.id, str(e))
        
        # Broadcast update
        await broadcast_update({
            'type': 'queue_updated',
            'stats': state['queue'].get_stats()
        })
```

## 📋 Checklist de Implementação

### Fase 1: Integração com API Real
- [ ] Implementar autenticação real no endpoint `/api/login`
- [ ] Buscar projetos reais da API do Bsmart-ALM
- [ ] Buscar work items reais da API
- [ ] Testar integração com API

### Fase 2: Seleção de Tarefa
- [ ] Adicionar endpoint para buscar detalhes da tarefa
- [ ] Atualizar HTML com seleção de tarefa
- [ ] Adicionar JavaScript para carregar e selecionar tarefas
- [ ] Mostrar acceptance criteria e especificações

### Fase 3: Contexto no Prompt
- [ ] Atualizar Task model com campos adicionais
- [ ] Implementar método `get_prompt_context()`
- [ ] Buscar contexto completo ao adicionar à fila
- [ ] Testar geração de prompt

### Fase 4: Processamento Real
- [ ] Implementar loop de processamento
- [ ] Integrar com agentes (Aider, Cursor, etc.)
- [ ] Atualizar status no Bsmart-ALM
- [ ] Adicionar comentários e links de PR

## 🚀 Como Continuar

### 1. Testar API do Bsmart-ALM

```bash
# Verificar se a API está rodando
curl http://localhost:8086/api/v1/projects

# Testar autenticação
curl -X POST http://localhost:8086/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@acme.com","password":"admin123"}'
```

### 2. Implementar Autenticação

Editar `services/ai_orchestrator/ai_orchestrator/web_ui.py`:

```python
@app.post("/api/login")
async def login(request: LoginRequest):
    try:
        # Fazer login real na API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{request.api_url}/auth/login",
                json={"email": request.email, "password": request.password}
            )
            response.raise_for_status()
            data = response.json()
            token = data['access_token']
        
        # Criar cliente com token real
        state['client'] = BsmartClient(request.api_url, token)
        state['authenticated'] = True
        
        # ... resto do código
```

### 3. Atualizar Busca de Projetos

```python
@app.get("/api/projects")
async def get_projects():
    if not state['authenticated'] or not state['client']:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        projects = await state['client']._get_projects()
        return {"projects": projects}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## 📝 Notas Importantes

1. **Autenticação:** O Bsmart-ALM usa JWT tokens. Você precisa fazer login primeiro e usar o token nas requisições subsequentes.

2. **Estrutura de Dados:** Verifique a estrutura exata dos dados retornados pela API do Bsmart-ALM (projetos, work items, etc.) e ajuste o código conforme necessário.

3. **Tratamento de Erros:** Adicione tratamento adequado de erros para todas as chamadas à API.

4. **Testes:** Teste cada endpoint individualmente antes de integrar tudo.

## 🎯 Resultado Final Esperado

Após implementar tudo:

1. Usuário faz login com credenciais reais
2. Sistema busca projetos reais do Bsmart-ALM
3. Usuário seleciona um projeto
4. Sistema busca tarefas reais daquele projeto
5. Usuário seleciona uma tarefa específica
6. Sistema mostra detalhes completos da tarefa
7. Usuário adiciona tarefa à fila
8. Sistema processa tarefa com agente
9. Agente recebe contexto completo (descrição, acceptance criteria, specs)
10. Agente executa tarefa e cria PR
11. Sistema atualiza status no Bsmart-ALM

**Acesse:** http://localhost:5010
