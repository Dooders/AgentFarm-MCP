# MCP Server - API Reference

Complete API documentation for all 23 tools.

---

## 📋 Table of Contents

- [Metadata Tools](#metadata-tools) (4)
- [Query Tools](#query-tools) (6)
- [Analysis Tools](#analysis-tools) (7)
- [Comparison Tools](#comparison-tools) (4)
- [Advanced Tools](#advanced-tools) (2)
- [Response Format](#response-format)
- [Error Handling](#error-handling)

---

## Metadata Tools

### 1. `list_simulations`

List all simulations with optional filtering and pagination.

**Parameters:**
- `status` (string, optional): Filter by status ("completed", "running", "failed", "pending")
- `experiment_id` (string, optional): Filter by experiment ID
- `limit` (integer, default=100, range=1-1000): Maximum results to return
- `offset` (integer, default=0, min=0): Pagination offset

**Returns:**
```json
{
  "simulations": [
    {
      "simulation_id": "sim_001",
      "experiment_id": "exp_001",
      "status": "completed",
      "start_time": "2025-09-28T...",
      "end_time": "2025-09-28T...",
      "parameters_summary": {...},
      "db_path": "/path/to/db"
    }
  ],
  "total_count": 150,
  "returned_count": 100,
  "limit": 100,
  "offset": 0
}
```

**Example:**
```python
tool = server.get_tool("list_simulations")
result = tool(status="completed", limit=50)
```

### 2. `get_simulation_info`

Get detailed information about a specific simulation.

**Parameters:**
- `simulation_id` (string, required): Simulation ID to query

**Returns:**
```json
{
  "simulation_id": "sim_001",
  "experiment_id": "exp_001",
  "status": "completed",
  "start_time": "2025-09-28T...",
  "end_time": "2025-09-28T...",
  "parameters": {...},
  "results_summary": {...},
  "db_path": "/path/to/db"
}
```

**Example:**
```python
tool = server.get_tool("get_simulation_info")
result = tool(simulation_id="sim_001")
```

### 3. `list_experiments`

List research experiments with optional filtering.

**Parameters:**
- `status` (string, optional): Filter by status
- `limit` (integer, default=100): Maximum results
- `offset` (integer, default=0): Pagination offset

**Returns:** List of experiments with simulation counts.

### 4. `get_experiment_info`

Get detailed experiment information.

**Parameters:**
- `experiment_id` (string, required): Experiment ID

**Returns:** Experiment metadata, variables, hypothesis, simulation count.

---

## Query Tools

### 5. `query_agents`

Query agents with flexible filtering options.

**Parameters:**
- `simulation_id` (string, required): Simulation to query
- `agent_type` (string, optional): Filter by agent type
- `generation` (integer, optional, min=0): Filter by generation
- `alive_only` (boolean, default=false): Return only living agents
- `limit` (integer, default=100, max=1000): Maximum results
- `offset` (integer, default=0): Pagination offset

**Returns:**
```json
{
  "agents": [
    {
      "agent_id": "agent_001",
      "agent_type": "BaseAgent",
      "generation": 0,
      "birth_time": 0,
      "death_time": 150,
      "position": {"x": 10.5, "y": 20.3},
      "initial_resources": 50.0,
      "starting_health": 100.0,
      "genome_id": "genome_123"
    }
  ],
  "total_count": 177,
  "returned_count": 100
}
```

**Example:**
```python
tool = server.get_tool("query_agents")
result = tool(
    simulation_id="sim_001",
    agent_type="BaseAgent",
    alive_only=True,
    limit=50
)
```

### 6. `query_actions`

Retrieve action logs with filtering.

**Parameters:**
- `simulation_id` (string, required)
- `agent_id` (string, optional): Filter by specific agent
- `action_type` (string, optional): Filter by action type
- `start_step` (integer, optional, min=0): Start of step range
- `end_step` (integer, optional, min=0): End of step range
- `limit`, `offset`: Pagination

**Returns:** Action logs with step, type, target, rewards, resource changes.

### 7. `query_states`

Get agent state data over time.

**Parameters:**
- `simulation_id` (string, required)
- `agent_id` (string, optional): Filter by agent
- `start_step`, `end_step` (optional): Step range
- `limit`, `offset`: Pagination

**Returns:** State history with position, resources, health, age.

### 8. `query_resources`

Fetch resource states from the environment.

**Parameters:**
- `simulation_id` (string, required)
- `step_number` (integer, optional): Specific step
- `start_step`, `end_step` (optional): Step range (if step_number not provided)
- `limit`, `offset`: Pagination

**Returns:** Resource positions and amounts.

### 9. `query_interactions`

Retrieve interaction data between entities.

**Parameters:**
- `simulation_id` (string, required)
- `interaction_type` (string, optional): Filter by type
- `source_id` (string, optional): Filter by source entity
- `target_id` (string, optional): Filter by target entity
- `start_step`, `end_step` (optional): Step range
- `limit`, `offset`: Pagination

**Returns:** Interaction events with source, target, type, details.

### 10. `get_simulation_metrics`

Get comprehensive step-level metrics.

**Parameters:**
- `simulation_id` (string, required)
- `start_step`, `end_step` (optional): Step range
- `limit` (default=1000, max=10000): Higher limit for time-series
- `offset`: Pagination

**Returns:**
```json
{
  "metrics": [
    {
      "step_number": 0,
      "total_agents": 60,
      "births": 0,
      "deaths": 0,
      "total_resources": 500.0,
      "average_agent_health": 100.0,
      "average_reward": 0.0,
      "combat_encounters": 0,
      "genetic_diversity": 0.7,
      ...
    }
  ],
  "total_count": 1001
}
```

---

## Analysis Tools

### 11. `analyze_population_dynamics`

Analyze population trends over time.

**Parameters:**
- `simulation_id` (string, required)
- `start_step`, `end_step` (optional): Analysis range
- `include_chart` (boolean, default=false): Include ASCII chart

**Returns:**
```json
{
  "population_summary": {
    "initial_population": 60,
    "final_population": 102,
    "peak_population": 102,
    "peak_step": 91,
    "average_population": 86.5,
    "total_growth_rate_percent": 70.0,
    "total_births": 102,
    "total_deaths": 0
  },
  "by_type": {
    "system": {"peak": 102, "average": 86.5, "final": 102},
    ...
  },
  "time_series": {...},
  "chart": "ASCII chart if requested"
}
```

### 12. `analyze_survival_rates`

Analyze survival rates by cohort.

**Parameters:**
- `simulation_id` (string, required)
- `group_by` (string, default="generation"): "generation" or "agent_type"

**Returns:** Survival statistics, lifespan data, cohort comparison.

### 13. `analyze_resource_efficiency`

Analyze resource utilization and efficiency.

**Parameters:**
- `simulation_id` (string, required)
- `start_step`, `end_step` (optional): Analysis range

**Returns:** Resource consumption, efficiency metrics, distribution stats.

### 14. `analyze_agent_performance`

Analyze individual agent performance.

**Parameters:**
- `simulation_id` (string, required)
- `agent_id` (string, required): Agent to analyze

**Returns:** Lifespan, status, performance metrics, genome info.

### 15. `identify_critical_events`

Detect significant events in simulation.

**Parameters:**
- `simulation_id` (string, required)
- `threshold_percent` (float, default=10.0, range=0-100): Change threshold

**Returns:**
```json
{
  "events": [
    {
      "type": "population_crash",
      "step": 105,
      "description": "Population dropped 11.8% (102 → 90)",
      "severity": "medium"
    }
  ],
  "summary": {
    "total_events": 22,
    "by_type": {...},
    "by_severity": {...}
  }
}
```

### 16. `analyze_social_patterns`

Analyze social interaction patterns.

**Parameters:**
- `simulation_id` (string, required)
- `limit` (integer, default=1000): Max interactions to analyze

**Returns:** Interaction type distribution, outcomes, resource sharing stats.

### 17. `analyze_reproduction`

Analyze reproduction success rates.

**Parameters:**
- `simulation_id` (string, required)

**Returns:** Success/failure rates, resource costs, failure reasons, generation progression.

---

## Comparison Tools

### 18. `compare_simulations`

Compare metrics across multiple simulations.

**Parameters:**
- `simulation_ids` (list of strings, min=2, max=10): Simulations to compare
- `metrics` (list of strings, optional): Specific metrics to compare

**Returns:**
```json
{
  "simulations": {
    "sim_001": {
      "total_agents": {"mean": 85.5, "std": 10.2, "min": 60, "max": 102},
      ...
    }
  },
  "pairwise_comparisons": {...},
  "rankings": {...}
}
```

### 19. `compare_parameters`

Analyze parameter impact on outcomes.

**Parameters:**
- `parameter_name` (string, required): Parameter to analyze
- `simulation_ids` (list, optional): Specific simulations
- `outcome_metric` (string, default="total_agents"): Metric to measure
- `limit` (integer, default=20): Max simulations

**Returns:** Groups by parameter value, outcome statistics per group.

### 20. `rank_configurations`

Rank simulations by performance.

**Parameters:**
- `metric_name` (string, default="total_agents"): Metric to rank by
- `aggregation` (string, default="mean"): "mean", "final", "max", or "min"
- `limit` (integer, default=20): Max to rank
- `status_filter` (string, optional): Filter by status

**Returns:** Ranked list with scores, configurations, statistics.

### 21. `compare_generations`

Compare performance across generations.

**Parameters:**
- `simulation_id` (string, required)
- `max_generations` (integer, default=10, max=50): Max to compare

**Returns:** Generation statistics, survival rates, lifespan data.

---

## Advanced Tools

### 22. `build_agent_lineage`

Build family tree for an agent.

**Parameters:**
- `simulation_id` (string, required)
- `agent_id` (string, required): Agent to trace
- `depth` (integer, default=3, range=1-10): Generations to trace

**Returns:**
```json
{
  "agent": {...},
  "ancestors": [
    {
      "agent_id": "parent_001",
      "generation": 0,
      "relationship": "parent",
      "reproduction_event": {
        "step": 20,
        "resources_cost": 20.0
      }
    }
  ],
  "descendants": [...]
}
```

### 23. `get_agent_lifecycle`

Get complete agent lifecycle data.

**Parameters:**
- `simulation_id` (string, required)
- `agent_id` (string, required)
- `include_actions` (boolean, default=true): Include action history
- `include_states` (boolean, default=true): Include state history
- `include_health` (boolean, default=true): Include health incidents

**Returns:**
```json
{
  "agent_info": {
    "agent_id": "agent_001",
    "lifespan": 1000,
    "status": "alive",
    ...
  },
  "states": [...],
  "actions": [...],
  "health_incidents": [...],
  "state_count": 1001,
  "action_count": 1000
}
```

---

## Response Format

All tools return a standardized response:

### Success Response

```json
{
  "success": true,
  "data": {
    // Tool-specific data
  },
  "metadata": {
    "tool": "tool_name",
    "timestamp": "2025-09-30T...",
    "from_cache": false,
    "execution_time_ms": 15.42
  },
  "error": null
}
```

### Error Response

```json
{
  "success": false,
  "data": null,
  "metadata": {
    "tool": "tool_name",
    "timestamp": "2025-09-30T..."
  },
  "error": {
    "type": "ValidationError",
    "message": "Detailed error message",
    "details": {...}
  }
}
```

---

## Error Handling

### Error Types

1. **ValidationError** - Invalid parameters
   ```python
   {
     "type": "ValidationError",
     "message": "limit must be >= 1",
     "details": [...]
   }
   ```

2. **DatabaseError** - Database operation failed
   ```python
   {
     "type": "DatabaseError",
     "message": "Query execution failed: ..."
   }
   ```

3. **SimulationNotFoundError** - Simulation doesn't exist
   ```python
   {
     "type": "DatabaseError",  # Wrapped
     "message": "Simulation not found: sim_999"
   }
   ```

4. **QueryTimeoutError** - Query exceeded timeout
   ```python
   {
     "type": "QueryTimeoutError",
     "message": "Query exceeded timeout of 30 seconds"
   }
   ```

### Error Handling Best Practices

```python
tool = server.get_tool("query_agents")
result = tool(simulation_id="sim_001", limit=10)

if result["success"]:
    # Process data
    agents = result["data"]["agents"]
    print(f"Found {len(agents)} agents")
else:
    # Handle error
    error = result["error"]
    print(f"Error ({error['type']}): {error['message']}")
    
    # Check if simulation not found
    if "not found" in error["message"].lower():
        print("Please check the simulation ID")
```

---

## Configuration

### MCPConfig

```python
from mcp import MCPConfig

# From database path (simplest)
config = MCPConfig.from_db_path("/path/to/db.sqlite")

# From YAML file
config = MCPConfig.from_yaml("config.yaml")

# From environment variables
config = MCPConfig.from_env()

# With custom settings
config = MCPConfig.from_db_path(
    "/path/to/db.sqlite",
    cache={"enabled": True, "max_size": 200},
    server={"log_level": "DEBUG"}
)
```

### Configuration Options

**DatabaseConfig:**
- `path` (string): Database file path
- `pool_size` (int, default=5, range=1-20): Connection pool size
- `query_timeout` (int, default=30, range=5-300): Query timeout in seconds
- `read_only` (bool, default=true): Read-only mode

**CacheConfig:**
- `enabled` (bool, default=true): Enable caching
- `max_size` (int, default=100, range=0-1000): Max cache entries
- `ttl_seconds` (int, default=300, min=0): Time to live

**ServerConfig:**
- `max_result_size` (int, default=10000, range=100-100000): Max results
- `default_limit` (int, default=100, range=10-1000): Default pagination
- `log_level` (string, default="INFO"): Logging level

---

## Server Management

### Initialize Server

```python
from mcp import SimulationMCPServer, MCPConfig

config = MCPConfig.from_db_path("/path/to/db.sqlite")
server = SimulationMCPServer(config)
```

### List Available Tools

```python
tools = server.list_tools()
print(f"Available tools: {len(tools)}")
for tool_name in tools:
    print(f"  - {tool_name}")
```

### Get Tool

```python
tool = server.get_tool("analyze_population_dynamics")

# Use the tool
result = tool(simulation_id="sim_001")
```

### Cache Management

```python
# Get cache statistics
stats = server.get_cache_stats()
print(f"Cache size: {stats['size']}/{stats['max_size']}")
print(f"Hit rate: {stats['hit_rate']:.1%}")

# Clear cache
server.clear_cache()
```

### Cleanup

```python
server.close()
```

---

## Common Patterns

### Chaining Tool Calls

```python
# Get a simulation list
list_tool = server.get_tool("list_simulations")
sims = list_tool(limit=1)

# Use the first simulation ID
sim_id = sims['data']['simulations'][0]['simulation_id']

# Get agents from that simulation
agents_tool = server.get_tool("query_agents")
agents = agents_tool(simulation_id=sim_id, limit=10)

# Get first agent ID
agent_id = agents['data']['agents'][0]['agent_id']

# Analyze that specific agent
perf_tool = server.get_tool("analyze_agent_performance")
performance = perf_tool(simulation_id=sim_id, agent_id=agent_id)
```

### Analyzing Time Windows

```python
tool = server.get_tool("analyze_population_dynamics")

# Early game (steps 0-100)
early = tool(simulation_id="sim_001", start_step=0, end_step=100)

# Mid game (steps 100-500)
mid = tool(simulation_id="sim_001", start_step=100, end_step=500)

# Late game (steps 500+)
late = tool(simulation_id="sim_001", start_step=500)

# Compare phases
print(f"Early growth: {early['data']['population_summary']['total_growth_rate_percent']}%")
print(f"Mid growth: {mid['data']['population_summary']['total_growth_rate_percent']}%")
```

### Pagination

```python
tool = server.get_tool("query_agents")

# Get all agents in batches
all_agents = []
offset = 0
limit = 100

while True:
    result = tool(simulation_id="sim_001", limit=limit, offset=offset)
    
    if not result["success"]:
        break
    
    agents = result["data"]["agents"]
    all_agents.extend(agents)
    
    # Check if we got all
    if len(agents) < limit:
        break
    
    offset += limit

print(f"Total agents retrieved: {len(all_agents)}")
```

---

## Performance Tips

### 1. Use Caching

Results are automatically cached. Repeated queries with same parameters are instant.

```python
# First call - executes query (~50ms)
result1 = tool(simulation_id="sim_001", limit=10)
# from_cache: false, execution_time_ms: 45.2

# Second call - from cache (~0ms)
result2 = tool(simulation_id="sim_001", limit=10)
# from_cache: true, execution_time_ms: 0.0
```

### 2. Use Appropriate Limits

```python
# For browsing
tool(simulation_id="sim_001", limit=10)

# For analysis (more data needed)
tool(simulation_id="sim_001", limit=1000)
```

### 3. Use Step Ranges

```python
# Don't query all steps if you only need a range
tool(simulation_id="sim_001", start_step=0, end_step=100)
```

### 4. Filter Early

```python
# More efficient
tool(simulation_id="sim_001", agent_type="BaseAgent", limit=50)

# Less efficient (returns more data)
tool(simulation_id="sim_001", limit=1000)
# Then filter in Python
```

---

## Type Definitions

### Pydantic Models

All parameters are validated via Pydantic. Common types:

```python
# Simulation ID (always required for simulation queries)
simulation_id: str = Field(..., description="Simulation ID to query")

# Pagination
limit: int = Field(100, ge=1, le=1000, description="Max results")
offset: int = Field(0, ge=0, description="Pagination offset")

# Step ranges
start_step: Optional[int] = Field(None, ge=0, description="Start step")
end_step: Optional[int] = Field(None, ge=0, description="End step")

# Filters
agent_type: Optional[str] = Field(None, description="Filter by type")
generation: Optional[int] = Field(None, ge=0, description="Filter by generation")
alive_only: bool = Field(False, description="Only living agents")
```

---

## CLI Reference

### Commands

```bash
# Basic usage
python3 -m mcp --db-path /path/to/db.sqlite

# With YAML config
python3 -m mcp --config config.yaml

# Debug mode
python3 -m mcp --db-path /path/to/db.sqlite --log-level DEBUG

# Disable cache
python3 -m mcp --db-path /path/to/db.sqlite --no-cache

# List tools and exit
python3 -m mcp --db-path /path/to/db.sqlite --list-tools

# With log file
python3 -m mcp --db-path /path/to/db.sqlite --log-file server.log
```

### CLI Options

- `--db-path PATH` - Database file path (required unless using --config)
- `--config FILE` - YAML configuration file
- `--log-level LEVEL` - Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `--log-file FILE` - Log file path (optional, logs to stdout by default)
- `--no-cache` - Disable caching
- `--list-tools` - List available tools and exit

---

## Troubleshooting

### Database Not Found

```
ValueError: Database file not found: /path/to/db.sqlite
```

**Solution:** Check the path is correct and file exists.

### Import Errors

```
ModuleNotFoundError: No module named 'mcp'
```

**Solution:** Install the package:
```bash
cd /workspace/mcp
pip install -e .
```

### Slow Queries

**Check cache is enabled:**
```python
config = MCPConfig.from_db_path(db_path, cache={"enabled": True})
```

**Use appropriate limits:**
```python
# Don't request all data if you only need a sample
tool(simulation_id="sim_001", limit=100)  # Good
tool(simulation_id="sim_001", limit=10000)  # Slow
```

### Memory Issues

**Reduce cache size:**
```python
config = MCPConfig.from_db_path(
    db_path,
    cache={"max_size": 50}  # Smaller cache
)
```

**Use pagination:**
```python
# Get data in chunks
tool(simulation_id="sim_001", limit=100, offset=0)
tool(simulation_id="sim_001", limit=100, offset=100)
```

---

## Examples

See working examples in:
- `test_server.py` - Basic usage
- `demo_all_tools.py` - All 23 tools
- `test_query_tools.py` - Query examples
- `test_analysis_tools.py` - Analysis examples
- `test_comparison_tools.py` - Comparison examples
- `test_advanced_tools.py` - Advanced usage

---

**For complete documentation, see:**
- [QUICK_START.md](QUICK_START.md) - Quick start guide
- [STATUS.md](STATUS.md) - Current capabilities  
- [FINAL_VERIFICATION.md](FINAL_VERIFICATION.md) - Project status

**Version:** 0.1.0  
**Tools:** 23  
**Tests:** 234 (91% coverage)  
**Status:** Production Ready ✅