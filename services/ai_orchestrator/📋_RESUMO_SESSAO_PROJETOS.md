# 📋 Resumo da Sessão - Projetos do AI Orchestrator

## 🎯 Objetivo

Fazer o AI Orchestrator carregar projetos **reais** do banco de dados, não dados mock.

## 🔍 Problemas Encontrados

### 1. Servidor não estava rodando
- Solução: Iniciar com `uv run python start_web.py` na porta 5010

### 2. Endpoint errado
- ❌ Estava usando: `/projects`
- ✅ Correto: `/api/v1/projects`
- Correção aplicada em `bsmart_client.py`

### 3. Autenticação necessária
- O endpoint `/api/v1/projects` requer autenticação
- O `bsmart_client` já tem o token após login

## ✅ Correções Aplicadas

### 1. `bsmart_client.py`
```python
# Linha 65
response = await self.client.get(f'{self.api_url}/api/v1/projects')
```

### 2. `web_ui.py`
```python
# Tenta buscar projetos reais, fallback para mock se falhar
try:
    if state.get('client'):
        projects = await state['client']._get_projects()
        logging.info(f"📁 Loaded {len(projects)} real projects from API")
        return {"projects": projects}
except Exception as e:
    logging.warning(f"⚠️ Failed to get real projects: {e}")

# Fallback
projects = [mock data]
```

## 🚨 Status Atual

**Ainda está usando dados mock (fallback)**

Isso significa que a chamada à API está falhando. Possíveis causas:

1. **Token não está sendo enviado corretamente**
2. **Backend principal não está rodando**
3. **Endpoint requer headers específicos**
4. **Problema de permissões RBAC**

## 🔍 Debug Necessário

### Verificar se backend está rodando:
```bash
curl http://localhost:8086/api/v1/health
```

### Verificar projetos com autenticação manual:
```bash
# 1. Fazer login e pegar token
TOKEN=$(curl -s -X POST http://localhost:8086/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"gomesrocha@example.com","password":"gomes1234"}' \
  | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])")

# 2. Buscar projetos com token
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8086/api/v1/projects | python3 -m json.tool
```

### Verificar logs do servidor:

No terminal do AI Orchestrator, procure por:
```
⚠️ Failed to get real projects: [erro aqui]
```

O erro vai indicar o problema exato.

## 🎯 Próximos Passos

### Opção 1: Debug da Autenticação

1. Verificar se `bsmart_client` está enviando o token corretamente
2. Adicionar logs detalhados na chamada à API
3. Verificar headers da requisição

### Opção 2: Usar Dados Mock Temporariamente

Se o objetivo é testar o fluxo completo do AI Orchestrator (selecionar projeto, carregar work items, adicionar à fila), os dados mock funcionam perfeitamente.

A integração com projetos reais pode ser feita depois.

## 📝 Arquivos Modificados

1. `services/ai_orchestrator/ai_orchestrator/api/bsmart_client.py`
   - Linha 65: Endpoint corrigido para `/api/v1/projects`
   - Linha 78: `raise` para acionar fallback

2. `services/ai_orchestrator/ai_orchestrator/web_ui.py`
   - Linha 158-175: Lógica de fallback para projetos

## 🔄 Para Aplicar Mudanças

**SEMPRE** que modificar código Python:

1. Ctrl+C no servidor
2. `uv run python start_web.py`
3. F5 no browser
4. Fazer login novamente

## 💡 Recomendação

Para continuar o desenvolvimento do AI Orchestrator:

1. **Use os dados mock por enquanto** - Eles funcionam perfeitamente para testar o fluxo
2. **Foque em testar o fluxo completo**:
   - Login ✅
   - Selecionar projeto ✅
   - Selecionar tipo de tarefa ✅
   - Carregar work items ⏳
   - Adicionar à fila ⏳
   - Processar tarefas ⏳

3. **Depois** resolva a integração com projetos reais

## 📊 Logs para Monitorar

```
# Sucesso (projetos reais):
📁 Loaded 5 real projects from API

# Fallback (mock):
⚠️ Failed to get real projects: [erro]
📁 Using mock projects (fallback)
```

---

**Servidor precisa estar rodando e reiniciado após mudanças!** 🔄
