# 🔴 Problemas Urgentes no Frontend

## 📊 Status Atual

### Usuários de Teste
1. **gomesrocha@gmail.com** - Super Admin
   - ❌ Login falha (senha incorreta?)
   - Deveria ter: TODAS as permissões

2. **acme@acme.com** - Admin do Tenant ACME
   - ✅ Login funciona
   - ❌ Retorna 0 roles
   - ❌ Retorna 0 permissions
   - Deveria ter: Permissões de admin do tenant

3. **odair@acme.com** - Gerente de Projetos
   - ✅ Login funciona
   - ❌ Retorna 0 roles
   - ❌ Retorna 0 permissions
   - Deveria ter: Permissões de gerente de projetos

## 🐛 Problemas Identificados

### 1. Endpoint `/auth/permissions` Retorna Vazio
**Sintoma:**
```json
{
  "roles": 0,
  "permissions": 0
}
```

**Causa Provável:**
- `PermissionService.get_user_roles()` não está retornando os roles
- Pode ser problema na query SQL
- Pode ser problema no relacionamento UserRole

### 2. Botão "Criar Projeto" Não Aparece
**Causa:**
- Componente `<Protected permission="project:create">` esconde o botão
- Como `permissions` está vazio, o botão não aparece

### 3. Não Consegue Atribuir Permissões em User Roles
**Causa:**
- Mesma razão: sem permissões, não pode fazer nada

## 🔧 Correções Necessárias

### Correção 1: Verificar Senha do Super Admin
```bash
# Resetar senha do gomesrocha
uv run python scripts/reset_gomes_password.py
```

### Correção 2: Debug do PermissionService
Adicionar logs no método `get_user_roles()` para ver o que está acontecendo:
```python
# Em services/identity/permission_service.py
async def get_user_roles(...):
    print(f"🔍 Getting roles for user: {user.id}")
    query = select(Role).join(UserRole).where(UserRole.user_id == user.id)
    print(f"🔍 Query: {query}")
    result = await session.execute(query)
    roles = list(result.scalars().all())
    print(f"🔍 Found {len(roles)} roles")
    return roles
```

### Correção 3: Verificar Relacionamento UserRole
```bash
# Verificar se user_roles existem no banco
uv run python scripts/check_user_roles_db.py
```

### Correção 4: Fallback Temporário no Frontend
Enquanto não corrigimos o backend, podemos usar fallback no frontend:
```typescript
// Em PermissionContext.tsx
// Se API retornar vazio, dar permissões baseadas no email
if (permissions.length === 0) {
  if (userResponse.data.email.includes('admin') || 
      userResponse.data.email === 'acme@acme.com') {
    // Dar permissões de admin
    setPermissions([
      'project:create', 'project:read', 'project:update', 'project:delete',
      'user:role:assign', 'user:role:remove',
      // ... todas as permissões de admin
    ])
  }
}
```

## 🚀 Plano de Ação

### Passo 1: Resetar Senha do Super Admin
```bash
uv run python scripts/reset_gomes_password.py
```

### Passo 2: Verificar Roles no Banco
```bash
uv run python scripts/check_user_roles_db.py
```

### Passo 3: Adicionar Logs no PermissionService
Editar `services/identity/permission_service.py` e adicionar logs

### Passo 4: Testar Novamente
```bash
uv run python scripts/check_all_users_permissions.py
```

### Passo 5: Se Ainda Não Funcionar
Implementar fallback temporário no frontend

## 📝 Scripts Criados

1. `scripts/check_all_users_permissions.py` - Verifica permissões de todos os usuários
2. `scripts/fix_user_permissions.py` - Tenta corrigir permissões (incompleto)
3. `scripts/test_permissions_frontend.py` - Testa permissões via API

## 🎯 Próximos Passos

1. Criar script para resetar senha do gomesrocha
2. Criar script para verificar user_roles no banco
3. Adicionar logs no PermissionService
4. Testar e corrigir

## 💡 Solução Temporária

Enquanto não corrigimos o backend, você pode:

1. **Usar o frontend com fallback temporário** (já implementado parcialmente)
2. **Logar como super admin** depois de resetar a senha
3. **Verificar logs do backend** para ver erros

## 🔍 Debug Checklist

- [ ] Verificar se user_roles existem no banco para acme@acme.com
- [ ] Verificar se roles têm permissions associadas
- [ ] Verificar se query SQL está correta
- [ ] Verificar se há erros nos logs do backend
- [ ] Testar endpoint `/auth/permissions` diretamente
- [ ] Verificar se cache está causando problema

## 📞 Status

**BLOQUEADO** - Não é possível testar o sistema sem permissões funcionando.

**PRIORIDADE MÁXIMA** - Corrigir permissões para desbloquear testes.
