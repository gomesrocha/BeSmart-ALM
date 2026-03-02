#!/bin/bash
# Setup AI Orchestrator

echo "🔧 Setting up AI Orchestrator..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv not found. Installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
uv venv

# Activate and install dependencies
echo "📥 Installing dependencies..."
source .venv/bin/activate
uv pip install -e .

echo "✅ Setup complete!"
echo ""
echo "To start the Web UI:"
echo "  uv run python start_web.py"
echo ""
echo "To start the CLI:"
echo "  uv run python start_cli.py"
echo ""
echo "Or activate the environment first:"
echo "  source .venv/bin/activate"
echo "  python start_web.py"
