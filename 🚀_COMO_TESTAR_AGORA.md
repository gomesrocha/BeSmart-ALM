# 🚀 Como Testar o Sistema Agora

**Data**: 25/02/2026  
**Status**: Guia de Teste Rápido

---

## ⚠️ Status Atual

O backend **NÃO está rodando** no momento. Você precisa iniciá-lo antes de testar.

---

## 📋 Passo a Passo para Testar

### 1️⃣ Iniciar o Backend

Abra um terminal e execute:

```bash
# Opção 1: Usando o script de inicialização
./start_backend.sh

# Opção 2: Manualmente com uv
uv run uvicorn services.api_gateway.main:app --host 0.0.0.0 --port 8086 --reload
```

**Aguarde até ver**:
```
INFO:     Uvicorn running on http://0.0.0.0:8086 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### 2️⃣ Verificar se o Backend Está Funcionando

Em outro terminal:

```bash
# Teste simples
curl http://localhost:8086/api/v1/health

# Deve retornar algo como:
# {"status":"healthy"}
```

### 3️⃣ Testar o Login

```bash
curl -X POST http://localhost:8086/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password":"admin123456"}'
```

**Resposta esperada**:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

Se retornar erro 401 ou 404, você precisa criar o usuário primeiro (veja seção "Criar Usuário de Teste").

### 4️⃣ Iniciar o Frontend

Em outro terminal:

```bash
cd frontend
npm run dev
```

**Aguarde até ver**:
```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

### 5️⃣ Testar no Browser

1. Abra http://localhost:5173
2. Faça login com:
   - **Email**: `admin@test.com`
   - **Password**: `admin123456`

3. Após o login, teste as novas funcionalidades:
   - **Filtro de Projeto em Work Items**: Vá para Work Items e veja o novo dropdown de projetos
   - **Filtro de Projeto no Kanban**: Vá para Kanban e selecione um projeto
   - **Permissões**: Tente criar/editar/deletar itens e veja se as permissões funcionam

---

## 🔧 Solução de Problemas

### Problema: "Failed to connect to localhost port 8086"

**Causa**: Backend não está rodando

**Solução**:
```bash
./start_backend.sh
```

### Problema: Login retorna 401 Unauthorized

**Causa**: Usuário não existe ou senha incorreta

**Solução**: Criar usuário de teste (veja próxima seção)

### Problema: Login retorna 500 Internal Server Error

**Causa**: Banco de dados não está configurado ou tabelas não existem

**Solução**:
```bash
# Criar tabelas RBAC
uv run python scripts/create_rbac_tables.py

# Criar roles padrão
uv run python scripts/seed_roles.py

# Criar usuário de teste
uv run python scripts/seed_db.py
```

### Problema: Frontend não carrega permissões

**Causa**: Endpoint de permissões não está funcionando

**Solução**: Verificar logs do backend e testar endpoint:
```bash
# Primeiro faça login e pegue o token
TOKEN="seu_token_aqui"

# Teste o endpoint de permissões
curl http://localhost:8086/api/v1/auth/permissions \
  -H "Authorization: Bearer $TOKEN"
```

---

## 🗄️ Criar Usuário de Teste

Se o login falhar porque o usuário não existe:

### Opção 1: Usar script de seed

```bash
uv run python scripts/seed_db.py
```

Este script cria:
- Tenant padrão
- Usuário admin com email `admin@test.com` e senha `admin123456`
- Roles básicos

### Opção 2: Criar manualmente via API

```bash
# 1. Criar tenant
curl -X POST http://localhost:8086/api/v1/tenants \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Company",
    "domain": "test.com"
  }'

# 2. Criar usuário (substitua TENANT_ID pelo ID retornado acima)
curl -X POST http://localhost:8086/api/v1/users \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@test.com",
    "password": "admin123456",
    "full_name": "Admin User",
    "tenant_id": "TENANT_ID"
  }'
```

---

## ✅ Checklist de Teste

