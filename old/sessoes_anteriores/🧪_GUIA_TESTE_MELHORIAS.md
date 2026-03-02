# 🧪 Guia de Teste - Melhorias Implementadas

## 🚀 Preparação

```bash
# 1. Certifique-se que o sistema está rodando
docker-compose up -d

# 2. Acesse o frontend
# http://localhost:5173

# 3. Faça login
# Email: admin@example.com
# Password: admin123
```

---

## 📝 Teste 1: Formatação de Requisitos

### Objetivo: Verificar visual profissional dos requisitos

### Passos:
```
1. Acesse "Work Items" no menu
2. Clique em qualquer work item que tenha requisitos
3. Role até a seção "Description"
```

### ✅ Verificações:
- [ ] User Story aparece em card azul com ícone 👤
- [ ] "As a", "I want", "So that" estão formatados
- [ ] Acceptance Criteria aparecem em cards numerados
- [ ] Given (roxo), When (azul), Then (verde) estão coloridos
- [ ] Hover nos cards mostra sombra
- [ ] Layout está organizado e legível

### 📸 Exemplo Esperado:
```
┌─────────────────────────────┐
│ 👤 User Story               │
│ As a: Product Manager       │
│ I want: Generate reqs       │
│ So that: Save time          │
└─────────────────────────────┘

┌─────────────────────────────┐
│ ✓ Acceptance Criteria       │
│ ① Upload Document           │
│   Given: User logged in     │
│   When: Uploads PDF         │
│   Then: Doc processed       │
└─────────────────────────────┘
```

---

## 📋 Teste 2: Kanban Board

### Objetivo: Verificar validação e feedback visual

### Passos:
```
1. Acesse "Work Items" → "Kanban View"
2. Veja as 6 colunas: Draft, In Review, Approved, Rejected, In Progress, Done
```

### ✅ Teste 2.1: Transição Válida
```
1. Arraste um card de "Draft"
2. Mova sobre "In Review"
3. Solte o card
```

**Esperado**:
- [ ] Coluna "In Review" fica verde ao passar o mouse
- [ ] Aparece texto "✓ Drop here"
- [ ] Card move com sucesso
- [ ] Status atualiza no backend

### ✅ Teste 2.2: Transição Inválida
```
1. Arraste um card de "Draft"
2. Mova sobre "Done"
3. Tente soltar
```

**Esperado**:
- [ ] Coluna "Done" fica vermelha/opaca
- [ ] Aparece texto "✗ Invalid"
- [ ] Alerta aparece ao tentar dropar
- [ ] Card volta para posição original

### ✅ Teste 2.3: Todas as Transições
```
Draft → In Review ✅
In Review → Approved ✅
In Review → Rejected ✅
Approved → In Progress ✅
Rejected → Draft ✅
In Progress → Done ✅
```

### ✅ Teste 2.4: Visual dos Cards
- [ ] Borda colorida por prioridade (vermelho/laranja/amarelo/verde)
- [ ] Badge de prioridade visível
- [ ] Ícone 👤 aparece se atribuído
- [ ] Tipo do work item visível
- [ ] Hover mostra sombra

---

## 🎯 Teste 3: Progress Steps

### Objetivo: Verificar que steps ficam verdes

### Passos:
```
1. Crie um novo projeto ou abra existente
2. Gere requisitos (se ainda não tiver)
3. Gere especificação
4. Gere arquitetura
```

### ✅ Verificações:
- [ ] Step 1 (Requirements) fica verde após gerar requisitos
- [ ] Step 2 (Specification) fica verde após gerar especificação
- [ ] Step 3 (Architecture) fica verde após gerar arquitetura
- [ ] Pode clicar nos steps para navegar
- [ ] Botões "View Document" aparecem

---

## 🔧 Teste 4: Edição de Projeto

### Objetivo: Verificar que settings são salvos

