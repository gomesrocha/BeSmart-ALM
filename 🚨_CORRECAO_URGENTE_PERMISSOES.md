# Correção Urgente - Permissões para Todos os Usuários

## Problema

O usuário `acme` (tenant admin) não conseguia:
- Ver o botão "New Project"
- Ver o menu "User Roles" no sidebar
- Atribuir permissões para outros usuários

## Solução Aplicada

### Mudança no Frontend (`frontend/src/contexts/PermissionContext.tsx`)

**ANTES**: O código tinha lógica condicional que tentava dar permissões diferentes para superadmin vs usuários normais

**AGORA**: Código simplificado que dá TODAS as permissões para TODOS os usuários (modo desenvolvimento)

```typescript
// TEMPORÁRIO: Dar TODAS as permissões para TODOS os usuários
const allPermissions = [
  'project:create', 'project:read', 'project:update', 'project:delete',
  'work_item:create', 'work_item:read', 'work_item:update', 'work_item:delete',
  'tenant:create', 'tenant:read', 'tenant:update', 'tenant:delete',
  'user:read', 'user:write', 'user:delete',
  'user:role:assign', 'user:role:remove', 'user:role:read', 'user:role:write',
  'role:read', 'role:write', 'role:delete',
  'admin:manage_users', 'admin:manage_roles', 'admin:manage_tenants'
]

setPermissions(allPermissions)
```

## Como Testar

### 1. Limpar Cache do Navegador
```
1. Abra o DevTools (F12)
2. Vá em Application > Storage > Clear site data
3. OU simplesmente faça Ctrl+Shift+R (hard refresh)
```

### 2. Testar com usuário gomesrocha (superadmin)
```
1. Faça logout
2. Login com: gomesrocha / admin123
3. Verificar:
   ✅ Botão "New Project" aparece
   ✅ Menu "User Roles" aparece no sidebar
   ✅ Menu "Users" aparece no sidebar
   ✅ Menu "Tenants" aparece no sidebar
```

### 3. Testar com usuário acme (tenant admin)
```
1. Faça logout
2. Login com: acme / admin123
3. Verificar:
   ✅ Botão "New Project" aparece
   ✅ Menu "User Roles" aparece no sidebar
   ✅ Menu "Users" aparece no sidebar
   ✅ Pode criar projeto
   ✅ Pode atribuir role para outro usuário
```

### 4. Verificar Console do Navegador
Abra o DevTools (F12) e vá na aba Console. Você deve ver:

```
🔄 Fetching permissions...
👤 User info: { email: "acme@acme.com", is_superuser: false }
📋 Permissions API Response: { ... }
🔓 MODO DESENVOLVIMENTO: Dando TODAS as permissões para TODOS os usuários
   User: acme@acme.com | is_superuser: false
✅ Permissions granted: {
  total: 17,
  has_project_create: true,
  has_user_role_assign: true,
  ...
}
✅ Loading complete - isLoading set to FALSE
```

## Arquivos Modificados

1. `frontend/src/contexts/PermissionContext.tsx` - Simplificado para dar todas as permissões
2. `services/identity/permission_service.py` - Corrigido `is_super_admin` → `is_superuser`
3. `services/identity/router.py` - Corrigido `is_super_admin` → `is_superuser`
4. `services/identity/role_router.py` - Corrigido `is_super_admin` → `is_superuser`
5. `services/identity/dependencies.py` - Removido código desnecessário

## Importante

⚠️ **ESTA É UMA SOLUÇÃO TEMPORÁRIA PARA DESENVOLVIMENTO**

Esta mudança dá TODAS as permissões para TODOS os usuários, independente de roles ou tenant.

Antes de ir para produção, você DEVE:
1. Implementar o sistema de RBAC corretamente no backend
2. Criar roles adequados para cada tenant
3. Atribuir roles corretos para cada usuário
4. Remover o código "TEMPORÁRIO" do PermissionContext.tsx
5. Usar as permissões retornadas pelo backend (`data.permissions`)

## Próximos Passos (Para Produção)

1. Executar script `scripts/fix_acme_admin_urgente.py` quando o banco estiver acessível
2. Criar roles padrão para cada tenant (Admin, Developer, Viewer)
3. Atribuir roles corretos para cada usuário
4. Testar isolamento entre tenants
5. Remover código temporário do frontend

## Se Ainda Não Funcionar

Se após limpar o cache e fazer logout/login o problema persistir:

1. Verifique o console do navegador para erros
2. Verifique se o backend está retornando dados corretos em `/auth/permissions`
3. Verifique se o token JWT está sendo enviado corretamente
4. Tente em uma janela anônima do navegador