Após iniciar o sistema, teste estas funcionalidades:

### Backend
- [ ] Backend está rodando (porta 8086)
- [ ] Login funciona
- [ ] Endpoint de permissões retorna dados
- [ ] Endpoint de projetos funciona
- [ ] Endpoint de work items funciona

### Frontend - Filtros de Projeto (Task 10)
- [ ] Componente ProjectSelector aparece em Work Items
- [ ] Dropdown carrega lista de projetos
- [ ] Filtro funciona (mostra apenas work items do projeto selecionado)
- [ ] Seleção persiste ao recarregar página
- [ ] Componente ProjectSelector aparece no Kanban
- [ ] Kanban exige seleção de projeto
- [ ] Mensagem informativa aparece quando nenhum projeto está selecionado
- [ ] Kanban filtra work items corretamente

### Frontend - Permissões (Task 9)
- [ ] Botões protegidos aparecem/desaparecem conforme permissões
- [ ] "New Project" só aparece se tiver permissão
- [ ] "New Work Item" só aparece se tiver permissão
- [ ] Botões de edição/deleção respeitam permissões

### Backend - RBAC
- [ ] Criar projeto sem permissão retorna 403
- [ ] Criar work item sem permissão retorna 403
- [ ] Usuários de diferentes tenants não veem dados uns dos outros
- [ ] Logs de auditoria são criados para ações importantes

---

## 🧪 Testes Automatizados

Se quiser rodar os testes automatizados:

```bash
# Todos os testes
uv run pytest tests/ -v

# Apenas testes de permissões
uv run pytest tests/test_permission_service.py -v

# Apenas testes de integração RBAC
uv run pytest tests/test_rbac_integration.py -v

# Apenas testes E2E
uv run pytest tests/test_e2e_user_flows.py -v
```

**Nota**: Os testes precisam do banco de dados configurado e podem falhar se houver dados inconsistentes.

---

## 📊 O Que Foi Implementado (Task 10 e 13)

### Task 10: Filtros de Projeto ✅

**Arquivos criados/modificados**:
- `frontend/src/components/ProjectSelector.tsx` (novo)
- `frontend/src/pages/WorkItems.tsx` (modificado)
- `frontend/src/pages/WorkItemsKanban.tsx` (modificado)

**Funcionalidades**:
- Dropdown de seleção de projetos
- Filtro em Work Items com persistência
- Filtro em Kanban com seleção obrigatória
- localStorage para manter seleção entre sessões

### Task 13: Testes ✅

**Arquivos criados**:
- `tests/test_permission_service.py` (15+ casos de teste)
- `tests/test_rbac_integration.py` (12+ casos de teste)
- `tests/test_e2e_user_flows.py` (1 teste E2E abrangente)

**Cobertura**:
- Testes unitários de PermissionService
- Testes de integração de RBAC
- Testes de isolamento multi-tenant
- Testes E2E de workflows completos

---

## 🎯 Próximos Passos

Após testar e confirmar que tudo funciona:

1. **Task 11**: Criar telas de gerenciamento (admin UI)
2. **Task 14**: Documentação completa
3. **Task 15**: Limpeza e organização

---

## 💡 Dicas

- Mantenha o backend rodando em um terminal separado
- Mantenha o frontend rodando em outro terminal
- Use o browser DevTools (F12) para ver erros no console
- Verifique os logs do backend para erros de API
- Use `Ctrl+C` para parar os servidores

---

## 📞 Se Algo Não Funcionar

1. Verifique se o backend está rodando (porta 8086)
2. Verifique se o frontend está rodando (porta 5173)
3. Verifique os logs de erro no terminal
4. Verifique o console do browser (F12)
5. Tente recriar o banco de dados:
   ```bash
   uv run python scripts/create_rbac_tables.py
   uv run python scripts/seed_roles.py
   uv run python scripts/seed_db.py
   ```

---

**Boa sorte com os testes! 🚀**
