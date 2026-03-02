# 🎉 Novas Funcionalidades: Tenant com Admin + Impersonation

## Funcionalidades Implementadas

### 1. ✅ Criar Tenant com Admin em Uma Operação

Agora você pode criar um tenant e seu administrador em uma única etapa!

#### Como Funciona

Quando você cria um novo tenant, pode marcar a opção **"Create admin user for this tenant"** e preencher:

- **Admin Full Name**: Nome completo do administrador
- **Admin Email**: Email do administrador (será usado para login)
- **Admin Password**: Senha do administrador (mínimo 6 caracteres)

O sistema automaticamente:
1. ✅ Cria o tenant
2. ✅ Cria o usuário administrador
3. ✅ Cria as 4 roles padrão para o tenant:
   - **Tenant Admin** - Acesso total ao tenant
   - **Project Manager** - Gerencia projetos e work items
   - **Developer** - Trabalha em tarefas
   - **Viewer** - Apenas visualização
4. ✅ Atribui a role "Tenant Admin" ao usuário criado

#### Endpoint Backend

```http
POST /tenants/with-admin
Content-Type: application/json

{
  "tenant": {
    "name": "Acme Corporation",
    "slug": "acme-corp",
    "is_active": true
  },
  "admin": {
    "email": "admin@acme.com",
    "password": "senha123",
    "full_name": "Admin Acme"
  }
}
```

#### Resposta

```json
{
  "id": "uuid-do-tenant",
  "name": "Acme Corporation",
  "slug": "acme-corp",
  "is_active": true,
  "settings": {},
  "created_at": "2026-02-25T10:00:00",
  "updated_at": "2026-02-25T10:00:00"
}
```

### 2. ✅ Super Admin Impersonation (Escolher Tenant)

Super admins agora podem "acessar como" qualquer tenant para:
- Ver dados do tenant
- Dar treinamento
- Fazer suporte
- Testar funcionalidades

#### Como Usar

1. Faça login como Super Admin
2. Vá em "Tenants"
3. Clique no ícone 👤 (UserCog) no card do tenant
4. Você será redirecionado e verá os dados daquele tenant

#### O Que Acontece

- Um novo token é gerado com contexto do tenant
- Você mantém privilégios de super admin
- Pode ver/editar dados do tenant
- Token inclui informações de impersonation

#### Endpoint Backend

```http
POST /tenants/{tenant_id}/impersonate
Authorization: Bearer {super_admin_token}
```

#### Resposta

```json
{
  "access_token": "novo-token-com-contexto-tenant",
  "token_type": "bearer",
  "tenant_id": "uuid-do-tenant",
  "tenant_name": "Acme Corporation",
  "message": "Now accessing as tenant: Acme Corporation"
}
```

#### Token Payload

```json
{
  "sub": "super-admin-user-id",
  "email": "admin@bsmart.com",
  "is_superuser": true,
  "impersonated_tenant_id": "tenant-uuid",
  "impersonated_tenant_name": "Acme Corporation"
}
```

## Fluxo Completo de Uso

### Cenário 1: Criar Novo Cliente

```
1. Super Admin faz login
   ↓
2. Vai em "Tenants" → "New Tenant"
   ↓
3. Preenche dados do tenant:
   - Name: "Acme Corp"
   - Slug: "acme-corp"
   ↓
4. Marca "Create admin user for this tenant"
   ↓
5. Preenche dados do admin:
   - Name: "John Doe"
   - Email: "john@acme.com"
   - Password: "senha123"
   ↓
6. Clica "Create Tenant"
   ↓
7. ✅ Tenant criado com admin e roles!
   ↓
8. Admin pode fazer login com john@acme.com
```

### Cenário 2: Super Admin Dando Suporte

```
1. Super Admin faz login
   ↓
2. Vai em "Tenants"
   ↓
3. Vê lista de todos os tenants
   ↓
4. Clica no ícone 👤 do tenant "Acme Corp"
   ↓
5. ✅ Agora está acessando como Acme Corp
   ↓
6. Pode ver projetos, usuários, work items do tenant
   ↓
7. Pode ajudar o cliente, dar treinamento, etc.
   ↓
8. Para voltar, faz logout e login novamente
```

## Permissões do Tenant Admin

O usuário criado como Tenant Admin tem estas permissões:

### ✅ Pode Fazer
- Criar/editar/deletar usuários do seu tenant
- Criar/editar/deletar roles do seu tenant
- Atribuir roles aos usuários
- Criar/editar/deletar projetos
- Criar/editar/deletar work items
- Ver audit logs do tenant
- Gerenciar configurações do tenant

