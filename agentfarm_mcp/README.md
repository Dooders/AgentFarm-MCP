# MCP Simulation Analysis Server

> FastMCP server for querying and analyzing agent-based simulation databases with LLM agents.

[![Tests](https://img.shields.io/badge/tests-234%20passing-brightgreen)]()
[![Coverage](https://img.shields.io/badge/coverage-91%25-brightgreen)]()
[![Python](https://img.shields.io/badge/python-3.8%2B-blue)]()
[![License](https://img.shields.io/badge/license-MIT-blue)]()

## 🎯 Overview

A production-ready Model Context Protocol (MCP) server that enables LLM agents (like Claude, GPT-4) to query and analyze simulation databases through natural language. Built with FastMCP, SQLAlchemy, and comprehensive error handling.

### Key Features

- ✅ **23 specialized tools** for simulation analysis
- ✅ **Read-only database access** for safety
- ✅ **Smart caching** (LRU + TTL) for performance
- ✅ **Comprehensive error handling** with detailed messages
- ✅ **Type-safe validation** via Pydantic schemas
- ✅ **High performance** (<100ms queries)
- ✅ **91% test coverage** with 234 unit tests
- ✅ **Flexible configuration** (YAML, ENV, code)

## 🚀 Quick Start

### Installation

```bash
cd /workspace/mcp
pip install -e .
```

### Start the Server

```bash
# List available tools (23 total)
python3 -m mcp --db-path /path/to/simulation.db --list-tools

# Run the server
python3 -m mcp --db-path /path/to/simulation.db

# With debugging
python3 -m mcp --db-path /path/to/simulation.db --log-level DEBUG
```

### Test It Works

```bash
# Run comprehensive demo
cd /workspace/mcp
python3 demo_all_tools.py

# Run unit tests
python3 -m pytest tests/ -v

# Check coverage
python3 -m pytest tests/ --cov=mcp --cov-report=html
```

## 📚 Documentation

### 🚀 Essential Docs (Start Here)
- **[QUICK_START.md](QUICK_START.md)** - Get running in 5 minutes
- **[USER_GUIDE.md](USER_GUIDE.md)** - Practical usage guide
- **[API_REFERENCE.md](API_REFERENCE.md)** - Complete API documentation
- **[TOOL_CATALOG.md](TOOL_CATALOG.md)** - Quick tool reference
- **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Problem solving

### 📊 Status & Verification
- **[STATUS.md](STATUS.md)** - Current capabilities
- **[FINAL_VERIFICATION.md](FINAL_VERIFICATION.md)** - Requirements compliance
- **[FINAL_TEST_REPORT.md](FINAL_TEST_REPORT.md)** - Test results (234 tests, 91% coverage)

### 📖 Complete Index
- **[DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)** - Complete documentation guide

## 🛠️ Available Tools (23)

### Metadata Tools (4)
Query simulation and experiment metadata
- `list_simulations` - List all simulations with filtering
- `get_simulation_info` - Get detailed simulation data
- `list_experiments` - List research experiments
- `get_experiment_info` - Get experiment details

### Query Tools (6)
Flexible data retrieval
- `query_agents` - Query agents with filters (type, generation, alive)
- `query_actions` - Retrieve action logs
- `query_states` - Get agent states over time
- `query_resources` - Fetch resource states
- `query_interactions` - Retrieve interaction data
- `get_simulation_metrics` - Get step-level metrics

### Analysis Tools (7)
Advanced analytics and insights
- `analyze_population_dynamics` - Population trends over time
- `analyze_survival_rates` - Survival analysis by cohort
- `analyze_resource_efficiency` - Resource utilization metrics
- `analyze_agent_performance` - Individual agent analysis
- `identify_critical_events` - Detect significant events
- `analyze_social_patterns` - Social interaction patterns
- `analyze_reproduction` - Reproduction success rates

### Comparison Tools (4)
Multi-simulation analysis
- `compare_simulations` - Compare metrics across simulations
- `compare_parameters` - Parameter impact analysis
- `rank_configurations` - Performance ranking
- `compare_generations` - Evolutionary progression

### Advanced Tools (2)
Specialized analysis
- `build_agent_lineage` - Construct family trees
- `get_agent_lifecycle` - Complete agent history

## 💻 Usage Examples

### Programmatic Usage

```python
from mcp import MCPConfig, SimulationMCPServer

# Initialize server
config = MCPConfig.from_db_path("/path/to/simulation.db")
server = SimulationMCPServer(config)

# List all simulations
list_sims = server.get_tool("list_simulations")
result = list_sims(limit=10)

if result["success"]:
    print(f"Found {result['data']['total_count']} simulations")

# Analyze population dynamics
analyze_pop = server.get_tool("analyze_population_dynamics")
result = analyze_pop(
    simulation_id="sim_001",
    start_step=0,
    end_step=100,
    include_chart=True
)

if result["success"]:
    summary = result['data']['population_summary']
    print(f"Growth rate: {summary['total_growth_rate_percent']}%")
    print(result['data']['chart'])  # ASCII visualization

# Get complete agent lifecycle
lifecycle = server.get_tool("get_agent_lifecycle")
result = lifecycle(
    simulation_id="sim_001",
    agent_id="agent_123",
    include_actions=True,
    include_states=True
)

if result["success"]:
    print(f"Agent lived {result['data']['agent_info']['lifespan']} steps")
    print(f"Took {result['data']['action_count']} actions")

# Cleanup
server.close()
```

### LLM Integration (Claude Desktop)

Add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "simulation-analysis": {
      "command": "python3",
      "args": [
        "-m",
        "mcp",
        "--db-path",
        "/absolute/path/to/simulation.db"
      ]
    }
  }
}
```

Then ask Claude:
- "What's the population growth rate in simulation sim_001?"
- "Show me the survival rates across generations"
- "Which agents lived the longest?"
- "Build a family tree for agent_123"
- "Identify critical events in the simulation"

## ⚙️ Configuration

### Simple (Database Path Only)

```python
config = MCPConfig.from_db_path("/path/to/simulation.db")
```

### YAML Configuration

Create `config.yaml`:

```yaml
database:
  path: "/path/to/simulation.db"
  pool_size: 5
  query_timeout: 30
  read_only: true

cache:
  enabled: true
  max_size: 100
  ttl_seconds: 300

server:
  max_result_size: 10000
  default_limit: 100
  log_level: "INFO"
```

Then load:

```python
config = MCPConfig.from_yaml("config.yaml")
```

### Environment Variables

```bash
export DB_PATH="/path/to/simulation.db"
export CACHE_ENABLED=true
export LOG_LEVEL=DEBUG
```

```python
config = MCPConfig.from_env()
```

## 🧪 Testing

### Run Tests

```bash
# All tests
python3 -m pytest tests/ -v

# With coverage
python3 -m pytest tests/ --cov=mcp --cov-report=html

# Specific category
python3 -m pytest tests/tools/ -v
python3 -m pytest tests/services/ -v
```

**Results:** 234 tests, 100% passing, 91% coverage ✅

### Run Demos

```bash
# Complete demo of all 23 tools
python3 demo_all_tools.py

# Test specific categories
python3 test_query_tools.py
python3 test_analysis_tools.py
python3 test_comparison_tools.py
```

## 📊 Performance

- **Query Speed:** <100ms (20x better than <2s target)
- **Metadata Queries:** 1-10ms
- **Data Queries:** 2-70ms
- **Analysis Tools:** 7-55ms
- **Comparison Tools:** 10-91ms

Tested with:
- 177 agents
- 41,147 actions
- 1,001 simulation steps
- Real database queries

## 🔒 Security

- ✅ **Read-only database access** (application-level enforcement)
- ✅ **SQL injection prevention** (parameterized queries via SQLAlchemy ORM)
- ✅ **Input validation** (21 Pydantic schemas)
- ✅ **Query timeouts** (30s default, configurable)
- ✅ **Result size limits** (10,000 max)
- ✅ **Connection pooling** (controlled resource usage)

## 🏗️ Architecture

```
LLM Agent (Claude/GPT)
        ↓
    MCP Protocol
        ↓
FastMCP Server (23 tools)
        ↓
    Services Layer
    ├── DatabaseService (SQLAlchemy + pooling)
    └── CacheService (LRU + TTL)
        ↓
   SQLite Database
```

## 🤝 Contributing

### Adding New Tools

1. Create tool class extending `ToolBase`:

```python
from mcp.tools.base import ToolBase
from pydantic import BaseModel, Field

class MyToolParams(BaseModel):
    simulation_id: str = Field(..., description="Simulation to query")
    # ... more parameters

class MyTool(ToolBase):
    @property
    def name(self):
        return "my_tool"
    
    @property
    def description(self):
        return "Description for LLM"
    
    @property
    def parameters_schema(self):
        return MyToolParams
    
    def execute(self, **params):
        # Your logic here
        return {"result": "data"}
```

2. Register in `server.py`:

```python
from mcp.tools.my_tools import MyTool

# In _register_tools():
tool_classes = [
    # ... existing tools
    MyTool,
]
```

3. Add tests in `tests/tools/test_my_tools.py`

## 📞 Support

- **Issues:** Check STATUS.md for known issues
- **Examples:** See test files for usage patterns
- **Documentation:** Start with QUICK_START.md
- **API Reference:** See docstrings in code

## 📄 License

MIT License - See LICENSE file for details

## 🎓 Credits

Built with:
- [FastMCP](https://github.com/jlowin/fastmcp) - MCP server framework
- [SQLAlchemy](https://www.sqlalchemy.org/) - Database ORM
- [Pydantic](https://pydantic-docs.helpmanual.io/) - Data validation
- [NumPy](https://numpy.org/) - Numerical analysis
- [Pandas](https://pandas.pydata.org/) - Data manipulation

---

**Version:** 0.1.0  
**Status:** Production Ready ✅  
**Tests:** 234 passing ✅  
**Coverage:** 91% ✅  
**Tools:** 23 ✅