# 🎯 Tarefas Pendentes - Bsmart Orchestrator

## 📋 Problemas Identificados

### 1. Nome do Sistema
❌ **Atual:** "AI Orchestrator"  
✅ **Deve ser:** "Bsmart Orchestrator"

**Onde mudar:**
- HTML (título, headers)
- Mensagens de log
- Documentação

### 2. Projetos Mockados
❌ **Problema:** Sistema mostra projetos fictícios (Sistema de Vendas, Portal Cliente, API Gateway)  
✅ **Solução:** Buscar projetos reais da API do Bsmart-ALM

**Endpoint da API:** `GET http://localhost:8086/api/v1/projects`

### 3. Work Items Mockados
❌ **Problema:** Work items não vêm do Bsmart-ALM  
✅ **Solução:** Buscar work items reais da API

**Endpoint da API:** `GET http://localhost:8086/api/v1/projects/{project_id}/work-items`

### 4. Processamento Simulado
❌ **Problema:** Não está claro onde o processamento acontece  
✅ **Solução:** 
- Mostrar logs detalhados
- Indicar repositório/pasta sendo processado
- Mostrar progresso real

**Atualmente:** Apenas simula processamento sem fazer nada real

## 🔧 Implementação

### Tarefa 1: Renomear para "Bsmart Orchestrator"

Arquivos a modificar:
- `ai_orchestrator/static/index.html` - Título e headers
- `start_web.py` - Mensagens de log
- Todos os arquivos de documentação

### Tarefa 2: Integrar com API Real do Bsmart-ALM

#### A. Buscar Projetos Reais

```python
@app.get("/api/projects")
async def get_projects():
    if not state['authenticated'] or not state['client']:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    try:
        # Buscar projetos reais da API
        projects = await state['client']._get_projects()
        return {"projects": projects}
    except Exception as e:
        logger.error(f"Failed to get projects: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

#### B. Buscar Work Items Reais

```python
@app.get("/api/work-items")
async def get_work_items():
    if not state['selected_project'] or not state['client']:
        raise HTTPException(status_code=400, detail="No project selected")
    
    try:
        # Buscar work items reais
        work_items = await state['client']._get_project_work_items(
            state['selected_project']['id'],
            status='ready'
        )
        return {"work_items": work_items}
    except Exception as e:
        logger.error(f"Failed to get work items: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

### Tarefa 3: Implementar Processamento Real

#### A. Adicionar Logs Detalhados

```python
async def process_tasks():
    """Process tasks from queue using agents."""
    logger.info("🚀 Starting task processing...")
    
    while state['processing'] and state['queue']:
        task = await state['queue'].get_next_task()
        if not task:
            await asyncio.sleep(1)
            continue
        
        logger.info(f"📝 Processing task: {task.title}")
        logger.info(f"📁 Project: {task.project_id}")
        logger.info(f"🎯 Work Item: {task.work_item_id}")
        
        try:
            # Route to agent
            agent = state['router'].route_task(task)
            logger.info(f"🤖 Using agent: {agent.name}")
            
            # Get repository path
            repo_path = f"/path/to/repos/{task.project_id}"
            logger.info(f"📂 Repository: {repo_path}")
            
            # Execute
            result = await agent.execute_task(task)
            
            if result.success:
                logger.info(f"✅ Task completed successfully")
                if result.pr_url:
                    logger.info(f"🔗 PR created: {result.pr_url}")
            else:
                logger.error(f"❌ Task failed: {result.error}")
                
        except Exception as e:
            logger.error(f"💥 Error processing task: {e}")
```

#### B. Adicionar Indicadores Visuais na Interface

Adicionar ao HTML:
```html
<div id="processingDetails" class="hidden">
    <h3>Processing Details</h3>
    <div id="currentTask"></div>
    <div id="currentRepo"></div>
    <div id="currentAgent"></div>
    <div id="processingLogs"></div>
</div>
```

#### C. Enviar Updates via WebSocket

```python
await broadcast_update({
    'type': 'task_processing',
    'task': {
        'id': task.id,
        'title': task.title,
        'project': task.project_id,
        'repository': repo_path,
        'agent': agent.name
    }
})
```

## 📝 Status Atual

### O Que Está Funcionando
- ✅ Servidor rodando
- ✅ Interface web carregando
- ✅ Login (mockado)
- ✅ Adicionar à fila
- ✅ Iniciar processamento (simulado)

### O Que NÃO Está Funcionando
- ❌ Projetos vêm mockados
- ❌ Work items vêm mockados
- ❌ Processamento não faz nada real
- ❌ Não mostra onde está processando
- ❌ Não há logs visíveis

## 🎯 Próximos Passos

1. ✅ Renomear para "Bsmart Orchestrator"
2. ✅ Implementar busca real de projetos
3. ✅ Implementar busca real de work items
4. ✅ Adicionar logs detalhados
5. ✅ Mostrar progresso na interface
6. ⏳ Implementar processamento real com agentes

## 💡 Nota Importante

**Atualmente o processamento é SIMULADO.** Ele apenas:
- Espera 5 segundos
- Atualiza estatísticas
- Não executa nenhum agente real
- Não modifica nenhum código
- Não cria PRs

Para implementar processamento real, é necessário:
1. Configurar repositório Git do projeto
2. Configurar agente (Aider, Cursor, etc.)
3. Passar contexto completo da tarefa
4. Executar agente no repositório
5. Criar PR com mudanças
6. Atualizar status no Bsmart-ALM

## 🚀 Quando Estiver Pronto

Após corrigir tudo isso, me avise para implementar a próxima demanda do frontend!
