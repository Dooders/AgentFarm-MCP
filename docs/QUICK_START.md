# MCP Server - Quick Start Guide

Get your MCP server running in minutes!

## Installation

```bash
cd /workspace/mcp
pip install -e .
```

## Test It Works

```bash
# List available tools
python3 -m mcp --db-path /workspace/simulation.db --list-tools
```

You should see:

```text
Available Tools:
============================================================
get_experiment_info
get_simulation_info
list_experiments
list_simulations
============================================================
Total: 4 tools
```

## Run Test Script

```bash
cd /workspace/mcp
python3 test_server.py
```

You should see:

```text
Testing MCP Server...
============================================================
1. Initializing server...
   ✓ Server initialized with 4 tools
...
============================================================
All tests completed!
```

## Use the Tools Programmatically

```python
from mcp.config import MCPConfig
from mcp.server import SimulationMCPServer

# Initialize server
config = MCPConfig.from_db_path("/workspace/simulation.db")
server = SimulationMCPServer(config)

# List all simulations
list_sims = server.get_tool("list_simulations")
result = list_sims(limit=10)

if result["success"]:
    print(f"Found {result['data']['total_count']} simulations")
    for sim in result['data']['simulations']:
        print(f"  - {sim['simulation_id']}: {sim['status']}")

# Get specific simulation info
get_sim = server.get_tool("get_simulation_info")
result = get_sim(simulation_id="sim_FApjURQ7D6")

if result["success"]:
    print(f"\nSimulation: {result['data']['simulation_id']}")
    print(f"Status: {result['data']['status']}")
    print(f"Cached: {result['metadata']['from_cache']}")

# Check cache stats
stats = server.get_cache_stats()
print(f"\nCache Stats:")
print(f"  Hits: {stats['hits']}, Misses: {stats['misses']}")
print(f"  Hit Rate: {stats['hit_rate']:.1%}")

# Cleanup
server.close()
```

## Configuration Options

### Simple (Just DB Path)

```python
config = MCPConfig.from_db_path("/path/to/db.sqlite")
```

### With Custom Cache Settings

```python
config = MCPConfig.from_db_path(
    "/path/to/db.sqlite",
    cache={"enabled": True, "max_size": 200, "ttl_seconds": 600}
)
```

### From YAML File

```python
config = MCPConfig.from_yaml("config.yaml")
```

### From Environment Variables

```python
# Set environment variables first
config = MCPConfig.from_env()
```

## CLI Options

```bash
# Basic usage
python3 -m mcp --db-path /workspace/simulation.db

# With YAML config
python3 -m mcp --config config.yaml

# Debug logging
python3 -m mcp --db-path /workspace/simulation.db --log-level DEBUG

# Disable cache
python3 -m mcp --db-path /workspace/simulation.db --no-cache

# List tools and exit
python3 -m mcp --db-path /workspace/simulation.db --list-tools
```

## Available Tools

### Metadata Tools

#### 1. get_simulation_info

Get detailed info about a specific simulation.

```python
tool = server.get_tool("get_simulation_info")
result = tool(simulation_id="sim_123")
```

#### 2. list_simulations

List all simulations with optional filters.

```python
tool = server.get_tool("list_simulations")

# All simulations
result = tool(limit=100)

# Filter by status
result = tool(status="completed", limit=50)

# Filter by experiment
result = tool(experiment_id="exp_001", limit=20)
```

#### 3. get_experiment_info

Get detailed info about an experiment.

```python
tool = server.get_tool("get_experiment_info")
result = tool(experiment_id="exp_001")
```

#### 4. list_experiments

List all experiments with optional filters.

```python
tool = server.get_tool("list_experiments")

# All experiments
result = tool(limit=50)

# Filter by status
result = tool(status="completed", limit=20)
```

## Response Format

All tools return the same structure:

```python
{
    "success": True/False,
    "data": {...},  # Tool-specific data
    "metadata": {
        "tool": "tool_name",
        "timestamp": "2025-09-30T...",
        "from_cache": False,
        "execution_time_ms": 2.5
    },
    "error": None  # or {"type": "...", "message": "..."}
}
```

## Error Handling

```python
result = tool(simulation_id="invalid")

if result["success"]:
    data = result["data"]
    # Process data
else:
    error = result["error"]
    print(f"Error: {error['type']}: {error['message']}")
```

## Common Errors

### SimulationNotFoundError

```json
{
  "type": "SimulationNotFoundError",
  "message": "Simulation not found: sim_123"
}
```

### ValidationError

```json
{
  "type": "ValidationError",
  "message": "Invalid parameter: limit must be >= 1"
}
```

### DatabaseError

```json
{
  "type": "DatabaseError",
  "message": "Query execution failed: ..."
}
```

## Cache Behavior

- **First call**: Executes query, caches result
- **Second call (same params)**: Returns cached result
- **Different params**: Executes new query
- **After TTL expires**: Executes query again

Check if result came from cache:

```python
if result["metadata"]["from_cache"]:
    print("This was cached!")
```

## Next Steps

1. **Explore the tools**: Try each tool with different parameters
2. **Check the docs**: Read `IMPLEMENTATION_SUMMARY.md` for details
3. **Extend it**: Add more tools following the pattern in `tools/base.py`
4. **Integrate**: Connect to your LLM client (Claude Desktop, etc.)

## Troubleshooting

### Database not found

```text
DatabaseError: Database file not found: /path/to/db
```

**Fix**: Check the path is correct and file exists

### Import errors

```text
ModuleNotFoundError: No module named 'mcp'
```

**Fix**: Run `pip install -e .` from the `/workspace/mcp` directory

### Slow queries

Check cache stats and enable caching:

```python
config = MCPConfig.from_db_path(db_path, cache={"enabled": True})
```

## Support

- **Documentation**: See `/workspace/mcp/IMPLEMENTATION_SUMMARY.md`
- **Examples**: Check `/workspace/mcp/test_server.py`
- **Code**: Browse `/workspace/mcp/`

Happy querying! 🚀
