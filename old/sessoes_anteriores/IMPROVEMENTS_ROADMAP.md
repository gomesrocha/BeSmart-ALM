# 🚀 Roadmap de Melhorias - Bsmart-ALM

## 📋 Melhorias Solicitadas

### 1. ✏️ Editar e Apagar Projeto
**Status**: 🔄 Planejado

**Funcionalidades**:
- Botão "Edit" na página de detalhes do projeto
- Modal/formulário para editar:
  - Nome
  - Descrição
  - Status (active, archived, on_hold)
  - Target Cloud (AWS, Azure, GCP, OCI)
  - MPS.BR Level
  - Whitelist URLs
- Botão "Delete" com confirmação
- Soft delete (arquivar ao invés de deletar)

**Backend**: Já existe endpoint PATCH /projects/{id}
**Frontend**: Precisa implementar UI

---

### 2. ✅ Aprovar Itens Individual ou em Grupo
**Status**: 🔄 Planejado

**Funcionalidades**:
- Checkbox em cada requisito gerado
- Botão "Approve Selected" (apenas selecionados)
- Botão "Approve All" (todos)
- Contador de selecionados
- Desmarcar todos

**Implementação**:
- Estado para controlar seleção
- Filtrar requisitos selecionados antes de aprovar
- UI com checkboxes

---

### 3. 📊 Visão Geral dos Requisitos do Projeto
**Status**: 🔄 Planejado

**Funcionalidades**:
- Seção "Requirements Overview" na página do projeto
- Listar todos os work items do tipo "requirement"
- Estatísticas:
  - Total de requisitos
  - Por status (draft, approved, in_progress, done)
  - Por prioridade
- Gráficos visuais
- Link para cada requisito

**Backend**: Endpoint GET /work-items?project_id={id}&type=requirement
**Frontend**: Nova seção na página ProjectDetail

---

### 4. 🎯 Target Cloud no Cadastro
**Status**: 🔄 Planejado

**Funcionalidades**:
- Campo "Target Cloud" no formulário de criação
- Dropdown com opções:
  - AWS
  - Azure
  - GCP
  - OCI
  - Multi-Cloud
  - On-Premise
- Campo "MPS.BR Level" também
- Salvar em project.settings

**Backend**: Já suporta (settings é JSON)
**Frontend**: Adicionar campos no formulário

---

### 5. 📝 Formato Gherkin + Complemento de Negócio
**Status**: 🔄 Planejado

**Formato Desejado**:

```gherkin
User Story:
Como um [papel]
Eu quero [funcionalidade]
Para que [benefício]

Contexto de Negócio:
[Informações adicionais sobre o valor de negócio, 
impacto, stakeholders, métricas de sucesso]

Critérios de Aceite (Gherkin):

Cenário: [Nome do cenário]
  Dado que [contexto inicial]
  Quando [ação do usuário]
  Então [resultado esperado]
  E [resultado adicional]

Cenário: [Outro cenário]
  Dado que [contexto]
  Quando [ação]
  Então [resultado]
```

**Implementação**:
- Atualizar prompt da IA para gerar neste formato
- Adicionar campo "business_context" no schema
- Gerar múltiplos cenários Gherkin
- Formatar melhor a visualização

---

### 6. 🔄 Geração Iterativa (Refinamento)
**Status**: 🔄 Planejado

**Funcionalidades**:
- Após gerar requisitos, mostrar botão "Refine Requirements"
- Campo para adicionar mais informações/feedback
- Botão "Generate More" para adicionar requisitos
- Histórico de iterações
- Manter contexto entre gerações

**Fluxo**:
```
1. Gerar requisitos iniciais
2. Usuário revisa
3. Usuário adiciona feedback: "Adicione requisitos de segurança"
4. Sistema gera mais requisitos com o contexto anterior
5. Combina com os existentes
6. Repete até satisfeito
```

**Implementação**:
- Estado para armazenar contexto acumulado
- Endpoint que aceita requisitos existentes + novo input
- UI com campo de refinamento
- Botão "Add More Requirements"

---

## 🎯 Priorização Sugerida

### Fase 1 - Essencial (Implementar Agora)
1. ✅ **Aprovar Individual/Grupo** - Melhora UX imediatamente
2. 📝 **Formato Gherkin** - Melhora qualidade dos requisitos
3. 🎯 **Target Cloud no Cadastro** - Dado importante

### Fase 2 - Importante (Próxima)
4. ✏️ **Editar/Apagar Projeto** - Funcionalidade básica
5. 📊 **Visão Geral** - Melhor visualização

### Fase 3 - Avançado (Depois)
6. 🔄 **Geração Iterativa** - Feature avançada

---

## 📝 Detalhamento Técnico

### 1. Aprovar Individual/Grupo

**Frontend**:
```typescript
const [selectedRequirements, setSelectedRequirements] = useState<Set<number>>(new Set())

const toggleRequirement = (index: number) => {
  const newSelected = new Set(selectedRequirements)
  if (newSelected.has(index)) {
    newSelected.delete(index)
  } else {
    newSelected.add(index)
  }
  setSelectedRequirements(newSelected)
}

const approveSelected = () => {
  const toApprove = requirements.filter((_, i) => selectedRequirements.has(i))
  // Aprovar apenas selecionados
}
```

