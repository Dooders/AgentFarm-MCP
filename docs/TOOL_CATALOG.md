# Tool Catalog - All 23 Tools

Quick reference for all available tools with parameters and use cases.

---

## 📋 Quick Index

| # | Tool Name | Category | Use For |
|---|-----------|----------|---------|
| 1 | list_simulations | Metadata | Browse simulations |
| 2 | get_simulation_info | Metadata | Get simulation details |
| 3 | list_experiments | Metadata | Browse experiments |
| 4 | get_experiment_info | Metadata | Get experiment details |
| 5 | query_agents | Query | Find agents |
| 6 | query_actions | Query | Get action logs |
| 7 | query_states | Query | Track agent states |
| 8 | query_resources | Query | Monitor resources |
| 9 | query_interactions | Query | Study interactions |
| 10 | get_simulation_metrics | Query | Get step metrics |
| 11 | analyze_population_dynamics | Analysis | Population trends |
| 12 | analyze_survival_rates | Analysis | Survival analysis |
| 13 | analyze_resource_efficiency | Analysis | Resource usage |
| 14 | analyze_agent_performance | Analysis | Individual agents |
| 15 | identify_critical_events | Analysis | Find key moments |
| 16 | analyze_social_patterns | Analysis | Social behavior |
| 17 | analyze_reproduction | Analysis | Reproduction success |
| 18 | compare_simulations | Comparison | Multi-sim comparison |
| 19 | compare_parameters | Comparison | Parameter impact |
| 20 | rank_configurations | Comparison | Performance ranking |
| 21 | compare_generations | Comparison | Evolution tracking |
| 22 | build_agent_lineage | Advanced | Family trees |
| 23 | get_agent_lifecycle | Advanced | Complete history |

---

## 📊 Tools by Use Case

### "I want to explore what simulations I have"
→ Use `list_simulations` (filter by status, experiment)
→ Use `get_simulation_info` (get details)
→ Use `list_experiments` (if using experiments)

### "I want to understand population dynamics"
→ Use `analyze_population_dynamics` (trends, charts)
→ Use `get_simulation_metrics` (raw step data)
→ Use `identify_critical_events` (find crashes/booms)

### "I want to study specific agents"
→ Use `query_agents` (find agents)
→ Use `analyze_agent_performance` (individual analysis)
→ Use `get_agent_lifecycle` (complete history)
→ Use `build_agent_lineage` (family tree)

### "I want to compare simulations"
→ Use `compare_simulations` (metric comparison)
→ Use `rank_configurations` (find best)
→ Use `compare_parameters` (parameter impact)

### "I want to track resources"
→ Use `query_resources` (resource states)
→ Use `analyze_resource_efficiency` (efficiency metrics)
→ Use `get_simulation_metrics` (resource per step)

### "I want to understand agent behavior"
→ Use `query_actions` (action logs)
→ Use `query_states` (state changes)
→ Use `analyze_social_patterns` (social behavior)
→ Use `query_interactions` (interactions)

### "I want to study evolution"
→ Use `analyze_survival_rates` (by generation)
→ Use `compare_generations` (generation comparison)
→ Use `analyze_reproduction` (reproduction success)
→ Use `build_agent_lineage` (genetic lineages)

---

## 🎯 Tool Details

### Metadata Tools (4)

#### list_simulations
**Purpose:** Browse available simulations  
**Key Parameters:** status, experiment_id, limit, offset  
**Returns:** List of simulations with metadata  
**Performance:** ~10ms  
**Cache:** Yes  

**When to use:**
- Starting point for analysis
- Finding simulations to study
- Checking simulation status
- Browsing by experiment

**Example:**
```python
tool(status="completed", limit=20)
```

#### get_simulation_info
**Purpose:** Get detailed simulation information  
**Key Parameters:** simulation_id  
**Returns:** Full metadata, parameters, results  
**Performance:** ~2ms  
**Cache:** Yes  

**When to use:**
- Need complete simulation details
- Checking configuration parameters
- Getting start/end times
- Understanding simulation setup

#### list_experiments
**Purpose:** Browse research experiments  
**Key Parameters:** status, limit, offset  
**Returns:** Experiments with simulation counts  
**Performance:** ~10ms  
**Cache:** Yes  

#### get_experiment_info
**Purpose:** Get experiment details  
**Key Parameters:** experiment_id  
**Returns:** Hypothesis, variables, results  
**Performance:** ~5ms  
**Cache:** Yes  

---

### Query Tools (6)

#### query_agents
**Purpose:** Find and filter agents  
**Key Parameters:** simulation_id, agent_type, generation, alive_only, limit  
**Returns:** Agent list with attributes  
**Performance:** ~7ms for 10 records  
**Cache:** Yes  

