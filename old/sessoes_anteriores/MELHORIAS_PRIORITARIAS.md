# 🎯 Melhorias Prioritárias - Bsmart-ALM

**Data**: 23/02/2026  
**Status**: 📋 **PLANEJAMENTO**

---

## 🔴 CRÍTICAS (Implementar Imediatamente)

### 1. ❌ Edição de Projeto Não Salva Settings
**Problema**: Ao editar target_cloud (AWS→OCI) ou mps_br_level, não salva.  
**Status**: ✅ **JÁ CORRIGIDO** (ver `FIX_PROJECT_EDIT_SETTINGS.md`)  
**Ação**: Reiniciar backend

### 2. ❌ Especificação/Arquitetura Perdida
**Problema**: Não tem botão "Save" no modal, conteúdo se perde ao fechar.  
**Status**: ⚠️ **PARCIALMENTE RESOLVIDO** - Salva automaticamente como documento  
**Ação Necessária**: 
- Adicionar botão "View Saved Document" no modal
- Redirecionar para DocumentViewer após salvar
- Mostrar link clicável na mensagem de sucesso

### 3. ❌ Documentos Anexados Não Aparecem
**Problema**: PDFs/URLs anexados para RAG não aparecem em Documents.  
**Causa**: Provavelmente filtro ou categoria incorreta  
**Ação**: Investigar e corrigir listagem de documentos

### 4. ❌ Progress Steps Não Ficam Verdes
**Problema**: Mesmo gerando especificação, step não fica verde.  
**Causa**: Lógica de verificação não implementada  
**Ação**: Implementar verificação de documentos gerados

### 5. ❌ Botão "Submit for Review" Não Funciona
**Problema**: No WorkItemDetail, botão não faz nada.  
**URL**: http://localhost:3000/work-items/{id}  
**Causa**: Transição de estado não implementada ou com erro  
**Ação**: Corrigir transição draft → review

### 6. ❌ Falta Botão de Aprovação
**Problema**: Work item fica em Draft, não tem como aprovar.  
**Requisito**: Adicionar botão "Approve" para aprovar work items  
**Ação**: Implementar transição review → approved

### 7. ❌ Falta Kanban Board
**Problema**: Não tem visualização Kanban para arrastar work items.  
**Requisito**: Board com colunas: Backlog → Draft → Review → Approved → In Progress → Done  
**Benefício**: Gestão visual e intuitiva  
**Ação**: Criar componente KanbanBoard

---

## 🟡 IMPORTANTES (Implementar em Seguida)

### 8. 🔄 Navegação por Progress Steps
**Requisito**: Clicar nos steps do gráfico para navegar entre etapas.  
**Benefício**: UX mais intuitiva  
**Implementação**:
- Tornar steps clicáveis
- Redirecionar para modal/página correspondente
- Desabilitar steps não disponíveis

### 9. 🔄 Confirmação ao Regenerar
**Requisito**: Perguntar "Refazer ou Atualizar?" ao clicar em gerar novamente.  
**Benefício**: Evita perda de edições  
**Implementação**:
- Verificar se documento já existe
- Mostrar modal de confirmação
- Opções: "Substituir", "Criar Nova Versão", "Cancelar"

### 10. 📄 Visualizar Spec/Arch Depois de Prontas
**Requisito**: Acessar especificação/arquitetura após geração.  
**Status**: ✅ **JÁ IMPLEMENTADO** via Documents  
**Melhoria**: Adicionar atalhos diretos no ProjectDetail

### 11. 📊 Estatísticas de Uso de IA
**Requisito**: Capturar tokens de entrada/saída para calcular custos.  
**Benefício**: Estimar custos com outros modelos (GPT, Claude, etc.)  
**Implementação**:
- Adicionar logging de tokens
- Criar tabela de estatísticas
- Dashboard de custos

### 12. 📥 Export para Markdown
**Requisito**: Exportar documentos gerados como .md  
**Benefício**: Usar em outras ferramentas  
**Implementação**:
- Botão "Download as Markdown"
- Gerar arquivo .md
- Download automático