### Passos:
```
1. Abra um projeto
2. Clique em "Edit Project"
3. Mude "Target Cloud" de AWS para OCI
4. Mude "MPS.BR Level" de G para F
5. Clique em "Save"
6. Recarregue a página (F5)
```

### ✅ Verificações:
- [ ] Modal de edição abre
- [ ] Campos estão preenchidos com valores atuais
- [ ] Consegue mudar valores
- [ ] Mensagem de sucesso aparece
- [ ] Valores persistem após reload
- [ ] Settings aparecem corretos no projeto

---

## 👥 Teste 5: Atribuição de Work Items

### Objetivo: Verificar que pode atribuir usuários

### Passos:
```
1. Abra um work item
2. Na sidebar direita, veja "Assigned To"
3. Selecione um usuário no dropdown
```

### ✅ Verificações:
- [ ] Dropdown carrega lista de usuários
- [ ] Mostra nome ou email do usuário
- [ ] Consegue selecionar usuário
- [ ] Mensagem de sucesso aparece
- [ ] Atribuição persiste após reload
- [ ] Aparece no Kanban (ícone 👤)

---

## 🔄 Teste 6: Mudança de Status

### Objetivo: Verificar transições de status

### Passos:
```
1. Abra um work item em "Draft"
2. Na sidebar, veja dropdown de "Status"
3. Mude para "In Review"
```

### ✅ Verificações:
- [ ] Dropdown mostra apenas transições válidas
- [ ] Consegue mudar status
- [ ] Botões de ação rápida aparecem (Submit, Approve, etc)
- [ ] Status atualiza imediatamente
- [ ] Mudança persiste após reload

---

## 📄 Teste 7: Navegação de Documentos

### Objetivo: Verificar que pode abrir documentos gerados

### Passos:
```
1. Gere uma especificação
2. Clique em "📄 View Document"
3. Documento deve abrir
```

### ✅ Verificações:
- [ ] Botão "View Document" aparece após gerar
- [ ] Clique navega para página do documento
- [ ] Documento é exibido corretamente
- [ ] Pode editar documento (se editável)
- [ ] Pode voltar para o projeto

---

## 🎨 Checklist Visual Geral

### Layout:
- [ ] Interface está limpa e organizada
- [ ] Cores são consistentes
- [ ] Espaçamento adequado
- [ ] Sem elementos sobrepostos

### Interatividade:
- [ ] Hover effects funcionam
- [ ] Transições são suaves
- [ ] Feedback visual é claro
- [ ] Loading states aparecem

### Responsividade:
- [ ] Funciona em tela grande
- [ ] Funciona em tela média
- [ ] Sidebar é acessível

---

## 🐛 Problemas Conhecidos

### Não Implementado:
- ❌ AI Stats (endpoint não existe)

### Precisa Verificação:
- ❓ Upload de documentos (testar manualmente)

---

## 📊 Resultado Esperado

Após todos os testes:
- ✅ 8/10 funcionalidades funcionando
- ✅ Interface profissional
- ✅ UX intuitiva
- ✅ Validações corretas
- ✅ Feedback visual rico

---

## 🆘 Troubleshooting

### Problema: Requisitos não aparecem formatados
**Solução**: Verifique se o work item tem description em formato JSON

### Problema: Kanban não valida transições
**Solução**: Limpe cache do navegador (Ctrl+Shift+R)

### Problema: Progress steps não ficam verdes
**Solução**: Verifique se documentos foram gerados com `is_generated=true`

### Problema: Edição de projeto não salva
**Solução**: Verifique console do navegador para erros

---

## 📞 Suporte

Se encontrar problemas:
1. Verifique console do navegador (F12)
2. Verifique logs do backend
3. Consulte documentação criada:
   - `🎨_MELHORIAS_IMPLEMENTADAS.md`
   - `✅_CORRECOES_SESSAO_ATUAL.md`
   - `🔍_ANALISE_CORRECOES.md`

---

**Data**: 24/02/2026  
**Versão**: 2.0  
**Status**: ✅ Pronto para Teste
