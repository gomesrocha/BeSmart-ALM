# ✅ Estrutura de Pacote Corrigida

## Problema Original

```
ImportError: attempted relative import beyond top-level package
```

## Causa Raiz

A estrutura do projeto estava incorreta. Os módulos (`agents`, `api`, `core`, `validators`) estavam no nível raiz, mas o Python precisa de uma estrutura de pacote adequada para imports relativos funcionarem.

## Solução Aplicada

### 1. Reestruturação do Projeto

**Antes:**
```
services/ai_orchestrator/
├── agents/
├── api/
├── core/
├── validators/
├── web_ui.py
├── cli.py
└── pyproject.toml
```

**Depois:**
```
services/ai_orchestrator/
├── ai_orchestrator/          # Pacote principal
│   ├── __init__.py
│   ├── agents/
│   ├── api/
│   ├── core/
│   ├── validators/
│   ├── web_ui.py
│   └── cli.py
├── start_web.py              # Script de inicialização
├── start_cli.py              # Script de inicialização
└── pyproject.toml
```

### 2. Atualização dos Imports

**Antes (imports relativos):**
```python
from api import BsmartClient
from core import QueueManager
from agents import AgentPool
```

**Depois (imports absolutos):**
```python
from ai_orchestrator.api import BsmartClient
from ai_orchestrator.core import QueueManager
from ai_orchestrator.agents import AgentPool
```

### 3. Atualização do pyproject.toml

```toml
[tool.hatch.build.targets.wheel]
packages = ["ai_orchestrator"]  # Antes: ["agents", "api", "core", "validators"]
```

### 4. Scripts de Inicialização

Os scripts agora usam o nome completo do módulo:

**start_web.py:**
```python
uvicorn.run("ai_orchestrator.web_ui:app", ...)
```

**start_cli.py:**
```python
from ai_orchestrator.cli import main
```

## Como Usar Agora

### Opção 1: Usar uv run (Recomendado)

```bash
cd services/ai_orchestrator

# Primeira vez - setup
./setup.sh

# Iniciar Web UI
uv run python start_web.py

# Iniciar CLI
uv run python start_cli.py
```

### Opção 2: Ativar ambiente virtual

```bash
cd services/ai_orchestrator

# Primeira vez - setup
./setup.sh

# Ativar ambiente
source .venv/bin/activate

# Iniciar
python start_web.py  # ou start_cli.py
```

### Se já tinha ambiente criado

```bash
cd services/ai_orchestrator

# Reinstalar com nova estrutura
./reinstall.sh

# Usar
uv run python start_web.py
```

## Arquivos Modificados

1. ✅ Estrutura de diretórios reorganizada
2. ✅ `ai_orchestrator/__init__.py` - Criado
3. ✅ `ai_orchestrator/web_ui.py` - Imports atualizados
4. ✅ `ai_orchestrator/cli.py` - Imports atualizados
5. ✅ `start_web.py` - Atualizado para usar módulo correto
6. ✅ `start_cli.py` - Atualizado para usar módulo correto
7. ✅ `pyproject.toml` - Configuração de pacote corrigida
8. ✅ `setup.sh` - Atualizado com instruções corretas
9. ✅ `reinstall.sh` - Novo script para reinstalação

## Teste Rápido

```bash
# Limpar ambiente anterior
cd services/ai_orchestrator
rm -rf .venv __pycache__ ai_orchestrator/__pycache__

# Setup completo
./setup.sh

# Testar Web UI
uv run python start_web.py
# Abrir http://localhost:8080

# Em outro terminal, testar CLI
cd services/ai_orchestrator
uv run python start_cli.py
```

## Por que usar `uv run`?

O comando `uv run` garante que:
1. O ambiente virtual está ativado
2. As dependências estão instaladas
3. O PYTHONPATH está configurado corretamente
4. O pacote está instalado em modo editable

## Vantagens da Nova Estrutura

1. ✅ Imports funcionam corretamente
2. ✅ Estrutura de pacote Python padrão
3. ✅ Compatível com ferramentas de build
4. ✅ Fácil de distribuir como pacote
5. ✅ Suporta imports absolutos e relativos
6. ✅ Funciona com IDEs e linters

## Status

✅ Estrutura corrigida
✅ Imports funcionando
✅ Scripts atualizados
✅ Documentação atualizada
✅ Pronto para uso com `uv run`
