#!/bin/bash

echo "🔧 Corrigindo problemas de instalação do npm..."
echo ""

# Limpar cache do npm
echo "1. Limpando cache do npm..."
npm cache clean --force

# Aumentar timeout
echo "2. Aumentando timeout do npm..."
npm config set fetch-timeout 60000
npm config set fetch-retry-mintimeout 20000
npm config set fetch-retry-maxtimeout 120000

# Tentar com registry alternativo (se o padrão estiver lento)
echo "3. Configurando registry..."
npm config set registry https://registry.npmjs.org/

# Limpar node_modules e package-lock
echo "4. Limpando instalações anteriores..."
rm -rf node_modules
rm -f package-lock.json

# Tentar instalar novamente
echo "5. Instalando dependências..."
npm install --verbose

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Instalação concluída com sucesso!"
else
    echo ""
    echo "❌ Ainda com problemas. Tentando alternativas..."
    echo ""
    
    # Tentar com --legacy-peer-deps
    echo "Tentando com --legacy-peer-deps..."
    npm install --legacy-peer-deps
    
    if [ $? -eq 0 ]; then
        echo "✅ Instalação concluída!"
    else
        echo ""
        echo "❌ Problemas persistem. Soluções manuais:"
        echo ""
        echo "1. Verificar conexão com internet"
        echo "2. Verificar se está atrás de proxy/firewall"
        echo "3. Tentar com outro registry:"
        echo "   npm config set registry https://registry.npmmirror.com"
        echo "4. Ou instalar offline (se tiver os pacotes):"
        echo "   npm install --prefer-offline"
    fi
fi
