# AgentFarm-MCP

A **Model Context Protocol (MCP) server** that enables LLM agents to query and analyze agent-based simulation databases through natural language. Built with FastMCP, SQLAlchemy, and comprehensive tooling for simulation analysis.

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/tests-234%20tests-green.svg)](tests/)
[![Coverage](https://img.shields.io/badge/coverage-91%25-brightgreen.svg)](htmlcov/)

## 🚀 Quick Start

```bash
# Install dependencies and setup dev environment
make setup

# Test it works
make test

# Run with development configuration
make run-dev
```

**🎨 Try the Interactive Demo!** See [DEMO_README.md](DEMO_README.md) for a beautiful chat interface to explore the MCP server.

**New to the improved codebase?** See [QUICKSTART_IMPROVEMENTS.md](QUICKSTART_IMPROVEMENTS.md) for the complete guide.

**📚 Recent Improvements:**
- ✅ Type safety with MyPy
- ✅ Pre-commit hooks for code quality
- ✅ Structured logging with context
- ✅ Redis caching for performance
- ✅ Modular model structure
- ✅ Multi-environment support (dev/staging/prod)

See [IMPROVEMENTS.md](IMPROVEMENTS.md) for details.

## 🎨 Interactive Demo

**Streamlit Demo App** - Chat interface with Claude AI to explore the MCP server.

👉 **[Demo Setup & Usage →](DEMO_README.md)**

```bash
pip install -r requirements.txt
pip install -r requirements-streamlit.txt
streamlit run streamlit_demo.py
```

## 📊 What It Does

This MCP server provides **25 specialized tools** for analyzing agent-based simulation data:

- **🔍 Query Tools**: Find agents, actions, states, resources, and interactions
- **📈 Analysis Tools**: Population dynamics, survival rates, resource efficiency
- **🔄 Comparison Tools**: Multi-simulation analysis and parameter impact studies
- **🌳 Advanced Tools**: Agent lineages, complete lifecycles, family trees
- **💚 Health Tools**: Server monitoring and system information

### Example LLM Interactions

> **User**: "What's the population growth rate in the latest simulation?"
> 
> **Claude**: *Uses `list_simulations` → `analyze_population_dynamics` → Reports 70% growth*

> **User**: "Which agents survived the longest and why?"
> 
> **Claude**: *Uses `query_agents` → `analyze_survival_rates` → `analyze_agent_performance` → Explains patterns*

> **User**: "Were there any critical events or population crashes?"
> 
> **Claude**: *Uses `identify_critical_events` → Reports 22 events including population crashes*

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   LLM Client    │◄──►│   MCP Server     │◄──►│  SQLite DB      │
│  (Claude, etc.) │    │  (25 Tools)      │    │ (Simulation)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌──────────────────┐
                       │   Cache Layer    │
                       │  (LRU + TTL)     │
                       └──────────────────┘
```

### Key Components

- **🔧 Configuration System**: Flexible setup via code, YAML, or environment variables
- **🗄️ Database Service**: SQLAlchemy with connection pooling and read-only enforcement
- **⚡ Cache Service**: LRU cache with TTL for performance
- **🛠️ Tool Base Class**: Abstract base with Pydantic validation and error handling
- **📊 25 Analysis Tools**: Comprehensive simulation analysis capabilities

## 📋 All 25 Tools

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
- `analyze_population_dynamics` - Population trends and growth analysis
- `analyze_survival_rates` - Survival statistics by cohort
- `analyze_resource_efficiency` - Resource utilization metrics
- `analyze_agent_performance` - Individual agent analysis
- `identify_critical_events` - Detect significant simulation moments
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
- `health_check` - Comprehensive server health monitoring
- `system_info` - System information and performance metrics

## 🛠️ Installation

### Prerequisites
- Python 3.8+
- SQLite database with simulation data

### Install from Source

```bash
git clone https://github.com/your-org/AgentFarm-MCP.git
cd AgentFarm-MCP
pip install -e .
```

### Dependencies
- `fastmcp>=0.1.0` - MCP server framework
- `sqlalchemy>=2.0.0` - Database ORM
- `pydantic>=2.0.0` - Data validation
- `pandas>=2.0.0` - Data manipulation
- `numpy>=1.24.0` - Numerical operations

## 🚀 Usage

### Command Line

```bash
# Basic usage
python -m agentfarm_mcp --db-path /path/to/simulation.db

# With custom configuration
python -m agentfarm_mcp --config config.yaml

# Debug mode
python -m agentfarm_mcp --db-path simulation.db --log-level DEBUG

# List available tools
python -m agentfarm_mcp --db-path simulation.db --list-tools
```

### Programmatic Usage

```python
from agentfarm_mcp import MCPConfig, SimulationMCPServer

# Initialize server
config = MCPConfig.from_db_path("simulation.db")
server = SimulationMCPServer(config)

# Use tools
tool = server.get_tool("analyze_population_dynamics")
result = tool(simulation_id="sim_001")

if result["success"]:
    print(f"Population growth: {result['data']['population_summary']['total_growth_rate_percent']}%")

server.close()
```

### Claude Desktop Integration

Add to your `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "simulation-analysis": {
      "command": "python",
      "args": [
        "-m", "agentfarm_mcp",
        "--db-path", "/absolute/path/to/simulation.db"
      ]
    }
  }
}
```

## 📊 Performance

- **Query Speed**: <100ms for typical operations
- **Cache Hit Rate**: ~85% for repeated queries
- **Memory Usage**: <200MB for typical workloads
- **Concurrent Queries**: Supports multiple LLM agents
- **Database Size**: Tested with 1M+ records

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=agentfarm_mcp

# Run specific test categories
pytest tests/tools/ -v
pytest tests/services/ -v
```

**Test Coverage**: 91% (234 tests)

## 📚 Documentation

- **[Quick Start Guide](docs/QUICK_START.md)** - Get running in minutes
- **[User Guide](docs/USER_GUIDE.md)** - Comprehensive usage patterns
- **[API Reference](docs/API_REFERENCE.md)** - Complete tool documentation
- **[Tool Catalog](docs/TOOL_CATALOG.md)** - Quick reference for all tools
- **[Troubleshooting](docs/TROUBLESHOOTING.md)** - Common issues and solutions

## 🔒 Security

- **Read-Only**: No database modifications possible
- **Input Validation**: All parameters validated via Pydantic
- **SQL Injection Protection**: Parameterized queries only
- **Error Handling**: Comprehensive error boundaries

## 🎯 Use Cases

### Research & Analysis
- Population dynamics studies
- Evolutionary algorithm analysis
- Resource optimization research
- Behavioral pattern analysis

### Development & Debugging
- Simulation validation
- Performance optimization
- Bug investigation
- Parameter tuning

### Education & Exploration
- Interactive simulation exploration
- Learning agent-based modeling
- Understanding emergent behaviors
- Data visualization support

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run linting
black agentfarm_mcp/
ruff check agentfarm_mcp/

# Run type checking
mypy agentfarm_mcp/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Built with [FastMCP](https://github.com/pydantic/fastmcp) for MCP server functionality
- Uses [SQLAlchemy](https://www.sqlalchemy.org/) for database operations
- Powered by [Pydantic](https://pydantic.dev/) for data validation
- Inspired by the Model Context Protocol specification

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-org/AgentFarm-MCP/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/AgentFarm-MCP/discussions)
- **Documentation**: [Full Documentation](docs/)
