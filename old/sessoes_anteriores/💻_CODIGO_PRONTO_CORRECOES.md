# 💻 Código Pronto - Correções Restantes

## ✅ Status: 2/13 Corrigidos

- ✅ Edição de Projeto
- ✅ Especificação Abre
- ⏳ 11 correções restantes

---

## 🔴 CORREÇÃO 3: Progress Step Não Fica Verde

### Arquivo: `frontend/src/pages/ProjectDetail.tsx`

**Problema**: Step de especificação não fica verde mesmo com documento gerado.

**Localizar a função `fetchProject`** e modificar a verificação:

```typescript
const fetchProject = async () => {
  try {
    setLoading(true)
    const { data } = await api.get(`/projects/${id}`)
    setProject(data)
    
    // Carregar documentos
    const { data: documents } = await api.get(`/projects/${id}/documents`)
    
    // Verificar especificação (CORRIGIDO)
    const hasSpec = documents.some((d: any) => 
      (d.category === 'SPECIFICATION' || d.category === 'specification') && 
      d.is_generated === true
    )
    
    // Verificar arquitetura (CORRIGIDO)
    const hasArch = documents.some((d: any) => 
      d.category === 'architecture' && 
      d.is_generated === true
    )
    
    setHasSpecification(hasSpec)
    setHasArchitecture(hasArch)
    
    console.log('📊 Documents check:', { 
      total: documents.length, 
      hasSpec, 
      hasArch,
      categories: documents.map((d: any) => d.category)
    })
    
    // ... resto do código
  } catch (error) {
    console.error('Failed to load project:', error)
  } finally {
    setLoading(false)
  }
}
```

**Teste**: Recarregue a página do projeto e veja se o step fica verde.

---

## 🔴 CORREÇÃO 4: Work Item - Mudança de Status

### Arquivo: `frontend/src/pages/WorkItemDetail.tsx`

**Problema**: Não há forma de mudar o status do work item.

**1. Adicionar estado (se não existir)**:
```typescript
const [workItem, setWorkItem] = useState<any>(null)
```

**2. Adicionar função**:
```typescript
const handleStatusChange = async (newStatus: string) => {
  try {
    await api.post(`/work-items/${id}/transition`, {
      to_state: newStatus
    })
    await fetchWorkItem()
    alert('Status updated successfully!')
  } catch (error: any) {
    const message = error.response?.data?.detail || 'Failed to change status'
    alert(message)
    console.error('Error changing status:', error)
  }
}
```

**3. Adicionar no JSX** (procure onde mostra o status atual e substitua):
```typescript
<div className="mb-4">
  <label className="block text-sm font-medium text-gray-700 mb-1">
    Status
  </label>
  <select
    value={workItem.status}
    onChange={(e) => handleStatusChange(e.target.value)}
    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
  >
    <option value="draft">Draft</option>
    <option value="in_review">In Review</option>
    <option value="approved">Approved</option>
    <option value="in_progress">In Progress</option>
    <option value="done">Done</option>
  </select>
</div>
```

**Teste**: Abra um work item e mude o status no dropdown.

---

## 🔴 CORREÇÃO 5: Assigned To Não Funciona

### Arquivo: `frontend/src/pages/WorkItemDetail.tsx`

**1. Adicionar estado**:
```typescript
const [users, setUsers] = useState<any[]>([])
```

**2. Adicionar no useEffect**:
```typescript
useEffect(() => {
  if (id) {
    fetchWorkItem()
    loadUsers()  // ADICIONAR ESTA LINHA
  }
}, [id])
```

**3. Adicionar função para carregar usuários**:
```typescript
const loadUsers = async () => {
  try {
    const { data } = await api.get('/users')
    setUsers(data)
  } catch (error) {
    console.error('Failed to load users:', error)
  }
}
```

**4. Adicionar função para mudar assignee**:
```typescript
const handleAssigneeChange = async (userId: string) => {
  try {
    await api.patch(`/work-items/${id}`, {
      assignee_id: userId || null
    })
    await fetchWorkItem()
    alert('Assignee updated successfully!')
  } catch (error: any) {
    const message = error.response?.data?.detail || 'Failed to assign'
    alert(message)
    console.error('Error assigning:', error)
  }
}
```

**5. Adicionar no JSX** (procure onde mostra "Unassigned" e substitua):
```typescript
<div className="mb-4">
  <label className="block text-sm font-medium text-gray-700 mb-1">
    Assigned To
  </label>
  <select
    value={workItem.assignee_id || ''}
    onChange={(e) => handleAssigneeChange(e.target.value)}
    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
  >
    <option value="">Unassigned</option>
    {users.map(user => (
      <option key={user.id} value={user.id}>
        {user.full_name || user.email}
      </option>
    ))}
  </select>
</div>
```

**Teste**: Abra um work item e selecione um usuário.

---

## 🔴 CORREÇÃO 6: Submit for Review com Erro

