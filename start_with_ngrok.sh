#!/bin/bash

# Script para iniciar o sistema com ngrok
# Ambos frontend e backend terão URLs dinâmicas

set -e

echo "🚀 Iniciando Bsmart-ALM com ngrok..."
echo ""

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar se ngrok está instalado
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok não está instalado!"
    echo "Instale com: sudo snap install ngrok"
    exit 1
fi

# Verificar se está autenticado
if ! ngrok config check &> /dev/null; then
    echo "❌ ngrok não está autenticado!"
    echo "Execute: ngrok config add-authtoken SEU_TOKEN"
    exit 1
fi

echo "✅ ngrok instalado e autenticado"
echo ""

# Criar diretório para logs
mkdir -p logs

# Função para cleanup ao sair
cleanup() {
    echo ""
    echo "🛑 Parando serviços..."
    kill $(jobs -p) 2>/dev/null || true
    rm -f ngrok_urls.txt
    exit 0
}

trap cleanup SIGINT SIGTERM

# 1. Iniciar Backend
echo "${BLUE}📦 Iniciando Backend...${NC}"
uv run uvicorn services.api_gateway.main:app --reload --host 0.0.0.0 --port 8086 > logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "   PID: $BACKEND_PID"
sleep 3

# Verificar se backend iniciou
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "❌ Falha ao iniciar backend"
    cat logs/backend.log
    exit 1
fi
echo "${GREEN}✅ Backend rodando${NC}"
echo ""

# 2. Criar túnel ngrok para Backend
echo "${BLUE}🌐 Criando túnel ngrok para Backend...${NC}"
ngrok http 8086 --log=stdout > logs/ngrok_backend.log 2>&1 &
NGROK_BACKEND_PID=$!
sleep 3

# Extrair URL do backend
BACKEND_URL=$(curl -s http://localhost:4040/api/tunnels | grep -o '"public_url":"https://[^"]*' | head -1 | cut -d'"' -f4)

if [ -z "$BACKEND_URL" ]; then
    echo "❌ Falha ao obter URL do ngrok para backend"
    cleanup
    exit 1
fi

echo "${GREEN}✅ Backend ngrok URL: $BACKEND_URL${NC}"
echo ""

# 3. Configurar Frontend com URL do Backend
echo "${BLUE}⚙️  Configurando Frontend...${NC}"
echo "VITE_API_URL=$BACKEND_URL/api/v1" > frontend/.env
echo "${GREEN}✅ Frontend configurado${NC}"
echo ""

# 4. Iniciar Frontend
echo "${BLUE}🎨 Iniciando Frontend...${NC}"
cd frontend
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo "   PID: $FRONTEND_PID"
sleep 5

# Verificar se frontend iniciou
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo "❌ Falha ao iniciar frontend"
    cat logs/frontend.log
    cleanup
    exit 1
fi
echo "${GREEN}✅ Frontend rodando${NC}"
echo ""

# 5. Criar túnel ngrok para Frontend
echo "${BLUE}🌐 Criando túnel ngrok para Frontend...${NC}"
ngrok http 3000 --log=stdout > logs/ngrok_frontend.log 2>&1 &
NGROK_FRONTEND_PID=$!
sleep 3

# Extrair URL do frontend
FRONTEND_URL=$(curl -s http://localhost:4041/api/tunnels | grep -o '"public_url":"https://[^"]*' | head -1 | cut -d'"' -f4)

if [ -z "$FRONTEND_URL" ]; then
    echo "❌ Falha ao obter URL do ngrok para frontend"
    cleanup
    exit 1
fi

echo "${GREEN}✅ Frontend ngrok URL: $FRONTEND_URL${NC}"
echo ""

# Salvar URLs em arquivo
cat > ngrok_urls.txt << EOF
🌐 URLs do ngrok - Bsmart-ALM
================================

Frontend (Interface):
$FRONTEND_URL

Backend (API):
$BACKEND_URL

Credenciais de Teste:
Email: admin@example.com
Senha: admin123

================================
Gerado em: $(date)
EOF

# Mostrar resumo
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║              🎉 Sistema Iniciado com Sucesso! 🎉          ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "${YELLOW}📱 Compartilhe com seus colegas:${NC}"
echo ""
echo "${GREEN}Frontend:${NC} $FRONTEND_URL"
echo "${GREEN}Backend:${NC}  $BACKEND_URL"
echo ""
echo "${YELLOW}🔑 Credenciais:${NC}"
echo "   Email: admin@example.com"
echo "   Senha: admin123"
echo ""
echo "${BLUE}📊 Dashboards:${NC}"
echo "   ngrok Backend:  http://localhost:4040"
echo "   ngrok Frontend: http://localhost:4041"
echo ""
echo "${YELLOW}📝 URLs salvas em: ngrok_urls.txt${NC}"
echo ""
echo "Pressione Ctrl+C para parar todos os serviços"
echo ""

# Manter script rodando
wait
