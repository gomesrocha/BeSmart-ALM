# 🧪 Guia de Teste Rápido - Novas Funcionalidades

## 🚀 Preparação

### 1. Executar Migração do Banco
```bash
uv run python scripts/migrate_ai_stats.py
```

### 2. Iniciar Backend
```bash
./RUN_APP.sh
```

### 3. Iniciar Frontend
```bash
cd frontend
npm run dev
```

---

## 📋 Teste 1: Kanban Board

### Passos:
1. Faça login no sistema
2. Navegue para "Work Items" no menu lateral
3. Clique no botão "📋 Kanban View"
4. Você verá 5 colunas: Draft, In Review, Approved, In Progress, Done

### Testes:
- [ ] Arraste um card de "Draft" para "In Review"
- [ ] Verifique que o card mudou de coluna
- [ ] Abra o console do navegador (F12)
- [ ] Veja as mensagens de log: "🔄 Moving item..." e "✅ Item moved..."
- [ ] Clique no card para ver os detalhes
- [ ] Verifique que o status foi atualizado
- [ ] Use o filtro de projeto
- [ ] Use a busca por texto
- [ ] Clique em "📄 List View" para voltar à lista

### Resultado Esperado:
✅ Cards se movem suavemente entre colunas
✅ Status é atualizado no backend
✅ Feedback visual durante o arrasto
✅ Contadores de items atualizados

---

## 🎯 Teste 2: Navegação por Steps

### Passos:
1. Navegue para "Projects"
2. Abra um projeto existente
3. Veja a barra de progresso no topo

### Testes:
- [ ] Clique no step "Visão Geral" → deve fazer scroll para o topo
- [ ] Clique no step "Requisitos" → deve fazer scroll para a seção de requisitos
- [ ] Clique no step "Especificação":
  - Se já existe: navega para o documento
  - Se não existe: abre modal de geração
- [ ] Clique no step "Arquitetura":
  - Se já existe: navega para o documento
  - Se não existe: abre modal de geração
- [ ] Clique no step "Implementação" → navega para work items do projeto

### Resultado Esperado:
✅ Navegação suave e intuitiva
✅ Modais abrem quando necessário
✅ Documentos são encontrados e abertos
✅ Hover effects funcionam

---

## 📥 Teste 3: Export para Markdown

### Passos:
1. Navegue para um projeto
2. Clique em "Documents" ou "View Documents"
3. Abra qualquer documento (Requirements, Specification, Architecture)

### Testes:
- [ ] Veja o botão "📥 Export MD" no topo
- [ ] Clique no botão
- [ ] Verifique que um arquivo .md foi baixado
- [ ] Abra o arquivo em um editor de texto
- [ ] Verifique que o conteúdo está correto
- [ ] Verifique que a formatação markdown está preservada

### Resultado Esperado:
✅ Arquivo baixado automaticamente
✅ Nome do arquivo baseado no título do documento
✅ Conteúdo markdown preservado
✅ Formatação correta

---

## 📊 Teste 4: Estatísticas de IA

### Preparação:
Primeiro, gere alguns dados:
1. Crie um novo projeto
2. Gere requisitos usando IA
3. Gere especificação
4. Gere arquitetura

### Passos:
1. Clique em "AI Stats" no menu lateral
2. Você verá o dashboard de estatísticas

### Testes:
- [ ] Verifique os 4 cards de métricas:
  - Total Operations
  - Total Tokens
  - Estimated Cost
  - Total Duration
- [ ] Veja o gráfico "Operations by Type"
- [ ] Veja a tabela "Cost by Model"
- [ ] Veja a tabela "Recent Operations"
- [ ] Mude o filtro de período (7, 30, 90 dias)
- [ ] Verifique que os dados são atualizados

### Testes Avançados:
- [ ] Gere mais requisitos
- [ ] Volte para AI Stats
- [ ] Verifique que os números aumentaram
- [ ] Verifique a operação na tabela "Recent Operations"
- [ ] Veja o status "Success" em verde

### Resultado Esperado:
✅ Métricas exibidas corretamente
✅ Gráficos funcionando
✅ Tabelas com dados reais
✅ Filtros funcionando
✅ Atualização em tempo real

---

## 🔍 Teste 5: Integração Completa

### Cenário: Criar um projeto do zero e usar todas as funcionalidades

1. **Criar Projeto**
   - [ ] Crie um novo projeto
   - [ ] Preencha nome e descrição

2. **Gerar Requisitos**
   - [ ] Use a IA para gerar requisitos
   - [ ] Aprove os requisitos
   - [ ] Verifique AI Stats (deve ter 1 operação)

