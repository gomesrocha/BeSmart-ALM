# 🧪 Guia de Testes - AI Orchestrator

## 📋 Pré-requisitos

### Setup Rápido
```bash
# 1. Navegar para o diretório
cd services/ai_orchestrator

# 2. Executar setup (instala uv se necessário e configura ambiente)
./setup.sh

# 3. Ativar ambiente virtual
source .venv/bin/activate
```

### 1. Instalar uv (manual, se preferir)
```bash
# Se ainda não tiver o uv instalado
curl -LsSf https://astral.sh/uv/install.sh | sh

# Verificar instalação
uv --version
```

### 2. Instalar Aider (opcional, mas recomendado)
```bash
pip install aider-chat

# Verificar instalação
aider --version
```

### 3. Instalar Ollama (opcional, para testes locais)
```bash
# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Mac
brew install ollama

# Baixar modelo
ollama pull codellama:13b
```

---

## 🚀 Setup Inicial

### 1. Criar Ambiente Virtual
```bash
cd services/ai_orchestrator

# Criar venv com uv
uv venv

# Ativar venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate  # Windows
```

### 2. Instalar Dependências
```bash
# Instalar pacote em modo desenvolvimento
uv pip install -e .

# Verificar instalação
python -c "import ai_orchestrator; print('✅ Instalação OK')"
```

---

## ✅ Testes de Componentes

### Teste 1: Imports Básicos
```bash
python << 'EOF'
# Testar imports dos módulos principais
try:
    from core import QueueManager, Task, TaskStatus, TaskComplexity
    print("✅ Core imports OK")
    
    from agents import AgentPool, AiderAgent, CodeAgent
    print("✅ Agents imports OK")
    
    from api import BsmartClient
    print("✅ API imports OK")
    
    print("\n🎉 Todos os imports funcionando!")
except Exception as e:
    print(f"❌ Erro: {e}")
EOF
```

### Teste 2: Queue Manager
```bash
python << 'EOF'
import asyncio
from core import QueueManager, Task, TaskStatus, TaskComplexity

async def test_queue():
    print("🧪 Testando Queue Manager...")
    
    # Criar queue
    queue = QueueManager(max_concurrent_tasks=3)
    
    # Criar tarefas de teste
    tasks = [
        Task(
            id=f'test-{i}',
            work_item_id=f'WI-{i}',
            project_id='proj-test',
            title=f'Test Task {i}',
            description=f'Description {i}',
            priority=i,
            complexity=TaskComplexity.SIMPLE
        )
        for i in range(5)
    ]
    
    # Adicionar tarefas
    for task in tasks:
        await queue.add_task(task)
    
    # Verificar estatísticas
    stats = queue.get_stats()
    print(f"✅ Tarefas na fila: {stats['pending_tasks']}")
    print(f"✅ Total: {stats['total_tasks']}")
    
    # Pegar próxima tarefa
    next_task = await queue.get_next_task()
    if next_task:
        print(f"✅ Próxima tarefa: {next_task.title} (prioridade: {next_task.priority})")
    
    print("\n🎉 Queue Manager funcionando!")

asyncio.run(test_queue())
EOF
```

### Teste 3: Task Router
```bash
python << 'EOF'
import asyncio
from core import TaskRouter, Task, TaskComplexity
from agents import AgentPool

async def test_router():
    print("🧪 Testando Task Router...")
    
    # Criar agent pool (vazio para teste)
    config = {'agents': {'aider_ollama': {'enabled': True}}}
    pool = AgentPool(config)
    
    # Criar router
    router = TaskRouter(pool)
    
    # Testar análise de complexidade
    work_items = [
        {
            'id': '1',
            'title': 'Fix typo',
            'description': 'Fix small typo in README'
        },
        {
            'id': '2',
            'title': 'Implement feature',
            'description': 'Implement new authentication feature with multiple files'
        },
        {
            'id': '3',
            'title': 'Refactor architecture',
            'description': 'Major refactor of the entire architecture with breaking changes'
        }
    ]
    
    for wi in work_items:
        complexity = router.analyze_complexity(wi)
        print(f"✅ '{wi['title']}' → {complexity.value}")
    
    print("\n🎉 Task Router funcionando!")

asyncio.run(test_router())
EOF
```

