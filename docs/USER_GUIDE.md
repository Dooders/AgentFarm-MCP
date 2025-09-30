# MCP Server - User Guide

A practical guide to using the MCP Simulation Analysis Server.

---

## 🎯 Table of Contents

1. [Getting Started](#getting-started)
2. [Basic Usage](#basic-usage)
3. [Common Workflows](#common-workflows)
4. [Advanced Usage](#advanced-usage)
5. [Best Practices](#best-practices)
6. [LLM Integration](#llm-integration)

---

## Getting Started

### Installation

```bash
cd /workspace/mcp
pip install -e .
```

### Verify Installation

```bash
# Should show 23 tools
python3 -m mcp --db-path /workspace/simulation.db --list-tools
```

### First Steps

```bash
# Run a demo
python3 demo_all_tools.py

# Or start Python and try programmatically
python3
```

```python
from mcp import MCPConfig, SimulationMCPServer

config = MCPConfig.from_db_path("/workspace/simulation.db")
server = SimulationMCPServer(config)

# List tools
print(f"Available tools: {len(server.list_tools())}")

# Try a simple tool
tool = server.get_tool("list_simulations")
result = tool(limit=5)

if result["success"]:
    print(f"Found {result['data']['total_count']} simulations")

server.close()
```

---

## Basic Usage

### 1. List Available Simulations

```python
from mcp import MCPConfig, SimulationMCPServer

config = MCPConfig.from_db_path("/workspace/simulation.db")
server = SimulationMCPServer(config)

# Get all simulations
list_tool = server.get_tool("list_simulations")
result = list_tool(limit=100)

if result["success"]:
    for sim in result["data"]["simulations"]:
        print(f"{sim['simulation_id']}: {sim['status']}")
        print(f"  Started: {sim['start_time']}")
        print(f"  Parameters: {sim['parameters_summary']}")

server.close()
```

### 2. Get Detailed Simulation Information

```python
# Get specific simulation
info_tool = server.get_tool("get_simulation_info")
result = info_tool(simulation_id="sim_001")

if result["success"]:
    data = result["data"]
    print(f"Simulation: {data['simulation_id']}")
    print(f"Status: {data['status']}")
    print(f"Parameters: {len(data['parameters'])} total")
    
    # Show sample parameters
    for key, value in list(data['parameters'].items())[:5]:
        print(f"  {key}: {value}")
```

### 3. Query Agents

```python
# Get all agents
agents_tool = server.get_tool("query_agents")
result = agents_tool(simulation_id="sim_001", limit=50)

if result["success"]:
    print(f"Total agents: {result['data']['total_count']}")
    
    for agent in result["data"]["agents"][:5]:
        status = "alive" if agent['death_time'] is None else "dead"
        print(f"{agent['agent_id']}: Gen {agent['generation']}, {status}")

# Filter for specific agent type
result = agents_tool(
    simulation_id="sim_001",
    agent_type="BaseAgent",
    alive_only=True,
    limit=20
)
```

### 4. Analyze Population

```python
# Get population dynamics
pop_tool = server.get_tool("analyze_population_dynamics")
result = pop_tool(
    simulation_id="sim_001",
    start_step=0,
    end_step=100,
    include_chart=True
)

if result["success"]:
    summary = result["data"]["population_summary"]
    print(f"Initial: {summary['initial_population']}")
    print(f"Final: {summary['final_population']}")
    print(f"Peak: {summary['peak_population']} at step {summary['peak_step']}")
    print(f"Growth: {summary['total_growth_rate_percent']}%")
    print(f"Births: {summary['total_births']}")
    print(f"Deaths: {summary['total_deaths']}")
    
    # Show chart
    if 'chart' in result["data"]:
        print(result["data"]["chart"])
```

---

## Common Workflows

### Workflow 1: Investigate Population Crash

```python
# Step 1: Get simulation metrics to see the crash
metrics_tool = server.get_tool("get_simulation_metrics")
metrics = metrics_tool(simulation_id="sim_001", limit=1000)

# Step 2: Identify critical events
events_tool = server.get_tool("identify_critical_events")
events = events_tool(simulation_id="sim_001", threshold_percent=10.0)

# Step 3: Find when population crashed
for event in events["data"]["events"]:
    if event["type"] == "population_crash":
        print(f"Crash at step {event['step']}: {event['description']}")

# Step 4: Query agents that died during crash
crash_step = events["data"]["events"][0]["step"]
agents_tool = server.get_tool("query_agents")
agents = agents_tool(simulation_id="sim_001", limit=100)

died_during_crash = [
    a for a in agents["data"]["agents"]
    if a["death_time"] and crash_step - 5 <= a["death_time"] <= crash_step + 5
]

print(f"Agents that died during crash: {len(died_during_crash)}")
```

### Workflow 2: Compare Best and Worst Agents

```python
# Step 1: Rank agents by survival time
agents_tool = server.get_tool("query_agents")
all_agents = agents_tool(simulation_id="sim_001", limit=1000)

# Step 2: Sort by lifespan
dead_agents = [
    a for a in all_agents["data"]["agents"]
    if a["death_time"] is not None
]

sorted_agents = sorted(
    dead_agents,
    key=lambda a: a["death_time"] - a["birth_time"],
    reverse=True
)

# Step 3: Analyze best and worst
perf_tool = server.get_tool("analyze_agent_performance")

print("Best agent:")
best = sorted_agents[0]
result = perf_tool(simulation_id="sim_001", agent_id=best["agent_id"])
print(f"  Lived: {result['data']['lifespan']} steps")

print("Worst agent:")
worst = sorted_agents[-1]
result = perf_tool(simulation_id="sim_001", agent_id=worst["agent_id"])
print(f"  Lived: {result['data']['lifespan']} steps")
```

### Workflow 3: Analyze Resource Efficiency Over Time

```python
# Step 1: Get resource metrics
resource_tool = server.get_tool("analyze_resource_efficiency")

# Early game
early = resource_tool(simulation_id="sim_001", start_step=0, end_step=100)

# Mid game
mid = resource_tool(simulation_id="sim_001", start_step=100, end_step=500)

# Late game
late = resource_tool(simulation_id="sim_001", start_step=500)

# Step 2: Compare efficiency
print("Resource Efficiency Trends:")
print(f"Early: {early['data']['efficiency_metrics']['average_efficiency']:.4f}")
print(f"Mid: {mid['data']['efficiency_metrics']['average_efficiency']:.4f}")
print(f"Late: {late['data']['efficiency_metrics']['average_efficiency']:.4f}")
```

### Workflow 4: Track Agent Lineage

```python
# Step 1: Find an interesting agent
agents_tool = server.get_tool("query_agents")
agents = agents_tool(simulation_id="sim_001", generation=2, limit=10)

agent_id = agents["data"]["agents"][0]["agent_id"]

# Step 2: Build family tree
lineage_tool = server.get_tool("build_agent_lineage")
lineage = lineage_tool(
    simulation_id="sim_001",
    agent_id=agent_id,
    depth=3
)

# Step 3: Print family tree
print(f"Agent: {lineage['data']['agent']['agent_id']}")
print(f"Generation: {lineage['data']['agent']['generation']}")

if lineage["data"]["ancestors"]:
    print("\nAncestors:")
    for ancestor in lineage["data"]["ancestors"]:
        print(f"  {ancestor['agent_id']} (Gen {ancestor['generation']})")

if lineage["data"]["descendants"]:
    print("\nDescendants:")
    for descendant in lineage["data"]["descendants"]:
        print(f"  {descendant['agent_id']} (Gen {descendant['generation']})")

# Step 4: Get complete lifecycle
lifecycle_tool = server.get_tool("get_agent_lifecycle")
lifecycle = lifecycle_tool(
    simulation_id="sim_001",
    agent_id=agent_id
)

print(f"\nLifecycle:")
print(f"  States: {lifecycle['data']['state_count']}")
print(f"  Actions: {lifecycle['data']['action_count']}")
print(f"  Lifespan: {lifecycle['data']['agent_info']['lifespan']} steps")
```

---

## Advanced Usage

### Custom Configuration

```python
from mcp import MCPConfig
from mcp.config import DatabaseConfig, CacheConfig, ServerConfig

# Fine-grained control
config = MCPConfig(
    database=DatabaseConfig(
        path="/path/to/db.sqlite",
        pool_size=10,
        query_timeout=60,
        read_only=True
    ),
    cache=CacheConfig(
        enabled=True,
        max_size=200,
        ttl_seconds=600
    ),
    server=ServerConfig(
        max_result_size=20000,
        default_limit=200,
        log_level="DEBUG"
    )
)

server = SimulationMCPServer(config)
```

### Batch Processing

```python
# Process all simulations
list_tool = server.get_tool("list_simulations")
all_sims = list_tool(limit=1000)

analyze_tool = server.get_tool("analyze_population_dynamics")

results = {}
for sim in all_sims["data"]["simulations"]:
    sim_id = sim["simulation_id"]
    result = analyze_tool(simulation_id=sim_id)
    
    if result["success"]:
        results[sim_id] = result["data"]["population_summary"]

# Find simulation with highest growth
best_sim = max(
    results.items(),
    key=lambda x: x[1]["total_growth_rate_percent"]
)

print(f"Best growth: {best_sim[0]} with {best_sim[1]['total_growth_rate_percent']}%")
```

### Export Data

```python
import json

# Query data
tool = server.get_tool("get_simulation_metrics")
result = tool(simulation_id="sim_001", limit=1000)

if result["success"]:
    # Save to JSON file
    with open("simulation_metrics.json", "w") as f:
        json.dump(result["data"], f, indent=2)
    
    print("Data exported to simulation_metrics.json")
```

---

## Best Practices

### 1. Always Use Error Handling

```python
def safe_query(tool, **params):
    """Safely execute a tool query."""
    result = tool(**params)
    
    if result["success"]:
        return result["data"]
    else:
        error = result["error"]
        raise Exception(f"{error['type']}: {error['message']}")

# Usage
try:
    data = safe_query(tool, simulation_id="sim_001", limit=10)
except Exception as e:
    print(f"Query failed: {e}")
```

### 2. Use Pagination for Large Datasets

```python
def get_all_agents(server, simulation_id, batch_size=100):
    """Get all agents using pagination."""
    tool = server.get_tool("query_agents")
    all_agents = []
    offset = 0
    
    while True:
        result = tool(
            simulation_id=simulation_id,
            limit=batch_size,
            offset=offset
        )
        
        if not result["success"]:
            break
        
        agents = result["data"]["agents"]
        all_agents.extend(agents)
        
        if len(agents) < batch_size:
            break
        
        offset += batch_size
    
    return all_agents
```

### 3. Monitor Performance

```python
import time

start = time.time()
result = tool(simulation_id="sim_001", limit=100)
elapsed = time.time() - start

print(f"Query took: {elapsed*1000:.2f}ms")
print(f"Server reported: {result['metadata']['execution_time_ms']:.2f}ms")
print(f"From cache: {result['metadata']['from_cache']}")
```

### 4. Cache Management

```python
# Check cache status
stats = server.get_cache_stats()
print(f"Cache: {stats['size']}/{stats['max_size']} entries")
print(f"Hit rate: {stats['hit_rate']:.1%}")

# Clear cache if needed
if stats['size'] > stats['max_size'] * 0.9:
    print("Cache nearly full, clearing...")
    server.clear_cache()
```

---

## LLM Integration

### Claude Desktop Setup

1. **Find Claude config file:**
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - Linux: `~/.config/Claude/claude_desktop_config.json`

2. **Add MCP server configuration:**

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

3. **Restart Claude Desktop**

4. **Test it works:**
   - Ask Claude: "What tools are available?"
   - Should see all 23 simulation analysis tools

### Example Claude Conversations

**Analyzing Population:**
> "What's the population growth rate in the simulation?"

Claude will:
1. List simulations to find available IDs
2. Call `analyze_population_dynamics`
3. Report the growth rate and key statistics

**Comparing Agents:**
> "Which agents survived the longest and why?"

Claude will:
1. Query all agents
2. Analyze survival rates
3. Compare agent performance
4. Report findings

**Identifying Problems:**
> "Were there any critical events in the simulation?"

Claude will:
1. Call `identify_critical_events`
2. Analyze population crashes or booms
3. Explain what happened

**Building Family Trees:**
> "Show me the family tree for agent_123"

Claude will:
1. Call `build_agent_lineage`
2. Present ancestors and descendants
3. Show reproduction events

---

## Common Patterns

### Pattern 1: Find Simulations, Then Analyze

```python
# Find interesting simulations
list_tool = server.get_tool("list_simulations")
sims = list_tool(status="completed", limit=10)

# Analyze each
analyze_tool = server.get_tool("analyze_population_dynamics")

for sim in sims["data"]["simulations"]:
    result = analyze_tool(simulation_id=sim["simulation_id"])
    
    if result["success"]:
        summary = result["data"]["population_summary"]
        print(f"{sim['simulation_id']}: {summary['total_growth_rate_percent']}% growth")
```

### Pattern 2: Deep Dive into Single Agent

```python
sim_id = "sim_001"
agent_id = "agent_123"

# 1. Basic info
perf_tool = server.get_tool("analyze_agent_performance")
perf = perf_tool(simulation_id=sim_id, agent_id=agent_id)

# 2. Complete lifecycle
lifecycle_tool = server.get_tool("get_agent_lifecycle")
lifecycle = lifecycle_tool(
    simulation_id=sim_id,
    agent_id=agent_id,
    include_actions=True,
    include_states=True,
    include_health=True
)

# 3. Family tree
lineage_tool = server.get_tool("build_agent_lineage")
lineage = lineage_tool(simulation_id=sim_id, agent_id=agent_id, depth=2)

# 4. Compile report
print(f"Agent Analysis: {agent_id}")
print(f"  Lifespan: {lifecycle['data']['agent_info']['lifespan']}")
print(f"  Actions: {lifecycle['data']['action_count']}")
print(f"  Ancestors: {len(lineage['data']['ancestors'])}")
print(f"  Descendants: {len(lineage['data']['descendants'])}")
```

### Pattern 3: Time-Series Analysis

```python
# Get metrics for entire simulation
metrics_tool = server.get_tool("get_simulation_metrics")
metrics = metrics_tool(simulation_id="sim_001", limit=1000)

# Extract time series
if metrics["success"]:
    steps = []
    populations = []
    resources = []
    
    for metric in metrics["data"]["metrics"]:
        steps.append(metric["step_number"])
        populations.append(metric["total_agents"])
        resources.append(metric["total_resources"])
    
    # Plot or analyze
    print(f"Analyzed {len(steps)} steps")
    print(f"Population range: {min(populations)} - {max(populations)}")
    print(f"Resource range: {min(resources)} - {max(resources)}")
```

### Pattern 4: Comparative Experiment Analysis

```python
# Find experiments
exp_tool = server.get_tool("list_experiments")
experiments = exp_tool(limit=10)

for exp in experiments["data"]["experiments"]:
    exp_id = exp["experiment_id"]
    
    # Get simulations for this experiment
    sims_tool = server.get_tool("list_simulations")
    sims = sims_tool(experiment_id=exp_id, limit=100)
    
    if sims["data"]["total_count"] >= 2:
        sim_ids = [s["simulation_id"] for s in sims["data"]["simulations"]]
        
        # Compare them
        compare_tool = server.get_tool("compare_simulations")
        comparison = compare_tool(simulation_ids=sim_ids[:5])  # Max 5
        
        if comparison["success"]:
            print(f"Experiment: {exp['name']}")
            print(f"  Simulations compared: {comparison['data']['simulation_count']}")
```

---

## Tips & Tricks

### Tip 1: Check Cache Effectiveness

```python
# Before
stats_before = server.get_cache_stats()

# Run some queries
tool(simulation_id="sim_001", limit=10)
tool(simulation_id="sim_001", limit=10)  # Same query

# After
stats_after = server.get_cache_stats()

print(f"Cache hits: {stats_after['hits'] - stats_before['hits']}")
print(f"Hit rate improved: {stats_after['hit_rate'] - stats_before['hit_rate']:.1%}")
```

### Tip 2: Use Step Ranges Effectively

```python
# Don't query all steps if you only need recent data
metrics_tool = server.get_tool("get_simulation_metrics")

# Get total step count first
all_metrics = metrics_tool(simulation_id="sim_001", limit=1)
total_steps = all_metrics["data"]["total_count"]

# Query last 100 steps
recent = metrics_tool(
    simulation_id="sim_001",
    start_step=max(0, total_steps - 100),
    end_step=total_steps
)
```

### Tip 3: Combine Query and Analysis Tools

```python
# Query provides raw data
query_tool = server.get_tool("query_agents")
agents = query_tool(simulation_id="sim_001", limit=100)

# Analysis provides insights
analyze_tool = server.get_tool("analyze_survival_rates")
survival = analyze_tool(simulation_id="sim_001", group_by="generation")

# Combine results
print(f"Total agents: {agents['data']['total_count']}")
print(f"Overall survival: {survival['data']['summary']['overall_survival_rate']}%")
```

---

## Real-World Examples

### Example 1: Daily Simulation Review

```python
"""Daily script to review simulation progress."""

def daily_review(server, simulation_id):
    # Get basic info
    info = server.get_tool("get_simulation_info")(simulation_id=simulation_id)
    print(f"Simulation: {info['data']['simulation_id']}")
    print(f"Status: {info['data']['status']}")
    
    # Population trend
    pop = server.get_tool("analyze_population_dynamics")(simulation_id=simulation_id)
    print(f"Population: {pop['data']['population_summary']['final_population']}")
    print(f"Growth: {pop['data']['population_summary']['total_growth_rate_percent']}%")
    
    # Critical events
    events = server.get_tool("identify_critical_events")(
        simulation_id=simulation_id,
        threshold_percent=10.0
    )
    print(f"Critical events: {events['data']['summary']['total_events']}")
    
    # Resource status
    resources = server.get_tool("analyze_resource_efficiency")(simulation_id=simulation_id)
    print(f"Resources consumed: {resources['data']['resource_summary']['total_consumed']}")

# Use it
daily_review(server, "sim_001")
```

### Example 2: Export Report to CSV

```python
"""Export simulation analysis to CSV."""

import csv

def export_population_report(server, simulation_id, output_file):
    tool = server.get_tool("get_simulation_metrics")
    result = tool(simulation_id=simulation_id, limit=10000)
    
    if result["success"]:
        with open(output_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=[
                "step_number", "total_agents", "births", "deaths",
                "average_health", "total_resources"
            ])
            writer.writeheader()
            
            for metric in result["data"]["metrics"]:
                writer.writerow({
                    "step_number": metric["step_number"],
                    "total_agents": metric["total_agents"],
                    "births": metric["births"],
                    "deaths": metric["deaths"],
                    "average_health": metric["average_agent_health"],
                    "total_resources": metric["total_resources"]
                })
        
        print(f"Exported to {output_file}")

# Use it
export_population_report(server, "sim_001", "population_report.csv")
```

---

## 📚 Next Steps

1. **Read API_REFERENCE.md** - Detailed API documentation
2. **Try demo scripts** - See working examples
3. **Check TROUBLESHOOTING.md** - If you encounter issues
4. **Explore test files** - More usage patterns in `tests/` directory

---

**Happy analyzing!** 🚀

For more information:
- API Reference: [API_REFERENCE.md](API_REFERENCE.md)
- Troubleshooting: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Quick Start: [QUICK_START.md](QUICK_START.md)