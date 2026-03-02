# 🔧 Troubleshooting - AI Orchestrator

## Problemas Comuns e Soluções

### ❌ ImportError: attempted relative import beyond top-level package

**Problema:**
```
ImportError: attempted relative import beyond top-level package
```

**Causa:** Executar scripts Python diretamente sem o ambiente configurado corretamente.

**Solução:**
```bash
# 1. Certifique-se de estar no diretório correto
cd services/ai_orchestrator

# 2. Execute o setup
./setup.sh

# 3. Ative o ambiente virtual
source .venv/bin/activate

# 4. Execute os scripts
python start_web.py  # ou start_cli.py
```

---

### ❌ ModuleNotFoundError: No module named 'uvicorn'

**Problema:**
```
ModuleNotFoundError: No module named 'uvicorn'
```

**Causa:** Dependências não instaladas.

**Solução:**
```bash
# Opção 1: Usar o setup.sh
./setup.sh

# Opção 2: Instalar manualmente
source .venv/bin/activate
uv pip install -e .
```

---

### ❌ uv: command not found

**Problema:**
```
bash: uv: command not found
```

**Causa:** uv não está instalado.

**Solução:**
```bash
# Instalar uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Adicionar ao PATH (adicione ao ~/.bashrc ou ~/.zshrc)
export PATH="$HOME/.cargo/bin:$PATH"

# Recarregar shell
source ~/.bashrc  # ou source ~/.zshrc
```

---

### ❌ Port 8080 already in use

**Problema:**
```
ERROR: [Errno 98] Address already in use
```

**Causa:** Porta 8080 já está sendo usada.

**Solução:**
```bash
# Opção 1: Matar processo na porta 8080
pkill -f start_web.py

# Opção 2: Usar outra porta
# Edite start_web.py e mude a porta:
# port=8081  # ao invés de 8080

# Opção 3: Encontrar e matar o processo
lsof -ti:8080 | xargs kill -9
```

---

### ❌ Web UI não carrega (mostra página diferente)

**Problema:** Ao acessar http://localhost:8080, aparece uma página diferente (ex: frontend do Bsmart).

**Causa:** Outro serviço está rodando na porta 8080.

**Solução:**
```bash
# 1. Verificar qual processo está usando a porta
lsof -i:8080

# 2. Se for o frontend do Bsmart, pare-o ou use outra porta
# Para o AI Orchestrator, edite start_web.py:
port=8081  # ou outra porta disponível

# 3. Acesse a nova URL
http://localhost:8081
```

---

### ❌ Aider não encontrado

**Problema:**
```
FileNotFoundError: aider command not found
```

**Causa:** Aider não está instalado.

**Solução:**
```bash
# Instalar aider
pip install aider-chat

# Verificar instalação
aider --version
```

---

### ❌ Ollama não conecta

**Problema:**
```
Connection refused to Ollama
```

**Causa:** Ollama não está rodando.

**Solução:**
```bash
# Iniciar Ollama
ollama serve

# Em outro terminal, baixar modelo
ollama pull codellama:13b

# Verificar modelos disponíveis
ollama list
```

---

### ❌ Git repository not found

**Problema:**
```
GitError: Repository not found
```

**Causa:** Tentando executar em diretório que não é um repositório Git.

**Solução:**
```bash
# Inicializar repositório Git
git init

# Ou executar em um diretório que já é um repositório
cd /path/to/your/git/repo
```

---

### ❌ Permission denied ao executar scripts

**Problema:**
```
bash: ./setup.sh: Permission denied
```

**Causa:** Scripts não têm permissão de execução.

**Solução:**
```bash
# Dar permissão de execução
chmod +x setup.sh start_web.py start_cli.py

# Executar
./setup.sh
```

---

## 🐛 Debug Mode

Para ativar logs detalhados:

```bash
# Definir nível de log
export LOG_LEVEL=DEBUG

# Executar com logs detalhados
python start_web.py
```

---

## 📝 Logs

Localização dos logs:

```bash
# Logs do Web UI
tail -f logs/web_ui.log

# Logs dos agentes
tail -f logs/agents.log

# Logs da fila
tail -f logs/queue.log
```

---

## 🔍 Verificação de Saúde

Script para verificar se tudo está funcionando:

```bash
# Criar script de health check
cat > health_check.sh << 'EOF'
#!/bin/bash
echo "🔍 Verificando AI Orchestrator..."

# Check uv
if command -v uv &> /dev/null; then
    echo "✅ uv instalado: $(uv --version)"
else
    echo "❌ uv não encontrado"
fi

# Check Python
if command -v python3 &> /dev/null; then
    echo "✅ Python instalado: $(python3 --version)"
else
    echo "❌ Python não encontrado"
fi

# Check venv
if [ -d ".venv" ]; then
    echo "✅ Virtual environment existe"
else
    echo "❌ Virtual environment não encontrado"
fi

# Check aider (opcional)
if command -v aider &> /dev/null; then
    echo "✅ Aider instalado: $(aider --version)"
else
    echo "⚠️  Aider não encontrado (opcional)"
fi

# Check ollama (opcional)
if command -v ollama &> /dev/null; then
    echo "✅ Ollama instalado"
else
    echo "⚠️  Ollama não encontrado (opcional)"
fi

echo ""
echo "🎯 Status: Pronto para uso!"
EOF

chmod +x health_check.sh
./health_check.sh
```

---

## 💡 Dicas

1. **Sempre ative o ambiente virtual** antes de executar os scripts
2. **Use o setup.sh** para configuração inicial
3. **Verifique os logs** quando algo não funcionar
4. **Teste componentes individualmente** antes de testar o sistema completo
5. **Mantenha as dependências atualizadas**: `uv pip install --upgrade -e .`

---

## 🆘 Ainda com problemas?

1. Verifique os logs em `logs/`
2. Execute o health check script acima
3. Certifique-se de que todas as dependências estão instaladas
4. Tente recriar o ambiente virtual:
   ```bash
   rm -rf .venv
   ./setup.sh
   ```
