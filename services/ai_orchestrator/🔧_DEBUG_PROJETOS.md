# 🔧 Debug: Projetos Não Aparecem

## ✅ Correções Aplicadas

### 1. Adicionado Logs no Console
Agora o JavaScript mostra logs detalhados no console do navegador:
- `✅ Login successful, loading projects...`
- `📁 Loading projects...`
- `Projects response status: 200`
- `Projects data: {...}`
- `✅ Found 3 projects`
- `- Added project: Bsmart Sec`

### 2. Chamada Direta de loadProjects()
Agora `loadProjects()` é chamado diretamente após login bem-sucedido, não depende apenas do WebSocket.

## 🧪 Como Debugar

### 1. Reiniciar o Servidor
```bash
# Parar o servidor atual (Ctrl+C)
# Reiniciar
cd services/ai_orchestrator
uv run python start_web.py
```

### 2. Abrir Console do Navegador
1. Acesse http://localhost:5010
2. Pressione F12 (ou Ctrl+Shift+I)
3. Vá para aba "Console"

### 3. Fazer Login
1. Preencha:
   - API URL: `http://localhost:8086/api/v1`
   - Email: `acme@acme.com`
   - Password: `acme1234`
   - Local Repository Path: `~/bsmart-repos`

2. Clique em "Login"

3. Observe os logs no console:
```
✅ Login successful, loading projects...
📁 Loading projects...
Projects response status: 200
Projects data: {projects: Array(3)}
✅ Found 3 projects
  - Added project: Bsmart Sec
  - Added project: Bsmart Sec
  - Added project: BSmart - Teste
```

### 4. Verificar Dropdown
Após o login, o dropdown "Select Project" deve mostrar:
```
-- Select Project --
Bsmart Sec
Bsmart Sec
BSmart - Teste
```

## 🔍 Possíveis Problemas

### Problema 1: Console mostra erro 401
**Sintoma:** `Projects response status: 401`

**Causa:** Sessão não autenticada

**Solução:**
1. Recarregue a página (F5)
2. Faça login novamente

### Problema 2: Console mostra erro 500
**Sintoma:** `Projects response status: 500`

**Causa:** Erro no backend

**Solução:**
1. Verifique logs do servidor
2. Verifique se API do Bsmart-ALM está rodando:
```bash
curl http://localhost:8086/api/v1/health
```

### Problema 3: Console mostra "No projects found"
**Sintoma:** `⚠️ No projects found`

**Causa:** API retornou lista vazia

**Solução:**
1. Teste diretamente a API:
```bash
uv run python services/ai_orchestrator/test_api_projects.py
```

2. Verifique se usuário tem projetos:
```bash
uv run python scripts/check_acme_roles.py
```

### Problema 4: Dropdown não atualiza
**Sintoma:** Dropdown continua vazio mesmo com logs de sucesso

**Causa:** Problema no DOM

**Solução:**
1. Inspecione o elemento (F12 → Elements)
2. Procure por `<select id="projectSelect">`
3. Verifique se tem `<option>` dentro
4. Se não tiver, recarregue a página (F5)

## 🧪 Teste Manual Completo

### Script de Teste
```bash
# Terminal 1: Iniciar servidor
cd services/ai_orchestrator
uv run python start_web.py

# Terminal 2: Testar API diretamente
uv run python services/ai_orchestrator/debug_web_ui.py
```

**Resultado esperado:**
```
✅ Login successful!
✅ Found 3 projects:
  - aa79dcae-14b0-4189-8671-d4b845c089e5: Bsmart Sec
  - 00619acf-2da7-48d0-8577-a504feabd592: Bsmart Sec
  - df23f0cb-7906-48db-a8c8-8fc7de09d411: BSmart - Teste
```

## 📊 Checklist de Verificação

Antes de reportar problema, verifique:

- [ ] Servidor está rodando em http://localhost:5010
- [ ] API Bsmart-ALM está rodando em http://localhost:8086
- [ ] Console do navegador está aberto (F12)
- [ ] Fez login com credenciais corretas
- [ ] Vê logs no console após login
- [ ] Teste direto da API funciona (debug_web_ui.py)

## 🎯 Status Atual

### ✅ Backend Funcionando
```bash
uv run python services/ai_orchestrator/debug_web_ui.py
# ✅ Login successful!
# ✅ Found 3 projects
```

### ✅ Correções Aplicadas
- [x] Logs detalhados no console
- [x] Chamada direta de loadProjects() após login
- [x] Tratamento de erros melhorado
- [x] Validação de resposta da API

### 🔄 Próximo Passo
1. Reinicie o servidor
2. Recarregue a página no navegador (F5)
3. Abra o console (F12)
4. Faça login
5. Observe os logs

## 📝 Logs Esperados

### No Servidor (Terminal)
```
🐝 Starting BeeSmart: AI Orchestrator Web UI...
📱 Open http://localhost:5010 in your browser
🤖 Using model: deepseek-coder-v2:latest
⏹️  Press Ctrl+C to stop
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:5010

# Após login:
INFO:     📂 Repository path: /home/user/bsmart-repos
INFO:     ✅ Real authentication successful
INFO:     🎉 BeeSmart: AI Orchestrator initialized successfully
INFO:     📁 Loaded 3 projects from API
```

### No Console do Navegador
```
✅ Login successful, loading projects...
📁 Loading projects...
Projects response status: 200
Projects data: {projects: Array(3)}
✅ Found 3 projects
  - Added project: Bsmart Sec
  - Added project: Bsmart Sec
  - Added project: BSmart - Teste
```

## 🎊 Conclusão

Com as correções aplicadas:
1. ✅ Logs detalhados para debug
2. ✅ Chamada direta de loadProjects()
3. ✅ Backend testado e funcionando
4. ✅ Pronto para testar no navegador

**Reinicie o servidor e teste novamente!**
