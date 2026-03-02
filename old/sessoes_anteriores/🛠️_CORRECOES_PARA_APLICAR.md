# 🛠️ Correções Para Aplicar - Guia Completo

Este documento contém todas as correções necessárias, organizadas por prioridade, com código pronto para aplicar.

---

## 🔴 CORREÇÃO 1: Edição de Projeto (P0)

### Problema
Ao editar projeto, alerta diz "salvo" mas dados não persistem (AWS → OCI não muda).

### Solução

#### Backend: `services/project/router.py`

Adicione o import no topo:
```python
from sqlalchemy.orm.attributes import flag_modified
```

Modifique a função `update_project`:
```python
@router.patch("/{project_id}")
async def update_project(
    project_id: UUID,
    update_data: ProjectUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """Update a project."""
    # Get project
    project = await session.get(Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Check access
    if project.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update basic fields
    if update_data.name is not None:
        project.name = update_data.name
    if update_data.description is not None:
        project.description = update_data.description
    if update_data.status is not None:
        project.status = update_data.status
    
    # Update settings (IMPORTANTE!)
    if update_data.settings is not None:
        if project.settings is None:
            project.settings = {}
        project.settings.update(update_data.settings)
        flag_modified(project, "settings")  # Marca como modificado para o SQLAlchemy
    
    project.updated_at = datetime.utcnow()
    
    await session.commit()
    await session.refresh(project)
    
    return project
```

#### Frontend: `frontend/src/pages/ProjectDetail.tsx`

Modifique a função `onEditProject`:
```typescript
const onEditProject = async (data: EditProjectForm) => {
  console.log('📝 Editing project with data:', data)
  try {
    const payload = {
      name: data.name,
      description: data.description,
      status: data.status,
      settings: {
        target_cloud: data.target_cloud,
        mps_br_level: data.mps_br_level
      }
    }
    console.log('📤 Sending payload:', payload)
    
    await api.patch(`/projects/${id}`, payload)
    console.log('✅ Project updated successfully')
    
    setShowEditModal(false)
    
    // IMPORTANTE: Recarregar o projeto
    await fetchProject()
    
    alert('Project updated successfully!')
  } catch (error: any) {
    console.error('❌ Failed to update project:', error)
    console.error('Error response:', error.response?.data)
    alert(error.response?.data?.detail || 'Failed to update project')
  }
}
```

### Teste
1. Edite um projeto
2. Mude AWS para OCI
3. Salve
4. Verifique se mudou na tela

---

## 🔴 CORREÇÃO 2: Especificação Não Abre (P0)

### Problema
Especificação gerada não abre, retorna "Failed to load document".

### Solução

#### Backend: `services/specification/router.py`

Verifique se está retornando o `document_id` como string:
```python
return {
    "specification": specification_content,
    "document_id": str(doc.id),  # Converter para string
    "message": "Specification generated successfully"
}
```

#### Frontend: `frontend/src/pages/ProjectDetail.tsx`

Na função `handleGenerateSpec`, adicione navegação:
```typescript
const handleGenerateSpec = async () => {
  setGeneratingSpec(true)
  setError('')
  try {
    const response = await api.post('/specification/generate', {
      project_id: id
    })
    setSpecContent(response.data.specification)
    setSpecDocumentId(response.data.document_id)
    
    // Recarregar projeto
    await fetchProject()
    
    // Navegar para o documento
    if (response.data.document_id) {
      navigate(`/projects/${id}/documents/${response.data.document_id}`)
    }
  } catch (err: any) {
    setError(err.response?.data?.detail || 'Failed to generate specification')
    console.error('Failed to generate specification:', err)
  } finally {
    setGeneratingSpec(false)
  }
}
```

### Teste
1. Gere uma especificação
2. Clique para abrir
3. Deve navegar para a página do documento

---

## 🔴 CORREÇÃO 3: Work Item - Mudança de Status (P0)

### Problema
Não há forma de mudar o status do work item.

### Solução

#### Frontend: `frontend/src/pages/WorkItemDetail.tsx`

Adicione um dropdown de status:

