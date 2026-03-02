# 🧪 Teste: Documentos Gerados Editáveis

**Tempo**: 5 minutos  
**Status**: Pronto para testar

---

## 🚀 Setup (3 comandos)

```bash
# Terminal 1: Backend
cd services && uvicorn api_gateway.main:app --reload --port 8086

# Terminal 2: Frontend
cd frontend && npm run dev

# Terminal 3: Ollama
ollama serve
```

---

## ✅ Teste Completo (5 minutos)

### 1. Gerar e Salvar Especificação (2 min)

1. **Login**: admin@example.com / admin123
2. **Abrir Projeto**: Qualquer projeto com requisitos
3. **Gerar Especificação**:
   - Clicar botão "Specification"
   - Clicar "Generate Specification"
   - Aguardar 10-30s
4. **Verificar Salvamento**:
   - ✅ Ver mensagem: "✅ Especificação salva como documento do projeto!"
   - ✅ Conteúdo aparece no modal
5. **Fechar Modal**

### 2. Gerar e Salvar Arquitetura (2 min)

1. **Gerar Arquitetura**:
   - Clicar botão "Architecture"
   - Clicar "Generate Architecture"
   - Aguardar 10-30s
2. **Verificar Salvamento**:
   - ✅ Ver mensagem: "✅ Arquitetura salva como documento do projeto!"
   - ✅ Conteúdo e diagramas aparecem
3. **Fechar Modal**

### 3. Ver Documentos Gerados (1 min)

1. **Ir para Documents**:
   - Clicar botão "Documents" no header do projeto
2. **Verificar Lista**:
   - ✅ Ver "Especificação Técnica - [Nome do Projeto]"
   - ✅ Badge "Generated" em roxo
   - ✅ Categoria "specification"
   - ✅ Ver "Arquitetura - [Nome do Projeto]"
   - ✅ Badge "Generated" em roxo
   - ✅ Categoria "architecture"

### 4. Visualizar Documento (30s)

1. **Clicar** em "Especificação Técnica"
2. **Verificar**:
   - ✅ Página DocumentViewer abre
   - ✅ Título correto
   - ✅ Badge "Generated"
   - ✅ Categoria e versão exibidas
   - ✅ Conteúdo formatado aparece
   - ✅ Botão "Edit" visível

### 5. Editar Documento (2 min)

1. **Entrar em Modo Edição**:
   - Clicar botão "Edit"
2. **Verificar**:
   - ✅ Textarea grande aparece
   - ✅ Conteúdo atual está no textarea
   - ✅ Botões "Cancel" e "Save" aparecem
3. **Fazer Edição**:
   - Adicionar texto no início:
     ```
     # EDITADO POR MIM
     Esta especificação foi revisada e completada.
     
     ```
4. **Salvar**:
   - Clicar "Save"
   - Aguardar salvamento
5. **Verificar**:
   - ✅ Modo visualização volta
   - ✅ Texto editado aparece
   - ✅ Versão incrementou (v2)

### 6. Cancelar Edição (30s)

1. **Clicar "Edit"** novamente
2. **Fazer Alteração**: Adicionar texto qualquer
3. **Clicar "Cancel"**
4. **Verificar**:
   - ✅ Modo visualização volta
   - ✅ Alteração foi descartada
   - ✅ Conteúdo anterior mantido

---

## 🎯 Checklist de Validação

### Geração e Salvamento
- [ ] Especificação gera e salva
- [ ] Arquitetura gera e salva
- [ ] Mensagem de sucesso aparece
- [ ] Documentos aparecem na lista

### Visualização
- [ ] DocumentViewer abre
- [ ] Conteúdo é exibido
- [ ] Badges corretos
- [ ] Versão é exibida
- [ ] Botão "Edit" aparece

### Edição
- [ ] Modo edição ativa
- [ ] Textarea aparece com conteúdo
- [ ] Botões "Cancel" e "Save" aparecem
- [ ] Salvar funciona
- [ ] Versão incrementa
- [ ] Alterações persistem

