# 🔧 Problemas Identificados e Correções Pendentes

**Data**: 25/02/2026  
**Status**: ⚠️ REQUER ATENÇÃO

---

## ❌ Problemas Identificados pelo Usuário

### 1. Botão "New Tenant" não aparece na tela de Tenants
**Causa**: Usuário não tem a permissão `tenant:create`  
**Status**: ⚠️ Requer correção no banco de dados

### 2. Links "Tenants" e "User Roles" não aparecem no menu lateral
**Causa**: Usuário não tem as permissões `tenant:read` e `user:role:read`  
**Status**: ⚠️ Requer correção no banco de dados

### 3. Não há roles para atribuir aos usuários
**Causa**: Roles não foram criados no banco de dados  
**Status**: ⚠️ Requer execução de script de seed

### 4. Endpoint `/auth/permissions` retorna erro 500
**Causa**: Método `get_user_roles` não existia no PermissionService  
**Status**: ✅ CORRIGIDO - Método adicionado

### 5. Roles duplicados no banco de dados
**Causa**: Script de seed foi executado múltiplas vezes  
**Status**: ⚠️ Requer limpeza do banco

---

## ✅ Correções Aplicadas

### 1. Método `get_user_roles` adicionado ao PermissionService
**Arquivo**: `services/identity/permission_service.py`

```python
@classmethod
async def get_user_roles(
    cls,
    user: User,
    session: AsyncSession,
    project_id: Optional[UUID] = None,
) -> List[Role]:
    """Retorna todos os roles do usuário."""
    # ... implementação
```

### 2. Endpoint `/auth/permissions` corrigido
**Arquivo**: `services/identity/router.py`

Corrigido para usar `is_superuser` em vez de `is_super_admin`.

### 3. Script de criação de roles criado
**Arquivo**: `scripts/create_default_roles.py`

Script para criar roles padrão para todos os tenants.

---

## 🔧 Correções Necessárias (Próxima Sessão)

### 1. Limpar Roles Duplicados

```sql
-- Identificar duplicados
SELECT tenant_id, name, COUNT(*) 
FROM role 
GROUP BY tenant_id, name 
HAVING COUNT(*) > 1;

-- Manter apenas o mais antigo de cada duplicado
DELETE FROM role 
WHERE id NOT IN (
    SELECT MIN(id) 
    FROM role 
    GROUP BY tenant_id, name
);
```

### 2. Criar Roles Padrão

Opção A - Via SQL direto:
```sql
-- Para cada tenant, criar roles se não existirem
INSERT INTO role (id, tenant_id, name, description, permissions, is_system, created_at, updated_at)
SELECT 
    gen_random_uuid(),
    t.id,
    'admin',
    'Administrator - Full tenant access',
    '["project:create", "project:read", "project:update", "project:delete", ...]'::jsonb,
    true,
    NOW(),
    NOW()
FROM tenant t
WHERE NOT EXISTS (
    SELECT 1 FROM role r 
    WHERE r.tenant_id = t.id AND r.name = 'admin'
);
```

Opção B - Via script Python (após corrigir psycopg2):
```bash
uv pip install psycopg2-binary
uv run python scripts/create_default_roles.py
```

### 3. Atribuir Role Admin ao Usuário Atual

```sql
-- Encontrar o usuário admin@test.com
SELECT id, tenant_id FROM "user" WHERE email = 'admin@test.com';

-- Encontrar o role admin do tenant
SELECT id FROM role WHERE tenant_id = '<TENANT_ID>' AND name = 'admin';

-- Criar user_role se não existir
INSERT INTO user_role (id, user_id, role_id, project_id, created_at, updated_at)
VALUES (
    gen_random_uuid(),
    '<USER_ID>',
    '<ROLE_ID>',
    NULL,
    NOW(),
    NOW()
)
ON CONFLICT DO NOTHING;
```

### 4. Verificar Permissões

Após atribuir o role, testar:
```bash
TOKEN=$(curl -s http://localhost:8086/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password":"admin123456"}' \
  | jq -r '.access_token')

curl http://localhost:8086/api/v1/auth/permissions \
  -H "Authorization: Bearer $TOKEN" | jq
```

Deve retornar:
```json
{
  "user_id": "...",
  "email": "admin@test.com",
  "tenant_id": "...",
  "is_super_admin": false,
  "permissions": [
    "project:create",
    "project:read",
    ...
  ],
  "roles": [
    {
      "id": "...",
      "name": "admin",
      "display_name": "admin",
      "description": "Administrator - Full tenant access"
    }
  ]
}
```

---

## 💡 Melhorias Solicitadas pelo Usuário

### 1. Botão Kanban em cada Projeto
**Descrição**: Adicionar botão "Kanban" em cada card de projeto que leva direto ao Kanban filtrado por aquele projeto.

**Implementação**:
```typescript
// Em frontend/src/pages/Projects.tsx
<Link 
  to={`/work-items/kanban?project=${project.id}`}
  className="btn btn-sm btn-secondary"
>
  <LayoutKanban className="h-4 w-4" />
  Kanban
</Link>
```

