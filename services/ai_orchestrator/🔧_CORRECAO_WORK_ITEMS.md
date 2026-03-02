# 🔧 Correção - Work Items Não Carregam

## ❌ Problema Identificado

O servidor está rodando uma **versão antiga do código**. O endpoint `/api/select-project` retorna 404 porque o código não foi recarregado.

## ✅ Solução

### 1. Parar o Servidor

No terminal onde está rodando, pressione `Ctrl+C`

### 2. Reiniciar o Servidor

```bash
cd services/ai_orchestrator
uv run python start_web.py
```

Você deve ver:

```
🐝 Starting BeeSmart: AI Orchestrator Web UI...
📱 Open http://localhost:5010 in your browser
🤖 Using model: deepseek-coder-v2:latest
⏹️  Press Ctrl+C to stop
INFO:     Started server process
INFO:     Uvicorn running on http://0.0.0.0:5010
```

### 3. Abrir o Browser

Abra: `http://localhost:5010`

### 4. Fazer Login

- **API URL**: `http://localhost:8086` (ou URL do ngrok)
- **Email**: `acme@acme.com`
- **Password**: `acme1234`
- **Repo Path**: `/home/fabio/organizacao/repository/bsmart-alm`

### 5. Testar Fluxo Completo

1. ✅ Login → Projetos carregam automaticamente
2. ✅ Selecionar projeto no dropdown
3. ✅ Selecionar tipo de tarefa (Requirements/Architecture/etc)
4. ✅ Clicar "Load Work Items"
5. ✅ Selecionar work items com checkboxes
6. ✅ Clicar "Add to Queue"

## 🧪 Verificar se Endpoints Funcionam

```bash
uv run python services/ai_orchestrator/test_endpoints.py
```

Deve mostrar:

```
🧪 Testing /api/select-project endpoint...
1️⃣ Logging in...
   Status: 200
   ✅ Login successful

2️⃣ Selecting project...
   Status: 200
   ✅ Project selected: Sistema de Vendas

3️⃣ Getting work items...
   Status: 200
   ✅ Got 3 work items
```

## 📋 Checklist

- [ ] Backend principal rodando (`./start_bsmart.sh`)
- [ ] AI Orchestrator **REINICIADO** (`uv run python start_web.py`)
- [ ] Browser aberto em `http://localhost:5010`
- [ ] Login realizado com sucesso
- [ ] Projetos carregados
- [ ] Projeto selecionado
- [ ] Work items carregados

## 🔍 Debug

Se ainda não funcionar, verifique os logs do servidor:

### Logs Esperados (Sucesso):

```
INFO:     127.0.0.1:xxxxx - "POST /api/login HTTP/1.1" 200 OK
📂 Repository path: /home/fabio/...
✅ Real authentication successful
🎉 BeeSmart: AI Orchestrator initialized successfully
INFO:     127.0.0.1:xxxxx - "GET /api/projects HTTP/1.1" 200 OK
📁 Loaded 3 projects from API
INFO:     127.0.0.1:xxxxx - "POST /api/select-project HTTP/1.1" 200 OK
📁 Selected project: Sistema de Vendas
INFO:     127.0.0.1:xxxxx - "GET /api/work-items HTTP/1.1" 200 OK
📋 Loaded 3 work items
```

### Logs de Erro (404):

```
INFO:     127.0.0.1:xxxxx - "POST /api/select-project HTTP/1.1" 404 Not Found
```

Se você vê 404, significa que o servidor **NÃO FOI REINICIADO** após as mudanças no código.

## 🚨 Importante

O FastAPI **NÃO recarrega automaticamente** quando `reload=False` no `start_web.py`. Você precisa:

1. Parar o servidor (Ctrl+C)
2. Reiniciar o servidor
3. Recarregar a página no browser

---

**REINICIE O SERVIDOR AGORA!** 🔄

