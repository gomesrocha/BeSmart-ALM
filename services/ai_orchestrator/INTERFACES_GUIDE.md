# 🖥️ Guia das Interfaces - AI Orchestrator

## 📋 Interfaces Disponíveis

O AI Orchestrator oferece **duas interfaces** para gerenciar o processo de automação:

1. **CLI Interativo** - Interface de linha de comando
2. **Web UI** - Interface web visual

---

## 🖥️ CLI Interativo

### Como Usar

```bash
cd services/ai_orchestrator

# Setup (primeira vez)
uv venv
source .venv/bin/activate
uv pip install -e .

# Iniciar CLI
python start_cli.py
```

### Funcionalidades

```
🤖 Bsmart AI Orchestrator
════════════════════════════════════════════════════════════
Status: ❌ Not authenticated

  1. 🔑 Login to Bsmart-ALM
  2. 📁 Select Project
  3. 🔍 View Work Items
  4. 🤖 View Agents Status
  5. ▶️  Start Processing
  6. 📊 View Queue Status
  7. ⚙️  Configuration
  8. 🚪 Exit
```

### Fluxo de Uso

1. **Login** (Opção 1)
   - URL da API: `http://localhost:8086/api/v1`
   - Email: `admin@acme.com`
   - Senha: `admin123`

2. **Selecionar Projeto** (Opção 2)
   - Lista projetos disponíveis
   - Escolha por ID

3. **Ver Work Items** (Opção 3)
   - Mostra work items "ready"
   - Opção de adicionar à fila

4. **Ver Status dos Agentes** (Opção 4)
   - Status de cada agente
   - Health check

5. **Iniciar Processamento** (Opção 5)
   - Processa work items na fila
   - ⚠️ Ainda não implementado

---

## 🌐 Web UI

### Como Usar

```bash
cd services/ai_orchestrator

# Setup (primeira vez)
uv venv
source .venv/bin/activate
uv pip install -e .

# Iniciar Web UI
python start_web.py
```

### Acessar

```
🌐 http://localhost:8080
```

### Interface Visual

#### 1. Tela de Login
```
┌─────────────────────────────────────────┐
│ 🤖 AI Orchestrator                      │
│ Autonomous coding agent orchestration   │
├─────────────────────────────────────────┤
│ 🔑 Login to Bsmart-ALM                  │
│                                         │
│ API URL: [http://localhost:8086/api/v1] │
│ Email:   [admin@acme.com              ] │
│ Password:[***********                 ] │
│                                         │
│ [Login]                                 │
└─────────────────────────────────────────┘
```

#### 2. Dashboard Principal
```
┌─────────────────────────────────────────┐
│ 🤖 AI Orchestrator                      │
├─────────────────────────────────────────┤
│ Status: ● Connected                     │
├─────────────────────────────────────────┤
│ 📁 Project Selection                    │
│ Select Project: [Sistema de Vendas ▼]   │
│                                         │
│ Sistema de Vendas                       │
│ Sistema principal da empresa            │
├─────────────────────────────────────────┤
│ 🔍 Work Items                           │
│ [Load Work Items]                       │
│                                         │
│ ☐ WI-1: Implementar autenticação [HIGH] │
│ ☐ WI-2: Corrigir bug no login [CRITICAL]│
│                                         │
│ [Add Selected to Queue]                 │
├─────────────────────────────────────────┤
│ 📊 Queue Status    │ 🤖 Agents Status   │
│ Pending:    2      │ aider_ollama: ✅   │
│ In Progress: 0     │ Available          │
│ Completed:   0     │ Healthy: 💚        │
│ Failed:      0     │                    │
├─────────────────────────────────────────┤
│ ▶️ Processing Controls                   │
│ [Start Processing] [Stop Processing]    │
└─────────────────────────────────────────┘
```

### Funcionalidades Web

1. **Login Visual**
   - Formulário intuitivo
   - Validação em tempo real

2. **Seleção de Projeto**
   - Dropdown com projetos
   - Informações do projeto selecionado

3. **Gestão de Work Items**
   - Lista visual com checkboxes
   - Cores por prioridade
   - Status visual

4. **Dashboard em Tempo Real**
   - WebSocket para atualizações
   - Estatísticas da fila
   - Status dos agentes

5. **Controles de Processamento**
   - Botões Start/Stop
   - Indicador visual de processamento

---

## 🔄 Fluxo Completo

### 1. Preparação
```bash
# Terminal 1: Iniciar Bsmart-ALM
./start_bsmart.sh

# Terminal 2: Iniciar AI Orchestrator
cd services/ai_orchestrator
python start_web.py  # ou start_cli.py
```

