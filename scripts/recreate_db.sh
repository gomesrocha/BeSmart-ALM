#!/bin/bash

# Script to reset database and seed with initial data

echo "🚀 Bsmart-ALM Database Reset"
echo "================================"
echo ""
echo "⚠️  WARNING: This will DELETE ALL DATA in the database!"
echo ""
read -p "Are you sure you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ Aborted"
    exit 1
fi

echo ""
echo "🔄 Resetting database..."

# Run Python script to reset and seed using uv
uv run python scripts/reset_and_seed.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Database reset complete!"
    echo ""
    echo "📝 Next steps:"
    echo "   1. Start backend: make dev"
    echo "   2. Start frontend: cd frontend && npm run dev"
    echo "   3. Login with: admin@example.com / admin123"
else
    echo ""
    echo "❌ Database reset failed!"
    exit 1
fi

