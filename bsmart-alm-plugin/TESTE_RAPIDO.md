# ⚡ Teste Rápido do Painel Lateral

## 🎯 Objetivo
Testar o novo painel lateral do Bsmart-ALM em 5 minutos!

---

## 📋 Pré-requisitos

- ✅ VS Code instalado
- ✅ Arquivo `bsmart-alm-plugin-1.0.0.vsix` disponível
- ✅ Backend Bsmart-ALM rodando (opcional para teste completo)

---

## ⚡ Instalação Rápida (1 minuto)

### Opção 1: Script Automático
```bash
cd bsmart-alm-plugin
./install-painel.sh
```

### Opção 2: Manual
```bash
cd bsmart-alm-plugin
code --install-extension bsmart-alm-plugin-1.0.0.vsix
```

### Opção 3: Interface Gráfica
1. Abra VS Code
2. `Ctrl+Shift+X` (Extensions)
3. Clique nos "..." no topo
4. "Install from VSIX..."
5. Selecione `bsmart-alm-plugin-1.0.0.vsix`

---

## 🔄 Recarregar VS Code (10 segundos)

```
Ctrl+Shift+P → "Reload Window"
```

Ou feche e abra o VS Code novamente.

---

## 🚀 Teste 1: Verificar Ícone (10 segundos)

### O que fazer:
1. Olhe para a barra lateral esquerda
2. Procure o ícone 🚀

### Resultado esperado:
```
┌─────┐
│ 📁  │
│ 🔍  │
│ 🌿  │
│ 🐛  │
│ 📦  │
│ 🚀  │ ← DEVE APARECER AQUI!
└─────┘
```

### ✅ Passou?
- [ ] Sim, vejo o ícone 🚀
- [ ] Não, não vejo o ícone

**Se não passou**: Recarregue o VS Code novamente.

---

## 🎨 Teste 2: Abrir Painel (5 segundos)

### O que fazer:
1. Clique no ícone 🚀

### Resultado esperado:
Um painel lateral abre com:
```
┌─────────────────────────────────┐
│ 🚀 Bsmart-ALM                   │
├─────────────────────────────────┤
│                                 │
│     Faça login para começar     │
│                                 │
│  [🔑 Fazer Login]               │
│                                 │
└─────────────────────────────────┘
```

### ✅ Passou?
- [ ] Sim, o painel abriu
- [ ] Não, nada aconteceu

**Se não passou**: 
1. Verifique se o plugin está ativado
2. Veja os logs: `Ctrl+Shift+U` → "Extension Host"

---

## 🔑 Teste 3: Interface de Login (30 segundos)

### O que fazer:
1. Clique no botão "🔑 Fazer Login"
2. Observe o que acontece

### Resultado esperado:
- Diálogo de configuração aparece
- Solicita URL da API
- Ou abre formulário de login

### ✅ Passou?
- [ ] Sim, diálogo apareceu
- [ ] Não, nada aconteceu

**Se não passou**: Verifique os logs do VS Code.

---

## 🎯 Teste 4: Login Completo (2 minutos)

**Nota**: Requer backend rodando!

### O que fazer:
1. Configure a URL da API (ex: `http://localhost:8000`)
2. Digite suas credenciais
3. Faça login

### Resultado esperado:
```
┌─────────────────────────────────┐
│ 🚀 Bsmart-ALM                   │
├─────────────────────────────────┤
│ USUÁRIO                         │
│ ┌─────────────────────────────┐ │
│ │ Seu Nome                    │ │
│ │ seu@email.com               │ │
│ └─────────────────────────────┘ │
│ [Sair]                          │
│                                 │
│ PROJETO                         │
│ ┌─────────────────────────────┐ │
│ │ Nenhum projeto selecionado  │ │
│ └─────────────────────────────┘ │
│ [📁 Selecionar Projeto]         │
└─────────────────────────────────┘
```

### ✅ Passou?
- [ ] Sim, vejo meus dados
- [ ] Não, erro de autenticação

**Se não passou**: 
- Verifique se o backend está rodando
- Confirme a URL da API
- Teste as credenciais

---

## 📁 Teste 5: Seleção de Projeto (1 minuto)

**Nota**: Requer login bem-sucedido!

### O que fazer:
1. Clique em "📁 Selecionar Projeto"
2. Escolha um projeto da lista

### Resultado esperado:
```
┌─────────────────────────────────┐
│ PROJETO                         │
│ ┌─────────────────────────────┐ │
│ │ Nome do Projeto             │ │
│ │ Descrição do projeto...     │ │
│ └─────────────────────────────┘ │
│ [📁 Selecionar Projeto]         │
│                                 │
│ WORK ITEMS                      │
│ ┌─────────────────────────────┐ │
│ │ Carregando...               │ │
│ └─────────────────────────────┘ │
│ [🔄 Atualizar]                  │
└─────────────────────────────────┘
```

