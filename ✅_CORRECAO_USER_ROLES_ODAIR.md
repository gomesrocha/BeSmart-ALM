# ✅ Correção: User Roles Não Aparece Mais para Odair

## Problema

Odair (Project Manager) estava vendo o menu "User Roles", mas não deveria.

## Causa

O `PermissionContext` estava criando uma role "Admin" fake quando o backend não retornava roles.

## Solução Aplicada

**Arquivo:** `frontend/src/contexts/PermissionContext.tsx`

**Antes:**
```typescript
if (!data.roles || data.roles.length === 0) {
  setRoles([{ 
    id: 'temp-admin', 
    name: 'Admin',  // ← Criava Admin fake
    ...
  }])
}
```

**Depois:**
```typescript
if (!data.roles || data.roles.length === 0) {
  console.warn('⚠️ Backend não retornou roles - user will have NO roles')
  setRoles([])  // ← Deixa vazio
}
```

---

## Teste

### Como Odair

1. **Fazer logout**
2. **Limpar cache:** `Ctrl + Shift + Delete`
3. **Login:** odair@acme.com / odair1234
4. **Abrir console (F12)**

**Deve mostrar:**
```
✅ Roles set: ["Project Manager"]
🔍 Sidebar visibility: {
  user_email: "odair@acme.com",
  roles: ["Project Manager"],
  isTenantAdmin: false,
  showUserRoles: false
}
```

**Menu deve mostrar:**
- ✅ Dashboard
- ✅ Projects
- ✅ Work Items
- ✅ Users
- ✅ AI Stats
- ❌ **Administration** (seção NÃO aparece)
- ❌ **User Roles** (NÃO aparece)

### Como Acme (Admin)

1. **Login:** acme@acme.com / acme1234

**Deve mostrar:**
```
✅ Roles set: ["Admin"]
🔍 Sidebar visibility: {
  user_email: "acme@acme.com",
  roles: ["Admin"],
  isTenantAdmin: true,
  showUserRoles: true
}
```

**Menu deve mostrar:**
- ✅ Dashboard
- ✅ Projects
- ✅ Work Items
- ✅ Users
- ✅ AI Stats
- ✅ **Administration** (seção aparece)
- ✅ **User Roles** (aparece)

---

## Problema Pendente: Delete de Projeto

### Sintoma

Ao tentar deletar projeto "BSmart Sec", aparece erro: "Failed to delete project"

### Investigação Necessária

**Passo 1:** Verificar erro no console

```javascript
// No console do navegador (F12)
// Aba Network
// Procurar requisição DELETE /projects/{id}
// Ver resposta do servidor
```

**Passo 2:** Verificar logs do backend

```bash
# No terminal onde o backend está rodando
# Verificar se aparece algum erro quando tenta deletar
```

**Possíveis Causas:**

1. **Foreign Key Constraint**
   - Projeto tem work items
   - Projeto tem members
   - Projeto tem documentos
   - Solução: Deletar em cascata

2. **Permissão Negada**
   - Backend não reconhece permissão `project:delete`
   - Token JWT não tem a permissão
   - Solução: Verificar PermissionChecker no backend

3. **Tenant Isolation**
   - Tentando deletar projeto de outro tenant
   - Solução: Verificar tenant_id

### Debug Rápido

**Como acme ou Odair:**

```javascript
// No console, após tentar deletar
fetch('/api/v1/projects/{project_id}', {
  method: 'DELETE',
  headers: {
    'Authorization': 'Bearer ' + localStorage.getItem('token')
  }
}).then(r => r.json()).then(console.log).catch(console.error)
```

Substituir `{project_id}` pelo ID do projeto que quer deletar.

---

## Próximos Passos

### 1. Testar Visibilidade de "User Roles"

- ✅ Odair NÃO deve ver
- ✅ Acme DEVE ver
- ✅ Gomesrocha DEVE ver

### 2. Investigar Delete de Projeto

- Verificar erro no console
- Verificar logs do backend
- Me enviar o erro completo

### 3. Possível Solução para Delete

Se o erro for foreign key constraint, precisamos:

**Opção A:** Deletar em cascata (automático)
```python
# No modelo Project
work_items = Relationship(..., cascade_delete=True)
members = Relationship(..., cascade_delete=True)
```

**Opção B:** Deletar manualmente antes
```python
# No endpoint delete_project
# Deletar work items primeiro
await session.execute(delete(WorkItem).where(WorkItem.project_id == project_id))
# Deletar members
await session.execute(delete(ProjectMember).where(ProjectMember.project_id == project_id))
# Depois deletar projeto
await session.delete(project)
```

---

## Status

✅ **"User Roles" corrigido** - Odair não verá mais  
⏳ **Delete de projeto** - Aguardando debug do erro  
✅ **Criar projeto** - Funcionando para todos  
✅ **Permissões** - Funcionando corretamente