```typescript
// No JSX, adicione após o campo de tipo:
<div>
  <label className="block text-sm font-medium text-gray-700 mb-1">
    Status
  </label>
  <select
    value={workItem.status}
    onChange={(e) => handleStatusChange(e.target.value)}
    className="input w-full"
  >
    <option value="draft">Draft</option>
    <option value="in_review">In Review</option>
    <option value="approved">Approved</option>
    <option value="in_progress">In Progress</option>
    <option value="done">Done</option>
  </select>
</div>

// Adicione a função:
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
    console.error('Error:', error)
  }
}
```

### Teste
1. Abra um work item
2. Mude o status no dropdown
3. Verifique se salvou

---

## 🔴 CORREÇÃO 4: Assigned To (P0)

### Problema
Assigned To sempre fica "Unassigned", não consegue atribuir.

### Solução

#### Frontend: `frontend/src/pages/WorkItemDetail.tsx`

```typescript
// Adicione no estado:
const [users, setUsers] = useState<any[]>([])

// Adicione no useEffect:
useEffect(() => {
  if (id) {
    fetchWorkItem()
    loadUsers()
  }
}, [id])

// Adicione a função:
const loadUsers = async () => {
  try {
    const { data } = await api.get('/users')
    setUsers(data)
  } catch (error) {
    console.error('Failed to load users:', error)
  }
}

// No JSX, substitua o campo Assigned To:
<div>
  <label className="block text-sm font-medium text-gray-700 mb-1">
    Assigned To
  </label>
  <select
    value={workItem.assignee_id || ''}
    onChange={(e) => handleAssigneeChange(e.target.value)}
    className="input w-full"
  >
    <option value="">Unassigned</option>
    {users.map(user => (
      <option key={user.id} value={user.id}>
        {user.full_name || user.email}
      </option>
    ))}
  </select>
</div>

// Adicione a função:
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
    console.error('Error:', error)
  }
}
```

### Teste
1. Abra um work item
2. Selecione um usuário no dropdown
3. Verifique se salvou

---

## 🔴 CORREÇÃO 5: Submit for Review (P0)

### Problema
Retorna "object object" ao invés de mensagem clara.

### Solução

#### Frontend: `frontend/src/pages/WorkItemDetail.tsx`

Melhore o error handling:
```typescript
const handleSubmitForReview = async () => {
  try {
    await api.post(`/work-items/${id}/transition`, {
      to_state: 'in_review'
    })
    await fetchWorkItem()
    alert('Submitted for review successfully!')
  } catch (error: any) {
    const message = error.response?.data?.detail || 
                   error.message || 
                   'Failed to submit for review'
    alert(message)
    console.error('Error submitting for review:', error)
  }
}
```

### Teste
1. Abra um work item
2. Clique em "Submit for Review"
3. Deve mostrar mensagem clara

---

## 🟡 CORREÇÃO 6: AI Stats Vazio (P1)

### Problema
AI Stats sempre mostra "No statistics available".

### Solução

#### 1. Executar Migração
```bash
uv run python scripts/migrate_ai_stats.py
```

#### 2. Verificar Tabela
```bash
docker exec -it bsmart-postgres psql -U bsmart -d bsmart_alm -c "SELECT COUNT(*) FROM ai_usage_stats;"
```

#### 3. Testar Tracking
Gere alguns requisitos/especificações e verifique se aparecem em AI Stats.

---

## 🟡 CORREÇÃO 7: Progress Steps (P1)

### Problema
Steps não ficam verdes mesmo com especificação gerada.

### Solução

#### Frontend: `frontend/src/pages/ProjectDetail.tsx`

Na função `fetchProject`, adicione verificação correta:
```typescript
const fetchProject = async () => {
  try {
    setLoading(true)
    const { data } = await api.get(`/projects/${id}`)
    setProject(data)
    
    // Carregar documentos
    const { data: documents } = await api.get(`/projects/${id}/documents`)
    
    // Verificar especificação
    const hasSpec = documents.some((d: any) => 
      d.category === 'SPECIFICATION' && d.is_generated === true
    )
    
    // Verificar arquitetura
    const hasArch = documents.some((d: any) => 
      d.category === 'architecture' && d.is_generated === true
    )
    
    setHasSpecification(hasSpec)
    setHasArchitecture(hasArch)
    
    // ... resto do código
  } catch (error) {
    console.error('Failed to load project:', error)
  } finally {
    setLoading(false)
  }
}
```