### Arquivo: `frontend/src/pages/WorkItemDetail.tsx`

**Localizar a função `handleSubmitForReview`** (ou similar) e substituir:

```typescript
const handleSubmitForReview = async () => {
  try {
    await api.post(`/work-items/${id}/transition`, {
      to_state: 'in_review'
    })
    await fetchWorkItem()
    alert('Submitted for review successfully!')
  } catch (error: any) {
    // Melhor error handling
    let message = 'Failed to submit for review'
    
    if (error.response?.data?.detail) {
      message = error.response.data.detail
    } else if (error.message) {
      message = error.message
    }
    
    alert(message)
    console.error('Error submitting for review:', error)
  }
}
```

**Teste**: Clique em "Submit for Review" e veja mensagem clara.

---

## 🟡 CORREÇÃO 7: AI Stats Vazio

### Comando no Terminal

```bash
uv run python scripts/migrate_ai_stats.py
```

**Teste**: Gere alguns requisitos/specs e veja em `/ai-stats`

---

## 🟡 CORREÇÃO 8: Formatação de Requisitos

### Arquivo: `frontend/src/pages/WorkItemDetail.tsx`

**Adicionar componente** (no início do arquivo, antes do componente principal):

```typescript
const RequirementDetails = ({ requirement }: { requirement: any }) => {
  const formatUserStory = (story: any) => {
    if (typeof story === 'string') return story
    if (story.as_a && story.i_want && story.so_that) {
      return `As a ${story.as_a}, I want ${story.i_want}, so that ${story.so_that}`
    }
    return JSON.stringify(story)
  }
  
  const getPriorityColor = (priority: string) => {
    switch (priority?.toLowerCase()) {
      case 'high': return 'bg-red-100 text-red-800'
      case 'medium': return 'bg-yellow-100 text-yellow-800'
      case 'low': return 'bg-green-100 text-green-800'
      default: return 'bg-gray-100 text-gray-800'
    }
  }
  
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 mb-4 shadow-sm">
      <div className="flex items-start justify-between mb-3">
        <h4 className="text-lg font-semibold text-gray-900">
          {requirement.title}
        </h4>
        {requirement.priority && (
          <span className={`px-3 py-1 rounded-full text-xs font-medium ${getPriorityColor(requirement.priority)}`}>
            {requirement.priority}
          </span>
        )}
      </div>
      
      {requirement.user_story && (
        <div className="bg-blue-50 border-l-4 border-blue-500 p-3 mb-3 rounded">
          <p className="text-sm font-medium text-blue-900 mb-1">User Story</p>
          <p className="text-sm text-blue-800">
            {formatUserStory(requirement.user_story)}
          </p>
        </div>
      )}
      
      {requirement.acceptance_criteria && requirement.acceptance_criteria.length > 0 && (
        <div>
          <p className="text-sm font-medium text-gray-900 mb-2">Acceptance Criteria</p>
          <ul className="space-y-2">
            {requirement.acceptance_criteria.map((criteria: any, i: number) => (
              <li key={i} className="flex items-start">
                <span className="flex-shrink-0 w-6 h-6 flex items-center justify-center bg-green-100 text-green-800 rounded-full text-xs font-medium mr-2 mt-0.5">
                  {i + 1}
                </span>
                <span className="text-sm text-gray-700 flex-1">
                  {typeof criteria === 'string' ? criteria : JSON.stringify(criteria)}
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
```

**Usar no JSX** (procure onde renderiza requirements):

```typescript
{workItem.requirements && workItem.requirements.length > 0 && (
  <div className="mt-6">
    <h3 className="text-lg font-semibold mb-4 text-gray-900">Requirements</h3>
    {workItem.requirements.map((req: any, index: number) => (
      <RequirementDetails key={index} requirement={req} />
    ))}
  </div>
)}
```

**Teste**: Abra um work item com requisitos e veja formatação melhorada.

---

## 📋 Checklist de Aplicação

### Críticas (P0)
- [ ] 3. Progress Step fica verde
- [ ] 4. Mudança de status
- [ ] 5. Assigned to
- [ ] 6. Submit for review

### Importantes (P1)
- [ ] 7. AI Stats (executar migração)
- [ ] 8. Formatação requisitos

### Testes
- [ ] Testar cada correção
- [ ] Verificar se não quebrou nada
- [ ] Reportar resultados

---

## 💡 Dicas

1. **Aplique uma correção por vez**
2. **Teste antes de passar para próxima**
3. **Use Ctrl+F para encontrar o código**
4. **Salve antes de testar**

---

## 🚀 Após Aplicar

Me avise:
- ✅ Quais funcionaram
- ❌ Quais tiveram problema
- 🤔 Dúvidas

Vou ajudar com qualquer problema! 💪

---

**Data**: 24/02/2026  
**Hora**: 13:15  
**Status**: ✅ Código Pronto para Aplicar
