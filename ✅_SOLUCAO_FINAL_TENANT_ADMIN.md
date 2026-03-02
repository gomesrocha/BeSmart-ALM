# Solução Final - Tenant Admin (acme)

## Problema Identificado

O Sidebar verifica se o usuário tem o **role** "Admin" ou "Tenant Admin":

```typescript
const isTenantAdmin = hasRole('Admin') || hasRole('Tenant Admin')
```

Mas o backend não está retornando roles para o usuário acme!

## Causa Raiz

O endpoint `/auth/permissions` retorna:
```json
{
  "permissions": [...],
  "roles": []  // ← VAZIO!
}
```

Isso acontece porque:
1. O usuário acme não tem roles atribuídos no banco de dados
2. OU o backend não está buscando os roles corretamente

## Solução Temporária (Rápida)

Modificar o Sidebar para não depender de roles, apenas de permissões:

```typescript
// ANTES
const isTenantAdmin = hasRole('Admin') || hasRole('Tenant Admin')

// DEPOIS
const isTenantAdmin = hasPermission('user:role:read') || hasPermission('user:role:assign')
```

## Solução Definitiva (Correta)

1. **Executar script** para criar roles e atribuir ao usuário acme
2. **Verificar backend** se está retornando roles corretamente
3. **Manter verificação de roles** no Sidebar

## Implementação da Solução Temporária

Vou modificar o Sidebar agora para usar permissões ao invés de roles.

## Por que isso resolve?

- O PermissionContext já está dando TODAS as permissões para TODOS
- Incluindo `user:role:read` e `user:role:assign`
- Então o tenant admin vai passar na verificação
- E o menu "User Roles" vai aparecer

## Logs para Verificar

Com o usuário acme logado, o console deve mostrar:

```
🔍 Sidebar visibility: {
  user_email: "acme@acme.com",
  is_superuser: false,
  isSuperAdmin: false,
  isTenantAdmin: true,  // ← Deve ser TRUE
  roles: [],  // ← Pode estar vazio
  showUserRoles: true  // ← Deve ser TRUE
}
```

Se `isTenantAdmin` for `false`, o menu não aparece!
