# 📦 Como Distribuir o Plugin para Usuários

## Visão Geral

Após compilar o plugin, você terá um arquivo `.vsix` que pode ser distribuído de 3 formas:

1. **Download direto** (mais simples)
2. **Servidor web/intranet**
3. **VS Code Marketplace** (público)

---

## 🎯 Passo 1: Gerar o Arquivo .vsix

### Opção A: Script Automático (Recomendado)
```bash
cd bsmart-alm-plugin
./build-release.sh
```

### Opção B: Manual
```bash
cd bsmart-alm-plugin

# 1. Instalar dependências
npm install

# 2. Compilar TypeScript
npm run compile

# 3. Instalar vsce (se ainda não tiver)
npm install -g @vscode/vsce

# 4. Gerar o .vsix
vsce package
```

Isso criará o arquivo: **`bsmart-alm-plugin-1.0.0.vsix`**

---

## 📤 Passo 2: Distribuir para Usuários

### Opção 1: Download Direto (Mais Simples)

**Para você (administrador):**
1. Gere o arquivo .vsix (passo 1)
2. Coloque o arquivo em um local acessível:
   - Pasta compartilhada na rede
   - Google Drive / Dropbox
   - Servidor web interno
   - Email para os usuários

**Para os usuários:**
1. Baixar o arquivo `bsmart-alm-plugin-1.0.0.vsix`
2. Abrir VS Code
3. Ir em Extensions (Ctrl+Shift+X)
4. Clicar no menu "..." (três pontos)
5. Selecionar "Install from VSIX..."
6. Escolher o arquivo baixado
7. Recarregar VS Code

**Via linha de comando:**
```bash
code --install-extension bsmart-alm-plugin-1.0.0.vsix
```

---

### Opção 2: Servidor Web/Intranet

Hospede o arquivo .vsix em um servidor web interno:

**1. Coloque o arquivo no servidor:**
```bash
# Exemplo com nginx
cp bsmart-alm-plugin-1.0.0.vsix /var/www/html/downloads/
```

**2. Crie uma página de download:**
```html
<!DOCTYPE html>
<html>
<head>
    <title>Bsmart-ALM Plugin</title>
</head>
<body>
    <h1>Plugin Bsmart-ALM para VS Code</h1>
    
    <h2>Download</h2>
    <a href="bsmart-alm-plugin-1.0.0.vsix" download>
        📦 Baixar Plugin (v1.0.0)
    </a>
    
    <h2>Instalação</h2>
    <ol>
        <li>Baixe o arquivo acima</li>
        <li>Abra o VS Code</li>
        <li>Vá em Extensions (Ctrl+Shift+X)</li>
        <li>Clique no menu "..." e selecione "Install from VSIX..."</li>
        <li>Selecione o arquivo baixado</li>
        <li>Recarregue o VS Code</li>
    </ol>
    
    <h2>Instalação via Linha de Comando</h2>
    <pre>code --install-extension bsmart-alm-plugin-1.0.0.vsix</pre>
</body>
</html>
```

**3. Usuários acessam:**
```
http://seu-servidor/downloads/
```

---

### Opção 3: VS Code Marketplace (Público)

Para disponibilizar publicamente no marketplace oficial:

**1. Criar conta:**
- Acesse https://marketplace.visualstudio.com/
- Crie uma conta Microsoft/Azure DevOps
- Crie um Personal Access Token (PAT)

**2. Publicar:**
```bash
# Login
vsce login seu-publisher-name

# Publicar
vsce publish
```

**3. Usuários instalam:**
- Abrem Extensions no VS Code
- Buscam "Bsmart-ALM"
- Clicam em Install

---

## 🔄 Passo 3: Atualizar o Plugin

Quando fizer mudanças:

**1. Atualizar versão no package.json:**
```json
{
  "version": "1.0.1"
}
```

**2. Gerar novo .vsix:**
```bash
npm run compile
vsce package
```

**3. Distribuir nova versão:**
- Substitua o arquivo antigo pelo novo
- Notifique os usuários
- Usuários reinstalam seguindo os mesmos passos

---

## 📋 Guia para Usuários Finais

Crie este documento para seus usuários:

### GUIA_INSTALACAO_USUARIO.md

