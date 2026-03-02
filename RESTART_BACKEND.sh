#!/bin/bash

echo "🔄 Reiniciando Backend..."

# Matar processos existentes
pkill -f "uvicorn services.api_gateway.main:app" 2>/dev/null
sleep 2

# Iniciar backend
echo "🚀 Iniciando backend..."
cd /home/fabio/organizacao/repository/bsmart-alm
uv run uvicorn services.api_gateway.main:app --reload --port 8086 &

echo "✅ Backend reiniciado!"
echo "📝 Aguarde alguns segundos para o backend inicializar..."
sleep 5

# Verificar se está rodando
if curl -s http://localhost:8086/health > /dev/null; then
    echo "✅ Backend está rodando!"
else
    echo "❌ Backend não está respondendo"
fi
