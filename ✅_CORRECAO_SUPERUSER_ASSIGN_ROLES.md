# ✅ Correção - Superuser Pode Atribuir Roles

## Problema Identificado

O **superuser conseguia ver o menu User Roles, mas não conseguia atribuir ou modificar roles**. O erro acontecia no backend.

## Causa Raiz

O endpoint `POST /roles/{role_id}/assign/{user_id}` estava verificando se o usuário pertencia ao mesmo tenant:

```python
# ANTES - Linha 318
result = await session.execute(
    select(User).where(User.id == user_id, User.tenant_id == tenant_id)
)
```

Isso falhava para superusers porque:
1. Superusers podem não ter `tenant_id`
2. Superusers precisam atribuir roles para usuários de QUALQUER tenant
3. A verificação `User.tenant_id == tenant_id` bloqueava a operação

## Correções Aplicadas

### 1. Endpoint `assign_role_to_user` (linha 318-337)

**ANTES:**
```python
# Verify user exists and belongs to same tenant
result = await session.execute(
    select(User).where(User.id == user_id, User.tenant_id == tenant_id)
)
```

**DEPOIS:**
```python
# Verify user exists
# Superusers can assign roles to users in any tenant
is_superuser = getattr(current_user, "is_superuser", False)

if is_superuser:
    # Superuser can assign to any user
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
else:
    # Regular users can only assign to users in same tenant
    result = await session.execute(
        select(User).where(User.id == user_id, User.tenant_id == tenant_id)
    )
```

### 2. Endpoint `get_user_roles` (linha 420-440)

**ANTES:**
```python
# Verify user exists and belongs to same tenant
result = await session.execute(
    select(User).where(User.id == user_id, User.tenant_id == tenant_id)
)
```

**DEPOIS:**
```python
# Verify user exists
# Superusers can view roles for users in any tenant
is_superuser = getattr(current_user, "is_superuser", False)

if is_superuser:
    # Superuser can view any user's roles
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
else:
    # Regular users can only view roles for users in same tenant
    result = await session.execute(
        select(User).where(User.id == user_id, User.tenant_id == tenant_id)
    )
```

### 3. Endpoint `list_roles` (linha 23-47)

**ANTES:**
```python
result = await session.execute(
    select(Role).where(Role.tenant_id == tenant_id).order_by(Role.name)
)
```

**DEPOIS:**
```python
# Superusers can see roles from all tenants
is_superuser = getattr(current_user, "is_superuser", False)

if is_superuser:
    # Return roles from all tenants
    result = await session.execute(
        select(Role).order_by(Role.tenant_id, Role.name)
    )
else:
    # Return only roles from current tenant
    result = await session.execute(
        select(Role).where(Role.tenant_id == tenant_id).order_by(Role.name)
    )
```

## Como Funciona Agora

### Para Superuser (gomesrocha)

1. **Listar Roles**: Vê roles de TODOS os tenants
2. **Atribuir Role**: Pode atribuir role para QUALQUER usuário de QUALQUER tenant
3. **Ver Roles de Usuário**: Pode ver roles de QUALQUER usuário
4. **Remover Role**: Pode remover role de QUALQUER usuário

### Para Tenant Admin (acme@acme.com)

1. **Listar Roles**: Vê apenas roles do SEU tenant
2. **Atribuir Role**: Pode atribuir role apenas para usuários do SEU tenant
3. **Ver Roles de Usuário**: Pode ver roles apenas de usuários do SEU tenant
4. **Remover Role**: Pode remover role apenas de usuários do SEU tenant

## Teste Agora

### 1. Reinicie o Backend

```bash
# Parar o backend (Ctrl+C no terminal onde está rodando)
# Iniciar novamente
./start_bsmart.sh
```

### 2. Teste com Superuser

1. Faça login como **gomesrocha**
2. Vá para **User Roles**
3. Selecione um usuário (pode ser de qualquer tenant)
4. Clique em **"+ Assign Role"**
5. Selecione um role
6. Clique em **"Assign"**

**Resultado esperado:**
- ✅ Role é atribuído com sucesso
- ✅ Aparece na lista de roles do usuário
- ✅ Sem erros no console

### 3. Teste com Tenant Admin

1. Faça logout
2. Faça login como **acme@acme.com**
3. Vá para **User Roles**
4. Selecione um usuário do tenant ACME
5. Clique em **"+ Assign Role"**
6. Selecione um role
7. Clique em **"Assign"**

**Resultado esperado:**
- ✅ Role é atribuído com sucesso
- ✅ Aparece na lista de roles do usuário
- ✅ Não consegue ver usuários de outros tenants (correto!)

## Arquivos Modificados

### services/identity/role_router.py

**Mudanças:**
1. Linha 23-47: `list_roles` - Superuser vê roles de todos os tenants
2. Linha 318-337: `assign_role_to_user` - Superuser pode atribuir para qualquer usuário
3. Linha 420-440: `get_user_roles` - Superuser pode ver roles de qualquer usuário

## Logs para Debug

Se ainda não funcionar, verifique os logs do backend:

```bash
# Ver logs do serviço identity
docker logs bsmart-identity -f
```

Procure por erros em:
- `POST /roles/{role_id}/assign/{user_id}`
- `GET /roles/user/{user_id}`
- `GET /roles`

## Resumo

✅ **Superuser agora pode atribuir roles** para qualquer usuário de qualquer tenant
✅ **Tenant Admin continua restrito** ao seu próprio tenant
✅ **Isolamento mantido** entre tenants para usuários não-superuser
✅ **Código limpo** com verificação explícita de `is_superuser`

**Reinicie o backend e teste agora!** 🚀