---

## 🟢 MELHORIAS (Implementar Depois)

### 13. 🏢 Multi-tenant Aprimorado
**Requisito Atual**: Sistema já é multi-tenant  
**Melhoria Solicitada**:
- Cadastro de empresa (tenant)
- Admin da empresa cadastra time
- Super admin acessa todos os tenants

**Implementação**:
- Página de cadastro de tenant
- Hierarquia: Super Admin → Tenant Admin → Users
- Switch entre tenants para super admin

---

## 📋 Priorização

### Sprint 1 (Imediato - 2-3 horas)
1. ✅ Corrigir edição de projeto (FEITO)
2. 🔧 Corrigir botão "Submit for Review" no work item
3. 🔧 Adicionar botão "Approve" no work item
4. ⚠️ Adicionar link para documento salvo nos modais
5. 🔍 Investigar documentos anexados não aparecendo
6. ✅ Corrigir progress steps ficando verdes

### Sprint 2 (Curto Prazo - 1-2 dias)
7. 📋 Implementar Kanban Board para work items
8. 🖱️ Navegação por progress steps clicáveis
9. ❓ Confirmação ao regenerar documentos
10. 🔗 Atalhos diretos para spec/arch no ProjectDetail

### Sprint 3 (Médio Prazo - 2-3 dias)
11. 📊 Sistema de estatísticas de IA
12. 📥 Export para Markdown
13. 🏢 Melhorias em multi-tenancy

---

## 🔧 Detalhamento das Correções

### 2. Link para Documento Salvo

**Problema Atual**:
```
Modal mostra:
"✅ Especificação salva como documento do projeto!"
[Close] [Regenerate] [Copy]
```

**Solução**:
```
Modal mostra:
"✅ Especificação salva como documento do projeto!"
[View Document] [Close] [Regenerate] [Copy]

Ao clicar "View Document":
→ Redireciona para /projects/{id}/documents/{doc_id}
→ Abre DocumentViewer
```

**Implementação**:
- Retornar `document_id` na resposta da API
- Adicionar botão "View Document"
- Usar `navigate()` para redirecionar

---

### 3. Documentos Anexados Não Aparecem

**Investigação Necessária**:
1. Verificar se documentos estão sendo salvos
2. Verificar categoria dos documentos anexados
3. Verificar filtros na listagem
4. Verificar se `is_generated=false` para anexados

**Query de Teste**:
```sql
SELECT id, name, type, category, is_generated, uploaded_at
FROM project_document
WHERE project_id = '{project_id}'
ORDER BY uploaded_at DESC;
```

---

### 4. Progress Steps Ficando Verdes

**Lógica Atual**:
```typescript
{
  id: 'specification',
  label: 'Especificação',
  completed: false, // TODO: Check if spec exists
}
```

**Lógica Nova**:
```typescript
{
  id: 'specification',
  label: 'Especificação',
  completed: hasSpecification, // ✅ Verificar se existe
}
```

**Implementação**:
- Buscar documentos com `category='specification'` e `is_generated=true`
- Se existir, `completed=true`
- Atualizar após gerar

---

### 5. Navegação por Steps

**Implementação**:
```typescript
const handleStepClick = (stepId: string) => {
  switch(stepId) {
    case 'requirements':
      // Scroll para seção de requisitos
      break;
    case 'specification':
      setShowSpecModal(true);
      break;
    case 'architecture':
      setShowArchModal(true);
      break;
    case 'work-items':
      navigate(`/work-items?project_id=${id}`);
      break;
  }
}
```

---

### 6. Confirmação ao Regenerar

**Implementação**:
```typescript
const handleGenerateSpec = async () => {
  // Verificar se já existe
  const existing = await checkExistingSpec(projectId);
  
  if (existing) {
    const action = await showConfirmDialog({
      title: "Especificação já existe",
      message: "O que deseja fazer?",
      options: [
        { label: "Substituir", value: "replace" },
        { label: "Criar Nova Versão", value: "version" },
        { label: "Cancelar", value: "cancel" }
      ]
    });
    
    if (action === "cancel") return;
    // Processar ação escolhida
  }
  
  // Gerar normalmente
}
```

