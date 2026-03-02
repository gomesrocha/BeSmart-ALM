# 🚀 Como Usar o Plugin Bsmart-ALM no VS Code

## 📍 Onde Encontrar o Plugin

Após instalar, o plugin aparece em 3 lugares principais:

### 1. Command Palette (Ctrl+Shift+P)
### 2. Explorer Sidebar (Ctrl+Shift+E)
### 3. Status Bar (barra inferior)

---

## 🎯 Passo a Passo Completo

### PASSO 1: Abrir Command Palette

**Atalho:** `Ctrl+Shift+P` (ou `Cmd+Shift+P` no Mac)

Você verá uma caixa de busca no topo do VS Code.

### PASSO 2: Fazer Login

**Digite:** `Bsmart: Login`

Ou procure por "Bsmart" e verá todos os comandos disponíveis:
```
> Bsmart: Login to Bsmart-ALM
> Bsmart: Logout from Bsmart-ALM
> Bsmart: Select Project
> Bsmart: Refresh Work Items
> Bsmart: Export to AI Tool
```

**Selecione:** `Bsmart: Login to Bsmart-ALM`

Uma tela de login visual abrirá! Preencha:
- Server URL: `http://localhost:8086` (ou seu servidor)
- Email: seu email
- Senha: sua senha

Clique em **"Entrar"**

✅ Você verá a mensagem: "Successfully logged in to Bsmart-ALM"

---

### PASSO 3: Selecionar Projeto

**Abra Command Palette novamente:** `Ctrl+Shift+P`

**Digite:** `Bsmart: Select Project`

Uma lista de projetos aparecerá. Selecione o seu projeto.

✅ Você verá a mensagem: "Selected project: [Nome do Projeto]"

---

### PASSO 4: Ver Work Items

**Abra o Explorer:** `Ctrl+Shift+E`

Na barra lateral esquerda, você verá uma nova seção:

```
📁 EXPLORER
  📁 Pasta do Projeto
  
📋 BSMART WORK ITEMS  ← AQUI!
  📝 Implementar Login
  📝 Criar Dashboard
  📝 Adicionar Testes
```

Se não aparecer, clique no ícone de refresh ou:
- `Ctrl+Shift+P` > `Bsmart: Refresh Work Items`

---

### PASSO 5: Trabalhar em um Work Item

**Clique em um work item** na lista

Um popup aparecerá:
```
┌─────────────────────────────────────┐
│ Deseja iniciar o trabalho em        │
│ "Implementar Login"?                │
│                                      │
│  [Não]  [Sim, Iniciar]              │
└─────────────────────────────────────┘
```

**Clique em "Sim, Iniciar"**

✅ O status muda automaticamente para "Em Progresso"
✅ A tela de detalhes abre

---

### PASSO 6: Exportar para IA

Na tela de detalhes, clique no botão:

**🤖 Exportar para IA**

O contexto completo do work item será enviado para:
- GitHub Copilot (se instalado)
- Continue (se instalado)
- Kiro (se instalado)
- Cursor (se instalado)
- Ou copiado para clipboard

Agora você pode usar sua ferramenta de IA para ajudar na implementação!

---

### PASSO 7: Marcar como Concluído

Quando terminar de implementar, volte para a tela de detalhes do work item.

**Clique no botão:**

**✅ Marcar como Concluído**

Um popup de confirmação aparecerá:
```
┌─────────────────────────────────────┐
│ Deseja marcar este item como        │
│ concluído?                          │
│                                      │
│  [Cancelar]  [OK]                   │
└─────────────────────────────────────┘
```

**Clique em "OK"**

✅ Status muda para "Concluído"
✅ Mensagem: "Work item marcado como concluído!"
✅ Lista atualiza automaticamente

---

## 🔍 Onde Está Cada Coisa?

### Command Palette (Ctrl+Shift+P)
```
Digite "Bsmart" e verá:

> Bsmart: Login to Bsmart-ALM
> Bsmart: Logout from Bsmart-ALM
> Bsmart: Select Project
> Bsmart: Refresh Work Items
> Bsmart: Export to AI Tool
> Bsmart: Update Status
> Bsmart: Add Comment
```

### Explorer Sidebar (Ctrl+Shift+E)
```
Procure por:

📋 BSMART WORK ITEMS
  📝 Work Item 1
  📝 Work Item 2
  📝 Work Item 3
```

Se não aparecer:
1. Verifique se fez login
2. Verifique se selecionou um projeto
3. Clique em refresh

### Status Bar (barra inferior)
```
Procure na barra inferior:

$(project) Nome do Projeto    $(checklist) Work Item Atual
```

---

## ❓ Não Encontro o Plugin?

### Verificar se está instalado:

