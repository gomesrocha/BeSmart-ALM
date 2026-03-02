#!/bin/bash

# 🛑 Script para parar o Bsmart-ALM

set -e

# Cores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}🛑 Parando Bsmart-ALM...${NC}"
echo ""

LOG_DIR="logs"

# Parar backend
if [ -f "$LOG_DIR/backend.pid" ]; then
    BACKEND_PID=$(cat $LOG_DIR/backend.pid)
    if ps -p $BACKEND_PID > /dev/null 2>&1; then
        echo -e "${YELLOW}🔧 Parando Backend (PID: $BACKEND_PID)...${NC}"
        kill $BACKEND_PID 2>/dev/null || true
        echo -e "${GREEN}✅ Backend parado${NC}"
    else
        echo -e "${YELLOW}⚠️  Backend já estava parado${NC}"
    fi
    rm $LOG_DIR/backend.pid
else
    echo -e "${YELLOW}⚠️  PID do backend não encontrado${NC}"
fi
echo ""

# Parar frontend
if [ -f "$LOG_DIR/frontend.pid" ]; then
    FRONTEND_PID=$(cat $LOG_DIR/frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null 2>&1; then
        echo -e "${YELLOW}🎨 Parando Frontend (PID: $FRONTEND_PID)...${NC}"
        kill $FRONTEND_PID 2>/dev/null || true
        echo -e "${GREEN}✅ Frontend parado${NC}"
    else
        echo -e "${YELLOW}⚠️  Frontend já estava parado${NC}"
    fi
    rm $LOG_DIR/frontend.pid
else
    echo -e "${YELLOW}⚠️  PID do frontend não encontrado${NC}"
fi
echo ""

# Parar containers Docker (opcional)
read -p "Deseja parar os containers Docker também? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}🐳 Parando containers Docker...${NC}"
    docker compose down
    echo -e "${GREEN}✅ Containers parados${NC}"
else
    echo -e "${YELLOW}⚠️  Containers Docker continuam rodando${NC}"
fi
echo ""

echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ Bsmart-ALM parado com sucesso!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${YELLOW}💡 Para iniciar novamente: ./RUN_APP.sh${NC}"
echo ""
