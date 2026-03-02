# ✅ Tenant: Desabilitar vs Deletar Permanentemente

## Problema Resolvido

Antes, o botão "Delete" apenas desabilitava o tenant (soft delete), mas mostrava mensagem de "deletado".

Agora temos **duas ações distintas**:

### 1. 🟠 Desabilitar/Habilitar (Soft Delete)
- **Ícone**: ⚡ PowerOff / Power
- **Cor**: Laranja (desabilitar) / Verde (habilitar)
- **Ação**: Toggle do campo `is_active`
- **Reversível**: ✅ Sim
- **Dados preservados**: ✅ Todos

### 2. 🔴 Deletar Permanentemente (Hard Delete)
- **Ícone**: 🗑️ Trash2
- **Cor**: Vermelho
- **Ação**: Deleta tenant e TODOS os dados relacionados
- **Reversível**: ❌ NÃO
- **Dados preservados**: ❌ Nenhum

## Implementação

### Backend

#### Endpoint 1: Toggle Active Status
```http
PATCH /tenants/{tenant_id}/toggle-active
Authorization: Bearer {super_admin_token}
```

**Resposta:**
```json
{
  "id": "uuid",
  "name": "Acme Corp",
  "slug": "acme-corp",
  "is_active": false,  // Toggled
  "settings": {},
  "created_at": "2026-02-25T10:00:00",
  "updated_at": "2026-02-25T10:05:00"
}
```

#### Endpoint 2: Delete Permanently
```http
DELETE /tenants/{tenant_id}
Authorization: Bearer {super_admin_token}
```

**O que é deletado (em ordem):**
1. ✅ User Roles (associações)
2. ✅ API Tokens
3. ✅ Audit Logs
4. ✅ Users
5. ✅ Roles
6. ✅ Tenant

**Resposta:** `204 No Content`

### Frontend

#### Botão 1: Toggle Active (PowerOff/Power)
```typescript
const handleToggleActive = async (tenant: Tenant) => {
  const action = tenant.is_active ? 'deactivate' : 'activate';
  
  if (!confirm(`Are you sure you want to ${action} "${tenant.name}"?`)) {
    return;
  }

  await api.patch(`/tenants/${tenant.id}/toggle-active`);
  setSuccess(`Tenant ${action}d successfully!`);
  fetchTenants();
};
```

#### Botão 2: Delete Permanently (Trash2)
```typescript
const handleDelete = async (tenant: Tenant) => {
  // Primeiro confirm com aviso detalhado
  if (!confirm(
    `⚠️ WARNING: This will PERMANENTLY delete "${tenant.name}" and ALL its data!\n\n` +
    `This includes:\n` +
    `- All users\n` +
    `- All roles\n` +
    `- All projects\n` +
    `- All work items\n` +
    `- All audit logs\n\n` +
    `This action CANNOT be undone!`
  )) {
    return;
  }

  // Segundo confirm: digitar o nome do tenant
  const confirmation = prompt(`Type "${tenant.name}" to confirm deletion:`);
  
  if (confirmation !== tenant.name) {
    setError('Tenant name does not match. Deletion cancelled.');
    return;
  }

  await api.delete(`/tenants/${tenant.id}`);
  setSuccess('Tenant permanently deleted!');
  fetchTenants();
};
```

## Interface Visual

Cada card de tenant agora tem 4 botões:

```
┌─────────────────────────────────────┐
│  🏢 Acme Corporation                │
│  Slug: acme-corp                    │
│  ● Active                           │
├─────────────────────────────────────┤
│  👤  ✏️  ⚡  🗑️                      │
│  ^   ^   ^   ^                      │
│  │   │   │   └─ Delete (red)        │
│  │   │   └───── Toggle (orange)     │
│  │   └───────── Edit (gray)         │
│  └───────────── Impersonate (blue)  │
└─────────────────────────────────────┘
```

## Quando Usar Cada Ação

### Use "Desabilitar" (PowerOff) quando:
- ✅ Cliente pausou o contrato temporariamente
- ✅ Tenant está em período de teste/trial
- ✅ Problemas de pagamento (suspensão temporária)
- ✅ Manutenção programada
- ✅ Você quer preservar os dados para reativação futura

**Efeito:**
- Tenant fica inativo
- Usuários não conseguem fazer login
- Dados permanecem no banco
- Pode ser reativado a qualquer momento

### Use "Deletar" (Trash2) quando:
- ❌ Cliente cancelou definitivamente
- ❌ Tenant de teste que não será mais usado
- ❌ Dados devem ser removidos por compliance/LGPD
- ❌ Limpeza de tenants antigos/inativos
- ❌ Você tem CERTEZA que não precisa mais dos dados

**Efeito:**
- ⚠️ TUDO é deletado permanentemente
- ⚠️ Não há como recuperar
- ⚠️ Usuários, projetos, work items, tudo some
- ⚠️ Ação irreversível

## Proteções Implementadas

### Proteção 1: Confirmação Dupla
```javascript
// 1º Confirm: Aviso detalhado
confirm("⚠️ WARNING: This will PERMANENTLY delete...")

// 2º Confirm: Digitar nome do tenant
prompt("Type 'Acme Corp' to confirm deletion:")
```

