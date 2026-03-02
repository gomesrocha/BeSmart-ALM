#!/bin/bash

# Script de atualização do Bsmart-ALM Plugin
# Versão: 1.0.1 (Correção de projetos)

echo "🔄 Atualizando Bsmart-ALM Plugin..."
echo ""

# Verificar se o arquivo .vsix existe
if [ ! -f "bsmart-alm-plugin-1.0.1.vsix" ]; then
    echo "❌ Erro: Arquivo bsmart-alm-plugin-1.0.1.vsix não encontrado!"
    echo "   Execute este script do diretório bsmart-alm-plugin/"
    exit 1
fi

# Verificar se o VS Code está instalado
if ! command -v code &> /dev/null; then
    echo "❌ Erro: VS Code não encontrado!"
    echo "   Instale o VS Code primeiro: https://code.visualstudio.com/"
    exit 1
fi

echo "📦 Desinstalando versão anterior..."
code --uninstall-extension bsmart-alm-plugin 2>/dev/null || true
echo ""

echo "📥 Instalando versão 1.0.1 (com correção de projetos)..."
code --install-extension bsmart-alm-plugin-1.0.1.vsix
echo ""

if [ $? -eq 0 ]; then
    echo "✅ Plugin atualizado com sucesso!"
    echo ""
    echo "🔧 Correção aplicada:"
    echo "   - Projetos agora aparecem corretamente na seleção"
    echo "   - Rota de API corrigida"
    echo ""
    echo "🎯 Próximos passos:"
    echo "   1. Recarregue o VS Code (Ctrl+Shift+P → 'Reload Window')"
    echo "   2. Clique no ícone 🚀 na barra lateral"
    echo "   3. Faça login"
    echo "   4. Clique em 'Selecionar Projeto'"
    echo "   5. Seus projetos devem aparecer agora!"
    echo ""
    echo "📚 Documentação:"
    echo "   - 🔧_CORRECAO_PROJETOS.md - Detalhes da correção"
    echo ""
    echo "🎊 Aproveite a versão corrigida!"
else
    echo "❌ Erro na instalação!"
    echo "   Tente instalar manualmente:"
    echo "   code --install-extension bsmart-alm-plugin-1.0.1.vsix"
    exit 1
fi
