#!/bin/bash

# Script para iniciar sistema com ngrok de forma automática
# Atualiza automaticamente o frontend com a URL do backend

echo "🚀 Iniciando Bsmart-ALM com ngrok..."
echo ""

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. Verificar se ngrok está instalado
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok não está instalado!"
    echo "Instale com: sudo snap install ngrok"
    exit 1
fi

# 2. Verificar se backend está rodando
if ! curl -s http://localhost:8086/api/health > /dev/null 2>&1; then
    echo "⚠️  Backend não está rodando!"
    echo "Inicie em outro terminal:"
    echo "  uv run uvicorn services.api_gateway.main:app --reload --host 0.0.0.0 --port 8086"
    echo ""
    read -p "Pressione Enter quando o backend estiver rodando..."
fi

# 3. Iniciar túnel do backend em background
echo "📡 Criando túnel para backend..."
ngrok http 8086 --log=stdout > /tmp/ngrok-backend.log 2>&1 &
NGROK_BACKEND_PID=$!

# Aguardar ngrok iniciar
sleep 3

# 4. Obter URL do backend
BACKEND_URL=$(curl -s http://localhost:4040/api/tunnels | grep -o '"public_url":"https://[^"]*' | head -1 | cut -d'"' -f4)

if [ -z "$BACKEND_URL" ]; then
    echo "❌ Falha ao obter URL do backend ngrok"
    kill $NGROK_BACKEND_PID 2>/dev/null
    exit 1
fi

echo -e "${GREEN}✅ Backend ngrok:${NC} $BACKEND_URL"

# 5. Atualizar frontend/.env
echo "📝 Atualizando frontend/.env..."
echo "VITE_API_URL=${BACKEND_URL}/api/v1" > frontend/.env

# 6. Verificar se frontend está rodando
if ! curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "⚠️  Frontend não está rodando!"
    echo "Inicie em outro terminal:"
    echo "  cd frontend && npm run dev"
    echo ""
    read -p "Pressione Enter quando o frontend estiver rodando..."
fi

# 7. Iniciar túnel do frontend em background
echo "📡 Criando túnel para frontend..."
ngrok http 3000 --log=stdout > /tmp/ngrok-frontend.log 2>&1 &
NGROK_FRONTEND_PID=$!

# Aguardar ngrok iniciar
sleep 3

# 8. Obter URL do frontend
FRONTEND_URL=$(curl -s http://localhost:4041/api/tunnels | grep -o '"public_url":"https://[^"]*' | head -1 | cut -d'"' -f4)

if [ -z "$FRONTEND_URL" ]; then
    echo "❌ Falha ao obter URL do frontend ngrok"
    kill $NGROK_BACKEND_PID 2>/dev/null
    kill $NGROK_FRONTEND_PID 2>/dev/null
    exit 1
fi

echo -e "${GREEN}✅ Frontend ngrok:${NC} $FRONTEND_URL"
echo ""

# 9. Mostrar informações
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${BLUE}🎉 Sistema pronto para compartilhar!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo -e "${YELLOW}📱 Compartilhe esta URL com seus colegas:${NC}"
echo -e "${GREEN}   $FRONTEND_URL${NC}"
echo ""
echo -e "${YELLOW}🔑 Credenciais de teste:${NC}"
echo "   Email: admin@example.com"
echo "   Senha: admin123"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📊 Dashboards ngrok:"
echo "   Backend:  http://localhost:4040"
echo "   Frontend: http://localhost:4041"
echo ""
echo "⚠️  IMPORTANTE:"
echo "   1. Ao acessar a URL, clique em 'Visit Site' na tela de aviso do ngrok"
echo "   2. Mantenha este terminal aberto"
echo "   3. Pressione Ctrl+C para parar os túneis"
echo ""

# 10. Salvar URLs em arquivo
cat > ngrok_urls.txt << EOF
# URLs ngrok - Geradas em $(date)

Frontend: $FRONTEND_URL
Backend:  $BACKEND_URL

Credenciais:
Email: admin@example.com
Senha: admin123

Dashboards:
Backend:  http://localhost:4040
Frontend: http://localhost:4041
EOF

echo "💾 URLs salvas em: ngrok_urls.txt"
echo ""

# 11. Aguardar Ctrl+C
trap "echo ''; echo '🛑 Parando túneis ngrok...'; kill $NGROK_BACKEND_PID $NGROK_FRONTEND_PID 2>/dev/null; echo '✅ Túneis fechados'; exit 0" INT

echo "⏳ Túneis ativos. Pressione Ctrl+C para parar..."
wait
