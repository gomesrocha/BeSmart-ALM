#!/bin/bash

# 🚀 Script para iniciar o Bsmart-ALM completo
# Este script inicia backend e frontend automaticamente

set -e

echo "🚀 Iniciando Bsmart-ALM..."
echo ""

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar se Docker está rodando
echo -e "${BLUE}📦 Verificando Docker...${NC}"
if ! docker info > /dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Docker não está rodando. Por favor, inicie o Docker primeiro.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker está rodando${NC}"
echo ""

# Verificar se os containers estão rodando
echo -e "${BLUE}🐳 Verificando containers...${NC}"
if ! docker compose ps | grep -q "Up"; then
    echo -e "${YELLOW}⚠️  Containers não estão rodando. Iniciando...${NC}"
    docker compose up -d
    echo -e "${YELLOW}⏳ Aguardando containers iniciarem (15 segundos)...${NC}"
    sleep 15
else
    echo -e "${GREEN}✅ Containers já estão rodando${NC}"
fi
echo ""

# Verificar se o banco está populado
echo -e "${BLUE}🗄️  Verificando banco de dados...${NC}"
if ! uv run python -c "from services.shared.database import engine; from sqlmodel import Session, select; from services.identity.models import User; session = Session(engine); users = session.exec(select(User)).all(); exit(0 if users else 1)" 2>/dev/null; then
    echo -e "${YELLOW}⚠️  Banco não está populado. Executando seed...${NC}"
    make seed
else
    echo -e "${GREEN}✅ Banco de dados está populado${NC}"
fi
echo ""

# Verificar se o frontend tem node_modules
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${BLUE}📦 Instalando dependências do frontend...${NC}"
    cd frontend
    npm install
    cd ..
    echo -e "${GREEN}✅ Dependências instaladas${NC}"
    echo ""
fi

# Criar arquivo de log
LOG_DIR="logs"
mkdir -p $LOG_DIR
BACKEND_LOG="$LOG_DIR/backend.log"
FRONTEND_LOG="$LOG_DIR/frontend.log"

# Limpar logs antigos
> $BACKEND_LOG
> $FRONTEND_LOG

# Verificar se a porta 8086 está em uso
echo -e "${BLUE}🔍 Verificando porta 8086...${NC}"
if lsof -Pi :8086 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}⚠️  Porta 8086 já está em uso. Liberando...${NC}"
    PID=$(lsof -Pi :8086 -sTCP:LISTEN -t)
    kill -9 $PID 2>/dev/null || true
    sleep 2
    echo -e "${GREEN}✅ Porta 8086 liberada${NC}"
fi
echo ""

echo -e "${BLUE}🚀 Iniciando serviços...${NC}"
echo ""

# Iniciar backend em background
echo -e "${BLUE}🔧 Iniciando Backend (porta 8086)...${NC}"
uv run uvicorn services.api_gateway.main:app --reload --port 8086 > $BACKEND_LOG 2>&1 &
BACKEND_PID=$!
echo -e "${GREEN}✅ Backend iniciado (PID: $BACKEND_PID)${NC}"
echo -e "   Log: $BACKEND_LOG"
echo ""

# Aguardar backend iniciar
echo -e "${YELLOW}⏳ Aguardando backend inicializar...${NC}"
for i in {1..30}; do
    if curl -s http://localhost:8086/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend está pronto!${NC}"
        break
    fi
    sleep 1
    if [ $i -eq 30 ]; then
        echo -e "${YELLOW}⚠️  Backend demorou para iniciar. Verifique o log: $BACKEND_LOG${NC}"
    fi
done
echo ""

# Iniciar frontend em background
echo -e "${BLUE}🎨 Iniciando Frontend (porta 3000)...${NC}"
cd frontend
npm run dev > ../$FRONTEND_LOG 2>&1 &
FRONTEND_PID=$!
cd ..
echo -e "${GREEN}✅ Frontend iniciado (PID: $FRONTEND_PID)${NC}"
echo -e "   Log: $FRONTEND_LOG"
echo ""

# Aguardar frontend iniciar
echo -e "${YELLOW}⏳ Aguardando frontend inicializar...${NC}"
sleep 5
echo -e "${GREEN}✅ Frontend está pronto!${NC}"
echo ""

# Salvar PIDs para poder parar depois
echo $BACKEND_PID > $LOG_DIR/backend.pid
echo $FRONTEND_PID > $LOG_DIR/frontend.pid

# Informações finais
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}🎉 Bsmart-ALM está rodando!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}📱 URLs:${NC}"
echo -e "   Frontend:  ${GREEN}http://localhost:3000${NC}"
echo -e "   Backend:   ${GREEN}http://localhost:8086${NC}"
echo -e "   Swagger:   ${GREEN}http://localhost:8086/docs${NC}"
echo ""
echo -e "${BLUE}🔐 Credenciais de teste:${NC}"
echo -e "   Email:     ${GREEN}admin@test.com${NC}"
echo -e "   Senha:     ${GREEN}admin123456${NC}"
echo ""
echo -e "${BLUE}📋 Logs:${NC}"
echo -e "   Backend:   ${YELLOW}tail -f $BACKEND_LOG${NC}"
echo -e "   Frontend:  ${YELLOW}tail -f $FRONTEND_LOG${NC}"
echo ""
echo -e "${BLUE}🛑 Para parar:${NC}"
echo -e "   ${YELLOW}./STOP_APP.sh${NC}"
echo ""
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}💡 Dica: Abra http://localhost:3000 no seu navegador!${NC}"
echo ""

# Manter o script rodando
echo -e "${BLUE}Pressione Ctrl+C para parar todos os serviços...${NC}"
echo ""

# Trap para limpar ao sair
trap "echo ''; echo -e '${YELLOW}🛑 Parando serviços...${NC}'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; echo -e '${GREEN}✅ Serviços parados${NC}'; exit 0" INT TERM

# Aguardar indefinidamente
wait