### ✅ Passou?
- [ ] Sim, projeto selecionado
- [ ] Não, erro ao selecionar

---

## 🔄 Teste 6: Atualizar Dados (30 segundos)

### O que fazer:
1. Clique no botão "🔄 Atualizar"

### Resultado esperado:
- Painel recarrega
- Dados são atualizados
- Work items aparecem (se houver)

### ✅ Passou?
- [ ] Sim, dados atualizados
- [ ] Não, erro ao atualizar

---

## 🎨 Teste 7: Verificar Estilos (30 segundos)

### O que fazer:
1. Observe o painel
2. Verifique se os estilos estão corretos

### Resultado esperado:
- ✅ Cores do tema VS Code aplicadas
- ✅ Botões com hover effect
- ✅ Seções bem separadas
- ✅ Texto legível
- ✅ Ícones visíveis

### ✅ Passou?
- [ ] Sim, tudo bonito
- [ ] Não, estilos quebrados

---

## 🚪 Teste 8: Logout (10 segundos)

### O que fazer:
1. Clique no botão "Sair"

### Resultado esperado:
```
┌─────────────────────────────────┐
│ 🚀 Bsmart-ALM                   │
├─────────────────────────────────┤
│                                 │
│     Faça login para começar     │
│                                 │
│  [🔑 Fazer Login]               │
│                                 │
└─────────────────────────────────┘
```

### ✅ Passou?
- [ ] Sim, voltou para tela de login
- [ ] Não, ainda logado

---

## 📊 Resultado Final

### Contagem de Testes
- Total de testes: 8
- Testes passados: ___
- Testes falhados: ___

### Status Geral
- [ ] ✅ Todos os testes passaram (8/8)
- [ ] ⚠️ Alguns testes falharam (5-7/8)
- [ ] ❌ Muitos testes falharam (<5/8)

---

## 🐛 Troubleshooting Rápido

### Problema: Ícone não aparece
**Solução**:
```bash
# Reinstalar plugin
code --uninstall-extension bsmart-alm-plugin
code --install-extension bsmart-alm-plugin-1.0.0.vsix

# Recarregar VS Code
Ctrl+Shift+P → "Reload Window"
```

### Problema: Painel não abre
**Solução**:
1. Verifique logs: `Ctrl+Shift+U` → "Extension Host"
2. Procure por erros relacionados a "bsmart"
3. Reinstale o plugin

### Problema: Erro de autenticação
**Solução**:
1. Verifique se o backend está rodando
2. Teste a URL no navegador
3. Confirme as credenciais
4. Veja os logs do backend

### Problema: Estilos quebrados
**Solução**:
1. Recarregue o VS Code
2. Troque o tema e volte
3. Reinstale o plugin

---

## 📝 Checklist de Funcionalidades

### Básicas (Sem Backend)
- [ ] Ícone aparece na Activity Bar
- [ ] Painel abre ao clicar
- [ ] Interface de login é exibida
- [ ] Estilos estão corretos
- [ ] Botões são clicáveis

### Completas (Com Backend)
- [ ] Login funciona
- [ ] Dados do usuário aparecem
- [ ] Seleção de projeto funciona
- [ ] Work items são listados
- [ ] Atualização funciona
- [ ] Logout funciona
- [ ] Ações nos work items funcionam

---

## 🎯 Próximos Passos

### Se todos os testes passaram:
1. ✅ Plugin está funcionando perfeitamente!
2. 📚 Leia `GUIA_VISUAL_PAINEL.md` para mais detalhes
3. 🚀 Comece a usar no dia a dia
4. 💡 Dê feedback para melhorias

### Se alguns testes falharam:
1. 📋 Anote quais testes falharam
2. 🐛 Consulte `TROUBLESHOOTING.md`
3. 📝 Verifique os logs do VS Code
4. 🔧 Tente as soluções sugeridas

### Se muitos testes falharam:
1. 🔄 Reinstale o plugin do zero
2. 🔍 Verifique pré-requisitos
3. 📞 Peça ajuda com os logs
4. 🐛 Reporte o problema

---

## 📞 Suporte

### Logs Importantes
```bash
# Logs da extensão
Ctrl+Shift+U → "Extension Host"

# Logs do VS Code
Help → Toggle Developer Tools → Console
```

### Informações para Suporte
Se precisar de ajuda, forneça:
1. Versão do VS Code
2. Sistema operacional
3. Logs da extensão
4. Passos para reproduzir o problema
5. Screenshots (se possível)

---

## 🎊 Conclusão

Se você chegou até aqui e todos os testes passaram:

**🎉 PARABÉNS! O painel lateral está funcionando perfeitamente!**

Agora você pode:
- Usar o plugin no dia a dia
- Explorar todas as funcionalidades
- Dar feedback para melhorias
- Compartilhar com a equipe

**Aproveite o novo painel lateral do Bsmart-ALM!** 🚀
