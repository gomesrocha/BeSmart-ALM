# Quick Start - Bsmart-ALM Plugin

## Instalação Rápida (Linux/Mac)

```bash
cd bsmart-alm-plugin
./install.sh
```

## Instalação Manual

### 1. Preparar
```bash
cd bsmart-alm-plugin
npm install
npm run compile
```

### 2. Testar (Modo Desenvolvimento)
```bash
code .
# Pressione F5 para abrir Extension Development Host
```

### 3. Instalar Permanentemente
```bash
npm install -g @vscode/vsce
vsce package
code --install-extension bsmart-alm-plugin-1.0.0.vsix
```

## Primeiro Uso

### 1. Login
1. Abra VS Code
2. Pressione `Ctrl+Shift+P`
3. Digite: `Bsmart: Login to Bsmart-ALM`
4. Insira:
   - Server URL (ex: http://localhost:8086)
   - Email
   - Password

### 2. Selecionar Projeto
1. Pressione `Ctrl+Shift+P`
2. Digite: `Bsmart: Select Project`
3. Escolha seu projeto

### 3. Ver Work Items
- Abra o Explorer (Ctrl+Shift+E)
- Veja a seção "Bsmart Work Items"
- Seus work items aparecerão listados

### 4. Trabalhar com Work Item
- Clique em um work item para ver detalhes
- Use o botão "Export to AI Tool" para enviar para Copilot/Continue/Kiro
- Atualize o status conforme progride

## Comandos Disponíveis

| Comando | Atalho | Descrição |
|---------|--------|-----------|
| `Bsmart: Login` | - | Fazer login no Bsmart-ALM |
| `Bsmart: Logout` | - | Fazer logout |
| `Bsmart: Select Project` | - | Selecionar projeto |
| `Bsmart: Refresh Work Items` | - | Atualizar lista |
| `Bsmart: Export to AI Tool` | - | Exportar para IA |

## Configurações

Acesse via `Ctrl+,` e busque "Bsmart":

```json
{
  "bsmart.serverUrl": "http://localhost:8086",
  "bsmart.defaultAITool": "copilot",
  "bsmart.autoRefresh": true,
  "bsmart.refreshInterval": 300
}
```

## Troubleshooting

### Plugin não aparece
```bash
# Recarregue o VS Code
Ctrl+Shift+P > "Reload Window"
```

### Erro de compilação
```bash
rm -rf node_modules
npm install
npm run compile
```

### Ver logs de erro
```bash
Ctrl+Shift+P > "Developer: Toggle Developer Tools"
# Vá na aba Console
```

## Próximos Passos

1. ✅ Instalar plugin
2. ✅ Fazer login
3. ✅ Selecionar projeto
4. ✅ Ver work items
5. ✅ Exportar para AI
6. ✅ Atualizar status
7. 🎯 Começar a codificar!

## Suporte

- 📖 Documentação completa: `INSTALLATION.md`
- 🐛 Problemas: Abra uma issue no repositório
- 💡 Sugestões: Entre em contato com a equipe