### 2. Adicionar Usuários ao Projeto
**Descrição**: Funcionalidade para adicionar membros/usuários a um projeto específico.

**Implementação**:
1. Criar tabela `project_member`:
```sql
CREATE TABLE project_member (
    id UUID PRIMARY KEY,
    project_id UUID NOT NULL REFERENCES project(id),
    user_id UUID NOT NULL REFERENCES "user"(id),
    role VARCHAR(50),
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    UNIQUE(project_id, user_id)
);
```

2. Criar endpoint backend:
```python
@router.post("/projects/{project_id}/members")
async def add_project_member(...)

@router.delete("/projects/{project_id}/members/{user_id}")
async def remove_project_member(...)

@router.get("/projects/{project_id}/members")
async def list_project_members(...)
```

3. Criar componente frontend:
```typescript
// frontend/src/components/ProjectMembers.tsx
// Modal para adicionar membros
// Lista de membros atuais
// Botão para remover
```

---

## 📝 Checklist de Correções

### Banco de Dados
- [ ] Limpar roles duplicados
- [ ] Criar roles padrão (admin, po, dev, qa, sec, auditor)
- [ ] Atribuir role admin ao usuário admin@test.com
- [ ] Verificar que user_role foi criado corretamente

### Backend
- [x] Adicionar método `get_user_roles` ao PermissionService
- [x] Corrigir endpoint `/auth/permissions`
- [ ] Adicionar endpoints de project members (opcional)

### Frontend
- [ ] Adicionar botão Kanban nos cards de projeto
- [ ] Criar componente ProjectMembers (opcional)
- [ ] Testar que links aparecem no menu após correção do banco

### Testes
- [ ] Testar login e obtenção de permissões
- [ ] Testar que botão "New Tenant" aparece
- [ ] Testar que links do menu aparecem
- [ ] Testar atribuição de roles

---

## 🚀 Comandos Rápidos para Correção

### 1. Acessar o banco de dados
```bash
# Se usando Docker
docker exec -it <container_name> psql -U postgres -d bsmart_alm

# Se local
psql -U postgres -d bsmart_alm
```

### 2. Limpar duplicados
```sql
\c bsmart_alm

-- Ver duplicados
SELECT tenant_id, name, COUNT(*) as count
FROM role 
GROUP BY tenant_id, name 
HAVING COUNT(*) > 1;

-- Deletar duplicados (manter o mais antigo)
DELETE FROM role 
WHERE id NOT IN (
    SELECT MIN(id) 
    FROM role 
    GROUP BY tenant_id, name
);
```

### 3. Criar role admin se não existir
```sql
-- Pegar tenant_id
SELECT id, name FROM tenant LIMIT 1;

-- Criar role admin
INSERT INTO role (id, tenant_id, name, description, permissions, is_system, created_at, updated_at)
VALUES (
    gen_random_uuid(),
    '<TENANT_ID>',  -- Substituir pelo ID do tenant
    'admin',
    'Administrator - Full tenant access',
    '["project:create","project:read","project:update","project:delete","project:manage_members","work_item:create","work_item:read","work_item:update","work_item:delete","work_item:approve","work_item:transition","requirements:create","requirements:read","requirements:update","requirements:delete","requirements:approve","code:generate","code:review","code:commit","testing:create","testing:execute","testing:view","security:scan","security:triage","security:view","management:view_dashboard","management:view_metrics","management:export_reports","admin:manage_users","admin:manage_roles","admin:manage_settings","admin:view_audit","audit:view"]'::jsonb,
    true,
    NOW(),
    NOW()
)
ON CONFLICT DO NOTHING;
```

### 4. Atribuir role ao usuário
```sql
-- Pegar user_id e role_id
SELECT u.id as user_id, r.id as role_id
FROM "user" u, role r
WHERE u.email = 'admin@test.com'
AND r.name = 'admin'
AND u.tenant_id = r.tenant_id;

-- Criar user_role
INSERT INTO user_role (id, user_id, role_id, project_id, created_at, updated_at)
VALUES (
    gen_random_uuid(),
    '<USER_ID>',    -- Substituir
    '<ROLE_ID>',    -- Substituir
    NULL,
    NOW(),
    NOW()
)
ON CONFLICT DO NOTHING;
```

### 5. Verificar
```sql
-- Ver roles do usuário
SELECT u.email, r.name, r.description
FROM "user" u
JOIN user_role ur ON ur.user_id = u.id
JOIN role r ON r.id = ur.role_id
WHERE u.email = 'admin@test.com';
```

---

## 📞 Próximos Passos

1. **Corrigir banco de dados** (prioridade alta)
   - Limpar duplicados
   - Criar roles
   - Atribuir roles ao usuário

2. **Testar funcionalidades**
   - Login
   - Permissões
   - Telas admin

3. **Implementar melhorias solicitadas**
   - Botão Kanban nos projetos
   - Adicionar membros ao projeto

4. **Continuar com Tasks 14 e 15**
   - Documentação
   - Limpeza

---

**Status Atual**: Sistema 87% completo, mas requer correções no banco de dados para funcionar completamente.