**When to use:**
- Finding specific agents
- Filtering by type or generation
- Getting agent population snapshot
- Finding alive/dead agents

**Tested with:** 177 agents

#### query_actions
**Purpose:** Get action logs  
**Key Parameters:** simulation_id, agent_id, action_type, start_step, end_step  
**Returns:** Action history with rewards  
**Performance:** ~22ms for 10 records  
**Cache:** Yes  

**When to use:**
- Studying agent behavior
- Analyzing action patterns
- Tracking rewards
- Debugging agent decisions

**Tested with:** 41,147 actions

#### query_states
**Purpose:** Track agent states over time  
**Key Parameters:** simulation_id, agent_id, start_step, end_step  
**Returns:** Position, health, resources per step  
**Performance:** ~20ms for 10 records  
**Cache:** Yes  

**When to use:**
- Tracking agent movement
- Monitoring health changes
- Analyzing resource accumulation
- Studying agent progression

**Tested with:** 41,296 state records

#### query_resources
**Purpose:** Monitor environmental resources  
**Key Parameters:** simulation_id, step_number, start_step, end_step  
**Returns:** Resource positions and amounts  
**Performance:** ~12ms for 10 records  
**Cache:** Yes  

**When to use:**
- Tracking resource distribution
- Finding resource hotspots
- Monitoring resource depletion
- Spatial resource analysis

**Tested with:** 20,040 resource records

#### query_interactions
**Purpose:** Study entity interactions  
**Key Parameters:** simulation_id, interaction_type, source_id, target_id  
**Returns:** Interaction events with details  
**Performance:** ~15ms for 10 records  
**Cache:** Yes  

**When to use:**
- Analyzing agent-agent interactions
- Studying resource gathering
- Tracking combat events
- Understanding social dynamics

**Tested with:** 17,231 interactions

#### get_simulation_metrics
**Purpose:** Get comprehensive step-level data  
**Key Parameters:** simulation_id, start_step, end_step, limit (up to 10K)  
**Returns:** All metrics per step  
**Performance:** ~19ms for 20 records  
**Cache:** Yes  

**When to use:**
- Time-series analysis
- Plotting population/resources
- Detailed simulation progression
- Metric correlation studies

**Tested with:** 1,001 steps

---

### Analysis Tools (7)

#### analyze_population_dynamics
**Purpose:** Analyze population trends  
**Key Parameters:** simulation_id, start_step, end_step, include_chart  
**Returns:** Population summary, time-series, optional chart  
**Performance:** ~7-23ms  
**Cache:** Yes  

**Insights provided:**
- Growth rate (detected 70% in test)
- Peak population and when it occurred
- Birth/death totals
- Breakdown by agent type
- ASCII chart visualization

**When to use:**
- Understanding population health
- Detecting growth patterns
- Comparing agent types
- Visualizing trends

#### analyze_survival_rates
**Purpose:** Calculate survival statistics  
**Key Parameters:** simulation_id, group_by ("generation" or "agent_type")  
**Returns:** Survival rates, lifespan stats per cohort  
**Performance:** ~20ms  
**Cache:** Yes  

**Insights provided:**
- Survival rate (18% in test)
- Average lifespan per cohort
- Alive vs dead counts
- Best/worst cohorts

**When to use:**
- Comparing generations
- Evaluating agent types
- Understanding mortality
- Fitness analysis

#### analyze_resource_efficiency
**Purpose:** Measure resource utilization  
**Key Parameters:** simulation_id, start_step, end_step  
**Returns:** Resource consumption, efficiency metrics  
**Performance:** ~4-13ms  
**Cache:** Yes  

**Insights provided:**
- Total consumed (606 units in test)
- Efficiency trends
- Per-agent resources
- Distribution entropy

**When to use:**
- Resource optimization
- Finding bottlenecks
- Efficiency improvements
- Sustainability analysis

#### analyze_agent_performance
**Purpose:** Evaluate individual agents  
**Key Parameters:** simulation_id, agent_id  
**Returns:** Lifespan, status, performance metrics  
**Performance:** ~14ms  
**Cache:** Yes  

**When to use:**
- Agent deep-dive
- Debugging agent behavior
- Identifying successful strategies
- Case studies

#### identify_critical_events
**Purpose:** Detect significant moments  
**Key Parameters:** simulation_id, threshold_percent  
**Returns:** Events with type, severity, description  
**Performance:** ~49ms  
**Cache:** Yes  

**Insights provided:**
- Population crashes/booms
- Mass death events
- Generation milestones
- 22 events detected in test

**When to use:**
- Finding turning points
- Understanding simulation dynamics
- Debugging issues
- Identifying patterns

