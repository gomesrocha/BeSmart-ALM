#!/bin/bash

echo "🚀 Instalando Bsmart-ALM Plugin..."
echo ""

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm não encontrado. Por favor, instale Node.js primeiro."
    exit 1
fi

# Check if code command is available
if ! command -v code &> /dev/null; then
    echo "❌ VS Code CLI não encontrado. Por favor, instale VS Code e adicione ao PATH."
    exit 1
fi

# Install dependencies
echo "📦 Instalando dependências..."
npm install

# Compile TypeScript
echo "🔨 Compilando TypeScript..."
npm run compile

# Check if vsce is installed
if ! command -v vsce &> /dev/null; then
    echo "📥 Instalando vsce..."
    npm install -g @vscode/vsce
fi

# Package extension
echo "📦 Empacotando extensão..."
vsce package --allow-star-activation

# Find the .vsix file
VSIX_FILE=$(ls *.vsix 2>/dev/null | head -n 1)

if [ -z "$VSIX_FILE" ]; then
    echo "❌ Erro ao criar arquivo .vsix"
    exit 1
fi

echo "✅ Arquivo criado: $VSIX_FILE"
echo ""

# Ask user if they want to install
read -p "Deseja instalar o plugin agora? (s/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[SsYy]$ ]]; then
    echo "📥 Instalando plugin no VS Code..."
    code --install-extension "$VSIX_FILE"
    
    echo ""
    echo "✅ Plugin instalado com sucesso!"
    echo ""
    echo "Para usar:"
    echo "1. Recarregue o VS Code (Ctrl+Shift+P > 'Reload Window')"
    echo "2. Abra Command Palette (Ctrl+Shift+P)"
    echo "3. Digite 'Bsmart: Login'"
    echo ""
else
    echo ""
    echo "Para instalar manualmente:"
    echo "  code --install-extension $VSIX_FILE"
    echo ""
fi

echo "📖 Veja INSTALLATION.md para mais detalhes"
