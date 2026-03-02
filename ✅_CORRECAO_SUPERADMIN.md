# ✅ Correção: Super Admin Access

## Problema
Usuário `admin@test.com` recebia erro "Super admin access required" ao tentar acessar a tela de Tenants, mesmo sendo super admin.

## Causa Raiz
Bug no decorador `@require_super_admin()` em `services/identity/decorators.py`:

```python
# ❌ ERRADO - verificava campo que não existe
if not getattr(current_user, "is_super_admin", False):
    raise HTTPException(...)
```

O modelo `User` tem o campo `is_superuser`, não `is_super_admin`.

## Correção Aplicada

### 1. Corrigido decorador `require_super_admin()`
```python
# ✅ CORRETO - verifica o campo correto
if not getattr(current_user, "is_superuser", False):
    raise HTTPException(
        status_code=403, detail="Super admin access required"
    )
```

### 2. Corrigido decorador `require_tenant_access()`
```python
# ✅ CORRETO - super admin bypass usa campo correto
if getattr(current_user, "is_superuser", False):
    return await func(*args, **kwargs)
```

### 3. Criado script para verificar/criar super admins

Script `scripts/fix_superadmin.py` que:
- Verifica se usuários são super admins
- Corrige flag `is_superuser` se necessário
- Cria novos super admins se não existirem

## Usuários Super Admin Disponíveis

Após executar o script, você tem 3 super admins:

1. **admin@test.com** / admin123
   - ✅ Já existia
   - ✅ is_superuser = True

2. **gomesrocha@gmail.com** / admin123
   - ✅ Criado pelo script
   - ✅ is_superuser = True

3. **admin@bsmart.com** / admin123
   - ⚠️ Não encontrado no banco
   - Pode ser criado se necessário

## Como Testar

### 1. Faça logout se estiver logado

### 2. Faça login com um dos super admins:
- admin@test.com / admin123
- gomesrocha@gmail.com / admin123

### 3. Acesse a tela "Tenants"
- Deve funcionar sem erro
- Deve mostrar lista de tenants
- Botão "New Tenant" deve estar visível

### 4. Teste criar um tenant
- Clique em "New Tenant"
- Preencha nome e slug
- Clique em "Create Tenant"
- Deve ver mensagem de sucesso verde

## Executar o Script Manualmente

Se precisar verificar/corrigir super admins novamente:

```bash
uv run scripts/fix_superadmin.py
```

O script mostra:
- Quais usuários foram encontrados
- Status de is_superuser de cada um
- Quais foram corrigidos
- Quais foram criados

## Arquivos Modificados

1. ✅ `services/identity/decorators.py` - Corrigido campo is_super_admin → is_superuser
2. ✅ `scripts/fix_superadmin.py` - Script para verificar/criar super admins

## Status

🟢 **RESOLVIDO** - Super admins agora funcionam corretamente!

Você pode fazer login com:
- admin@test.com / admin123
- gomesrocha@gmail.com / admin123

E acessar todas as funcionalidades de super admin, incluindo:
- Gerenciar Tenants
- Gerenciar Usuários de todos os tenants
- Atribuir roles
- Ver logs de auditoria