### 2. Configuração
1. **Login**
   - URL: `http://localhost:8086/api/v1`
   - Credenciais do Bsmart-ALM

2. **Selecionar Projeto**
   - Escolher projeto com work items "ready"

3. **Carregar Work Items**
   - Ver work items disponíveis
   - Selecionar os que deseja automatizar

### 3. Processamento
1. **Adicionar à Fila**
   - Work items vão para fila de processamento
   - Análise automática de complexidade

2. **Iniciar Processamento**
   - Agentes começam a trabalhar
   - Monitoramento em tempo real

3. **Acompanhar Progresso**
   - Ver status da fila
   - Verificar saúde dos agentes
   - Receber atualizações automáticas

---

## 🎯 Diferenças entre Interfaces

| Funcionalidade | CLI | Web UI |
|----------------|-----|--------|
| Login | ✅ Interativo | ✅ Formulário |
| Seleção de Projeto | ✅ Lista numerada | ✅ Dropdown |
| Work Items | ✅ Tabela | ✅ Visual com checkboxes |
| Queue Status | ✅ Estatísticas | ✅ Dashboard |
| Agents Status | ✅ Tabela + Health | ✅ Cards + Health |
| Tempo Real | ❌ Manual | ✅ WebSocket |
| Processamento | ⚠️ Simulado | ⚠️ Simulado |
| Facilidade | 🔧 Técnico | 👥 Usuário |

---

## 🚀 Exemplos de Uso

### Cenário 1: Desenvolvedor Técnico
```bash
# Prefere CLI para automação
python start_cli.py

# Fluxo rápido
1 → admin@acme.com → admin123
2 → 1 (Sistema de Vendas)
3 → y (adicionar à fila)
5 → y (iniciar processamento)
```

### Cenário 2: Product Manager
```bash
# Prefere interface visual
python start_web.py

# Abre navegador em http://localhost:8080
# Interface visual intuitiva
# Cliques e seleções visuais
```

### Cenário 3: Automação CI/CD
```bash
# Usar CLI em scripts
python start_cli.py --config production.yaml --auto-process
```

---

## 📊 Monitoramento

### CLI - Visualização de Status
```
📊 Queue Status
════════════════════════════════════════
Pending:    5
In Progress: 2
Completed:   10
Failed:      1
Total:       18
Success Rate: 90.9%
```

### Web UI - Dashboard Visual
- Gráficos em tempo real
- Cores indicativas
- Atualização automática via WebSocket
- Histórico de processamento

---

## ⚙️ Configuração

### Arquivo de Configuração
```yaml
# config.yaml
api:
  url: "http://localhost:8086/api/v1"
  timeout: 30

queue:
  max_concurrent_tasks: 3
  retry_attempts: 3
  retry_delay: 60

agents:
  aider_ollama:
    enabled: true
    model: "codellama:13b"
    max_tokens: 4096
```

### Variáveis de Ambiente
```bash
export BSMART_API_URL="http://localhost:8086/api/v1"
export BSMART_EMAIL="admin@acme.com"
export BSMART_PASSWORD="admin123"
export ORCHESTRATOR_PORT=8080
```

---

## 🔧 Troubleshooting

### CLI não inicia
```bash
# Verificar dependências
uv pip list | grep -E "click|rich"

# Reinstalar
uv pip install -e . --force-reinstall
```

### Web UI não conecta
```bash
# Verificar porta
lsof -i :8080

# Testar API
curl http://localhost:8086/api/v1/health
```

### Agentes não respondem
```bash
# Verificar Ollama
ollama list
ollama ps

# Testar modelo
ollama run codellama:13b "test"
```

---

## 📝 Próximos Passos

### Implementações Pendentes

1. **Loop de Processamento Real**
   - Integrar com agentes
   - Executar work items
   - Atualizar status no Bsmart-ALM

2. **Autenticação Real**
   - Implementar login via API
   - Gerenciar tokens
   - Refresh automático

3. **Persistência**
   - Salvar estado da fila
   - Histórico de execuções
   - Logs detalhados

4. **Notificações**
   - Email ao completar
   - Slack/Discord webhooks
   - Alertas de erro

---

## 🎓 Recursos Adicionais

- [README.md](README.md) - Visão geral do projeto
- [GUIA_TESTES.md](GUIA_TESTES.md) - Como testar componentes
- [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) - Status da implementação
- [config.yaml](config.yaml) - Configuração de exemplo
