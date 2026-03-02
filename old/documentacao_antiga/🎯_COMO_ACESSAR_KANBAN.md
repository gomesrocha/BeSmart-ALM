# 🎯 Como Acessar o Kanban Board

## 📍 Localização

O Kanban Board está acessível através da página de Work Items.

---

## 🚀 Passo a Passo

### Método 1: Através do Menu Principal

```
1. Faça login no sistema
2. Clique em "Work Items" no menu lateral
3. Na página de Work Items, clique no botão "Kanban View" (roxo)
4. Você será redirecionado para /work-items/kanban
```

### Método 2: URL Direta

```
Acesse diretamente: http://localhost:5173/work-items/kanban
```

---

## 🎨 Visual do Botão

Na página de Work Items, você verá:

```
┌─────────────────────────────────────────────────────┐
│ Work Items                    [Kanban View] [+ New] │
│ Manage requirements, user stories, tasks and more   │
└─────────────────────────────────────────────────────┘
```

O botão **"Kanban View"** é roxo e fica ao lado do botão "New Work Item".

---

## 📋 O Que Você Verá no Kanban

### 6 Colunas:
```
┌────────┐ ┌──────────┐ ┌─────────┐ ┌─────────┐ ┌──────────┐ ┌──────┐
│ Draft  │ │In Review │ │Approved │ │Rejected │ │Progress  │ │ Done │
└────────┘ └──────────┘ └─────────┘ └─────────┘ └──────────┘ └──────┘
```

### Funcionalidades:
- ✅ Arrastar e soltar cards entre colunas
- ✅ Validação de transições (verde = válido, vermelho = inválido)
- ✅ Feedback visual ao arrastar
- ✅ Contador de items por coluna
- ✅ Prioridade colorida nos cards
- ✅ Indicador de atribuição (👤)

---

## 🧪 Teste Rápido

1. **Acesse Work Items**
   ```
   Menu → Work Items
   ```

2. **Clique em "Kanban View"**
   ```
   Botão roxo no canto superior direito
   ```

3. **Arraste um Card**
   ```
   - Pegue um card de "Draft"
   - Arraste para "In Review"
   - Veja a validação em ação
   ```

---

## ❓ Troubleshooting

### Problema: Não vejo o botão "Kanban View"
**Solução**: 
- Limpe o cache do navegador (Ctrl+Shift+R)
- Verifique se está na página /work-items
- Recarregue o frontend

### Problema: Botão não funciona
**Solução**:
- Verifique console do navegador (F12)
- Certifique-se que o frontend está rodando
- Tente acessar diretamente: /work-items/kanban

### Problema: Página Kanban não carrega
**Solução**:
- Verifique se há work items criados
- Verifique se o backend está rodando
- Veja logs do console

---

## 📸 Screenshots Esperados

### 1. Página Work Items com Botão
```
┌──────────────────────────────────────────────────────────┐
│ Work Items                                               │
│ Manage requirements, user stories, tasks and more        │
│                                                          │
│                    [🟣 Kanban View] [🔵 + New Work Item]│
└──────────────────────────────────────────────────────────┘
```

### 2. Kanban Board
```
┌──────────────────────────────────────────────────────────┐
│ ← Back to Work Items    Kanban Board    [+ New Work Item]│
│ Drag and drop to change status                           │
├──────────────────────────────────────────────────────────┤
│                                                          │
│ [Draft] [In Review] [Approved] [Rejected] [Progress] [Done]│
│                                                          │
│  Card1   Card2      Card3      (empty)    Card4     Card5│
│  Card6                                                   │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## ✅ Checklist de Verificação

Após acessar o Kanban, verifique:

- [ ] Vejo 6 colunas
- [ ] Vejo cards nos work items existentes
- [ ] Posso arrastar cards
- [ ] Vejo feedback visual (verde/vermelho)
- [ ] Transições inválidas são bloqueadas
- [ ] Contador de items está correto
- [ ] Prioridades estão coloridas
- [ ] Posso clicar em um card para ver detalhes

---

## 🎯 Transições Válidas

Lembre-se das transições permitidas:

```
Draft → In Review ✅
In Review → Approved ✅
In Review → Rejected ✅
Approved → In Progress ✅
Rejected → Draft ✅
In Progress → Done ✅

Draft → Done ❌ (bloqueado)
Done → qualquer ❌ (estado final)
```

---

## 📞 Suporte

Se ainda não conseguir acessar:
1. Verifique se o sistema está rodando
2. Verifique console do navegador
3. Consulte `🧪_GUIA_TESTE_MELHORIAS.md`
4. Consulte `🎨_MELHORIAS_IMPLEMENTADAS.md`

---

**Atualizado**: 24/02/2026  
**Status**: ✅ Botão Adicionado  
**Localização**: Work Items → Kanban View
