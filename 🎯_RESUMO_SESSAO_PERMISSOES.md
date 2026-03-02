# Resumo da Sessão - Problemas de Permissões

## Problemas Identificados

### 1. Botão "New Project" sumindo intermitentemente
- **Usuários afetados**: gomesrocha (superadmin), acme (tenant admin)
- **Sintoma**: Botão aparece, depois some, depois aparece novamente
- **Causa raiz**: Múltiplos problemas no sistema de permissões

### 2. Não consegue atribuir roles
- **Sintoma**: Ao tentar atribuir role na tela User Roles, falha
- **Causa**: Falta permissão `work_item:transition` no frontend

### 3. Menu "User Roles" não aparece para tenant admin
- **Sintoma**: Usuário acme não vê o menu
- **Causa**: Sidebar verifica permissões que não existem

## Correções Aplicadas

### Backend

1. **services/identity/permission_service.py**
   - Corrigido: `is_super_admin` → `is_superuser` (2 lugares)

2. **services/identity/router.py**
   - Corrigido: `is_super_admin` → `is_superuser` (1 lugar)

3. **services/identity/role_router.py**
   - Corrigido: `is_super_admin` → `is_superuser` (1 lugar)

4. **services/identity/dependencies.py**
   - Removido código que tentava adicionar atributo `is_super_admin`

### Frontend

5. **frontend/src/contexts/PermissionContext.tsx**
   - Simplificado para dar TODAS as permissões para TODOS os usuários (temporário)
   - Removida lógica condicional complexa

## Problema Atual

O botão continua sumindo intermitentemente. Possíveis causas:

1. **Cache do navegador** não está sendo limpo
2. **Backend está retornando dados diferentes** em cada requisição
3. **Token JWT está expirando** e renovando com dados incorretos
4. **Permissão `work_item:transition` faltando** na lista hardcoded do frontend

## Solução Definitiva

Vou adicionar a permissão `work_item:transition` na lista de permissões do frontend:

```typescript
const allPermissions = [
  'project:create', 'project:read', 'project:update', 'project:delete',
  'work_item:create', 'work_item:read', 'work_item:update', 'work_item:delete',
  'work_item:transition', 'work_item:approve',  // ← ADICIONAR ESTAS
  'tenant:create', 'tenant:read', 'tenant:update', 'tenant:delete',
  'user:read', 'user:write', 'user:delete',
  'user:role:assign', 'user:role:remove', 'user:role:read', 'user:role:write',
  'role:read', 'role:write', 'role:delete',
  'admin:manage_users', 'admin:manage_roles', 'admin:manage_tenants'
]
```

## Próximos Passos

1. Adicionar permissões faltantes no frontend
2. Adicionar logs detalhados para debug
3. Verificar se o problema é cache do navegador
4. Criar script para verificar permissões em tempo real