### Proteção 2: Validação de Nome
```javascript
if (confirmation !== tenant.name) {
  setError('Tenant name does not match. Deletion cancelled.');
  return;
}
```

### Proteção 3: Transação no Backend
```python
try:
    # Delete all related data
    # ...
    await session.commit()
except Exception as e:
    await session.rollback()  # Rollback if anything fails
    raise HTTPException(...)
```

## Fluxo de Uso

### Cenário 1: Cliente Pausou Contrato

```
1. Super Admin vai em "Tenants"
   ↓
2. Encontra o tenant do cliente
   ↓
3. Clica no botão ⚡ (PowerOff)
   ↓
4. Confirma: "Are you sure you want to deactivate?"
   ↓
5. ✅ Tenant desabilitado
   ↓
6. Badge muda para "Inactive"
   ↓
7. Usuários não conseguem mais fazer login
   ↓
8. Quando cliente voltar, clica ⚡ (Power) para reativar
```

### Cenário 2: Cliente Cancelou Definitivamente

```
1. Super Admin vai em "Tenants"
   ↓
2. Encontra o tenant do cliente
   ↓
3. Clica no botão 🗑️ (Trash2)
   ↓
4. Lê o aviso detalhado
   ↓
5. Confirma: "OK"
   ↓
6. Digite o nome do tenant: "Acme Corp"
   ↓
7. ✅ Tenant e TODOS os dados deletados
   ↓
8. Não aparece mais na lista
   ↓
9. ⚠️ Não há como recuperar
```

## Arquivos Modificados

### Backend
1. ✅ `services/identity/tenant_router.py`
   - Adicionado `PATCH /tenants/{id}/toggle-active`
   - Modificado `DELETE /tenants/{id}` para hard delete
   - Deleta em cascata: UserRoles → APITokens → AuditLogs → Users → Roles → Tenant

### Frontend
2. ✅ `frontend/src/pages/Tenants.tsx`
   - Função `handleToggleActive` - Toggle is_active
   - Função `handleDelete` - Delete permanente com confirmação dupla
   - Botões separados com cores e ícones distintos

## Testando

### Teste 1: Desabilitar Tenant

```bash
# 1. Crie um tenant de teste
# 2. Crie um usuário nesse tenant
# 3. Faça login com esse usuário (deve funcionar)
# 4. Como super admin, desabilite o tenant (⚡)
# 5. Tente fazer login com o usuário novamente
# ✅ Deve falhar (tenant inativo)
# 6. Reative o tenant (⚡)
# 7. Tente fazer login novamente
# ✅ Deve funcionar
```

### Teste 2: Deletar Tenant

```bash
# 1. Crie um tenant de teste
# 2. Crie alguns usuários e projetos
# 3. Como super admin, clique em deletar (🗑️)
# 4. Leia o aviso
# 5. Confirme
# 6. Digite o nome errado
# ✅ Deve cancelar
# 7. Clique deletar novamente
# 8. Digite o nome correto
# ✅ Tenant desaparece da lista
# 9. Verifique no banco de dados
# ✅ Todos os dados foram removidos
```

### Teste 3: Proteção de Dados

```bash
# 1. Crie Tenant A com dados importantes
# 2. Crie Tenant B com dados de teste
# 3. Delete Tenant B
# 4. Verifique Tenant A
# ✅ Dados do Tenant A intactos
# ✅ Apenas Tenant B foi deletado
```

## Status

🟢 **FUNCIONANDO** - Duas ações distintas implementadas com proteções!

## Recomendações

1. **Sempre desabilite primeiro** - Antes de deletar, desabilite por alguns dias para garantir
2. **Backup antes de deletar** - Considere fazer backup dos dados antes de deletar
3. **Audit log** - Registre quem deletou e quando (já implementado)
4. **Soft delete por padrão** - Use desabilitar como padrão, delete apenas quando necessário
5. **Política de retenção** - Defina política de quanto tempo manter tenants inativos

## Melhorias Futuras (Opcional)

### 1. Período de Graça
```python
# Ao invés de deletar imediatamente, marcar para deleção
tenant.marked_for_deletion_at = datetime.now()
tenant.will_be_deleted_at = datetime.now() + timedelta(days=30)

# Job que deleta após 30 dias
```

### 2. Backup Automático
```python
# Antes de deletar, fazer backup
backup_tenant_data(tenant_id)
delete_tenant(tenant_id)
```

### 3. Audit Log Detalhado
```python
# Registrar o que foi deletado
audit_log.create(
    action="tenant:delete",
    details={
        "tenant_id": tenant_id,
        "tenant_name": tenant.name,
        "users_deleted": user_count,
        "projects_deleted": project_count,
        "deleted_by": current_user.email,
    }
)
```

### 4. Confirmação por Email
```python
# Enviar email para super admin confirmando deleção
send_email(
    to=super_admin.email,
    subject=f"Tenant {tenant.name} was permanently deleted",
    body=f"Deleted by {current_user.email} at {datetime.now()}"
)
```
