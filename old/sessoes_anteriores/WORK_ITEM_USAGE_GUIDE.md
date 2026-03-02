# 📋 Guia de Uso: Work Items

## Como Mudar Status e Assignee

### 🔄 Mudar Status do Work Item

#### Método 1: Transições Automáticas (Recomendado)
1. Abra o work item (clique nele na lista)
2. Olhe na **sidebar direita**
3. Seção **"Status"**:
   - Ver status atual (badge colorido)
   - Ver **"Available Transitions"** (botões abaixo)
4. Clicar no botão da transição desejada:
   - `→ Submit for Review` (Draft → In Review)
   - `→ Approve` (In Review → Approved)
   - `→ Start Work` (Approved → In Progress)
   - `→ Complete` (In Progress → Done)

**Exemplo de Fluxo**:
```
Draft 
  ↓ [Submit for Review]
In Review
  ↓ [Approve]
Approved
  ↓ [Start Work]
In Progress
  ↓ [Complete]
Done ✓
```

#### Transições Disponíveis por Status:

**Draft**:
- → Submit for Review (vai para In Review)

**In Review**:
- → Approve (vai para Approved)
- → Reject (vai para Rejected)
- → Back to Draft (volta para Draft)

**Approved**:
- → Start Work (vai para In Progress)

**Rejected**:
- → Revise (volta para Draft)

**In Progress**:
- → Complete (vai para Done)
- → Back to Approved (volta para Approved)

**Done**:
- (Estado final, sem transições)

### 👤 Atribuir Desenvolvedor (Assignee)

#### Passo a Passo:
1. Abra o work item
2. Clique no botão **"Edit"** (canto superior direito)
3. No formulário de edição:
   - Campo **"Assigned To"** (dropdown)
   - Selecione o desenvolvedor
4. Clique em **"Save Changes"**

#### Visualizar Assignee:
- **Sidebar direita** → Seção "Information"
- Campo **"Assigned To"**
- Mostra nome ou email do desenvolvedor

### 🎨 Cores dos Status

- **Draft**: Cinza
- **In Review**: Roxo
- **Approved**: Verde claro
- **Rejected**: Vermelho
- **In Progress**: Amarelo
- **Done**: Verde

### 🎯 Cores das Prioridades

- **Low**: Cinza
- **Medium**: Azul
- **High**: Laranja
- **Critical**: Vermelho

## 📝 Workflow Completo

### Cenário: Desenvolver uma Feature

1. **Product Owner cria requisito**:
   - Gera requisitos com IA
   - Aprova requisitos
   - Work items criados automaticamente em **Draft**

2. **Product Owner revisa**:
   - Abre work item
   - Clica "Submit for Review"
   - Status → **In Review**

3. **Tech Lead aprova**:
   - Abre work item
   - Revisa descrição
   - Clica "Approve"
   - Status → **Approved**

4. **Product Owner atribui desenvolvedor**:
   - Clica "Edit"
   - Seleciona desenvolvedor no "Assigned To"
   - Salva

5. **Desenvolvedor inicia trabalho**:
   - Abre work item atribuído a ele
   - Clica "Start Work"
   - Status → **In Progress**
   - Adiciona comentários conforme progride

6. **Desenvolvedor completa**:
   - Clica "Complete"
   - Status → **Done**
   - Adiciona comentário final

## 🔍 Troubleshooting

### Não vejo botões de transição
**Problema**: Sidebar não mostra "Available Transitions"

**Soluções**:
1. Verificar se o work item está carregado (não está em loading)
2. Verificar se há erro (mensagem vermelha no topo)
3. Verificar console do browser (F12) para erros
4. Recarregar a página

**Causa comum**: Backend não está retornando transições

**Verificar backend**:
```bash
# Ver logs do backend
# Deve mostrar: GET /work-items/{id}/transitions
```

### Assignee não aparece no dropdown
**Problema**: Lista de usuários vazia

