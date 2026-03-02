#!/bin/bash

# Script para iniciar Bsmart-ALM com domínios fixos do ngrok
# Backend: projectmanager.ngrok.app
# Frontend: bsmart.ngrok.app

set -e

echo "🚀 Iniciando Bsmart-ALM..."
echo ""

# Cores
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Domínios fixos
BACKEND_DOMAIN="projectmanager.ngrok.app"
FRONTEND_DOMAIN="bsmart.ngrok.app"
BACKEND_URL="https://$BACKEND_DOMAIN"
FRONTEND_URL="https://$FRONTEND_DOMAIN"

# Verificar ngrok
if ! command -v ngrok &> /dev/null; then
    echo -e "${RED}❌ ngrok não está instalado!${NC}"
    echo "Instale com: sudo snap install ngrok"
    exit 1
fi

echo -e "${GREEN}✅ ngrok instalado${NC}"
echo ""

# Criar diretório para logs
mkdir -p logs

# Função de cleanup
cleanup() {
    echo ""
    echo -e "${YELLOW}🛑 Parando serviços...${NC}"
    kill $(jobs -p) 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

# 1. Configurar Frontend
echo -e "${BLUE}⚙️  Configurando Frontend...${NC}"
cat > frontend/.env << EOF
VITE_API_URL=$BACKEND_URL/api/v1
EOF
echo -e "${GREEN}✅ Frontend configurado para usar: $BACKEND_URL/api/v1${NC}"
echo ""

# 2. Iniciar Backend
echo -e "${BLUE}📦 Iniciando Backend...${NC}"
uv run uvicorn services.api_gateway.main:app --reload --host 0.0.0.0 --port 8086 > logs/backend.log 2>&1 &
BACKEND_PID=$!
echo "   PID: $BACKEND_PID"
sleep 3

if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo -e "${RED}❌ Falha ao iniciar backend${NC}"
    cat logs/backend.log
    exit 1
fi
echo -e "${GREEN}✅ Backend rodando na porta 8086${NC}"
echo ""

# 3. Criar túnel ngrok para Backend
echo -e "${BLUE}🌐 Criando túnel ngrok para Backend...${NC}"
echo "   Domínio: $BACKEND_DOMAIN"
ngrok http 8086 --domain=$BACKEND_DOMAIN --log=stdout > logs/ngrok_backend.log 2>&1 &
NGROK_BACKEND_PID=$!
sleep 3

if ! kill -0 $NGROK_BACKEND_PID 2>/dev/null; then
    echo -e "${RED}❌ Falha ao criar túnel backend${NC}"
    cat logs/ngrok_backend.log
    cleanup
    exit 1
fi
echo -e "${GREEN}✅ Backend acessível em: $BACKEND_URL${NC}"
echo ""

# 4. Iniciar Frontend
echo -e "${BLUE}🎨 Iniciando Frontend...${NC}"
cd frontend
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo "   PID: $FRONTEND_PID"
sleep 5

if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo -e "${RED}❌ Falha ao iniciar frontend${NC}"
    cat logs/frontend.log
    cleanup
    exit 1
fi
echo -e "${GREEN}✅ Frontend rodando na porta 3000${NC}"
echo ""

# 5. Criar túnel ngrok para Frontend
echo -e "${BLUE}🌐 Criando túnel ngrok para Frontend...${NC}"
echo "   Domínio: $FRONTEND_DOMAIN"
ngrok http 3000 --domain=$FRONTEND_DOMAIN --log=stdout > logs/ngrok_frontend.log 2>&1 &
NGROK_FRONTEND_PID=$!
sleep 3

if ! kill -0 $NGROK_FRONTEND_PID 2>/dev/null; then
    echo -e "${RED}❌ Falha ao criar túnel frontend${NC}"
    cat logs/ngrok_frontend.log
    cleanup
    exit 1
fi
echo -e "${GREEN}✅ Frontend acessível em: $FRONTEND_URL${NC}"
echo ""

# Salvar informações
cat > bsmart_urls.txt << EOF
🌐 Bsmart-ALM - URLs de Acesso
================================

Frontend (Interface):
$FRONTEND_URL

Backend (API):
$BACKEND_URL

Credenciais de Teste:
Email: admin@example.com
Senha: admin123

================================
Iniciado em: $(date)

Compartilhe a URL do Frontend com seus colegas!
EOF

# Mostrar resumo
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                                                            ║"
echo "║              🎉 Bsmart-ALM Iniciado! 🎉                   ║"
echo "║                                                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo -e "${YELLOW}📱 Compartilhe com seus colegas:${NC}"
echo ""
echo -e "${GREEN}🌐 Frontend:${NC} $FRONTEND_URL"
echo -e "${BLUE}🔧 Backend:${NC}  $BACKEND_URL"
echo ""
echo -e "${YELLOW}🔑 Credenciais:${NC}"
echo "   Email: admin@example.com"
echo "   Senha: admin123"
echo ""
echo -e "${BLUE}📊 Dashboards ngrok:${NC}"
echo "   Backend:  http://localhost:4040"
echo "   Frontend: http://localhost:4041"
echo ""
echo -e "${YELLOW}📝 Informações salvas em: bsmart_urls.txt${NC}"
echo ""
echo -e "${GREEN}✨ Sistema pronto para uso!${NC}"
echo ""
echo "Pressione Ctrl+C para parar todos os serviços"
echo ""

# Manter script rodando
wait