3. **Gerar Especificação**
   - [ ] Clique no step "Especificação"
   - [ ] Gere a especificação
   - [ ] Exporte para Markdown
   - [ ] Verifique AI Stats (deve ter 2 operações)

4. **Gerar Arquitetura**
   - [ ] Clique no step "Arquitetura"
   - [ ] Gere a arquitetura
   - [ ] Exporte para Markdown
   - [ ] Verifique AI Stats (deve ter 3 operações)

5. **Criar Work Items**
   - [ ] Clique no step "Implementação"
   - [ ] Crie alguns work items
   - [ ] Vá para Kanban View
   - [ ] Mova os items entre colunas

6. **Verificar Estatísticas**
   - [ ] Vá para AI Stats
   - [ ] Veja todas as operações
   - [ ] Verifique os custos estimados
   - [ ] Verifique a duração total

### Resultado Esperado:
✅ Fluxo completo funciona perfeitamente
✅ Todas as funcionalidades integradas
✅ Dados consistentes em todo o sistema
✅ Experiência de usuário fluida

---

## 🐛 Troubleshooting

### Problema: Kanban não carrega
**Solução**: 
- Verifique se há work items no projeto
- Verifique o console do navegador
- Verifique se o backend está rodando

### Problema: Steps não navegam
**Solução**:
- Verifique se os documentos existem
- Verifique o console para erros
- Recarregue a página

### Problema: Export não funciona
**Solução**:
- Verifique se o documento tem conteúdo
- Verifique permissões do navegador para downloads
- Tente outro navegador

### Problema: AI Stats vazio
**Solução**:
- Execute a migração: `uv run python scripts/migrate_ai_stats.py`
- Gere alguns requisitos/specs
- Recarregue a página

### Problema: Drag & drop não funciona
**Solução**:
- Verifique se as dependências foram instaladas: `npm install`
- Limpe o cache: `npm run build`
- Recarregue a página

---

## ✅ Checklist Final

Após todos os testes, verifique:

- [ ] Kanban funciona perfeitamente
- [ ] Navegação por steps é intuitiva
- [ ] Export para MD funciona
- [ ] AI Stats mostra dados corretos
- [ ] Todas as integrações funcionam
- [ ] Sem erros no console
- [ ] Performance é boa
- [ ] UI/UX é agradável

---

## 📸 Screenshots Esperados

### Kanban Board
```
┌─────────┬─────────┬─────────┬─────────┬─────────┐
│ Draft   │In Review│Approved │Progress │  Done   │
│  (3)    │  (2)    │  (1)    │  (4)    │  (5)    │
├─────────┼─────────┼─────────┼─────────┼─────────┤
│ [Card1] │ [Card4] │ [Card7] │ [Card8] │ [Card13]│
│ [Card2] │ [Card5] │         │ [Card9] │ [Card14]│
│ [Card3] │         │         │ [Card10]│ [Card15]│
│         │         │         │ [Card11]│ [Card16]│
│         │         │         │         │ [Card17]│
└─────────┴─────────┴─────────┴─────────┴─────────┘
```

### Progress Steps
```
(✓) ──── (✓) ──── (2) ──── (3) ──── (4)
Overview Requirements Spec  Arch  Impl
```

### AI Stats Dashboard
```
┌──────────────┬──────────────┬──────────────┬──────────────┐
│ Operations   │ Tokens       │ Cost         │ Duration     │
│    15        │  45,230      │  $0.00       │  12.5m       │
└──────────────┴──────────────┴──────────────┴──────────────┘

Operations by Type:
requirements  ████████ 8
specification ████ 4
architecture  ███ 3

Recent Operations:
┌──────────────┬────────┬────────┬────────┬─────────┐
│ Operation    │ Model  │ Tokens │ Cost   │ Status  │
├──────────────┼────────┼────────┼────────┼─────────┤
│ architecture │llama3.2│ 15,234 │ $0.00  │ Success │
│ specification│llama3.2│ 12,456 │ $0.00  │ Success │
│ requirements │llama3.2│  8,901 │ $0.00  │ Success │
└──────────────┴────────┴────────┴────────┴─────────┘
```

---

## 🎉 Conclusão

Se todos os testes passaram, o sistema está funcionando perfeitamente! 

**Próximos passos**:
1. Teste com usuários reais
2. Colete feedback
3. Implemente melhorias sugeridas
4. Adicione mais funcionalidades

**Divirta-se usando o Bsmart-ALM! 🚀**
