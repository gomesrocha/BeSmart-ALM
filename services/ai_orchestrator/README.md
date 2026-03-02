# Bsmart AI Orchestrator

Orquestrador autônomo que consome work items do Bsmart-ALM, distribui tarefas para agentes de coding AI (Aider, OpenHands), executa validações com ferramentas de qualidade, e atualiza o status das tarefas automaticamente ao fazer commit/push no Git.

## Funcionalidades

- 🤖 **Múltiplos Agentes de IA**: Aider (Ollama, Grok, Gemini) e OpenHands
- 📋 **Consumo Automático**: Busca work items "Ready" do Bsmart-ALM
- 🎯 **Roteamento Inteligente**: Seleciona agente baseado na complexidade
- ✅ **Validação Automática**: Continue, Security Checks, Testes
- 🔄 **Git Automático**: Commit, push e criação de PR
- 📊 **Monitoramento**: Logs estruturados e métricas
- 🔁 **Retry Logic**: Tentativas automáticas em caso de falha

## Instalação

### Pré-requisitos

- Python 3.11+
- uv (gerenciador de pacotes Python)
- Git
- Docker (para OpenHands)
- Aider CLI
- Ollama (opcional, para modelos locais)

### Setup com uv

```bash
# Instalar uv se ainda não tiver
curl -LsSf https://astral.sh/uv/install.sh | sh

# Criar ambiente virtual e instalar dependências
cd services/ai_orchestrator
uv venv
source .venv/bin/activate  # Linux/Mac
# ou
.venv\Scripts\activate  # Windows

# Instalar dependências
uv pip install -e .

# Instalar dependências de desenvolvimento
uv pip install -e ".[dev]"
```

### Instalar Aider

```bash
# Via pip
pip install aider-chat

# Ou via pipx
pipx install aider-chat
```

### Instalar Ollama (Opcional)

```bash
# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Mac
brew install ollama

# Baixar modelo
ollama pull codellama:13b
```

## Configuração

Copie o arquivo de configuração e ajuste conforme necessário:

```bash
cp config.yaml config.local.yaml
```

Edite `config.local.yaml` e configure:

1. **Bsmart-ALM API**:
   ```yaml
   bsmart_alm:
     api_url: "http://localhost:8086/api/v1"
     api_key: "your-api-key"
   ```

2. **Git Provider**:
   ```yaml
   git:
     provider: "github"  # ou "gitlab"
     api_token: "your-github-token"
   ```

3. **Agentes**:
   ```yaml
   agents:
     aider_ollama:
       enabled: true
     aider_grok:
       enabled: true
       api_key: "your-xai-key"
   ```

### Variáveis de Ambiente

Crie um arquivo `.env`:

```bash
BSMART_API_KEY=your-bsmart-api-key
GIT_API_TOKEN=your-github-token
XAI_API_KEY=your-xai-key
GOOGLE_API_KEY=your-google-key
OPENAI_API_KEY=your-openai-key
```

## Uso

### 🖥️ Interfaces Disponíveis

O AI Orchestrator oferece **duas interfaces** para gerenciamento:

#### 1. Web UI (Recomendado)
```bash
python start_web.py
# Acesse: http://localhost:8080
```

Interface visual com:
- Dashboard em tempo real
- Gestão de work items
- Monitoramento de agentes
- Controles de processamento

#### 2. CLI Interativo
```bash
python start_cli.py
```

Interface de linha de comando com menu interativo.

📖 **Guia Completo**: Veja [INTERFACES_GUIDE.md](INTERFACES_GUIDE.md) para detalhes.

### Executar Orquestrador (Modo Daemon)

```bash
# Com uv
uv run python -m ai_orchestrator

# Ou ativando o venv
source .venv/bin/activate
python -m ai_orchestrator
```

### Executar com Docker

```bash
docker-compose up -d
```

## Arquitetura

```
ai_orchestrator/
├── core/              # Componentes principais
│   ├── models.py      # Modelos de dados
│   ├── queue_manager.py  # Gerenciamento de fila
│   └── task_router.py    # Roteamento de tarefas
├── agents/            # Agentes de coding
│   ├── base.py        # Interface base
│   ├── aider.py       # Agente Aider
│   └── openhands.py   # Agente OpenHands
├── validators/        # Pipeline de validação
│   ├── continue.py    # Validador Continue
│   ├── security.py    # Security checks
│   └── tests.py       # Test runner
├── api/               # Integrações externas
│   ├── bsmart_client.py  # Cliente Bsmart-ALM
│   └── git_manager.py    # Gerenciamento Git
└── orchestrator.py    # Orquestrador principal
```

## Fluxo de Trabalho

1. **Poll**: Busca work items "Ready" do Bsmart-ALM
2. **Analyze**: Analisa complexidade da tarefa
3. **Route**: Seleciona agente apropriado
4. **Execute**: Agente implementa a tarefa
5. **Validate**: Executa pipeline de validação
6. **Commit**: Faz commit e push das mudanças
7. **PR**: Cria pull request
8. **Update**: Atualiza status no Bsmart-ALM

## Desenvolvimento

### Executar Testes

```bash
# Todos os testes
uv run pytest

# Com cobertura
uv run pytest --cov=ai_orchestrator --cov-report=html

# Testes específicos
uv run pytest tests/test_queue_manager.py
```

### Linting e Formatação

```bash
# Formatar código
uv run black .

# Lint
uv run ruff check .

# Type checking
uv run mypy .
```

## Monitoramento

### Logs

Logs são escritos em formato JSON estruturado:

```bash
tail -f logs/orchestrator.log | jq
```

### Métricas

Métricas Prometheus disponíveis em `http://localhost:9090/metrics`

### Health Check

```bash
curl http://localhost:8080/health
```

## Troubleshooting

### Agente não disponível

Verifique se o agente está configurado e habilitado em `config.yaml`.

### Erro de autenticação

Verifique se as API keys estão corretas no `.env`.

### Timeout em tarefas

Aumente o timeout em `config.yaml`:

```yaml
validation:
  tests:
    timeout: 600  # 10 minutos
```

## Contribuindo

1. Fork o repositório
2. Crie uma branch para sua feature
3. Faça commit das mudanças
4. Push para a branch
5. Abra um Pull Request

## Licença

MIT License - veja LICENSE para detalhes.
