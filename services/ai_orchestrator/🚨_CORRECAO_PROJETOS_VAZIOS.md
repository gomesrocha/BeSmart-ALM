# 🚨 Correção - Projetos Não Aparecem

## ❌ Problema

Após o login, a lista de projetos está vazia: `{"projects":[]}`

## 🔍 Causa

O método `_get_projects()` no `bsmart_client.py` retornava `[]` quando havia erro, em vez de lançar exceção. Isso impedia o fallback de dados mock.

## ✅ Correção Aplicada

Modificado `services/ai_orchestrator/ai_orchestrator/api/bsmart_client.py`:

```python
except Exception as e:
    logger.error(f"Failed to get projects: {e}")
    raise  # Re-raise para acionar fallback
```

## 🔄 AÇÃO NECESSÁRIA

**VOCÊ PRECISA REINICIAR O SERVIDOR!**

### 1. Parar o Servidor

No terminal onde está rodando, pressione `Ctrl+C`

### 2. Reiniciar o Servidor

```bash
cd services/ai_orchestrator
uv run python start_web.py
```

### 3. Recarregar o Browser

Pressione `F5` em `http://localhost:5010`

### 4. Fazer Login Novamente

- **API URL**: `http://localhost:8086`
- **Email**: `acme@acme.com`
- **Password**: `acme1234`
- **Repo Path**: `/home/fabio/organizacao/repository/bsmart-alm`

### 5. Verificar Projetos

Após o login, você deve ver 3 projetos no dropdown:
- Sistema de Vendas
- Portal Cliente
- API Gateway

## 🧪 Testar Após Reiniciar

```bash
uv run python services/ai_orchestrator/debug_login_flow.py
```

Deve mostrar:

```
✅ Login successful!
✅ Got 3 projects:
   - 1: Sistema de Vendas
   - 2: Portal Cliente
   - 3: API Gateway
✅ Project selected!
✅ Got 3 work items:
   - WI-1: Implementar autenticação
   - WI-2: Corrigir bug no login
   - WI-3: Refatorar arquitetura
```

## 📋 Fluxo Esperado

1. Login → `200 OK`
2. Get Projects → `200 OK` com 3 projetos (fallback)
3. Select Project → `200 OK`
4. Get Work Items → `200 OK` com work items

## 🔍 Logs Esperados

No terminal do servidor, você deve ver:

```
INFO:     127.0.0.1:xxxxx - "POST /api/login HTTP/1.1" 200 OK
📂 Repository path: /home/fabio/...
✅ Real authentication successful
INFO:     127.0.0.1:xxxxx - "GET /api/projects HTTP/1.1" 200 OK
⚠️ Failed to get real projects, using fallback: ...
📁 Loaded 3 projects (fallback)
```

## ⚠️ Importante

O servidor com `reload=False` **NÃO recarrega automaticamente**. Sempre que modificar o código Python, você precisa:

1. Ctrl+C (parar)
2. `uv run python start_web.py` (reiniciar)
3. F5 no browser (recarregar página)

---

**REINICIE O SERVIDOR AGORA!** 🔄
