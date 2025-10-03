#!/bin/bash
# Launch script for the MCP Streamlit Demo

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found"
    echo ""
    echo "Please create a .env file with your configuration:"
    echo "  cp .env.example .env"
    echo ""
    echo "Then edit .env and set your ANTHROPIC_API_KEY"
    exit 1
fi

# Check if ANTHROPIC_API_KEY is set
source .env
if [ -z "$ANTHROPIC_API_KEY" ] || [ "$ANTHROPIC_API_KEY" = "your_anthropic_api_key_here" ]; then
    echo "❌ Error: ANTHROPIC_API_KEY not configured"
    echo ""
    echo "Please edit .env and set a valid ANTHROPIC_API_KEY"
    echo "Get your API key from: https://console.anthropic.com"
    exit 1
fi

# Check if database exists
if [ ! -f "${DB_PATH:-simulation.db}" ]; then
    echo "❌ Error: Database file not found: ${DB_PATH:-simulation.db}"
    echo ""
    echo "Please ensure the simulation database exists"
    exit 1
fi

# Launch Streamlit
echo "🚀 Launching MCP Streamlit Demo..."
echo ""
streamlit run streamlit_demo.py
