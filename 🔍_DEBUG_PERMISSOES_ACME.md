# 🔍 Debug - Permissões do Acme

## Problema

1. ❌ Menu "User Roles" não aparece para acme@acme.com
2. ❌ Botão "Novo Projeto" não aparece para acme@acme.com
3. ✅ Funciona para gomesrocha@gmail.com (super admin)

## Correções Aplicadas

### 1. Sidebar Atualizado

Agora usa `usePermissions()` para verificar se tem role "Admin":

```typescript
const { hasRole, isSuperAdmin: isSuperAdminFromPermissions } = usePermissions()

const isSuperAdmin = user?.is_superuser === true || isSuperAdminFromPermissions
const isTenantAdmin = hasRole('Admin')  // ← NOVO
const showUserRoles = isSuperAdmin || isTenantAdmin
```

### 2. Logs de Debug Adicionados

O `PermissionContext` agora mostra logs detalhados no console:

```javascript
📋 Permissions API Response: {
  is_super_admin: false,
  permissions_count: 0,
  roles_count: 1,
  roles: [{name: 'Admin', ...}]
}

👤 Regular user: {
  hasAdminRole: true,
  permissions_from_backend: 0
}

✅ Admin role detected - granting admin permissions
```

---

## Como Testar

### Passo 1: Limpar Cache

```javascript
// No console do navegador (F12)
localStorage.clear()
// Recarregar página (F5)
```

### Passo 2: Login como acme@acme.com

```
Email: acme@acme.com
Password: acme1234
```

### Passo 3: Abrir Console do Navegador (F12)

Verificar os logs:

**Esperado:**
```
📋 Permissions API Response: {
  is_super_admin: false,
  permissions_count: 0,
  roles_count: 1,
  roles: [{id: "...", name: "Admin", ...}]
}

👤 Regular user: {
  hasAdminRole: true,
  permissions_from_backend: 0
}

✅ Admin role detected - granting admin permissions
```

### Passo 4: Verificar Menu

**Deve aparecer:**
- ✅ Dashboard
- ✅ Projects
- ✅ Work Items
- ✅ Users
- ✅ AI Stats
- ✅ **Administration** (seção)
- ✅ **User Roles** (dentro de Administration)

**NÃO deve aparecer:**
- ❌ Tenants (apenas para super admins)

### Passo 5: Ir em Projects

**Deve aparecer:**
- ✅ Botão "New Project" no canto superior direito

### Passo 6: Ir em User Roles

**Deve aparecer:**
- ✅ Lista de usuários do tenant Acme
- ✅ Ao selecionar odair, deve mostrar botão "Assign Role"
- ✅ Ao clicar em "Assign Role", deve mostrar role "Admin" disponível

---

## Possíveis Problemas

### Problema 1: Roles Vazias

**Sintoma:** Console mostra `roles_count: 0`

**Causa:** O endpoint `/auth/permissions` não está retornando as roles do usuário

**Solução:** Verificar se acme@acme.com tem a role "Admin" atribuída

```bash
# Executar script
uv run python scripts/setup_user_permissions.py
```

### Problema 2: hasRole('Admin') Retorna False

**Sintoma:** Menu "User Roles" não aparece mesmo com role Admin

**Causa:** O `hasRole` não está encontrando a role

**Debug:**
```javascript
// No console do navegador
// Após login como acme
const permissions = JSON.parse(localStorage.getItem('permissions') || '{}')
console.log('Roles:', permissions.roles)
```

### Problema 3: Botão "Novo Projeto" Não Aparece

**Sintoma:** Menu aparece mas botão não

**Causa:** Permissão `project:create` não foi concedida

**Debug:**
```javascript
// No console do navegador
const permissions = JSON.parse(localStorage.getItem('permissions') || '{}')
console.log('Has project:create?', permissions.permissions.includes('project:create'))
```

---

## Script de Verificação

Execute este script para verificar se acme tem a role Admin:

```bash
cat > scripts/check_acme_roles.py << 'EOF'
#!/usr/bin/env python3
import asyncio
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.shared.database import async_session_maker
from services.identity.models import User, UserRole, Role
from sqlmodel import select

async def main():
    async with async_session_maker() as session:
        # Find acme user
        result = await session.execute(
            select(User).where(User.email == "acme@acme.com")
        )
        acme = result.scalar_one_or_none()
        
        if not acme:
            print("❌ User acme@acme.com not found")
            return
        
        print(f"✅ Found user: {acme.email}")
        print(f"   Tenant ID: {acme.tenant_id}")
        
        # Find user roles
        result = await session.execute(
            select(UserRole).where(UserRole.user_id == acme.id)
        )
        user_roles = result.scalars().all()
        
        print(f"\n📋 User Roles: {len(user_roles)}")
        
        for ur in user_roles:
            # Get role details
            result = await session.execute(
                select(Role).where(Role.id == ur.role_id)
            )
            role = result.scalar_one_or_none()
            
            if role:
                print(f"\n  Role: {role.name}")
                print(f"    ID: {role.id}")
                print(f"    Description: {role.description}")
                print(f"    Permissions: {len(role.permissions)} items")
                print(f"    Permissions: {role.permissions}")

if __name__ == "__main__":
    asyncio.run(main())
EOF

uv run python scripts/check_acme_roles.py
```

---

## Resultado Esperado

Após as correções e limpeza de cache:

### Para acme@acme.com

✅ Vê menu "User Roles"  
✅ Vê botão "New Project"  
✅ Pode atribuir roles para usuários do tenant  
✅ Pode criar projetos no tenant  
❌ NÃO vê menu "Tenants"

### Para gomesrocha@gmail.com

✅ Vê menu "Tenants"  
✅ Vê menu "User Roles"  
✅ Vê botão "New Project"  
✅ Pode fazer tudo

---

## Status

⚠️ **Aguardando teste do usuário**

Após fazer logout, limpar cache e login novamente como acme@acme.com, verificar:
1. Console do navegador mostra os logs corretos?
2. Menu "User Roles" aparece?
3. Botão "New Project" aparece?

Se ainda não funcionar, executar o script `check_acme_roles.py` e enviar o resultado.
