# 🚀 Próximas Implementações - Guia Completo

## 📋 Pendências Identificadas

### 1. Modal de Geração de Especificação ⏳
**Status**: Backend pronto, falta frontend
**Prioridade**: Alta
**Tempo estimado**: 30 minutos

### 2. Modal de Geração de Arquitetura ⏳
**Status**: Backend pronto, falta frontend
**Prioridade**: Alta
**Tempo estimado**: 30 minutos

### 3. Corrigir Lista de Usuários no Work Item ⏳
**Status**: Código implementado, verificar bug
**Prioridade**: Média
**Tempo estimado**: 15 minutos

---

## 🔧 Implementação 1: Modal de Especificação

### Backend (JÁ PRONTO ✅)
- Endpoint: `POST /specification/generate`
- Arquivo: `services/specification/router.py`
- Prompts: `services/specification/prompts.py`

### Frontend (A FAZER)

#### Passo 1: Atualizar ProjectDetail.tsx
Substituir o alert por função real:

```typescript
// Adicionar estado
const [showSpecModal, setShowSpecModal] = useState(false)
const [generatingSpec, setGeneratingSpec] = useState(false)
const [specContent, setSpecContent] = useState('')

// Substituir o onClick do botão Specification
<button
  onClick={() => setShowSpecModal(true)}
  className="btn btn-secondary flex items-center space-x-2"
>
  <BookOpen className="h-4 w-4" />
  <span>Specification</span>
</button>

// Adicionar função de geração
const handleGenerateSpec = async () => {
  setGeneratingSpec(true)
  try {
    const response = await api.post('/specification/generate', {
      project_id: id
    })
    setSpecContent(response.data.content)
    alert('Specification generated successfully!')
  } catch (err: any) {
    alert(err.response?.data?.detail || 'Failed to generate specification')
  } finally {
    setGeneratingSpec(false)
  }
}

// Adicionar modal antes do </div> final
{showSpecModal && (
  <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div className="bg-white rounded-lg p-6 max-w-4xl w-full mx-4 max-h-[80vh] overflow-y-auto">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold">Generate Specification</h2>
        <button onClick={() => setShowSpecModal(false)} className="text-gray-500 hover:text-gray-700">
          ✕
        </button>
      </div>
      
      {!specContent ? (
        <div className="space-y-4">
          <p className="text-gray-600">
            Generate a detailed specification document based on approved requirements.
          </p>
          <button
            onClick={handleGenerateSpec}
            disabled={generatingSpec}
            className="btn-primary w-full"
          >
            {generatingSpec ? 'Generating...' : 'Generate Specification'}
          </button>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="prose prose-sm max-w-none">
            <pre className="whitespace-pre-wrap bg-gray-50 p-4 rounded">
              {specContent}
            </pre>
          </div>
          <div className="flex gap-2">
            <button onClick={() => setShowSpecModal(false)} className="btn-primary">
              Close
            </button>
            <button
              onClick={() => {
                setSpecContent('')
                handleGenerateSpec()
              }}
              className="btn-secondary"
            >
              Regenerate
            </button>
          </div>
        </div>
      )}
    </div>
  </div>
)}
```

---

## 🔧 Implementação 2: Modal de Arquitetura

### Backend (JÁ PRONTO ✅)
- Endpoint: `POST /architecture/generate`
- Arquivo: `services/architecture/router.py`
- Prompts: `services/architecture/prompts.py`

### Frontend (A FAZER)

Similar ao modal de especificação, mas para arquitetura:

```typescript
// Adicionar estados
const [showArchModal, setShowArchModal] = useState(false)
const [generatingArch, setGeneratingArch] = useState(false)
const [archContent, setArchContent] = useState('')

// Substituir onClick do botão Architecture
<button
  onClick={() => setShowArchModal(true)}
  className="btn btn-secondary flex items-center space-x-2"
>
  <Network className="h-4 w-4" />
  <span>Architecture</span>
</button>

// Função de geração
const handleGenerateArch = async () => {
  setGeneratingArch(true)
  try {
    const response = await api.post('/architecture/generate', {
      project_id: id
    })
    setArchContent(response.data.content)
    alert('Architecture generated successfully!')
  } catch (err: any) {
    alert(err.response?.data?.detail || 'Failed to generate architecture')
  } finally {
    setGeneratingArch(false)
  }
}

// Modal (similar ao de spec)
```

---

## 🔧 Implementação 3: Corrigir Lista de Usuários

### Problema
Lista de usuários vazia no dropdown de assignee

### Solução

#### Verificar em WorkItemDetail.tsx:

