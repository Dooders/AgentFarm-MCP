#!/bin/bash
# Setup script for the MCP Streamlit Demo

set -e  # Exit on error

echo "🚀 Setting up MCP Streamlit Demo..."
echo ""

# Check Python version
echo "📋 Checking Python version..."
python3 --version

# Install base dependencies
echo ""
echo "📦 Installing base MCP server dependencies..."
pip install -q -r requirements.txt

# Install Streamlit demo dependencies
echo ""
echo "📦 Installing Streamlit demo dependencies..."
pip install -q -r requirements-streamlit.txt

# Check for .env file
echo ""
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Creating from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your ANTHROPIC_API_KEY"
else
    echo "✅ .env file exists"
fi

# Check for database
echo ""
if [ -f "simulation.db" ]; then
    echo "✅ Database file found: simulation.db"
else
    echo "⚠️  No simulation.db file found"
    echo "   Make sure you have a simulation database before running the demo"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "   1. Edit .env and add your ANTHROPIC_API_KEY"
echo "   2. Ensure simulation.db exists in this directory"
echo "   3. Run: streamlit run streamlit_demo.py"
echo ""
