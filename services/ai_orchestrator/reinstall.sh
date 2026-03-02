#!/bin/bash
# Reinstall AI Orchestrator after restructuring

echo "🔄 Reinstalling AI Orchestrator..."

# Activate venv if exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "❌ No virtual environment found. Run ./setup.sh first"
    exit 1
fi

# Reinstall package
echo "📦 Reinstalling package..."
uv pip install -e . --force-reinstall --no-deps

# Install dependencies
echo "📥 Installing dependencies..."
uv pip install -e .

echo "✅ Reinstallation complete!"
echo ""
echo "Test with:"
echo "  uv run python start_web.py"
