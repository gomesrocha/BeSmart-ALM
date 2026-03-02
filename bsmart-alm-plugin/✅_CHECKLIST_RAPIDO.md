# ✅ Checklist Rápido - Plugin Bsmart-ALM

## 🔍 Verificar se está instalado

```bash
# Listar extensões instaladas
code --list-extensions | grep bsmart
```

**Deve aparecer:** `bsmart.bsmart-alm-plugin`

Se não aparecer, instale:
```bash
code --install-extension bsmart-alm-plugin-1.0.0.vsix
```

---

## 🚀 Usar o Plugin - 3 Passos

### 1️⃣ Login
```
Ctrl+Shift+P
Digite: Bsmart: Login
Preencha: Server URL, Email, Senha
Clique: Entrar
```

### 2️⃣ Selecionar Projeto
```
Ctrl+Shift+P
Digite: Bsmart: Select Project
Escolha seu projeto
```

### 3️⃣ Ver Work Items
```
Ctrl+Shift+E (Explorer)
Procure: "BSMART WORK ITEMS" na sidebar
```

---

## 📍 Onde Encontrar

### Command Palette (Ctrl+Shift+P)
Digite `Bsmart` e verá todos os comandos

### Explorer Sidebar (Ctrl+Shift+E)
Procure seção `BSMART WORK ITEMS`

### Status Bar (barra inferior)
Veja `$(project) Nome do Projeto`

---

## ❌ Não Aparece?

### Solução 1: Recarregar
```
Ctrl+Shift+P
Digite: Reload Window
```

### Solução 2: Verificar Instalação
```
Ctrl+Shift+X (Extensions)
Procure: Bsmart
```

### Solução 3: Ver Logs
```
Ctrl+Shift+P
Digite: Developer: Toggle Developer Tools
Veja aba Console
```

---

## 🎯 Teste Rápido

Execute estes comandos em ordem:

1. ✅ `Ctrl+Shift+P` > `Bsmart: Login`
2. ✅ Preencha credenciais
3. ✅ `Ctrl+Shift+P` > `Bsmart: Select Project`
4. ✅ `Ctrl+Shift+E` > Veja "BSMART WORK ITEMS"
5. ✅ Clique em um work item

Se tudo funcionar, está pronto! 🎉

---

## 📞 Precisa de Ajuda?

Veja: `🚀_COMO_USAR.md` - Guia completo passo a passo
