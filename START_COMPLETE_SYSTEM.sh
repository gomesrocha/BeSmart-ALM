#!/bin/bash

# 🚀 Bsmart-ALM - Complete System Startup Script
# This script starts the complete system with all new features

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║         🚀 Bsmart-ALM - Complete System Startup          ║"
echo "║                  Sprint 3 - Advanced Features             ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored messages
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Docker is running
print_info "Checking Docker..."
if ! docker info > /dev/null 2>&1; then
    print_error "Docker is not running. Please start Docker first."
    exit 1
fi
print_success "Docker is running"

# Check if .env exists
if [ ! -f .env ]; then
    print_warning ".env file not found. Creating from .env.example..."
    cp .env.example .env
    print_success ".env file created"
fi

# Start PostgreSQL
print_info "Starting PostgreSQL..."
docker-compose up -d postgres
sleep 3
print_success "PostgreSQL started"

# Check if database needs migration
print_info "Checking database migrations..."
if ! uv run python -c "from services.shared.database import engine; import asyncio; asyncio.run(engine.connect())" 2>/dev/null; then
    print_warning "Database needs initialization"
    print_info "Running database migrations..."
    uv run python scripts/migrate_ai_stats.py
    print_success "Database migrations completed"
else
    print_success "Database is ready"
fi

# Check if we need to seed data
print_info "Checking if database has data..."
HAS_DATA=$(docker exec -it bsmart-alm-postgres-1 psql -U postgres -d bsmart_alm -t -c "SELECT COUNT(*) FROM tenant;" 2>/dev/null | tr -d ' \n\r' || echo "0")
if [ "$HAS_DATA" = "0" ]; then
    print_warning "Database is empty. Seeding initial data..."
    uv run python scripts/seed_db.py
    print_success "Database seeded"
else
    print_success "Database has data"
fi

# Install frontend dependencies if needed
if [ ! -d "frontend/node_modules" ]; then
    print_info "Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
    print_success "Frontend dependencies installed"
fi

# Build frontend
print_info "Building frontend..."
cd frontend
npm run build
cd ..
print_success "Frontend built successfully"

# Start backend
print_info "Starting backend server..."
echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                    🎉 System Ready!                       ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 New Features Available:"
echo "   • Kanban Board with Drag & Drop"
echo "   • Clickable Progress Steps Navigation"
echo "   • Markdown Export for Documents"
echo "   • AI Usage Statistics Dashboard"
echo ""
echo "🌐 Access the application at:"
echo "   Frontend: http://localhost:5173"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "👤 Default Login:"
echo "   Email:    admin@example.com"
echo "   Password: admin123"
echo ""
echo "📚 Documentation:"
echo "   • GUIA_TESTE_RAPIDO.md - Quick test guide"
echo "   • IMPLEMENTACOES_AVANCADAS_COMPLETAS.md - Complete implementation"
echo "   • RESUMO_EXECUTIVO_SPRINT3.md - Executive summary"
echo ""
echo "🚀 Starting backend server..."
echo "   Press Ctrl+C to stop"
echo ""

# Start backend in foreground
uv run uvicorn services.api_gateway.main:app --reload --host 0.0.0.0 --port 8000