### Teste 4: Aider Agent Health Check
```bash
python << 'EOF'
import asyncio
from agents import AiderAgent

async def test_aider():
    print("🧪 Testando Aider Agent...")
    
    # Criar agente
    agent = AiderAgent('test-aider', {
        'model': 'gpt-4',
        'api_key': 'test-key'
    })
    
    # Health check
    is_healthy = await agent.health_check()
    
    if is_healthy:
        print("✅ Aider está instalado e funcionando!")
    else:
        print("⚠️  Aider não encontrado. Instale com: pip install aider-chat")
    
    # Testar disponibilidade
    print(f"✅ Agente disponível: {agent.is_available()}")
    
    print("\n🎉 Aider Agent testado!")

asyncio.run(test_aider())
EOF
```

### Teste 5: Agent Pool
```bash
python << 'EOF'
import asyncio
from agents import AgentPool

async def test_pool():
    print("🧪 Testando Agent Pool...")
    
    # Configuração de teste
    config = {
        'agents': {
            'aider_ollama': {
                'enabled': True,
                'model': 'codellama:13b',
                'base_url': 'http://localhost:11434'
            },
            'aider_grok': {
                'enabled': False,
                'model': 'grok-beta',
                'api_key': 'test-key'
            }
        }
    }
    
    # Criar pool
    pool = AgentPool(config)
    
    # Verificar agentes
    stats = pool.get_stats()
    print(f"✅ Total de agentes: {stats['total_agents']}")
    print(f"✅ Agentes disponíveis: {stats['available']}")
    
    # Listar agentes
    for name, info in stats['agents'].items():
        status = "✅ Disponível" if info['available'] else "⏳ Ocupado"
        print(f"   - {name}: {status}")
    
    # Health check
    print("\n🔍 Verificando saúde dos agentes...")
    health = await pool.health_check_all()
    for name, is_healthy in health.items():
        status = "✅" if is_healthy else "❌"
        print(f"   {status} {name}")
    
    print("\n🎉 Agent Pool funcionando!")

asyncio.run(test_pool())
EOF
```

### Teste 6: Bsmart Client (Mock)
```bash
python << 'EOF'
import asyncio
from api import BsmartClient

async def test_client():
    print("🧪 Testando Bsmart Client...")
    
    # Criar cliente (com URL fake para teste)
    client = BsmartClient(
        api_url='http://localhost:8086/api/v1',
        api_key='test-key'
    )
    
    print("✅ Cliente criado com sucesso")
    print(f"✅ API URL: {client.api_url}")
    
    # Fechar cliente
    await client.close()
    
    print("\n🎉 Bsmart Client testado!")

asyncio.run(test_client())
EOF
```

---

## 🔬 Teste Integrado Completo

### Script de Teste Completo
```bash
python << 'EOF'
import asyncio
from core import QueueManager, Task, TaskStatus, TaskComplexity, TaskRouter
from agents import AgentPool
from api import BsmartClient

async def test_integration():
    print("=" * 60)
    print("🧪 TESTE INTEGRADO DO AI ORCHESTRATOR")
    print("=" * 60)
    
    # 1. Setup
    print("\n1️⃣  Setup de componentes...")
    
    config = {
        'agents': {
            'aider_ollama': {
                'enabled': True,
                'model': 'codellama:13b'
            }
        }
    }
    
    queue = QueueManager(max_concurrent_tasks=3)
    pool = AgentPool(config)
    router = TaskRouter(pool)
    client = BsmartClient('http://localhost:8086/api/v1', 'test-key')
    
    print("   ✅ Queue Manager")
    print("   ✅ Agent Pool")
    print("   ✅ Task Router")
    print("   ✅ Bsmart Client")
    
    # 2. Criar tarefas de teste
    print("\n2️⃣  Criando tarefas de teste...")
    
    work_items = [
        {
            'id': 'WI-1',
            'title': 'Fix bug in login',
            'description': 'Small bug fix in authentication'
        },
        {
            'id': 'WI-2',
            'title': 'Implement new feature',
            'description': 'Implement complex feature with multiple files'
        }
    ]
    
    for wi in work_items:
        complexity = router.analyze_complexity(wi)
        task = Task(
            id=f"task-{wi['id']}",
            work_item_id=wi['id'],
            project_id='test-project',
            title=wi['title'],
            description=wi['description'],
            priority=5,
            complexity=complexity
        )
        await queue.add_task(task)
        print(f"   ✅ {wi['title']} ({complexity.value})")
    
    # 3. Verificar estatísticas
    print("\n3️⃣  Estatísticas da fila...")
    
    stats = queue.get_stats()
    print(f"   📊 Tarefas pendentes: {stats['pending_tasks']}")
    print(f"   📊 Total: {stats['total_tasks']}")
    
    # 4. Verificar agentes
    print("\n4️⃣  Verificando agentes...")
    
    agent_stats = pool.get_stats()
    print(f"   🤖 Total de agentes: {agent_stats['total_agents']}")
    print(f"   🤖 Disponíveis: {agent_stats['available']}")
    
    # 5. Simular seleção de agente
    print("\n5️⃣  Simulando seleção de agente...")
    
    next_task = await queue.get_next_task()
    if next_task:
        agent_name = router.select_agent(next_task)
        if agent_name:
            print(f"   ✅ Tarefa: {next_task.title}")
            print(f"   ✅ Agente selecionado: {agent_name}")
        else:
            print("   ⚠️  Nenhum agente disponível")
    
    # 6. Cleanup
    await client.close()
    
    print("\n" + "=" * 60)
    print("🎉 TESTE INTEGRADO COMPLETO!")
    print("=" * 60)
    print("\n✅ Todos os componentes implementados estão funcionando!")
    print("⏳ Faltam: Validadores, Orquestrador Principal, Monitoramento")

asyncio.run(test_integration())
EOF
```

