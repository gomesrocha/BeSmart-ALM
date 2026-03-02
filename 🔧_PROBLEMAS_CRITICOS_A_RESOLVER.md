# 🔧 Problemas Críticos a Resolver

## Resumo dos Problemas

1. ✅ **RESOLVIDO:** Criar usuário odair@acme.com
2. ⚠️ **CRÍTICO:** Botão "Novo Projeto" não aparece para super admins
3. ⚠️ **IMPORTANTE:** Nome do tenant não aparece no sidebar
4. ⚠️ **IMPORTANTE:** Não consegue atribuir roles para usuários do tenant

---

## 1. ✅ Usuário odair@acme.com Criado

**Credenciais:**
```
Email: odair@acme.com
Password: odair1234
Tenant: Acme Corp One
is_superuser: False
```

**Script usado:**
```bash
uv run python scripts/create_odair_user.py
```

---

## 2. ⚠️ Botão "Novo Projeto" Não Aparece

### Causa Raiz

O botão está protegido por permissão `project:create`:

```typescript
<Protected permission="project:create">
  <button>New Project</button>
</Protected>
```

O `PermissionContext` já tem a lógica correta:
```typescript
const hasPermission = (permission: string): boolean => {
  if (isSuperAdmin) return true  // ← Super admins têm TODAS as permissões
  return permissions.includes(permission)
}
```

**MAS** o problema é que `isSuperAdmin` não está sendo setado corretamente!

### Diagnóstico

O endpoint `/auth/permissions` retorna:
```json
{
  "is_super_admin": false,  // ← Deveria ser true para gomesrocha
  "permissions": [],
  "roles": []
}
```

### Solução

O backend está retornando `is_super_admin` mas o frontend espera `is_superuser`. Precisamos:

**Opção 1:** Atualizar backend para retornar `is_superuser` também
**Opção 2:** Atualizar frontend para usar `is_super_admin`

### Correção Temporária

O `PermissionContext` já tem um fallback que dá permissões de admin em caso de erro. Mas isso não está funcionando para super admins.

### Teste Rápido

```bash
# Teste o endpoint
curl -H "Authorization: Bearer {token}" \
  http://localhost:8086/api/v1/auth/permissions
```

Deveria retornar:
```json
{
  "user_id": "...",
  "email": "gomesrocha@gmail.com",
  "tenant_id": "...",
  "is_super_admin": true,  // ← IMPORTANTE
  "permissions": [...],
  "roles": [...]
}
```

---

## 3. ⚠️ Nome do Tenant no Sidebar

### Problema

O sidebar mostra:
```
Bsmart-ALM
AI-First ALM
```

Deveria mostrar:
```
Bsmart-ALM
AI-First ALM
Tenant: Acme Corp One  ← FALTA ISSO
```

### Solução

1. Adicionar `tenant_name` no `User` interface
2. Buscar nome do tenant no login
3. Mostrar no sidebar

### Código Necessário

**authStore.ts:**
```typescript
interface User {
  id: string
  email: string
  full_name: string
  tenant_id: string
  tenant_name?: string  // ← ADICIONAR
  is_superuser: boolean
}
```

**Sidebar.tsx:**
```typescript
<div className="p-6">
  <h1 className="text-2xl font-bold text-primary-600">Bsmart-ALM</h1>
  <p className="text-sm text-gray-500 mt-1">AI-First ALM</p>
  {user && (
    <p className="text-xs text-gray-400 mt-1">
      Tenant: {user.tenant_name || 'Loading...'}
    </p>
  )}
</div>
```

---

## 4. ⚠️ Não Consegue Atribuir Roles

### Problema

Ao tentar atribuir role para odair@acme.com, não funciona.

### Possíveis Causas

1. **Endpoint errado:** `/users/{user_id}/roles` pode não existir
2. **Permissão negada:** acme@acme.com não tem permissão `user:role:assign`
3. **Tenant isolation:** Tentando atribuir role de outro tenant

### Diagnóstico Necessário

```bash
# 1. Verificar se endpoint existe
curl -X GET http://localhost:8086/api/v1/roles \
  -H "Authorization: Bearer {token}"

# 2. Verificar permissões do acme
curl -X GET http://localhost:8086/api/v1/auth/permissions \
  -H "Authorization: Bearer {acme_token}"

# 3. Tentar atribuir role
curl -X POST http://localhost:8086/api/v1/users/{odair_id}/roles \
  -H "Authorization: Bearer {acme_token}" \
  -H "Content-Type: application/json" \
  -d '{"role_id": "{role_id}"}'
```

### Solução Provável

Dar permissão `user:role:assign` para a role "Admin" do tenant:

```python
# Em scripts/setup_user_permissions.py
admin_role.permissions = [
    "user:read", "user:write", "user:delete",
    "user:role:read", "user:role:write", "user:role:assign",  # ← ADICIONAR
    "project:read", "project:write", "project:delete",
    "workitem:read", "workitem:write", "workitem:delete",
    "role:read", "role:write", "role:delete",
]
```

---

## Prioridade de Correção

### 🔴 URGENTE (Bloqueia uso)

1. **Botão "Novo Projeto" não aparece**
   - Impede criação de projetos
   - Afeta super admins e admins de tenant
   - **Ação:** Corrigir endpoint `/auth/permissions` para retornar `is_super_admin: true`

2. **Não consegue atribuir roles**
   - Impede gerenciamento de usuários
   - Afeta admins de tenant
   - **Ação:** Adicionar permissão `user:role:assign` na role Admin

### 🟡 IMPORTANTE (Melhora UX)

3. **Nome do tenant no sidebar**
   - Usuário não sabe em qual tenant está
   - Confuso para super admins que trocam de tenant
   - **Ação:** Adicionar tenant_name no User e mostrar no sidebar

---

## Próximos Passos

### Passo 1: Corrigir Permissões (URGENTE)

```bash
# Atualizar role Admin com permissões corretas
uv run python scripts/setup_user_permissions.py
```

### Passo 2: Testar Endpoint de Permissões

```bash
# Criar script de teste
uv run python scripts/test_permissions_endpoint.py
```

### Passo 3: Adicionar Nome do Tenant

```bash
# Atualizar authStore e Sidebar
# (Requer mudanças no frontend)
```

---

## Scripts Úteis

### Verificar Usuários
```bash
uv run python scripts/check_users.py
```

### Criar Usuário
```bash
uv run python scripts/create_odair_user.py
```

### Testar Logins
```bash
uv run python scripts/test_all_logins.py
```

### Configurar Permissões
```bash
uv run python scripts/setup_user_permissions.py
```

---

## Status Atual

✅ **Usuários criados:** gomesrocha, admin@test.com, acme, odair  
⚠️ **Botão Novo Projeto:** NÃO funciona (permissões)  
⚠️ **Atribuir Roles:** NÃO funciona (permissões)  
⚠️ **Nome do Tenant:** NÃO aparece (falta implementar)  
✅ **Isolamento de tenant:** Funcionando  
✅ **Login:** Funcionando para todos
