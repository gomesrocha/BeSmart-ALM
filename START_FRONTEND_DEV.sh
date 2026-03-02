#!/bin/bash

# 🎨 Bsmart-ALM - Frontend Development Server
# This script starts the frontend in development mode

set -e

echo "╔════════════════════════════════════════════════════════════╗"
echo "║         🎨 Bsmart-ALM - Frontend Dev Server              ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Check if node_modules exists
if [ ! -d "frontend/node_modules" ]; then
    print_info "Installing dependencies..."
    cd frontend
    npm install
    cd ..
    print_success "Dependencies installed"
fi

# Start frontend dev server
print_info "Starting frontend development server..."
echo ""
echo "🌐 Frontend will be available at: http://localhost:5173"
echo "🔄 Hot reload enabled"
echo ""
echo "📋 New Features:"
echo "   • Kanban Board (/work-items/kanban)"
echo "   • AI Statistics (/ai-stats)"
echo "   • Clickable Progress Steps"
echo "   • Markdown Export"
echo ""
echo "Press Ctrl+C to stop"
echo ""

cd frontend
npm run dev