```markdown
# Como Instalar o Plugin Bsmart-ALM

## Passo 1: Baixar o Plugin
1. Acesse [LINK DO SERVIDOR]
2. Baixe o arquivo `bsmart-alm-plugin-1.0.0.vsix`

## Passo 2: Instalar no VS Code

### Método 1: Interface Gráfica
1. Abra o VS Code
2. Clique no ícone de Extensions (Ctrl+Shift+X)
3. Clique no menu "..." (três pontos no topo)
4. Selecione "Install from VSIX..."
5. Navegue até o arquivo baixado
6. Clique em "Install"
7. Recarregue o VS Code quando solicitado

### Método 2: Linha de Comando
```bash
code --install-extension bsmart-alm-plugin-1.0.0.vsix
```

## Passo 3: Configurar

1. Abra o VS Code
2. Pressione Ctrl+Shift+P
3. Digite "Bsmart: Login"
4. Insira suas credenciais:
   - Server URL: http://seu-servidor:8086
   - Email: seu@email.com
   - Senha: sua-senha

## Verificar Instalação

1. Pressione Ctrl+Shift+P
2. Digite "Bsmart" - você deve ver os comandos disponíveis
3. No Explorer (Ctrl+Shift+E), deve aparecer "Bsmart Work Items"

## Suporte

Em caso de problemas:
- Email: suporte@empresa.com
- Slack: #bsmart-suporte
```

---

## 🚀 Script de Build para Distribuição

Criei um script `build-release.sh` que automatiza tudo:

```bash
./build-release.sh
```

Ele vai:
1. Limpar builds anteriores
2. Instalar dependências
3. Compilar TypeScript
4. Gerar o .vsix
5. Criar um README de distribuição
6. Comprimir tudo em um .zip para distribuição

---

## 📊 Estrutura de Distribuição

Após executar o build, você terá:

```
bsmart-alm-plugin/
├── bsmart-alm-plugin-1.0.0.vsix    ← Arquivo principal
├── GUIA_INSTALACAO_USUARIO.md      ← Guia para usuários
└── release/
    └── bsmart-alm-plugin-v1.0.0.zip ← Pacote completo
```

---

## 💡 Dicas de Distribuição

### Para Empresas/Intranet:
1. **Servidor interno**: Hospede em servidor web interno
2. **Email**: Envie por email com instruções
3. **Confluence/Wiki**: Crie página com link e instruções
4. **Slack/Teams**: Compartilhe no canal da equipe

### Para Controle de Versão:
1. Use Git tags: `git tag v1.0.0`
2. Crie releases no GitHub/GitLab
3. Anexe o .vsix ao release
4. Mantenha changelog atualizado

### Para Atualizações:
1. Notifique usuários via email/chat
2. Mantenha versões antigas disponíveis
3. Documente breaking changes
4. Forneça script de migração se necessário

---

## 🔒 Segurança

### Verificação de Integridade:
```bash
# Gerar checksum
sha256sum bsmart-alm-plugin-1.0.0.vsix > checksum.txt

# Usuários podem verificar
sha256sum -c checksum.txt
```

### Assinatura Digital (Opcional):
```bash
# Assinar o arquivo
gpg --sign bsmart-alm-plugin-1.0.0.vsix

# Usuários verificam
gpg --verify bsmart-alm-plugin-1.0.0.vsix.sig
```

---

## 📞 Suporte aos Usuários

### FAQ Comum:

**P: Plugin não aparece após instalação**
R: Recarregue o VS Code (Ctrl+Shift+P > "Reload Window")

**P: Erro ao instalar**
R: Verifique se tem permissões de administrador

**P: Como atualizar?**
R: Desinstale a versão antiga e instale a nova

**P: Funciona em VS Code Insiders?**
R: Sim, use o mesmo processo

---

## ✅ Checklist de Distribuição

Antes de distribuir:

- [ ] Versão atualizada no package.json
- [ ] Código compilado sem erros
- [ ] Testado em ambiente limpo
- [ ] Documentação atualizada
- [ ] Changelog criado
- [ ] .vsix gerado
- [ ] Guia de instalação criado
- [ ] Servidor/local de download preparado
- [ ] Usuários notificados
- [ ] Suporte preparado para dúvidas

---

## 🎉 Pronto!

Agora você pode distribuir o plugin para seus usuários de forma profissional e organizada!
```
