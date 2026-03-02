# 📋 Plano de Correções e Melhorias - Bsmart-ALM

## 🎯 Objetivo

Corrigir todos os bugs críticos e implementar melhorias para tornar o sistema 100% funcional e com boa experiência de usuário.

---

## 📊 Visão Geral

### Status Atual
- ✗ 13 bugs identificados
- ✗ 5 bugs críticos (P0)
- ✗ 6 bugs importantes (P1)
- ✗ 2 bugs médios (P2)
- ✗ ~40% do fluxo funcional

### Meta
- ✅ 0 bugs críticos
- ✅ 0 bugs importantes
- ✅ 100% do fluxo funcional
- ✅ Testes automatizados
- ✅ Documentação atualizada

---

## 🗓️ Cronograma

### Sprint de Correções (5-7 dias)

#### Dia 1 - Correções Urgentes
- [x] Fix enum arquitetura ✅
- [ ] Fix AI Stats migration
- [x] Fix navegação especificação ✅
- [x] Fix edição de projeto ✅

#### Dia 2 - Work Items
- [x] Fix mudança de status ✅
- [x] Fix assigned to ✅
- [x] Fix submit for review ✅
- [x] Melhorar formatação requisitos ✅

#### Dia 3 - Kanban e Documentos
- [x] Fazer Kanban funcionar ✅
- [ ] Fix documentos uploaded
- [x] Fix progress steps ✅

#### Dia 4-5 - Funcionalidades Faltantes
- [ ] Implementar Settings
- [ ] Completar multi-tenant
- [ ] Adicionar testes

#### Dia 6-7 - Polimento e Testes
- [ ] Testes E2E completos
- [ ] Atualizar documentação
- [ ] Code review
- [ ] Deploy

---

## 📝 Tarefas Detalhadas

### 🔴 FASE 1: Correções Críticas (Dia 1)

#### 1.1 Fix Enum Arquitetura
**Problema**: `invalid input value for enum documentcategory: "ARCHITECTURE"`

**Solução**:
```bash
# Executar script existente
uv run python scripts/fix_architecture_enum.py
```

**Arquivos**:
- `scripts/fix_architecture_enum.py` (já existe)

**Tempo**: 15 minutos

---

#### 1.2 Fix AI Stats Migration
**Problema**: AI Stats sempre vazio

**Solução**:
```bash
# Executar migração
uv run python scripts/migrate_ai_stats.py

# Verificar tabela
docker exec -it bsmart-alm-postgres-1 psql -U postgres -d bsmart_alm -c "\d ai_usage_stats"
```

**Arquivos**:
- `scripts/migrate_ai_stats.py` (já existe)

**Tempo**: 15 minutos

---

#### 1.3 Fix Navegação para Especificação
**Problema**: Especificação gerada não abre

**Solução**:
1. Verificar se documento está sendo salvo
2. Corrigir retorno do document_id
3. Corrigir navegação no frontend

**Arquivos**:
- `services/specification/router.py`
- `frontend/src/pages/ProjectDetail.tsx`

**Código**:
```python
# Backend - Garantir que retorna document_id
return {
    "specification": spec_content,
    "document_id": str(document.id),  # Converter para string
    "message": "Specification generated successfully"
}
```

```typescript
// Frontend - Navegar corretamente
if (specDoc && specDoc.id) {
  navigate(`/projects/${id}/documents/${specDoc.id}`)
}
```

**Tempo**: 1 hora

---

#### 1.4 Fix Edição de Projeto
**Problema**: Dados não são salvos (AWS → OCI não muda)

**Solução**:
1. Verificar payload no frontend
2. Corrigir backend para processar settings
3. Adicionar refresh após save

**Arquivos**:
- `services/project/router.py`
- `frontend/src/pages/ProjectDetail.tsx`

**Código**:
```python
# Backend - Processar settings corretamente
@router.patch("/{project_id}")
async def update_project(
    project_id: UUID,
    update_data: ProjectUpdate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    project = await session.get(Project, project_id)
    
    # Atualizar campos básicos
    if update_data.name:
        project.name = update_data.name
    if update_data.description:
        project.description = update_data.description
    if update_data.status:
        project.status = update_data.status
    
    # Atualizar settings
    if update_data.settings:
        if not project.settings:
            project.settings = {}
        project.settings.update(update_data.settings)
        flag_modified(project, "settings")
    
    await session.commit()
    await session.refresh(project)
    
    return project
```