### Teste
1. Gere uma especificação
2. Verifique se o step fica verde

---

## 🟡 CORREÇÃO 8: Documentos Uploaded (P1)

### Problema
Documentos feitos upload não aparecem na lista.

### Solução

#### Backend: `services/project/document_router.py`

Verifique se a query não está filtrando incorretamente:
```python
@router.get("/{project_id}/documents")
async def list_documents(
    project_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """List all documents for a project."""
    query = select(ProjectDocument).where(
        ProjectDocument.project_id == project_id,
        ProjectDocument.tenant_id == current_user.tenant_id
    ).order_by(ProjectDocument.created_at.desc())
    
    result = await session.execute(query)
    documents = result.scalars().all()
    
    return documents
```

### Teste
1. Faça upload de um documento
2. Verifique se aparece na lista

---

## 🟡 CORREÇÃO 9: Formatação de Requisitos (P1)

### Problema
Details dos requisitos não ficam visualmente bonitos.

### Solução

#### Frontend: `frontend/src/pages/WorkItemDetail.tsx`

Adicione CSS melhor para os requisitos:
```typescript
// Componente de formatação
const RequirementDetails = ({ requirement }: { requirement: any }) => {
  const formatUserStory = (story: any) => {
    if (typeof story === 'string') return story
    return `As a ${story.as_a}, I want ${story.i_want}, so that ${story.so_that}`
  }
  
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 mb-4">
      <div className="flex items-start justify-between mb-3">
        <h4 className="text-lg font-semibold text-gray-900">
          {requirement.title}
        </h4>
        <span className={`px-3 py-1 rounded-full text-xs font-medium ${
          requirement.priority === 'high' ? 'bg-red-100 text-red-800' :
          requirement.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
          'bg-green-100 text-green-800'
        }`}>
          {requirement.priority}
        </span>
      </div>
      
      {requirement.user_story && (
        <div className="bg-blue-50 border-l-4 border-blue-500 p-3 mb-3">
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
                <span className="flex-shrink-0 w-6 h-6 flex items-center justify-center bg-green-100 text-green-800 rounded-full text-xs font-medium mr-2">
                  {i + 1}
                </span>
                <span className="text-sm text-gray-700">
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

// Use no JSX:
{workItem.requirements && workItem.requirements.length > 0 && (
  <div className="mt-6">
    <h3 className="text-lg font-semibold mb-4">Requirements</h3>
    {workItem.requirements.map((req: any, index: number) => (
      <RequirementDetails key={index} requirement={req} />
    ))}
  </div>
)}
```

### Teste
1. Abra um work item com requisitos
2. Verifique se está visualmente melhor

---

## 📝 Checklist de Aplicação

### Correções Críticas (P0)
- [ ] 1. Edição de projeto
- [ ] 2. Especificação não abre
- [ ] 3. Mudança de status
- [ ] 4. Assigned to
- [ ] 5. Submit for review

### Correções Importantes (P1)
- [ ] 6. AI Stats vazio
- [ ] 7. Progress steps
- [ ] 8. Documentos uploaded
- [ ] 9. Formatação requisitos

### Testes
- [ ] Testar cada correção individualmente
- [ ] Testar fluxo completo
- [ ] Verificar se não quebrou nada

---

## 🚀 Ordem de Aplicação Recomendada

1. **Backend primeiro**: Correções 1, 2, 8
2. **Frontend depois**: Correções 3, 4, 5, 7, 9
3. **Infraestrutura**: Correção 6
4. **Testes completos**

---

## 💡 Dicas

1. **Faça uma correção por vez**
2. **Teste antes de passar para a próxima**
3. **Commit após cada correção funcional**
4. **Mantenha backup antes de começar**

---

## 📞 Se Precisar de Ajuda

Se encontrar problemas:
1. Verifique os logs do backend
2. Verifique o console do navegador
3. Teste a API diretamente com curl
4. Consulte os documentos de troubleshooting

---

**Data**: 24/02/2026  
**Versão**: 1.0  
**Status**: ✅ Pronto para Aplicar
