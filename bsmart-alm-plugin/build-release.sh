#!/bin/bash

echo "🚀 Bsmart-ALM Plugin - Build para Distribuição"
echo "=============================================="
echo ""

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Função para mensagens
info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

success() {
    echo -e "${GREEN}✓${NC} $1"
}

warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

error() {
    echo -e "${RED}✗${NC} $1"
}

# Verificar se npm está instalado
if ! command -v npm &> /dev/null; then
    error "npm não encontrado. Instale Node.js primeiro."
    exit 1
fi

# Limpar builds anteriores
info "Limpando builds anteriores..."
rm -rf out/
rm -rf node_modules/
rm -f *.vsix
success "Limpeza concluída"

# Instalar dependências
info "Instalando dependências..."
npm install
if [ $? -ne 0 ]; then
    error "Falha ao instalar dependências"
    exit 1
fi
success "Dependências instaladas"

# Compilar TypeScript
info "Compilando TypeScript..."
npm run compile
if [ $? -ne 0 ]; then
    error "Falha na compilação"
    exit 1
fi
success "Compilação concluída"

# Verificar/instalar vsce
if ! command -v vsce &> /dev/null; then
    info "Instalando vsce..."
    npm install -g @vscode/vsce
fi

# Obter versão do package.json
VERSION=$(node -p "require('./package.json').version")
info "Versão: $VERSION"

# Gerar .vsix
info "Gerando arquivo .vsix..."
vsce package --allow-star-activation
if [ $? -ne 0 ]; then
    error "Falha ao gerar .vsix"
    exit 1
fi

VSIX_FILE="bsmart-alm-plugin-${VERSION}.vsix"
success "Arquivo gerado: $VSIX_FILE"

# Calcular checksum
info "Calculando checksum..."
sha256sum "$VSIX_FILE" > "${VSIX_FILE}.sha256"
success "Checksum salvo em ${VSIX_FILE}.sha256"

# Criar diretório de release
info "Criando pacote de distribuição..."
mkdir -p release
cp "$VSIX_FILE" release/
cp "${VSIX_FILE}.sha256" release/

# Criar guia de instalação para usuários
cat > release/GUIA_INSTALACAO.md << 'EOF'
# Guia de Instalação - Plugin Bsmart-ALM

## 📦 Instalação

### Método 1: Interface Gráfica (Recomendado)

1. **Baixe o arquivo** `bsmart-alm-plugin-X.X.X.vsix`

2. **Abra o VS Code**

3. **Vá em Extensions**
   - Pressione `Ctrl+Shift+X`
   - Ou clique no ícone de Extensions na barra lateral

4. **Instale o plugin**
   - Clique no menu "..." (três pontos no topo)
   - Selecione "Install from VSIX..."
   - Navegue até o arquivo baixado
   - Clique em "Instalar"

5. **Recarregue o VS Code**
   - Pressione `Ctrl+Shift+P`
   - Digite "Reload Window"
   - Pressione Enter

### Método 2: Linha de Comando

```bash
code --install-extension bsmart-alm-plugin-X.X.X.vsix
```

## ⚙️ Configuração Inicial

1. **Fazer Login**
   - Pressione `Ctrl+Shift+P`
   - Digite "Bsmart: Login"
   - Insira:
     - Server URL: `http://seu-servidor:8086`
     - Email: seu email
     - Senha: sua senha

2. **Selecionar Projeto**
   - Pressione `Ctrl+Shift+P`
   - Digite "Bsmart: Select Project"
   - Escolha seu projeto

3. **Verificar Instalação**
   - Abra o Explorer (`Ctrl+Shift+E`)
   - Você deve ver "Bsmart Work Items" na sidebar

## 🎯 Como Usar

### Ver Work Items
- Abra o Explorer
- Veja seus work items em "Bsmart Work Items"
- Clique em um item para ver detalhes

### Exportar para IA
- Clique com botão direito em um work item
- Selecione "Export to AI Tool"
- O contexto será enviado para sua ferramenta de IA

### Atualizar Status
- Abra um work item
- Clique em "Start Work" ou "Mark as Done"

## 🔧 Configurações

Acesse via `Ctrl+,` e busque "Bsmart":

- **Server URL**: URL do servidor Bsmart-ALM
- **Default AI Tool**: Ferramenta de IA padrão (copilot, continue, kiro, cursor)
- **Auto Refresh**: Atualizar automaticamente
- **Refresh Interval**: Intervalo de atualização (segundos)

## ❓ Problemas Comuns

### Plugin não aparece
```
Ctrl+Shift+P > "Reload Window"
```

### Erro de autenticação
- Verifique se o servidor está acessível
- Confirme suas credenciais
- Verifique a URL do servidor

### Work items não aparecem
- Faça login novamente
- Selecione um projeto
- Clique em "Refresh Work Items"

## 📞 Suporte

Em caso de problemas, entre em contato com:
- Email: suporte@empresa.com
- Slack: #bsmart-suporte
EOF

success "Guia de instalação criado"

# Criar arquivo de release notes
cat > release/RELEASE_NOTES.md << EOF
# Release Notes - v${VERSION}

## 📦 Arquivos

- \`bsmart-alm-plugin-${VERSION}.vsix\` - Plugin para instalação
- \`bsmart-alm-plugin-${VERSION}.vsix.sha256\` - Checksum para verificação
- \`GUIA_INSTALACAO.md\` - Guia de instalação para usuários

## ✨ Funcionalidades

- ✅ Autenticação com Bsmart-ALM
- ✅ Visualização de work items
- ✅ Seleção de projetos
- ✅ Export para ferramentas de IA (Copilot, Continue, Kiro, Cursor)
- ✅ Integração com Git
- ✅ Atualização de status
- ✅ Adição de comentários

## 📋 Requisitos

- VS Code 1.80.0 ou superior
- Acesso ao servidor Bsmart-ALM

## 🔒 Verificação de Integridade

Para verificar a integridade do arquivo:

\`\`\`bash
sha256sum -c bsmart-alm-plugin-${VERSION}.vsix.sha256
\`\`\`

## 📝 Instalação

Veja o arquivo \`GUIA_INSTALACAO.md\` para instruções detalhadas.

## 🐛 Problemas Conhecidos

Nenhum no momento.

## 📞 Suporte

- Email: suporte@empresa.com
- Documentação: [link]
EOF

success "Release notes criadas"

# Comprimir tudo
info "Comprimindo pacote de distribuição..."
cd release
zip -r "bsmart-alm-plugin-v${VERSION}.zip" *
cd ..
success "Pacote criado: release/bsmart-alm-plugin-v${VERSION}.zip"

# Resumo final
echo ""
echo "=============================================="
echo -e "${GREEN}✓ Build concluído com sucesso!${NC}"
echo "=============================================="
echo ""
echo "📦 Arquivos gerados:"
echo "  - $VSIX_FILE"
echo "  - ${VSIX_FILE}.sha256"
echo "  - release/bsmart-alm-plugin-v${VERSION}.zip"
echo ""
echo "📋 Próximos passos:"
echo "  1. Teste o plugin: code --install-extension $VSIX_FILE"
echo "  2. Distribua o arquivo .vsix ou o .zip para os usuários"
echo "  3. Compartilhe o GUIA_INSTALACAO.md"
echo ""
echo "📖 Veja DISTRIBUICAO.md para mais detalhes sobre distribuição"
echo ""