```typescript
// Verificar se loadUsers está sendo chamado
useEffect(() => {
  loadWorkItem()
  loadUsers()  // ← Deve estar aqui
}, [id])

// Verificar função loadUsers
const loadUsers = async () => {
  try {
    const response = await api.get('/identity/users')
    setUsers(response.data)
    console.log('Users loaded:', response.data) // Debug
  } catch (err) {
    console.error('Failed to load users:', err)
  }
}
```

#### Se não funcionar, verificar backend:

```bash
# Testar endpoint
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:8086/api/v1/identity/users
```

#### Alternativa: Usar endpoint correto

Se o endpoint for diferente, atualizar:

```typescript
const response = await api.get('/identity/users')
// ou
const response = await api.get('/users')
```

---

## 📝 Checklist de Implementação

### Modal de Especificação
- [ ] Adicionar estados (showSpecModal, generatingSpec, specContent)
- [ ] Substituir alert por setShowSpecModal(true)
- [ ] Adicionar função handleGenerateSpec
- [ ] Adicionar modal JSX
- [ ] Testar geração
- [ ] Testar regeneração
- [ ] Testar fechar modal

### Modal de Arquitetura
- [ ] Adicionar estados (showArchModal, generatingArch, archContent)
- [ ] Substituir alert por setShowArchModal(true)
- [ ] Adicionar função handleGenerateArch
- [ ] Adicionar modal JSX
- [ ] Testar geração
- [ ] Testar regeneração
- [ ] Testar fechar modal

### Lista de Usuários
- [ ] Verificar console do browser (F12)
- [ ] Verificar se loadUsers é chamado
- [ ] Verificar resposta da API
- [ ] Verificar endpoint correto
- [ ] Testar com usuários criados
- [ ] Verificar dropdown populado

---

## 🧪 Como Testar

### Testar Especificação
1. Login como admin
2. Criar projeto
3. Gerar e aprovar requisitos
4. Clicar em "Specification"
5. Ver modal
6. Clicar em "Generate Specification"
7. Aguardar (10-30s)
8. Ver conteúdo gerado
9. Testar "Regenerate"
10. Testar "Close"

### Testar Arquitetura
1. Ter especificação gerada
2. Clicar em "Architecture"
3. Ver modal
4. Clicar em "Generate Architecture"
5. Aguardar (10-30s)
6. Ver diagramas Mermaid
7. Testar "Regenerate"
8. Testar "Close"

### Testar Assignee
1. Criar usuários (se não existir)
2. Abrir work item
3. Clicar "Edit"
4. Ver dropdown "Assigned To"
5. Ver lista de usuários
6. Selecionar usuário
7. Salvar
8. Ver nome na sidebar

---

## 🎯 Resultado Esperado

Após implementar tudo:

### ✅ Especificação
- Modal funcional
- Geração com IA
- Conteúdo em markdown
- Regeneração possível

### ✅ Arquitetura
- Modal funcional
- Geração com IA
- Diagramas Mermaid
- Regeneração possível

### ✅ Assignee
- Lista de usuários carregada
- Dropdown populado
- Seleção funcional
- Nome exibido corretamente

---

## 📚 Arquivos a Modificar

### Frontend
1. `frontend/src/pages/ProjectDetail.tsx` - Adicionar modals
2. `frontend/src/pages/WorkItemDetail.tsx` - Verificar loadUsers

### Backend (Já Pronto)
1. `services/specification/router.py` ✅
2. `services/architecture/router.py` ✅
3. `services/identity/user_router.py` ✅

---

## 🚀 Ordem de Implementação Recomendada

1. **Corrigir lista de usuários** (15 min)
   - Mais simples
   - Impacto imediato
   - Necessário para workflow

2. **Modal de especificação** (30 min)
   - Backend pronto
   - Funcionalidade importante
   - Base para arquitetura

3. **Modal de arquitetura** (30 min)
   - Similar ao de spec
   - Complementa o workflow
   - Finaliza o ciclo

**Tempo total estimado**: ~1h15min

---

## 💡 Dicas

1. **Copiar e colar** o código dos modals
2. **Testar incrementalmente** (um modal por vez)
3. **Usar console.log** para debug
4. **Verificar network tab** (F12) para ver requests
5. **Testar com Ollama rodando**

---

## 🎉 Após Implementar

O sistema estará **100% completo** com:
- ✅ Geração de requisitos
- ✅ Geração de especificação
- ✅ Geração de arquitetura
- ✅ Gerenciamento completo de work items
- ✅ Assignees funcionando
- ✅ Workflow end-to-end

**Sistema pronto para produção!** 🚀

---

## 📞 Suporte

Se tiver dúvidas:
1. Consultar `COMPLETE_SYSTEM_GUIDE.md`
2. Ver `WORK_ITEM_USAGE_GUIDE.md`
3. Verificar `TROUBLESHOOTING.md`
4. Revisar código existente similar

**Boa implementação!** 💪