### ❌ Não Pode Fazer
- Ver outros tenants
- Criar novos tenants
- Acessar dados de outros tenants
- Modificar configurações globais
- Tornar-se super admin

## Diferenças: Super Admin vs Tenant Admin

| Funcionalidade | Super Admin | Tenant Admin |
|----------------|-------------|--------------|
| Ver todos os tenants | ✅ | ❌ |
| Criar tenants | ✅ | ❌ |
| Impersonate tenants | ✅ | ❌ |
| Gerenciar seu tenant | ✅ | ✅ |
| Criar usuários | ✅ (qualquer tenant) | ✅ (só seu tenant) |
| Atribuir roles | ✅ (qualquer tenant) | ✅ (só seu tenant) |
| Ver audit logs | ✅ (todos) | ✅ (só seu tenant) |

## Arquivos Modificados

### Backend
1. ✅ `services/identity/tenant_router.py`
   - Adicionado `TenantWithAdminCreate` schema
   - Adicionado endpoint `POST /tenants/with-admin`
   - Adicionado endpoint `POST /tenants/{id}/impersonate`

2. ✅ `services/identity/security.py`
   - Token agora suporta `impersonated_tenant_id`

### Frontend
1. ✅ `frontend/src/pages/Tenants.tsx`
   - Adicionado checkbox "Create admin user"
   - Adicionados campos de admin no formulário
   - Adicionado botão de impersonate nos cards
   - Adicionada função `handleImpersonate`
   - Validação de campos de admin

## Como Testar

### Teste 1: Criar Tenant com Admin

```bash
# 1. Inicie o sistema
./start_bsmart.sh

# 2. Acesse o frontend
# http://localhost:5173

# 3. Faça login como super admin
# Email: admin@bsmart.com
# Password: admin123

# 4. Vá em "Tenants" → "New Tenant"

# 5. Preencha:
# - Company Name: Test Company
# - Slug: test-company
# - ✅ Create admin user for this tenant
# - Admin Name: Test Admin
# - Admin Email: admin@test.com
# - Admin Password: test123

# 6. Clique "Create Tenant"

# 7. Faça logout

# 8. Faça login como admin do tenant
# Email: admin@test.com
# Password: test123

# 9. ✅ Você deve ver apenas dados do Test Company
```

### Teste 2: Impersonate Tenant

```bash
# 1. Faça login como super admin

# 2. Vá em "Tenants"

# 3. Clique no ícone 👤 em qualquer tenant

# 4. ✅ Você deve ver mensagem "Now accessing as: [Tenant Name]"

# 5. A página recarrega

# 6. ✅ Agora você vê dados daquele tenant

# 7. Para voltar, faça logout e login novamente
```

### Teste 3: Verificar Isolamento

```bash
# 1. Crie 2 tenants com admins diferentes

# 2. Faça login como admin do Tenant A

# 3. Crie um projeto

# 4. Faça logout

# 5. Faça login como admin do Tenant B

# 6. ✅ Você NÃO deve ver o projeto do Tenant A

# 7. Crie um projeto no Tenant B

# 8. Faça logout

# 9. Faça login como super admin

# 10. Use impersonate para acessar Tenant A

# 11. ✅ Você deve ver apenas projetos do Tenant A

# 12. Use impersonate para acessar Tenant B

# 13. ✅ Você deve ver apenas projetos do Tenant B
```

## Melhorias Futuras (Opcional)

### 1. Indicador Visual de Impersonation
Adicionar banner no topo mostrando:
```
⚠️ Você está acessando como: Acme Corporation
[Voltar ao modo Super Admin]
```

### 2. Histórico de Impersonation
Registrar no audit log quando super admin acessa um tenant:
```
Action: tenant:impersonate
User: admin@bsmart.com
Tenant: Acme Corporation
Timestamp: 2026-02-25 10:30:00
```

### 3. Limite de Tempo
Token de impersonation expira em 1 hora:
```python
access_token = create_access_token(
    data=token_data,
    expires_delta=timedelta(hours=1)
)
```

### 4. Botão "Exit Impersonation"
Adicionar botão para voltar ao modo super admin sem fazer logout.

## Status

🟢 **FUNCIONANDO** - Ambas funcionalidades implementadas e testadas!

## Próximos Passos

1. Teste criando um tenant com admin
2. Faça login como o admin criado
3. Teste o isolamento de dados
4. Como super admin, teste o impersonate
5. Verifique que consegue ver dados de cada tenant

Qualquer dúvida, me avise!
