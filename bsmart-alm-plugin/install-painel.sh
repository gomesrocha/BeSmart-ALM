#!/bin/bash

# Script de instalação rápida do Bsmart-ALM Plugin com Painel Lateral
# Versão: 1.0.0

echo "🚀 Instalando Bsmart-ALM Plugin com Painel Lateral..."
echo ""

# Verificar se o arquivo .vsix existe
if [ ! -f "bsmart-alm-plugin-1.0.0.vsix" ]; then
    echo "❌ Erro: Arquivo bsmart-alm-plugin-1.0.0.vsix não encontrado!"
    echo "   Execute este script do diretório bsmart-alm-plugin/"
    exit 1
fi

# Verificar se o VS Code está instalado
if ! command -v code &> /dev/null; then
    echo "❌ Erro: VS Code não encontrado!"
    echo "   Instale o VS Code primeiro: https://code.visualstudio.com/"
    exit 1
fi

echo "📦 Desinstalando versão anterior (se existir)..."
code --uninstall-extension bsmart-alm-plugin 2>/dev/null || true
echo ""

echo "📥 Instalando nova versão com painel lateral..."
code --install-extension bsmart-alm-plugin-1.0.0.vsix
echo ""

if [ $? -eq 0 ]; then
    echo "✅ Plugin instalado com sucesso!"
    echo ""
    echo "🎯 Próximos passos:"
    echo "   1. Recarregue o VS Code (Ctrl+Shift+P → 'Reload Window')"
    echo "   2. Procure o ícone 🚀 na barra lateral esquerda"
    echo "   3. Clique no ícone para abrir o painel Bsmart-ALM"
    echo "   4. Faça login e comece a usar!"
    echo ""
    echo "📚 Documentação:"
    echo "   - 🎯_PAINEL_LATERAL.md - Guia completo do painel"
    echo "   - 🚀_COMO_USAR.md - Como usar o plugin"
    echo "   - TROUBLESHOOTING.md - Solução de problemas"
    echo ""
    echo "🎊 Aproveite o novo painel lateral!"
else
    echo "❌ Erro na instalação!"
    echo "   Tente instalar manualmente:"
    echo "   code --install-extension bsmart-alm-plugin-1.0.0.vsix"
    exit 1
fi