```typescript
// Frontend - Refresh após save
const onEditProject = async (data: EditProjectForm) => {
  try {
    await api.patch(`/projects/${id}`, {
      name: data.name,
      description: data.description,
      status: data.status,
      settings: {
        target_cloud: data.target_cloud,
        mps_br_level: data.mps_br_level
      }
    })
    
    setShowEditModal(false)
    await fetchProject() // Refresh
    alert('Project updated successfully!')
  } catch (error) {
    console.error('Failed to update:', error)
    alert('Failed to update project')
  }
}
```

**Tempo**: 2 horas

---

### 🟡 FASE 2: Work Items (Dia 2)

#### 2.1 Fix Mudança de Status
**Problema**: Não há forma de mudar status

**Solução**: Adicionar dropdown de status na tela de detalhes

**Arquivos**:
- `frontend/src/pages/WorkItemDetail.tsx`

**Código**:
```typescript
// Adicionar dropdown de status
<div>
  <label>Status</label>
  <select
    value={workItem.status}
    onChange={(e) => handleStatusChange(e.target.value)}
    className="input"
  >
    <option value="draft">Draft</option>
    <option value="in_review">In Review</option>
    <option value="approved">Approved</option>
    <option value="in_progress">In Progress</option>
    <option value="done">Done</option>
  </select>
</div>

const handleStatusChange = async (newStatus: string) => {
  try {
    await api.post(`/work-items/${id}/transition`, {
      to_state: newStatus
    })
    await fetchWorkItem()
  } catch (error) {
    alert('Failed to change status')
  }
}
```

**Tempo**: 1 hora

---

#### 2.2 Fix Assigned To
**Problema**: Sempre fica "Unassigned"

**Solução**: 
1. Carregar lista de usuários
2. Adicionar dropdown funcional
3. Salvar assignee_id

**Arquivos**:
- `frontend/src/pages/WorkItemDetail.tsx`

**Código**:
```typescript
const [users, setUsers] = useState<User[]>([])

useEffect(() => {
  loadUsers()
}, [])

const loadUsers = async () => {
  const { data } = await api.get('/users')
  setUsers(data)
}

<select
  value={workItem.assignee_id || ''}
  onChange={(e) => handleAssigneeChange(e.target.value)}
  className="input"
>
  <option value="">Unassigned</option>
  {users.map(user => (
    <option key={user.id} value={user.id}>
      {user.full_name || user.email}
    </option>
  ))}
</select>

const handleAssigneeChange = async (userId: string) => {
  try {
    await api.patch(`/work-items/${id}`, {
      assignee_id: userId || null
    })
    await fetchWorkItem()
  } catch (error) {
    alert('Failed to assign')
  }
}
```

**Tempo**: 1.5 horas

---

#### 2.3 Fix Submit for Review
**Problema**: Retorna "object object"

**Solução**: Melhorar error handling

**Arquivos**:
- `frontend/src/pages/WorkItemDetail.tsx`

**Código**:
```typescript
const handleSubmitForReview = async () => {
  try {
    await api.post(`/work-items/${id}/transition`, {
      to_state: 'in_review'
    })
    await fetchWorkItem()
    alert('Submitted for review successfully!')
  } catch (error: any) {
    const message = error.response?.data?.detail || 'Failed to submit for review'
    alert(message)
    console.error('Error:', error)
  }
}
```

**Tempo**: 30 minutos

---

#### 2.4 Melhorar Formatação de Requisitos
**Problema**: Details não ficam bonitos

**Solução**: Adicionar CSS e estrutura HTML melhor

**Arquivos**:
- `frontend/src/pages/WorkItemDetail.tsx`
- `frontend/src/index.css`

