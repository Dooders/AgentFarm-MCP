# MCP Simulation Server - Streamlit Demo App

A beautiful, interactive chat interface to demo the functionality of the MCP Simulation Server using an LLM agent powered by Claude.

## 🎯 Features

- **💬 Natural Language Interface**: Ask questions about your simulation data in plain English
- **🤖 Intelligent Agent**: Claude analyzes your queries and calls the appropriate MCP tools
- **📊 Rich Visualizations**: Interactive charts, tables, and formatted results
- **🔧 25 Available Tools**: Full access to all MCP server capabilities
- **⚡ Real-time Results**: See tool execution times and cached responses
- **📈 Data Exploration**: Population dynamics, agent analysis, survival rates, and more

## 🚀 Quick Start

### Prerequisites

1. **Python 3.8+**
2. **Anthropic API Key** - Get one from [console.anthropic.com](https://console.anthropic.com)
3. **Simulation Database** - The `simulation.db` file with your simulation data

### Installation

```bash
# 1. Install base dependencies (if not already installed)
pip install -r requirements.txt

# 2. Install Streamlit demo dependencies
pip install -r requirements-streamlit.txt

# Alternatively, install all at once:
pip install streamlit>=1.28.0 plotly>=5.17.0 anthropic>=0.21.0
```

### Configuration

Create a `.env` file in the workspace root with your API key:

```bash
# Required: Anthropic API key
ANTHROPIC_API_KEY=your_api_key_here

# Optional: Database path (defaults to simulation.db)
DB_PATH=simulation.db
```

Or export environment variables:

```bash
export ANTHROPIC_API_KEY="your_api_key_here"
export DB_PATH="simulation.db"
```

### Running the Demo

```bash
streamlit run streamlit_demo.py
```

The app will open in your browser at `http://localhost:8501`

## 💡 Usage Examples

### Example Queries

Try these natural language queries in the chat interface:

#### 🔍 Discovery & Exploration
- "List all available simulations"
- "Show me the details of the latest simulation"
- "What experiments are in the database?"

#### 📈 Population Analysis
- "What's the population growth rate in the latest simulation?"
- "Analyze population dynamics and show me a chart"
- "Were there any population crashes or critical events?"
- "Show me the population trends over time"

#### 👤 Agent Analysis
- "Show me the top 10 agents that survived the longest"
- "Find all agents from generation 2"
- "Get detailed information about agent X"
- "Build a family tree for agent X"

#### 📊 Statistical Analysis
- "Compare survival rates by generation"
- "What's the resource efficiency in the simulation?"
- "Analyze reproduction success rates"
- "Show me social interaction patterns"

#### 🔄 Comparisons
- "Compare multiple simulations"
- "Rank configurations by total agents"
- "Compare different generations"
- "What parameters have the most impact?"

#### 💚 System Monitoring
- "Check server health"
- "Show me system information"
- "What's the cache hit rate?"

## 🏗️ Architecture

### Components

```
┌─────────────────────────────────────────────────┐
│           Streamlit Web Interface               │
│  (Chat UI, Visualizations, Session State)       │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│         Anthropic Claude Agent                  │
│  (Natural Language → Tool Selection)            │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│           MCP Server (25 Tools)                 │
│  • Metadata Tools (4)                           │
│  • Query Tools (6)                              │
│  • Analysis Tools (7)                           │
│  • Comparison Tools (4)                         │
│  • Advanced Tools (2)                           │
│  • Health Tools (2)                             │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│         SQLite Simulation Database              │
│  (Agents, Actions, States, Resources, etc.)     │
└─────────────────────────────────────────────────┘
```

### How It Works

1. **User Input**: You type a natural language query in the chat interface
2. **Claude Analysis**: The Anthropic Claude model analyzes your query
3. **Tool Selection**: Claude decides which MCP tools to call and with what parameters
4. **Tool Execution**: The app executes the selected tools against the MCP server
5. **Result Formatting**: Results are formatted with visualizations, tables, and JSON
6. **Display**: The formatted results are displayed in the chat interface

### Key Features

- **Agentic Loop**: Claude can call multiple tools in sequence to answer complex queries
- **Smart Caching**: MCP server caches results for faster repeated queries
- **Type Safety**: All tool inputs are validated using Pydantic schemas
- **Error Handling**: Comprehensive error messages help debug issues
- **Session State**: Chat history is preserved during your session

## 📊 Visualizations

The demo app includes smart visualizations for different tool results:

### Population Dynamics
- **Line charts** showing population over time
- **Birth/death trends** with interactive hover details
- **Growth rate indicators**

### Agent Data Tables
- **Sortable tables** with key agent attributes
- **Filterable columns** for easy exploration
- **Export capabilities** (via Streamlit)

### JSON Data Viewers
- **Collapsible JSON** for detailed inspection
- **Syntax highlighting** for readability
- **Copy-to-clipboard** functionality

## 🛠️ Available MCP Tools

### Metadata Tools (4)
- `list_simulations` - Browse available simulations
- `get_simulation_info` - Get detailed simulation metadata
- `list_experiments` - Browse research experiments
- `get_experiment_info` - Get experiment details

### Query Tools (6)
- `query_agents` - Find agents with flexible filtering
- `query_actions` - Get action logs and behavior data
- `query_states` - Track agent states over time
- `query_resources` - Monitor environmental resources
- `query_interactions` - Study entity interactions
- `get_simulation_metrics` - Get comprehensive step-level data

### Analysis Tools (7)
- `analyze_population_dynamics` - Population trends and growth
- `analyze_survival_rates` - Survival statistics by cohort
- `analyze_resource_efficiency` - Resource utilization metrics
- `analyze_agent_performance` - Individual agent analysis
- `identify_critical_events` - Detect significant moments
- `analyze_social_patterns` - Social interaction analysis
- `analyze_reproduction` - Reproduction success rates

### Comparison Tools (4)
- `compare_simulations` - Multi-simulation comparison
- `compare_parameters` - Parameter impact analysis
- `rank_configurations` - Performance ranking
- `compare_generations` - Evolutionary progress tracking

### Advanced Tools (2)
- `build_agent_lineage` - Construct family trees
- `get_agent_lifecycle` - Complete agent history

### Health & Monitoring Tools (2)
- `health_check` - Server health monitoring
- `system_info` - System performance metrics

## 🎨 User Interface

### Sidebar
- **Server Status**: Real-time health check indicators
- **Database Info**: Connection status and details
- **Cache Stats**: Hit rate and size information
- **Example Queries**: Pre-built queries to get started
- **Clear Chat**: Reset conversation history
- **Tool Catalog**: Quick reference of available tools

### Main Chat Area
- **Message History**: Full conversation with the agent
- **Tool Results**: Expandable sections showing tool calls
- **Visualizations**: Charts and tables embedded in results
- **Execution Times**: Performance metrics for each tool call

## ⚡ Performance

- **Tool Execution**: <100ms for most queries
- **Cache Hits**: ~0ms for repeated queries
- **Chart Rendering**: Interactive Plotly charts
- **Responsive UI**: Streamlit's reactive framework

## 🔧 Customization

### Modify LLM Settings

Edit `streamlit_demo.py` to change Claude settings:

```python
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",  # Change model here
    max_tokens=4096,  # Adjust token limit
    tools=tools,
    messages=messages,
)
```

### Add Custom Visualizations

Add new visualization functions in `streamlit_demo.py`:

```python
def visualize_your_data(data: Dict[str, Any]) -> Optional[go.Figure]:
    """Create custom visualization."""
    # Your visualization logic here
    return fig
```

### Customize Styling

Modify the CSS in the `st.markdown()` section:

```python
st.markdown(
    """
    <style>
    /* Your custom CSS here */
    </style>
    """,
    unsafe_allow_html=True,
)
```

## 🐛 Troubleshooting

### API Key Issues
```
Error: ANTHROPIC_API_KEY environment variable not set!
```
**Solution**: Set your API key in `.env` or as an environment variable

### Database Not Found
```
Error: Database file not found: simulation.db
```
**Solution**: Ensure `simulation.db` exists in the workspace or set `DB_PATH` in `.env`

### Import Errors
```
ModuleNotFoundError: No module named 'streamlit'
```
**Solution**: Install requirements: `pip install -r requirements-streamlit.txt`

### Server Health Issues
Red indicator in sidebar or "unhealthy" status

**Solution**: 
1. Check database connection
2. Verify cache service is running
3. Check tool registry (should show 25/25 tools)

### Slow Performance
Tool calls taking too long

**Solution**:
1. Enable caching in config (should be enabled by default)
2. Check database size and optimize if needed
3. Reduce query limits for large datasets

## 📚 Related Documentation

- [Main README](README.md) - MCP Server overview
- [User Guide](docs/USER_GUIDE.md) - Comprehensive usage patterns
- [Tool Catalog](docs/TOOL_CATALOG.md) - Complete tool reference
- [API Reference](docs/API_REFERENCE.md) - Detailed API documentation
- [Troubleshooting](docs/TROUBLESHOOTING.md) - Common issues

## 🤝 Contributing

Improvements and suggestions welcome! Areas for enhancement:

- Additional visualizations (network graphs, heatmaps, etc.)
- More sophisticated agent conversation flows
- Export functionality for results
- Custom themes and styling
- Multi-simulation comparison visualizations

## 📄 License

This demo app is part of the AgentFarm-MCP project and follows the same MIT License.

## 🙏 Acknowledgments

- **Streamlit** - Beautiful web framework for Python
- **Anthropic Claude** - Powerful LLM with tool calling
- **Plotly** - Interactive visualization library
- **FastMCP** - MCP server framework
- **SQLAlchemy** - Database ORM

---

**Ready to explore your simulation data?** 🚀

```bash
streamlit run streamlit_demo.py
```
