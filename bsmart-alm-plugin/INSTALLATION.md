# Como Instalar o Plugin Bsmart-ALM no VS Code

## Opção 1: Desenvolvimento/Teste (Recomendado para agora)

Esta é a forma mais rápida para testar o plugin durante o desenvolvimento:

### Passo 1: Preparar o ambiente
```bash
cd bsmart-alm-plugin
npm install
npm run compile
```

### Passo 2: Abrir no VS Code
```bash
code .
```

### Passo 3: Executar em modo debug
1. Pressione `F5` (ou vá em Run > Start Debugging)
2. Uma nova janela do VS Code será aberta (Extension Development Host)
3. Nesta nova janela, o plugin estará ativo e funcionando
4. Você pode testar todas as funcionalidades

### Passo 4: Testar o plugin
Na janela Extension Development Host:
1. Abra Command Palette (`Ctrl+Shift+P`)
2. Digite "Bsmart: Login"
3. Siga o fluxo de autenticação

---

## Opção 2: Instalar Localmente (Arquivo .vsix)

Para instalar permanentemente no seu VS Code:

### Passo 1: Instalar vsce (VS Code Extension Manager)
```bash
npm install -g @vscode/vsce
```

### Passo 2: Compilar e empacotar
```bash
cd bsmart-alm-plugin
npm install
npm run compile
vsce package
```

Isso criará um arquivo `bsmart-alm-plugin-1.0.0.vsix`

### Passo 3: Instalar no VS Code

**Opção A - Via Command Line:**
```bash
code --install-extension bsmart-alm-plugin-1.0.0.vsix
```

**Opção B - Via Interface:**
1. Abra VS Code
2. Vá em Extensions (Ctrl+Shift+X)
3. Clique no menu "..." (três pontos) no topo
4. Selecione "Install from VSIX..."
5. Navegue até o arquivo `.vsix` e selecione

### Passo 4: Recarregar VS Code
1. Pressione `Ctrl+Shift+P`
2. Digite "Reload Window"
3. O plugin estará instalado e ativo

---

## Opção 3: Publicar no Marketplace (Futuro)

Para disponibilizar publicamente:

### Passo 1: Criar conta no Visual Studio Marketplace
1. Acesse https://marketplace.visualstudio.com/
2. Crie uma conta Microsoft/Azure DevOps
3. Crie um Personal Access Token

### Passo 2: Publicar
```bash
vsce login <publisher-name>
vsce publish
```

Depois disso, qualquer pessoa poderá instalar via:
1. Extensions no VS Code
2. Buscar por "Bsmart-ALM"
3. Clicar em Install

---

## Verificar Instalação

Após instalar, verifique se está funcionando:

1. Abra Command Palette (`Ctrl+Shift+P`)
2. Digite "Bsmart" - você deve ver os comandos:
   - Bsmart: Login to Bsmart-ALM
   - Bsmart: Logout from Bsmart-ALM
   - Bsmart: Select Project
   - Bsmart: Refresh Work Items
   - etc.

3. No Explorer (sidebar esquerda), você deve ver uma seção "Bsmart Work Items"

---

## Desinstalar

**Via Interface:**
1. Vá em Extensions (Ctrl+Shift+X)
2. Procure "Bsmart-ALM Integration"
3. Clique em "Uninstall"

**Via Command Line:**
```bash
code --uninstall-extension bsmart.bsmart-alm-plugin
```

---

## Troubleshooting

### Plugin não aparece após instalação
- Recarregue a janela: `Ctrl+Shift+P` > "Reload Window"
- Verifique se não há erros: `Ctrl+Shift+P` > "Developer: Toggle Developer Tools"

### Erro ao compilar
```bash
# Limpe e reinstale dependências
rm -rf node_modules
rm package-lock.json
npm install
npm run compile
```

### Erro ao empacotar
```bash
# Verifique se vsce está instalado
npm install -g @vscode/vsce

# Tente novamente
vsce package --allow-star-activation
```

---

## Configuração Inicial

Após instalar, configure:

1. Abra Settings (`Ctrl+,`)
2. Busque por "Bsmart"
3. Configure:
   - **Server URL**: URL do seu servidor Bsmart-ALM (ex: http://localhost:8086)
   - **Default AI Tool**: Ferramenta de IA preferida (copilot, continue, kiro, cursor)
   - **Auto Refresh**: Ativar refresh automático
   - **Refresh Interval**: Intervalo em segundos

Ou edite diretamente no `settings.json`:
```json
{
  "bsmart.serverUrl": "http://localhost:8086",
  "bsmart.defaultAITool": "copilot",
  "bsmart.autoRefresh": true,
  "bsmart.refreshInterval": 300
}
```