**Código**:
```typescript
// Componente de formatação
const RequirementDetails = ({ requirement }: { requirement: any }) => {
  return (
    <div className="requirement-details">
      <div className="requirement-header">
        <h3>{requirement.title}</h3>
        <span className="priority-badge">{requirement.priority}</span>
      </div>
      
      {requirement.user_story && (
        <div className="user-story">
          <strong>User Story:</strong>
          <p>{formatUserStory(requirement.user_story)}</p>
        </div>
      )}
      
      {requirement.acceptance_criteria && (
        <div className="acceptance-criteria">
          <strong>Acceptance Criteria:</strong>
          <ul>
            {requirement.acceptance_criteria.map((criteria, i) => (
              <li key={i}>{formatCriteria(criteria)}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
```

```css
/* CSS */
.requirement-details {
  padding: 1rem;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  margin-bottom: 1rem;
}

.requirement-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.priority-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 500;
}

.user-story {
  background: #f9fafb;
  padding: 1rem;
  border-radius: 0.375rem;
  margin-bottom: 1rem;
}

.acceptance-criteria ul {
  list-style: disc;
  padding-left: 1.5rem;
}

.acceptance-criteria li {
  margin-bottom: 0.5rem;
}
```

**Tempo**: 1 hora

---

### 🟢 FASE 3: Kanban e Documentos (Dia 3)

#### 3.1 Fazer Kanban Funcionar
**Problema**: Código existe mas não está acessível

**Solução**:
1. Verificar rota no App.tsx
2. Testar drag & drop
3. Corrigir bugs de navegação

**Arquivos**:
- `frontend/src/App.tsx`
- `frontend/src/pages/WorkItemsKanban.tsx`

**Verificações**:
```typescript
// App.tsx - Verificar se rota existe
<Route path="work-items/kanban" element={<WorkItemsKanban />} />

// WorkItems.tsx - Verificar se link existe
<Link to="/work-items/kanban" className="btn-secondary">
  📋 Kanban View
</Link>
```

**Testes**:
1. Acessar /work-items/kanban
2. Arrastar card entre colunas
3. Verificar atualização no backend
4. Verificar filtros

**Tempo**: 2 horas

---

#### 3.2 Fix Documentos Uploaded
**Problema**: Documentos não aparecem na lista

**Solução**: Corrigir query para incluir todos os documentos

**Arquivos**:
- `services/project/document_router.py`
- `frontend/src/pages/ProjectDocumentsPage.tsx`

**Código**:
```python
# Backend - Incluir todos os documentos
@router.get("/{project_id}/documents")
async def list_documents(
    project_id: UUID,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    query = select(ProjectDocument).where(
        ProjectDocument.project_id == project_id,
        ProjectDocument.tenant_id == current_user.tenant_id
    ).order_by(ProjectDocument.created_at.desc())
    
    result = await session.execute(query)
    documents = result.scalars().all()
    
    return documents
```

**Tempo**: 1 hora

---

#### 3.3 Fix Progress Steps
**Problema**: Step não fica verde mesmo com especificação

**Solução**: Corrigir lógica de verificação

**Arquivos**:
- `frontend/src/pages/ProjectDetail.tsx`

**Código**:
```typescript
// Verificar documentos gerados corretamente
const { data: documents } = await api.get(`/projects/${id}/documents`)

const hasSpec = documents.some((d: any) => 
  d.category === 'specification' && d.is_generated === true
)

const hasArch = documents.some((d: any) => 
  d.category === 'architecture' && d.is_generated === true
)

setHasSpecification(hasSpec)
setHasArchitecture(hasArch)
```

**Tempo**: 30 minutos

---

### 🔵 FASE 4: Funcionalidades Faltantes (Dia 4-5)

#### 4.1 Implementar Settings
**Problema**: Página não existe

**Solução**: Criar página de configurações

**Arquivos**:
- `frontend/src/pages/Settings.tsx` (novo)

**Funcionalidades**:
- Configurações de usuário
- Configurações de tenant
- Preferências de sistema
- Integrações

**Tempo**: 4 horas

---

#### 4.2 Completar Multi-tenant
**Problema**: Sistema não está isolando dados corretamente

**Solução**:
1. Verificar todas as queries
2. Adicionar filtro de tenant_id
3. Testar isolamento

**Arquivos**:
- Todos os routers em `services/*/router.py`

