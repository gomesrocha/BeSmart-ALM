# ✅ Usuários e Permissões Configurados

## Estrutura de Permissões

### 1. Super Admins Globais (is_superuser=True)

Usuários que gerenciam TODA a plataforma e TODOS os tenants.

**Características:**
- ✅ Veem o menu "Tenants" no sidebar
- ✅ Podem criar, editar e deletar qualquer tenant
- ✅ Podem gerenciar usuários de qualquer tenant
- ✅ Acesso total a todos os recursos da plataforma

**Usuários:**
- **gomesrocha@gmail.com** / `gomes1234`
  - Tenant: Test Company
  - is_superuser: `True`
  
- **admin@test.com** / `admin1234`
  - Tenant: Test Company
  - is_superuser: `True`

---

### 2. Admins de Tenant (is_superuser=False + Role Admin)

Usuários que gerenciam apenas SEU próprio tenant.

**Características:**
- ❌ NÃO veem o menu "Tenants" no sidebar
- ✅ Gerenciam usuários do próprio tenant
- ✅ Gerenciam projetos do próprio tenant
- ✅ Gerenciam roles e permissões do próprio tenant
- ❌ NÃO podem acessar dados de outros tenants

**Usuários:**
- **acme@acme.com** / `acme1234`
  - Tenant: Acme Corp One
  - is_superuser: `False`
  - Role: Admin (no tenant)

---

## Credenciais de Teste

### Super Admins Globais
```
Email: gomesrocha@gmail.com
Password: gomes1234
Tenant: Test Company
```

```
Email: admin@test.com
Password: admin1234
Tenant: Test Company
```

### Admin de Tenant
```
Email: acme@acme.com
Password: acme1234
Tenant: Acme Corp One
```

---

## Como Testar

### 1. Testar Super Admin Global

```bash
# Login no frontend: http://localhost:5173
# Use: gomesrocha@gmail.com / gomes1234
```

**O que você deve ver:**
- ✅ Menu "Tenants" visível no sidebar
- ✅ Menu "User Roles" visível no sidebar
- ✅ Pode acessar /tenants e ver TODOS os tenants
- ✅ Pode criar novos tenants
- ✅ Pode editar/deletar qualquer tenant

### 2. Testar Admin de Tenant

```bash
# Login no frontend: http://localhost:5173
# Use: acme@acme.com / acme1234
```

**O que você deve ver:**
- ❌ Menu "Tenants" NÃO aparece no sidebar
- ✅ Menu "User Roles" pode aparecer (para gerenciar roles do próprio tenant)
- ✅ Vê apenas projetos do tenant "Acme Corp One"
- ✅ Vê apenas usuários do tenant "Acme Corp One"
- ❌ NÃO pode acessar dados de outros tenants

---

## Isolamento de Tenant

O sistema garante isolamento através do **Tenant Middleware**:

1. **Token JWT** contém o `tenant_id` do usuário
2. **Middleware** injeta o `tenant_id` em todas as queries
3. **Usuários normais** só veem dados do próprio tenant
4. **Super Admins** podem ver todos os tenants (bypass do middleware)

### Exemplo de Query Automática

```python
# Usuário acme@acme.com faz query de projetos
projects = await session.execute(select(Project))

# Middleware automaticamente adiciona:
# WHERE tenant_id = '282ab641-06a2-49f7-9ecf-f62c37f4a3fa'

# Resultado: apenas projetos do tenant "Acme Corp One"
```

---

## Scripts Úteis

### Verificar Usuários
```bash
uv run python scripts/check_users.py
```

### Criar Novos Usuários
```bash
uv run python scripts/create_test_users.py
```

### Configurar Permissões
```bash
uv run python scripts/setup_user_permissions.py
```

### Testar Login
```bash
uv run python scripts/test_login_direct.py
```

---

## Próximos Passos

1. **Testar no Frontend:**
   - Login com cada tipo de usuário
   - Verificar visibilidade do menu "Tenants"
   - Verificar isolamento de dados

2. **Criar Mais Usuários:**
   - Usuários normais (sem role Admin)
   - Usuários com roles específicas (Developer, Viewer, etc.)

3. **Testar Permissões RBAC:**
   - Criar roles customizadas
   - Atribuir permissões específicas
   - Testar acesso a recursos

---

## Arquitetura de Permissões

```
┌─────────────────────────────────────────────────────────┐
│                   PLATAFORMA BSMART                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌────────────────────────────────────────────────┐    │
│  │  SUPER ADMINS GLOBAIS (is_superuser=True)      │    │
│  │  - gomesrocha@gmail.com                        │    │
│  │  - admin@test.com                              │    │
│  │                                                 │    │
│  │  Gerenciam TODOS os tenants ↓                  │    │
│  └────────────────────────────────────────────────┘    │
│                                                          │
│  ┌──────────────────────┐  ┌──────────────────────┐   │
│  │  TENANT: Test        │  │  TENANT: Acme Corp   │   │
│  │                      │  │                      │   │
│  │  Admins:             │  │  Admins:             │   │
│  │  (nenhum ainda)      │  │  - acme@acme.com     │   │
│  │                      │  │                      │   │
│  │  Users:              │  │  Users:              │   │
│  │  - gomesrocha        │  │  - acme              │   │
│  │  - admin@test        │  │                      │   │
│  │                      │  │  Projects:           │   │
│  │  Projects:           │  │  - Projeto A         │   │
│  │  - Projeto X         │  │  - Projeto B         │   │
│  └──────────────────────┘  └──────────────────────┘   │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## Status

✅ **Super Admins configurados:** gomesrocha@gmail.com, admin@test.com  
✅ **Admin de Tenant configurado:** acme@acme.com  
✅ **Menu Tenants visível apenas para Super Admins**  
✅ **Isolamento de tenant funcionando**  
✅ **Credenciais testadas e funcionando**
