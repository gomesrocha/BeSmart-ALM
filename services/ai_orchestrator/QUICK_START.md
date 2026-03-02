# 🚀 Quick Start - AI Orchestrator

## ⚡ Início Rápido (2 minutos)

### Opção 1: Usar uv run (Recomendado)
```bash
cd services/ai_orchestrator

# Setup automático (primeira vez)
./setup.sh

# Iniciar Web UI
uv run python start_web.py

# Ou iniciar CLI
uv run python start_cli.py
```

### Opção 2: Ativar ambiente virtual
```bash
cd services/ai_orchestrator

# Setup (primeira vez)
./setup.sh

# Ativar ambiente
source .venv/bin/activate

# Iniciar
python start_web.py  # ou start_cli.py
```

### 2. Escolher Interface

#### Opção A: Web UI (Recomendado)
```bash
python start_web.py
```
Abra: http://localhost:8080

#### Opção B: CLI Interativo
```bash
python start_cli.py
```

### 3. Primeiro Uso

**Login:**
- API URL: `http://localhost:8086/api/v1`
- Email: `admin@acme.com`
- Password: `admin123`

**Selecionar Projeto:**
- Escolha "Sistema de Vendas" (ou outro disponível)

**Carregar Work Items:**
- Clique em "Load Work Items" (Web) ou opção 3 (CLI)

**Adicionar à Fila:**
- Selecione work items desejados
- Clique em "Add to Queue"

**Iniciar Processamento:**
- Clique em "Start Processing" (Web) ou opção 5 (CLI)

## 📋 Pré-requisitos

### Obrigatórios
- Python 3.11+
- uv (gerenciador de pacotes)

### Opcionais (para funcionalidade completa)
- Bsmart-ALM rodando (http://localhost:8086)
- Ollama com modelo instalado
- Aider CLI instalado
- Git configurado

## 🔧 Instalação de Dependências Opcionais

### Instalar Ollama
```bash
# Linux
curl -fsSL https://ollama.com/install.sh | sh

# Mac
brew install ollama

# Baixar modelo
ollama pull codellama:13b
```

### Instalar Aider
```bash
pip install aider-chat
# ou
pipx install aider-chat
```

### Verificar Instalações
```bash
# Verificar Ollama
ollama list

# Verificar Aider
aider --version

# Verificar Git
git --version
```

## 🎯 Casos de Uso

### Caso 1: Testar Interface
```bash
# Apenas testar a interface sem processar
python start_web.py
# Navegar pela interface, ver work items, etc.
```

### Caso 2: Processar Work Items (Simulado)
```bash
# Iniciar Web UI
python start_web.py

# 1. Login
# 2. Selecionar projeto
# 3. Carregar work items
# 4. Adicionar à fila
# 5. Iniciar processamento (simulado)
```

### Caso 3: Automação via CLI
```bash
# Usar CLI para automação
python start_cli.py

# Seguir menu:
# 1 → Login
# 2 → Selecionar projeto
# 3 → Ver work items → Adicionar à fila
# 5 → Iniciar processamento
```

## 📊 Verificar Status

### Via Web UI
- Dashboard mostra estatísticas em tempo real
- WebSocket atualiza automaticamente

### Via CLI
```bash
# Opção 6: View Queue Status
# Opção 4: View Agents Status
```

## 🐛 Troubleshooting

### Erro: "Module not found"
```bash
# Reinstalar dependências
uv pip install -e . --force-reinstall
```

### Erro: "Port 8080 already in use"
```bash
# Verificar processo usando a porta
lsof -i :8080

# Matar processo
kill -9 <PID>

# Ou usar outra porta
# Editar start_web.py e mudar port=8080
```

### Erro: "Cannot connect to Bsmart-ALM"
```bash
# Verificar se Bsmart-ALM está rodando
curl http://localhost:8086/api/v1/health

# Iniciar Bsmart-ALM
cd ../..
./start_bsmart.sh
```

### CLI não mostra cores
```bash
# Instalar Rich
uv pip install rich

# Verificar terminal suporta cores
echo $TERM
```

## 📚 Próximos Passos

Depois de testar as interfaces:

1. **Ler Documentação Completa**
   - [INTERFACES_GUIDE.md](INTERFACES_GUIDE.md) - Guia detalhado
   - [README.md](README.md) - Documentação principal
   - [GUIA_TESTES.md](GUIA_TESTES.md) - Como testar

2. **Configurar Agentes**
   - Editar `config.yaml`
   - Configurar API keys
   - Habilitar agentes desejados

3. **Testar Componentes**
   - Seguir [GUIA_TESTES.md](GUIA_TESTES.md)
   - Testar cada componente individualmente

4. **Implementar Funcionalidades**
   - Ver [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md)
   - Contribuir com componentes pendentes

## 🎓 Recursos

- **Documentação**: Todos os arquivos .md no diretório
- **Configuração**: `config.yaml`
- **Exemplos**: Scripts de teste em `tests/`
- **Logs**: Diretório `logs/` (quando implementado)

## 💡 Dicas

1. **Use Web UI para visualização**: Mais intuitivo e visual
2. **Use CLI para automação**: Melhor para scripts
3. **Monitore logs**: Acompanhe o que está acontecendo
4. **Teste incrementalmente**: Um componente por vez
5. **Leia a documentação**: Está tudo documentado!

## 🆘 Ajuda

Se encontrar problemas:
1. Verifique [INTERFACES_GUIDE.md](INTERFACES_GUIDE.md) - Seção Troubleshooting
2. Verifique logs (quando implementado)
3. Teste componentes individualmente ([GUIA_TESTES.md](GUIA_TESTES.md))
4. Abra uma issue no repositório

---

**Tempo estimado**: 5-10 minutos para setup inicial
**Dificuldade**: Fácil
**Pré-requisitos**: Python 3.11+ e uv instalados