### Cancelamento
- [ ] Cancel descarta alterações
- [ ] Volta para modo visualização
- [ ] Conteúdo original mantido

---

## 📸 Screenshots Esperados

### Lista de Documentos
```
┌─────────────────────────────────────────┐
│ Project Documents                       │
├─────────────────────────────────────────┤
│ 📄 Especificação Técnica - Projeto X   │
│    [Generated] [specification] [v1]    │
│                                         │
│ 🌐 Arquitetura - Projeto X             │
│    [Generated] [architecture] [v1]     │
│                                         │
│ 📄 Pitch Deck.pdf                       │
│    [Uploaded] [rag_source]              │
└─────────────────────────────────────────┘
```

### DocumentViewer - Visualização
```
┌─────────────────────────────────────────┐
│ ← 📄 Especificação Técnica - Projeto X │
│ [Generated] [specification] [v2]  [Edit]│
├─────────────────────────────────────────┤
│ # EDITADO POR MIM                       │
│ Esta especificação foi revisada...      │
│                                         │
│ # 1. Visão Geral do Projeto            │
│ - Objetivo: ...                         │
│ - Escopo: ...                           │
│ ...                                     │
└─────────────────────────────────────────┘
```

### DocumentViewer - Edição
```
┌─────────────────────────────────────────┐
│ ← 📄 Especificação Técnica - Projeto X │
│ [Generated] [specification] [v2]        │
│                          [Cancel] [Save]│
├─────────────────────────────────────────┤
│ Edit Content                            │
│ ┌─────────────────────────────────────┐ │
│ │ # EDITADO POR MIM                   │ │
│ │ Esta especificação foi revisada...  │ │
│ │                                     │ │
│ │ # 1. Visão Geral do Projeto        │ │
│ │ - Objetivo: ...                     │ │
│ │ ...                                 │ │
│ │ [Editável - 30 linhas]              │ │
│ └─────────────────────────────────────┘ │
│ Markdown formatting is supported        │
└─────────────────────────────────────────┘
```

---

## 🐛 Troubleshooting

### Documento não aparece na lista
**Causa**: Geração falhou ou não salvou  
**Solução**: 
1. Verificar logs do backend
2. Regenerar documento
3. Verificar se requisitos existem

### Erro ao salvar edição
**Causa**: Permissões ou documento não editável  
**Solução**:
1. Verificar se `is_editable=true`
2. Verificar permissões do usuário
3. Ver logs do backend

### Conteúdo não carrega
**Causa**: Documento não tem conteúdo  
**Solução**:
1. Verificar se é documento gerado
2. Regenerar se necessário
3. Verificar endpoint de conteúdo

### Versão não incrementa
**Causa**: Salvamento falhou  
**Solução**:
1. Verificar logs do backend
2. Tentar salvar novamente
3. Recarregar página

---

## 🎉 Sucesso!

Se todos os itens do checklist estão ✅:

**Parabéns! Os documentos editáveis estão funcionando!** 🚀

### O Que Você Tem Agora

1. ✅ **Geração Automática**: IA gera documentação
2. ✅ **Salvamento Automático**: Documentos persistem
3. ✅ **Visualização Elegante**: Interface profissional
4. ✅ **Edição Completa**: Completar e corrigir
5. ✅ **Versionamento**: Rastrear mudanças
6. ✅ **Organização**: RAG vs Gerados separados

---

## 📚 Próximos Passos

### Usar em Projeto Real
1. Criar projeto real
2. Gerar requisitos
3. Gerar especificação
4. Gerar arquitetura
5. Editar e completar documentos
6. Usar documentação no desenvolvimento

### Explorar Mais
- Ver `FASE10_DOCUMENTOS_EDITAVEIS.md` para detalhes técnicos
- Ver `COMPLETE_SYSTEM_GUIDE.md` para guia completo
- Testar versionamento (editar múltiplas vezes)
- Testar com diferentes usuários

---

**Pronto para usar!** ✨

**Status**: ✅ **TESTÁVEL AGORA**  
**Tempo**: 5 minutos  
**Dificuldade**: Fácil

🎊 **Boa sorte!** 🚀