---

### 8. Estatísticas de IA

**Modelo de Dados**:
```python
class AIUsageStats(BaseTenantModel, table=True):
    """AI usage statistics."""
    __tablename__ = "ai_usage_stats"
    
    project_id: UUID
    operation: str  # 'requirements', 'specification', 'architecture'
    model: str  # 'llama3.2', 'gpt-4', etc.
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    duration_seconds: float
    cost_estimate: float  # Estimated cost in USD
    created_at: datetime
```

**Captura**:
```python
# No OllamaClient
async def generate(self, prompt: str, system: str):
    start_time = time.time()
    
    response = await ollama.generate(...)
    
    duration = time.time() - start_time
    
    # Salvar estatísticas
    stats = AIUsageStats(
        project_id=project_id,
        operation=operation,
        model=self.model,
        prompt_tokens=len(prompt.split()),  # Aproximado
        completion_tokens=len(response.split()),
        total_tokens=len(prompt.split()) + len(response.split()),
        duration_seconds=duration,
        cost_estimate=calculate_cost(tokens, "gpt-4")  # Estimativa
    )
```

**Dashboard**:
- Total de tokens usados
- Custo estimado por modelo
- Comparação de custos
- Uso por projeto

---

### 9. Export para Markdown

**Implementação**:
```typescript
const handleExportMarkdown = () => {
  const blob = new Blob([content], { type: 'text/markdown' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = `${document.name}.md`;
  a.click();
  URL.revokeObjectURL(url);
}
```

**Botão**:
```typescript
<button onClick={handleExportMarkdown} className="btn-secondary">
  <Download className="h-4 w-4" />
  Export as Markdown
</button>
```

---

### 10. Multi-tenant Aprimorado

**Modelo Atual**:
```
Tenant (empresa)
  └── Users (todos os usuários)
```

**Modelo Novo**:
```
Super Admin (acessa tudo)
  └── Tenant (empresa)
      └── Tenant Admin (admin da empresa)
          └── Users (time da empresa)
```

**Implementação**:
- Página de cadastro de tenant
- Role "super_admin"
- Tenant switcher para super admin
- Tenant admin pode gerenciar apenas seu tenant

---

## 📊 Resumo de Prioridades

| # | Item | Prioridade | Esforço | Impacto |
|---|------|------------|---------|---------|
| 1 | Edição de projeto | 🔴 Crítica | ✅ Feito | Alto |
| 2 | Submit for Review | 🔴 Crítica | 1h | Alto |
| 3 | Botão Approve | 🔴 Crítica | 1h | Alto |
| 4 | Link para documento salvo | 🔴 Crítica | 1h | Alto |
| 5 | Docs anexados não aparecem | 🔴 Crítica | 2h | Alto |
| 6 | Progress steps verdes | 🔴 Crítica | 2h | Médio |
| 7 | Kanban Board | 🟡 Importante | 1 dia | Alto |
| 8 | Navegação por steps | 🟡 Importante | 3h | Alto |
| 9 | Confirmação ao regenerar | 🟡 Importante | 2h | Médio |
| 10 | Atalhos spec/arch | 🟡 Importante | 1h | Médio |
| 11 | Estatísticas de IA | 🟢 Melhoria | 1 dia | Médio |
| 12 | Export Markdown | 🟢 Melhoria | 2h | Baixo |
| 13 | Multi-tenant aprimorado | 🟢 Melhoria | 2 dias | Médio |

---

## 🎯 Próximos Passos Imediatos

### 1. Reiniciar Backend (AGORA!)
```bash
cd services
uvicorn api_gateway.main:app --reload --port 8086
```

### 2. Testar Edição de Projeto
- Editar target_cloud
- Verificar se salva

