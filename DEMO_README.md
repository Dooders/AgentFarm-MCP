# MCP Streamlit Demo

Interactive chat interface to demo the MCP Simulation Server with Claude AI.

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt requirements-streamlit.txt

# 2. Configure API key
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY

# 3. Launch
streamlit run streamlit_demo.py
```

## Features

- 💬 **Natural Language Interface** - Ask questions in plain English
- 🤖 **Claude 3.5 Sonnet** - Intelligent agent with tool calling
- 🔧 **25 MCP Tools** - Full access to all simulation analysis tools
- 📊 **Interactive Charts** - Population dynamics and data visualizations
- ⚡ **Real-time Monitoring** - Server health and cache statistics

## Example Queries

Try these in the chat interface:

- "List all available simulations"
- "What's the population growth rate?"
- "Show me the top 10 longest-surviving agents"
- "Analyze population dynamics with a chart"
- "What were the critical events?"

## Files

- `streamlit_demo.py` - Main application
- `requirements-streamlit.txt` - Additional dependencies
- `.env.example` - Configuration template
- `tests/test_streamlit_demo.py` - Test suite
- `validate_demo.py` - Setup validation

## Testing

```bash
# Validate setup
python3 validate_demo.py

# Run tests
pytest tests/test_streamlit_demo.py -v
```

## Troubleshooting

**Missing API Key?**
```bash
export ANTHROPIC_API_KEY="your-key-here"
```

**Port in use?**
```bash
streamlit run streamlit_demo.py --server.port 8502
```

**Dependencies?**
```bash
pip install streamlit plotly anthropic
```

## Documentation

- See `DEMO_TESTING.md` for testing guide
- See `DEMO_TROUBLESHOOTING.md` for detailed troubleshooting
- See main `README.md` for MCP server documentation

---

**Status**: Production-ready  
**Launch**: `streamlit run streamlit_demo.py`