#### analyze_social_patterns
**Purpose:** Study social interactions  
**Key Parameters:** simulation_id, limit  
**Returns:** Interaction types, outcomes, resource sharing  
**Performance:** ~8ms  
**Cache:** Yes  

**When to use:**
- Social behavior analysis
- Cooperation patterns
- Conflict detection
- Resource sharing studies

#### analyze_reproduction
**Purpose:** Evaluate reproduction success  
**Key Parameters:** simulation_id  
**Returns:** Success rates, resource costs, failure reasons  
**Performance:** ~8ms  
**Cache:** Yes  

**When to use:**
- Reproduction analysis
- Population growth studies
- Resource cost evaluation
- Evolutionary fitness

---

### Comparison Tools (4)

#### compare_simulations
**Purpose:** Compare multiple simulations  
**Key Parameters:** simulation_ids (2-10), metrics  
**Returns:** Statistics per sim, pairwise comparisons, rankings  
**Performance:** ~50ms  
**Cache:** Yes  

**When to use:**
- A/B testing
- Experiment analysis
- Configuration comparison
- Finding best setup

#### compare_parameters
**Purpose:** Analyze parameter impact  
**Key Parameters:** parameter_name, outcome_metric, simulation_ids  
**Returns:** Groups by parameter value, outcome stats  
**Performance:** ~30ms  
**Cache:** Yes  

**When to use:**
- Hypothesis testing
- Parameter tuning
- Understanding parameter effects
- Optimization

#### rank_configurations
**Purpose:** Rank simulations by performance  
**Key Parameters:** metric_name, aggregation, limit, status_filter  
**Returns:** Ranked list with scores and configurations  
**Performance:** ~47ms  
**Cache:** Yes  

**When to use:**
- Finding best configurations
- Performance benchmarking
- Quick comparisons
- Top-N analysis

#### compare_generations
**Purpose:** Track evolutionary progress  
**Key Parameters:** simulation_id, max_generations  
**Returns:** Per-generation stats, survival rates, lifespans  
**Performance:** ~19ms  
**Cache:** Yes  

**Insights provided:**
- 4 generations analyzed in test
- Gen 2 best survival (84.62%)
- Lifespan trends
- Evolutionary fitness

**When to use:**
- Evolution studies
- Generational fitness
- Adaptation analysis
- Long-term trends

---

### Advanced Tools (2)

#### build_agent_lineage
**Purpose:** Construct family trees  
**Key Parameters:** simulation_id, agent_id, depth  
**Returns:** Ancestors, descendants, reproduction events  
**Performance:** ~7ms  
**Cache:** Yes  

**When to use:**
- Genetic lineage tracking
- Family tree visualization
- Ancestry research
- Reproduction path analysis

#### get_agent_lifecycle
**Purpose:** Get complete agent history  
**Key Parameters:** simulation_id, agent_id, include_actions, include_states, include_health  
**Returns:** Full lifecycle with states, actions, health  
**Performance:** ~70ms  
**Cache:** Yes  

**Insights provided:**
- 1,001 state records
- 1,000 actions
- Complete history

**When to use:**
- Detailed agent analysis
- Debugging agent behavior
- Understanding agent story
- Comprehensive studies

---

## 🎯 Tool Selection Guide

### Choose By Goal

**Goal: Quick Overview**
→ `list_simulations` → `get_simulation_info`

**Goal: Understand What Happened**
→ `analyze_population_dynamics` → `identify_critical_events`

**Goal: Deep Agent Analysis**
→ `query_agents` → `analyze_agent_performance` → `get_agent_lifecycle`

**Goal: Compare Experiments**
→ `list_simulations` → `compare_simulations` → `rank_configurations`

**Goal: Debug Population Crash**
→ `analyze_population_dynamics` → `identify_critical_events` → `query_agents` (around crash time)

**Goal: Study Evolution**
→ `analyze_survival_rates` → `compare_generations` → `build_agent_lineage`

---

## ⚡ Performance Guide

### Fast Queries (<10ms)
- list_simulations
- get_simulation_info
- analyze_agent_performance
- compare_generations

### Medium Queries (10-30ms)
- query_agents
- query_resources
- analyze_population_dynamics
- analyze_survival_rates
- analyze_resource_efficiency

### Slower Queries (30-100ms)
- query_actions (large dataset)
- query_states (large dataset)
- get_simulation_metrics
- identify_critical_events (complex analysis)
- rank_configurations
- get_agent_lifecycle (comprehensive data)

**Tip:** All queries benefit from caching. Second call is ~0ms!

---

## 📚 Related Documentation

- **API_REFERENCE.md** - Detailed API docs
- **USER_GUIDE.md** - Usage patterns
- **TROUBLESHOOTING.md** - Common issues

---

**Total Tools:** 23  
**All Tested:** ✅  
**Performance:** <100ms  
**Coverage:** 91%