**Verificações**:
```python
# Garantir que todas as queries filtram por tenant_id
query = select(Model).where(
    Model.tenant_id == current_user.tenant_id
)
```

**Tempo**: 6 horas

---

#### 4.3 Adicionar Testes Automatizados
**Problema**: Falta cobertura de testes

**Solução**: Criar testes E2E e unitários

**Arquivos**:
- `tests/test_projects.py`
- `tests/test_work_items.py`
- `tests/test_specifications.py`

**Testes**:
1. Criar projeto
2. Gerar requisitos
3. Gerar especificação
4. Gerar arquitetura
5. Criar work items
6. Mudar status
7. Atribuir usuário

**Tempo**: 8 horas

---

### ✅ FASE 5: Polimento (Dia 6-7)

#### 5.1 Testes E2E Completos
- [ ] Testar fluxo completo
- [ ] Testar todos os bugs corrigidos
- [ ] Testar edge cases
- [ ] Documentar resultados

**Tempo**: 4 horas

---

#### 5.2 Atualizar Documentação
- [ ] Atualizar README
- [ ] Atualizar guias
- [ ] Remover docs desatualizados
- [ ] Adicionar troubleshooting

**Tempo**: 2 horas

---

#### 5.3 Code Review
- [ ] Revisar todas as mudanças
- [ ] Verificar padrões de código
- [ ] Verificar segurança
- [ ] Verificar performance

**Tempo**: 2 horas

---

#### 5.4 Deploy
- [ ] Build de produção
- [ ] Testes em staging
- [ ] Deploy em produção
- [ ] Monitoramento

**Tempo**: 2 horas

---

## 📊 Painel Kanban de Tarefas

### 📋 Backlog
- [ ] Implementar Settings
- [ ] Completar multi-tenant
- [ ] Adicionar mais testes
- [ ] Melhorar documentação

### 🏃 To Do
- [ ] Fix enum arquitetura
- [ ] Fix AI Stats migration
- [ ] Fix navegação especificação
- [ ] Fix edição de projeto

### 🔄 In Progress
- [ ] (Vazio)

### ✅ Done
- [ ] (Vazio)

---

## 🎯 Métricas de Sucesso

### Antes
- ✗ 13 bugs
- ✗ 40% funcional
- ✗ 0 testes automatizados
- ✗ Documentação desatualizada

### Depois (Meta)
- ✅ 0 bugs críticos
- ✅ 100% funcional
- ✅ 80%+ cobertura de testes
- ✅ Documentação atualizada

---

## 📝 Checklist de Validação

### Funcionalidades Básicas
- [ ] Criar projeto
- [ ] Editar projeto (AWS → OCI funciona)
- [ ] Gerar requisitos
- [ ] Gerar especificação
- [ ] Abrir especificação gerada
- [ ] Gerar arquitetura
- [ ] Abrir arquitetura gerada
- [ ] Upload de documento
- [ ] Ver documento uploaded

### Work Items
- [ ] Criar work item
- [ ] Editar work item
- [ ] Mudar status
- [ ] Atribuir usuário
- [ ] Submit for review
- [ ] Ver no Kanban
- [ ] Arrastar no Kanban

### Progress e Stats
- [ ] Progress steps ficam verdes
- [ ] Navegação por steps funciona
- [ ] AI Stats mostra dados
- [ ] Métricas corretas

### Multi-tenant
- [ ] Dados isolados por tenant
- [ ] Usuários não veem dados de outros tenants
- [ ] Queries filtram corretamente

---

## 🚀 Próximos Passos Após Correções

1. **Melhorias de UX**
   - Animações
   - Feedback visual
   - Loading states
   - Error messages melhores

2. **Performance**
   - Otimizar queries
   - Adicionar cache
   - Lazy loading
   - Pagination

3. **Novas Funcionalidades**
   - Notificações
   - Comentários
   - Histórico de mudanças
   - Relatórios

4. **Integrações**
   - Jira
   - GitHub
   - Slack
   - Email

---

**Data de Criação**: 24/02/2026  
**Responsável**: Kiro AI Assistant  
**Status**: 📋 Planejado  
**Início Previsto**: Imediato  
**Conclusão Prevista**: 7 dias