---

## 📊 Verificar Instalação

### Script de Verificação Rápida
```bash
cd services/ai_orchestrator

python << 'EOF'
import sys

print("🔍 Verificando instalação do AI Orchestrator...\n")

# 1. Python version
print(f"✅ Python: {sys.version.split()[0]}")

# 2. Imports
try:
    from core import QueueManager
    print("✅ Core modules")
except:
    print("❌ Core modules")

try:
    from agents import AgentPool
    print("✅ Agent modules")
except:
    print("❌ Agent modules")

try:
    from api import BsmartClient
    print("✅ API modules")
except:
    print("❌ API modules")

# 3. Dependencies
try:
    import git
    print("✅ GitPython")
except:
    print("❌ GitPython (instale: uv pip install gitpython)")

try:
    import httpx
    print("✅ httpx")
except:
    print("❌ httpx (instale: uv pip install httpx)")

# 4. Aider
import subprocess
try:
    result = subprocess.run(['aider', '--version'], capture_output=True)
    if result.returncode == 0:
        print("✅ Aider CLI")
    else:
        print("⚠️  Aider CLI (instale: pip install aider-chat)")
except:
    print("⚠️  Aider CLI (instale: pip install aider-chat)")

# 5. Ollama (opcional)
try:
    result = subprocess.run(['ollama', '--version'], capture_output=True)
    if result.returncode == 0:
        print("✅ Ollama (opcional)")
    else:
        print("ℹ️  Ollama não instalado (opcional)")
except:
    print("ℹ️  Ollama não instalado (opcional)")

print("\n🎉 Verificação completa!")
EOF
```

---

## 🐛 Troubleshooting

### Problema: Import Error
```bash
# Reinstalar dependências
cd services/ai_orchestrator
uv pip install -e . --force-reinstall
```

### Problema: Aider não encontrado
```bash
# Instalar Aider
pip install aider-chat

# Ou com pipx
pipx install aider-chat
```

### Problema: Módulos não encontrados
```bash
# Verificar se está no venv correto
which python

# Deve mostrar: .../ai_orchestrator/.venv/bin/python
```

---

## 📝 Próximos Testes (Quando Implementado)

### Validadores
```bash
# Quando implementado
python -c "from validators import ContinueValidator; print('✅ Validators OK')"
```

### Orquestrador Principal
```bash
# Quando implementado
python -m ai_orchestrator --help
```

### Testes Unitários
```bash
# Quando implementado
pytest tests/
```

---

## 🎯 Resumo

### O Que Pode Ser Testado Agora (60%)
- ✅ Core models e data structures
- ✅ Queue Manager com prioridade
- ✅ Task Router com análise de complexidade
- ✅ Agent Pool e Aider Agent
- ✅ Bsmart Client (estrutura)
- ✅ Git Manager (estrutura)

### O Que Ainda Não Pode Ser Testado (40%)
- ⏳ Validadores (Continue, Security, Tests)
- ⏳ Orquestrador principal
- ⏳ Loops de processamento
- ⏳ Execução end-to-end completa

---

## 🚀 Teste Rápido (1 Minuto)

```bash
cd services/ai_orchestrator
uv venv && source .venv/bin/activate
uv pip install -e .
python -c "from core import QueueManager; from agents import AgentPool; from api import BsmartClient; print('🎉 AI Orchestrator OK!')"
```

Se este comando funcionar, a instalação está correta!

---

**Última atualização**: 27/02/2026  
**Status**: Testes para componentes implementados (60%)
