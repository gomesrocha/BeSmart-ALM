#!/bin/bash

echo "🚀 Iniciando Bsmart-ALM Backend..."
echo ""

# Matar processos antigos
echo "🔄 Parando processos antigos..."
pkill -f "uvicorn.*8086" 2>/dev/null || true
sleep 2

# Iniciar o servidor
echo "✅ Iniciando servidor na porta 8086..."
cd "$(dirname "$0")"
uv run uvicorn services.api_gateway.main:app --host 0.0.0.0 --port 8086 --reload