**1. Abra Extensions:**
- Atalho: `Ctrl+Shift+X`
- Ou clique no ícone de quadrados na barra lateral

**2. Procure por "Bsmart"**

Você deve ver:
```
🚀 Bsmart-ALM Integration
   Integrate your IDE with Bsmart-ALM
   [Desinstalar] [⚙️]
```

Se não aparecer, o plugin não está instalado!

### Instalar o plugin:

**Via Interface:**
1. Extensions (`Ctrl+Shift+X`)
2. Clique no menu "..." (três pontos no topo)
3. "Install from VSIX..."
4. Selecione `bsmart-alm-plugin-1.0.0.vsix`

**Via Comando:**
```bash
code --install-extension bsmart-alm-plugin-1.0.0.vsix
```

**Depois de instalar:**
1. Recarregue o VS Code: `Ctrl+Shift+P` > "Reload Window"
2. Tente novamente

---

## 🐛 Troubleshooting

### Plugin instalado mas não aparece nada

**1. Recarregue o VS Code:**
```
Ctrl+Shift+P > "Reload Window"
```

**2. Verifique se está ativado:**
```
Ctrl+Shift+P > Digite "Bsmart"
```

Se não aparecer nenhum comando, o plugin não está ativo.

**3. Veja os logs:**
```
Ctrl+Shift+P > "Developer: Toggle Developer Tools"
```

Vá na aba "Console" e procure por erros.

### Não vejo "Bsmart Work Items" na sidebar

**Possíveis causas:**

1. **Não fez login**
   - Solução: `Ctrl+Shift+P` > "Bsmart: Login"

2. **Não selecionou projeto**
   - Solução: `Ctrl+Shift+P` > "Bsmart: Select Project"

3. **Não tem work items atribuídos**
   - Solução: Verifique no frontend se tem work items

4. **Cache desatualizado**
   - Solução: `Ctrl+Shift+P` > "Bsmart: Refresh Work Items"

### Erro ao fazer login

**Verifique:**

1. **Server URL está correto?**
   - Deve ser: `http://localhost:8086` ou seu servidor

2. **Servidor está rodando?**
   ```bash
   curl http://localhost:8086/api/v1/health
   ```

3. **Credenciais estão corretas?**
   - Teste no frontend primeiro

4. **Firewall/Proxy?**
   - Verifique se não está bloqueando

---

## 📸 Guia Visual

### 1. Command Palette
```
┌─────────────────────────────────────────┐
│ > Bsmart                                │ ← Digite aqui
├─────────────────────────────────────────┤
│ > Bsmart: Login to Bsmart-ALM          │
│ > Bsmart: Logout from Bsmart-ALM       │
│ > Bsmart: Select Project                │
│ > Bsmart: Refresh Work Items            │
└─────────────────────────────────────────┘
```

### 2. Explorer Sidebar
```
┌─────────────────────────────────────────┐
│ EXPLORER                                │
│   📁 meu-projeto                        │
│   📁 src                                │
│                                         │
│ BSMART WORK ITEMS                       │ ← Aqui!
│   📝 Implementar Login                  │
│   📝 Criar Dashboard                    │
│   📝 Adicionar Testes                   │
└─────────────────────────────────────────┘
```

### 3. Status Bar
```
┌─────────────────────────────────────────┐
│ $(project) Meu Projeto  $(checklist) ... │ ← Aqui!
└─────────────────────────────────────────┘
```

---

## ⌨️ Atalhos Úteis

| Ação | Atalho |
|------|--------|
| Command Palette | `Ctrl+Shift+P` |
| Explorer | `Ctrl+Shift+E` |
| Extensions | `Ctrl+Shift+X` |
| Reload Window | `Ctrl+R` (após Ctrl+Shift+P) |

---

## 🎯 Fluxo Rápido

```
1. Ctrl+Shift+P
2. Digite: Bsmart: Login
3. Preencha credenciais
4. Ctrl+Shift+P
5. Digite: Bsmart: Select Project
6. Escolha projeto
7. Ctrl+Shift+E (Explorer)
8. Veja "BSMART WORK ITEMS"
9. Clique em um item
10. Clique "Sim, Iniciar"
11. Clique "Exportar para IA"
12. Desenvolva
13. Clique "Marcar como Concluído"
14. Pronto! ✅
```

---

## 📞 Ainda com Dúvidas?

1. Veja `TROUBLESHOOTING.md` para problemas comuns
2. Veja `INSTALLATION.md` para reinstalar
3. Entre em contato com suporte

---

## 🎉 Pronto!

Agora você sabe como usar o plugin! 

**Dica:** Mantenha o Explorer aberto (`Ctrl+Shift+E`) para sempre ver seus work items na sidebar.

**Bom trabalho! 🚀**