### 3. Implementar Correções Críticas
- Link para documento salvo
- Investigar documentos anexados
- Corrigir progress steps

---

**Prioridade**: 🔴 **ALTA**  
**Próxima Ação**: Implementar itens 2, 3 e 4  
**Tempo Estimado**: 4-5 horas

🚀 **Vamos começar pelas correções críticas!**


---

## 🔧 Detalhamento dos Novos Itens

### 5. Botão "Submit for Review" Não Funciona

**Problema Atual**:
- Botão existe no WorkItemDetail
- Ao clicar, nada acontece
- Work item continua em Draft

**Investigação**:
1. Verificar se transição está implementada no state_machine
2. Verificar se endpoint está funcionando
3. Verificar se há erro no console

**Solução**:
```typescript
const handleSubmitForReview = async () => {
  try {
    await api.post(`/work-items/${id}/transition`, {
      action: 'submit_for_review'
    });
    // Recarregar work item
    fetchWorkItem();
  } catch (error) {
    console.error('Failed to submit for review:', error);
  }
}
```

---

### 6. Adicionar Botão de Aprovação

**Requisito**:
- Botão "Approve" para aprovar work items
- Transição: review → approved
- Apenas para usuários com permissão

**Implementação**:
```typescript
{workItem.status === 'review' && (
  <button
    onClick={handleApprove}
    className="btn btn-success"
  >
    <Check className="h-4 w-4" />
    Approve
  </button>
)}
```

**Backend**:
- Verificar se transição `approve` existe no state_machine
- Adicionar se necessário

---

### 7. Kanban Board

**Requisito**:
- Visualização Kanban dos work items
- Colunas: Backlog, Draft, Review, Approved, In Progress, Done
- Drag & drop entre colunas
- Filtro por projeto

**Implementação**:
```typescript
// Componente KanbanBoard
const columns = [
  { id: 'backlog', title: 'Backlog', status: 'backlog' },
  { id: 'draft', title: 'Draft', status: 'draft' },
  { id: 'review', title: 'Review', status: 'review' },
  { id: 'approved', title: 'Approved', status: 'approved' },
  { id: 'in_progress', title: 'In Progress', status: 'in_progress' },
  { id: 'done', title: 'Done', status: 'done' },
];

// Drag & drop
const onDragEnd = async (result) => {
  const { draggableId, destination } = result;
  if (!destination) return;
  
  const newStatus = destination.droppableId;
  await api.patch(`/work-items/${draggableId}`, {
    status: newStatus
  });
  
  // Atualizar lista
  fetchWorkItems();
}
```

**Biblioteca**: `react-beautiful-dnd` ou `@dnd-kit/core`

**Rota**: `/work-items/kanban` ou toggle view na página de work items

---

## 🎯 Ordem de Implementação Atualizada

### Fase 1: Correções Críticas (3-4 horas)
1. ✅ Edição de projeto (FEITO)
2. 🔧 Corrigir "Submit for Review" (1h)
3. 🔧 Adicionar botão "Approve" (1h)
4. 🔗 Link para documento salvo (1h)

### Fase 2: Melhorias Importantes (1 dia)
5. 🔍 Investigar documentos anexados (2h)
6. ✅ Progress steps verdes (2h)
7. 📋 Kanban Board básico (4h)

### Fase 3: UX Avançada (1-2 dias)
8. 🖱️ Navegação por steps (3h)
9. ❓ Confirmação ao regenerar (2h)
10. 🔗 Atalhos spec/arch (1h)
11. 📥 Export Markdown (2h)

### Fase 4: Features Avançadas (3-5 dias)
12. 📊 Estatísticas de IA (1 dia)
13. 🏢 Multi-tenant aprimorado (2 dias)

---

## 🚀 Começando Agora

**Prioridade Máxima**:
1. Corrigir "Submit for Review"
2. Adicionar botão "Approve"
3. Link para documento salvo

**Tempo Estimado**: 3 horas  
**Impacto**: Alto - Funcionalidades críticas

Vamos começar! 🎯
