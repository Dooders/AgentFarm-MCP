# 🚀 Streamlit Demo - Quick Start Guide

Get the MCP Simulation Server demo running in 5 minutes!

## Prerequisites

- **Python 3.8+** installed
- **Anthropic API Key** ([Get one free](https://console.anthropic.com))
- **Git** (to clone the repository)

## Step-by-Step Setup

### 1. Clone and Navigate

```bash
git clone <repository-url>
cd AgentFarm-MCP
```

### 2. Install Dependencies

```bash
# Install base requirements
pip install -r requirements.txt

# Install Streamlit demo requirements
pip install -r requirements-streamlit.txt
```

Or install everything at once:

```bash
pip install streamlit plotly anthropic fastmcp sqlalchemy pydantic pandas numpy python-dotenv pyyaml
```

### 3. Configure Environment

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your API key
nano .env  # or use your favorite editor
```

Set your API key in `.env`:
```
ANTHROPIC_API_KEY=sk-ant-api03-...your-key-here...
DB_PATH=simulation.db
```

### 4. Verify Setup

```bash
# Run the validation script
python3 validate_demo.py
```

You should see all green checkmarks ✅

### 5. Launch the Demo

```bash
# Using the launch script (recommended)
./run_demo.sh

# Or directly with Streamlit
streamlit run streamlit_demo.py
```

The app will open automatically in your browser at `http://localhost:8501`

## First Steps in the Demo

### Try These Queries

1. **Get Started**
   - Click the example queries in the sidebar, OR
   - Type your own question in the chat

2. **Example Questions**
   ```
   List all available simulations
   What's the population growth rate?
   Show me the top 10 longest-surviving agents
   Analyze population dynamics with a chart
   ```

3. **Explore Tool Results**
   - Click on the expandable "🔧 Tool" sections
   - View JSON data, tables, and interactive charts
   - Check execution times and cache hits

## Troubleshooting

### "ANTHROPIC_API_KEY not set"
**Fix:** Make sure you created `.env` and added your API key

### "Database file not found"
**Fix:** The `simulation.db` should be in the workspace. Check `DB_PATH` in `.env`

### "No module named 'streamlit'"
**Fix:** Install requirements: `pip install -r requirements-streamlit.txt`

### Port Already in Use
**Fix:** Streamlit is already running. Stop it or use: `streamlit run streamlit_demo.py --server.port 8502`

## Using the Interface

### Sidebar Features
- **Server Status**: Real-time health indicator
- **Example Queries**: Click to try pre-built questions
- **Clear Chat**: Reset conversation
- **Tool Catalog**: Quick reference

### Main Chat
- **Type naturally**: Ask questions in plain English
- **View results**: Expandable tool results with visualizations
- **See timing**: Every tool shows execution time

### Visualizations
- **Population charts**: Interactive Plotly graphs
- **Data tables**: Sortable, filterable agent data
- **JSON viewers**: Explore detailed results

## What Can You Ask?

The demo has access to **25 MCP tools** across these categories:

### 🔍 Discovery
- "List all simulations"
- "Show simulation details"
- "What experiments exist?"

### 📈 Analysis
- "Analyze population dynamics"
- "What's the growth rate?"
- "Show survival rates by generation"
- "Find critical events"

### 👤 Agents
- "Find all agents from generation 2"
- "Show top 10 survivors"
- "Get agent X's complete lifecycle"
- "Build a family tree for agent Y"

### 🔄 Comparisons
- "Compare multiple simulations"
- "Rank configurations by performance"
- "Compare different generations"

### 💚 System
- "Check server health"
- "Show system info"

## Next Steps

1. **Explore the tools** - Try different queries to see what's possible
2. **Read the docs** - Check [STREAMLIT_DEMO_README.md](STREAMLIT_DEMO_README.md) for details
3. **Customize** - Modify `streamlit_demo.py` to add your own features
4. **Share** - Show your team the power of LLM + MCP!

## Getting Help

- **Tool Reference**: See [docs/TOOL_CATALOG.md](docs/TOOL_CATALOG.md)
- **Full README**: See [STREAMLIT_DEMO_README.md](STREAMLIT_DEMO_README.md)
- **Troubleshooting**: See [docs/TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

---

**Ready? Let's go!** 🎉

```bash
./run_demo.sh
```
