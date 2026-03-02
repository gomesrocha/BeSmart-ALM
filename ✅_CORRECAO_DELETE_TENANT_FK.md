# ✅ Correção: Delete Tenant com Foreign Keys

## Problema

Ao tentar deletar um tenant que tinha projetos, ocorria erro:

```
ForeignKeyViolationError: update or delete on table "user" violates 
foreign key constraint "project_created_by_fkey" on table "project"
```

## Causa

A ordem de deleção estava incorreta. Tentávamos deletar usuários antes de deletar os projetos que os referenciam através da foreign key `created_by`.

## Solução

Corrigida a ordem de deleção para respeitar as foreign keys:

### Ordem Correta de Deleção

```python
# 1. User Roles (associações)
# 2. API Tokens
# 3. Audit Logs
# 4. Work Items (antes de projetos)
# 5. Projects (antes de usuários - pois referenciam created_by)
# 6. Users
# 7. Roles
# 8. Tenant
```

### Código Implementado

```python
@router.delete("/{tenant_id}", status_code=status.HTTP_204_NO_CONTENT)
@require_super_admin()
async def delete_tenant_permanently(
    tenant_id: UUID,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    """Permanently delete tenant and all related data."""
    
    try:
        # 1. Delete user roles
        result = await session.execute(
            select(UserRole).join(User).where(User.tenant_id == tenant_id)
        )
        user_roles = result.scalars().all()
        for ur in user_roles:
            await session.delete(ur)
        
        # 2. Delete API tokens
        result = await session.execute(
            select(APIToken).where(APIToken.tenant_id == tenant_id)
        )
        tokens = result.scalars().all()
        for token in tokens:
            await session.delete(token)
        
        # 3. Delete audit logs
        result = await session.execute(
            select(AuditLog).where(AuditLog.tenant_id == tenant_id)
        )
        logs = result.scalars().all()
        for log in logs:
            await session.delete(log)
        
        # 4. Delete work items (before projects)
        try:
            from services.work_item.models import WorkItem
            result = await session.execute(
                select(WorkItem).where(WorkItem.tenant_id == tenant_id)
            )
            work_items = result.scalars().all()
            for wi in work_items:
                await session.delete(wi)
        except ImportError:
            pass  # WorkItem model may not exist yet
        
        # 5. Delete projects (before users!)
        try:
            from services.project.models import Project
            result = await session.execute(
                select(Project).where(Project.tenant_id == tenant_id)
            )
            projects = result.scalars().all()
            for project in projects:
                await session.delete(project)
        except ImportError:
            pass  # Project model may not exist yet
        
        # 6. Delete users (after projects)
        result = await session.execute(
            select(User).where(User.tenant_id == tenant_id)
        )
        users = result.scalars().all()
        for user in users:
            await session.delete(user)
        
        # 7. Delete roles
        result = await session.execute(
            select(Role).where(Role.tenant_id == tenant_id)
        )
        roles = result.scalars().all()
        for role in roles:
            await session.delete(role)
        
        # 8. Finally, delete tenant
        await session.delete(tenant)
        await session.commit()
        
    except Exception as e:
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete tenant: {str(e)}"
        )
```

## Por Que Esta Ordem?

### Foreign Keys no Sistema

```
WorkItem → Project (project_id FK)
Project → User (created_by FK)
User → Tenant (tenant_id FK)
Role → Tenant (tenant_id FK)
UserRole → User (user_id FK)
UserRole → Role (role_id FK)
```

### Regra Geral

**Sempre delete "filhos" antes de "pais"**

Se A referencia B (A tem FK para B), delete A antes de B.

### Exemplo Prático

```
WorkItem.project_id → Project.id
  ↓ Delete WorkItems primeiro

Project.created_by → User.id
  ↓ Delete Projects primeiro

User.tenant_id → Tenant.id
  ↓ Delete Users primeiro

Tenant
  ↓ Delete Tenant por último
```

## Proteções Implementadas

### 1. Try/Except para Imports Opcionais

```python
try:
    from services.work_item.models import WorkItem
    # Delete work items
except ImportError:
    pass  # Model may not exist yet
```

Isso permite que o código funcione mesmo se alguns modelos ainda não existirem.

### 2. Rollback em Caso de Erro

```python
except Exception as e:
    await session.rollback()
    raise HTTPException(...)
```

Se qualquer deleção falhar, todas as mudanças são revertidas (transação atômica).

### 3. Mensagem de Erro Detalhada

```python
detail=f"Failed to delete tenant: {str(e)}"
```

O erro original é incluído na resposta para facilitar debug.

## Testando

### Teste 1: Tenant com Projetos

```bash
# 1. Crie um tenant com admin
# 2. Faça login como admin do tenant
# 3. Crie alguns projetos
# 4. Crie alguns work items
# 5. Faça logout
# 6. Faça login como super admin
# 7. Delete o tenant
# ✅ Deve deletar tudo sem erros
```

### Teste 2: Verificar Deleção Completa

```sql
-- Após deletar tenant, verificar no banco:

SELECT COUNT(*) FROM tenant WHERE id = '<tenant_id>';
-- Deve retornar 0

SELECT COUNT(*) FROM "user" WHERE tenant_id = '<tenant_id>';
-- Deve retornar 0

SELECT COUNT(*) FROM project WHERE tenant_id = '<tenant_id>';
-- Deve retornar 0

SELECT COUNT(*) FROM work_item WHERE tenant_id = '<tenant_id>';
-- Deve retornar 0
```

### Teste 3: Rollback em Erro

```bash
# Simular erro no meio da deleção
# (pode ser feito desconectando o banco temporariamente)
# ✅ Nenhum dado deve ser deletado (rollback)
```

## Arquivos Modificados

1. ✅ `services/identity/tenant_router.py`
   - Corrigida ordem de deleção
   - Adicionada deleção de Projects e WorkItems
   - Melhorado tratamento de erros

## Status

🟢 **CORRIGIDO** - Delete tenant agora funciona mesmo com projetos e work items!

## Melhorias Futuras (Opcional)

### 1. Deleção em Cascata no Banco

Configurar CASCADE no banco de dados:

```sql
ALTER TABLE project 
DROP CONSTRAINT project_created_by_fkey,
ADD CONSTRAINT project_created_by_fkey 
  FOREIGN KEY (created_by) 
  REFERENCES "user"(id) 
  ON DELETE CASCADE;
```

Vantagem: Banco cuida da ordem automaticamente.

### 2. Soft Delete para Projetos

Ao invés de deletar, marcar como deletado:

```python
project.is_deleted = True
project.deleted_at = datetime.now()
```

Vantagem: Possível recuperar dados.

### 3. Backup Antes de Deletar

```python
# Fazer backup antes de deletar
backup_data = {
    "tenant": tenant_to_dict(tenant),
    "users": [user_to_dict(u) for u in users],
    "projects": [project_to_dict(p) for p in projects],
    # ...
}
save_backup(f"tenant_{tenant_id}_backup.json", backup_data)

# Depois deletar
delete_tenant(tenant_id)
```

### 4. Job Assíncrono

Para tenants grandes, fazer deleção em background:

```python
# Marcar para deleção
tenant.marked_for_deletion = True
await session.commit()

# Job em background deleta depois
background_tasks.add_task(delete_tenant_data, tenant_id)
```

## Lições Aprendidas

1. **Sempre respeite foreign keys** - Delete filhos antes de pais
2. **Use transações** - Rollback se algo der errado
3. **Teste com dados reais** - Tenants vazios não revelam problemas de FK
4. **Documente a ordem** - Facilita manutenção futura
5. **Considere CASCADE** - Pode simplificar o código