**Soluções**:
1. Verificar se há usuários cadastrados
2. Ir em "Users" no menu
3. Criar usuários se necessário
4. Recarregar página do work item

### Transição não funciona
**Problema**: Clico no botão mas nada acontece

**Soluções**:
1. Verificar console do browser (F12)
2. Verificar se backend está rodando
3. Verificar se há erro de permissão
4. Tentar fazer logout/login

## 🎬 Demonstração Visual

### Tela do Work Item:

```
┌─────────────────────────────────────────────────────────────┐
│ ← Back to Work Items                                        │
│                                                              │
│ Autenticação de Usuários                    [Edit] [Delete] │
│ E-commerce Platform • requirement                            │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ ┌─────────────────────────┐  ┌──────────────────────────┐  │
│ │ Details                 │  │ Status                   │  │
│ │                         │  │ ┌──────────────────────┐ │  │
│ │ **User Story:**         │  │ │ IN PROGRESS          │ │  │
│ │ As a Admin              │  │ └──────────────────────┘ │  │
│ │ I want ...              │  │                          │  │
│ │ So that ...             │  │ Available Transitions:   │  │
│ │                         │  │ [→ Complete]             │  │
│ │ **Acceptance Criteria:**│  │ [→ Back to Approved]     │  │
│ │ 1. Scenario...          │  │                          │  │
│ │    - Given: ...         │  │ Information              │  │
│ │    - When: ...          │  │ Priority: HIGH           │  │
│ │    - Then: ...          │  │ Assigned To: John Dev    │  │
│ └─────────────────────────┘  │ Created: 23/02/2026      │  │
│                              │ Updated: 23/02/2026      │  │
│ ┌─────────────────────────┐  └──────────────────────────┘  │
│ │ Comments (2)            │                                │
│ │                         │                                │
│ │ [Add comment...]        │                                │
│ │ [Add Comment]           │                                │
│ └─────────────────────────┘                                │
└─────────────────────────────────────────────────────────────┘
```

### Modo de Edição:

```
┌─────────────────────────────────────────────────────────────┐
│ Details                                                      │
│                                                              │
│ Title: [Autenticação de Usuários                        ]   │
│                                                              │
│ Description:                                                 │
│ [                                                        ]   │
│ [  User story and acceptance criteria...                ]   │
│ [                                                        ]   │
│                                                              │
│ Priority:        Assigned To:                                │
│ [High      ▼]    [John Dev              ▼]                  │
│                                                              │
│ [Save Changes]  [Cancel]                                     │
└─────────────────────────────────────────────────────────────┘
```

## ✅ Checklist de Teste

### Testar Transições:
- [ ] Criar work item (fica em Draft)
- [ ] Clicar "Submit for Review" → vira In Review
- [ ] Clicar "Approve" → vira Approved
- [ ] Clicar "Start Work" → vira In Progress
- [ ] Clicar "Complete" → vira Done

### Testar Assignee:
- [ ] Clicar "Edit"
- [ ] Selecionar desenvolvedor
- [ ] Salvar
- [ ] Ver nome na sidebar
- [ ] Recarregar página
- [ ] Verificar que manteve

### Testar Prioridade:
- [ ] Clicar "Edit"
- [ ] Mudar prioridade
- [ ] Salvar
- [ ] Ver cor atualizada

## 🚀 Dicas

1. **Use transições** em vez de editar status manualmente
2. **Atribua logo** após aprovar
3. **Adicione comentários** ao fazer transições
4. **Use prioridades** para organizar trabalho
5. **Filtre por assignee** na lista de work items

## 📞 Suporte

Se ainda tiver problemas:
1. Verificar se backend está rodando
2. Verificar console do browser (F12)
3. Verificar logs do backend
4. Tentar com outro work item
5. Resetar banco de dados se necessário

```bash
# Reset database
uv run python scripts/reset_and_seed.py
```

---

**Funcionalidades Implementadas**: ✅
**Status**: Pronto para uso
**Última atualização**: 23/02/2026
