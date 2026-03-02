# 🔧 Como Reinstalar o Plugin v1.0.2

## Problema

O VS Code está usando a versão antiga do plugin em cache. Você precisa desinstalar completamente e reinstalar.

## Solução: Reinstalação Completa

### Passo 1: Desinstalar Versão Antiga

```bash
# Desinstalar via linha de comando
code --uninstall-extension bsmart.bsmart-alm-plugin
```

Ou via VS Code UI:
1. Extensions (Ctrl+Shift+X)
2. Procure "Bsmart-ALM"
3. Clique em "Uninstall"
4. **Feche COMPLETAMENTE o VS Code** (todas as janelas)

### Passo 2: Limpar Cache (IMPORTANTE!)

```bash
# Linux/Mac
rm -rf ~/.vscode/extensions/bsmart.bsmart-alm-plugin-*

# Ou manualmente, delete a pasta:
# ~/.vscode/extensions/bsmart.bsmart-alm-plugin-1.0.1/
# ~/.vscode/extensions/bsmart.bsmart-alm-plugin-1.0.2/
```

### Passo 3: Instalar Nova Versão

```bash
cd bsmart-alm-plugin
code --install-extension bsmart-alm-plugin-1.0.2.vsix
```

### Passo 4: Reiniciar VS Code

**IMPORTANTE**: Feche TODAS as janelas do VS Code e abra novamente.

### Passo 5: Verificar Instalação

1. Abra VS Code
2. Extensions (Ctrl+Shift+X)
3. Procure "Bsmart-ALM"
4. Verifique se a versão é **1.0.2**

### Passo 6: Testar

1. Faça login: `Ctrl+Shift+P` → "Bsmart: Login"
2. Selecione projeto: `Ctrl+Shift+P` → "Bsmart: Select Project"
3. Veja a árvore na barra lateral (ícone 🚀)
4. Você deve ver:
   ```
   📋 Specification
   🏗️ Architecture
   📝 Work Items
      ├── Work Item 1
      └── ...
   ```

## Script Automático (Linux/Mac)

Crie um arquivo `reinstall.sh`:

```bash
#!/bin/bash

echo "🔧 Desinstalando versão antiga..."
code --uninstall-extension bsmart.bsmart-alm-plugin

echo "🧹 Limpando cache..."
rm -rf ~/.vscode/extensions/bsmart.bsmart-alm-plugin-*

echo "📦 Instalando v1.0.2..."
code --install-extension bsmart-alm-plugin/bsmart-alm-plugin-1.0.2.vsix

echo "✅ Pronto! Reinicie o VS Code."
```

Execute:
```bash
chmod +x reinstall.sh
./reinstall.sh
```

## Verificar Logs

Se ainda não funcionar, verifique os logs:

1. View → Output (Ctrl+Shift+U)
2. Selecione "Bsmart-ALM" no dropdown
3. Procure por erros ou mensagens de debug

Você deve ver:
```
[WorkItemService] Fetching work items for project...
[SpecificationService] Fetching specification...
[ArchitectureService] Fetching architecture...
```

## Troubleshooting

### Ainda mostra versão antiga

1. Feche TODAS as janelas do VS Code
2. Delete manualmente: `~/.vscode/extensions/bsmart.bsmart-alm-plugin-*`
3. Reinstale o VSIX
4. Reinicie o VS Code

### Não aparece na lista de extensões

1. Verifique se o arquivo VSIX existe: `ls -lh bsmart-alm-plugin/bsmart-alm-plugin-1.0.2.vsix`
2. Tente instalar via UI: Extensions → "..." → "Install from VSIX..."

### Erro ao instalar

Se der erro de "publisher", edite o `package.json` e adicione:
```json
"publisher": "bsmart-team"
```

Depois recompile e gere o VSIX novamente.

## Confirmação de Sucesso

Você saberá que funcionou quando:
- ✅ Versão mostrada é 1.0.2
- ✅ Aparece "📋 Specification" na árvore
- ✅ Aparece "🏗️ Architecture" na árvore
- ✅ Aparece "📝 Work Items" (expandível)
- ✅ Work items carregam após selecionar projeto

---

**Se ainda não funcionar, me avise e vou investigar mais a fundo!**