---

### 2. Formato Gherkin

**Prompt Atualizado**:
```python
GHERKIN_PROMPT = """Generate requirements in Gherkin format:

{{
  "requirements": [
    {{
      "title": "User Story Title",
      "user_story": {{
        "as_a": "role",
        "i_want": "feature",
        "so_that": "benefit"
      }},
      "business_context": "Detailed business value, impact, stakeholders, success metrics",
      "acceptance_criteria": [
        {{
          "scenario": "Scenario name",
          "given": "initial context",
          "when": "user action",
          "then": "expected result",
          "and": ["additional results"]
        }}
      ],
      "priority": "high|medium|low"
    }}
  ]
}}
"""
```

---

### 3. Target Cloud no Cadastro

**Frontend - Projects.tsx**:
```typescript
<select {...register('target_cloud', { required: true })}>
  <option value="">Select Target Cloud</option>
  <option value="AWS">AWS</option>
  <option value="Azure">Azure</option>
  <option value="GCP">GCP</option>
  <option value="OCI">OCI</option>
  <option value="Multi-Cloud">Multi-Cloud</option>
  <option value="On-Premise">On-Premise</option>
</select>

<select {...register('mps_br_level')}>
  <option value="">Select MPS.BR Level</option>
  <option value="G">G - Parcialmente Gerenciado</option>
  <option value="F">F - Gerenciado</option>
  <option value="E">E - Parcialmente Definido</option>
  <option value="D">D - Largamente Definido</option>
  <option value="C">C - Definido</option>
  <option value="B">B - Gerenciado Quantitativamente</option>
  <option value="A">A - Em Otimização</option>
</select>
```

---

### 4. Visão Geral dos Requisitos

**Nova Seção**:
```typescript
<div className="card">
  <h2>Requirements Overview</h2>
  <div className="grid grid-cols-4 gap-4">
    <StatCard title="Total" value={totalReqs} />
    <StatCard title="Draft" value={draftReqs} />
    <StatCard title="Approved" value={approvedReqs} />
    <StatCard title="Done" value={doneReqs} />
  </div>
  <div className="mt-4">
    <h3>Recent Requirements</h3>
    {recentReqs.map(req => (
      <RequirementCard key={req.id} requirement={req} />
    ))}
  </div>
</div>
```

---

### 5. Geração Iterativa

**Backend - Novo Endpoint**:
```python
@router.post("/refine-requirements")
async def refine_requirements(
    project_id: str,
    existing_requirements: List[RequirementItem],
    additional_input: str,
    ...
):
    # Combinar requisitos existentes com novo input
    context = build_context(existing_requirements, additional_input)
    
    # Gerar novos requisitos
    new_requirements = await generate_with_context(context)
    
    return {
        "requirements": new_requirements,
        "iteration": iteration_number
    }
```

**Frontend**:
```typescript
const [iterations, setIterations] = useState<RequirementItem[][]>([])
const [refinementInput, setRefinementInput] = useState('')

const refineRequirements = async () => {
  const response = await api.post('/requirements/refine', {
    project_id: id,
    existing_requirements: requirements,
    additional_input: refinementInput
  })
  
  setRequirements([...requirements, ...response.data.requirements])
  setIterations([...iterations, response.data.requirements])
}
```

---

## ✅ Checklist de Implementação

### Fase 1
- [ ] Aprovar individual/grupo
  - [ ] Estado de seleção
  - [ ] Checkboxes na UI
  - [ ] Botões "Approve Selected" e "Approve All"
  - [ ] Contador de selecionados

- [ ] Formato Gherkin
  - [ ] Atualizar prompt
  - [ ] Novo schema com business_context
  - [ ] Múltiplos cenários
  - [ ] Formatação visual melhorada

- [ ] Target Cloud no cadastro
  - [ ] Campo no formulário de criação
  - [ ] Campo no formulário de edição
  - [ ] Validação
  - [ ] Salvar em settings

### Fase 2
- [ ] Editar/Apagar projeto
  - [ ] Botão Edit
  - [ ] Modal de edição
  - [ ] Botão Delete
  - [ ] Confirmação
  - [ ] Integração com API

- [ ] Visão geral
  - [ ] Endpoint para buscar requisitos do projeto
  - [ ] Cards de estatísticas
  - [ ] Lista de requisitos recentes
  - [ ] Gráficos (opcional)

### Fase 3
- [ ] Geração iterativa
  - [ ] Endpoint de refinamento
  - [ ] Campo de feedback
  - [ ] Botão "Refine"
  - [ ] Botão "Add More"
  - [ ] Histórico de iterações
  - [ ] Contexto acumulado

---

## 🎉 Resultado Esperado

Após implementar todas as melhorias:

✅ Projetos totalmente editáveis
✅ Aprovação flexível de requisitos
✅ Visão completa do projeto
✅ Requisitos em formato Gherkin profissional
✅ Geração iterativa e refinamento
✅ Melhor captura de informações do projeto

**Sistema muito mais completo e profissional!** 🚀
