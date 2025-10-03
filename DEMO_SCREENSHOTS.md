# 📸 Streamlit Demo - Visual Guide

## Overview

This guide provides a visual walkthrough of the MCP Simulation Server Streamlit demo app.

## 🖥️ Main Interface

### Layout Structure

```
┌─────────────────────────────────────────────────────────────────┐
│  🤖 MCP Simulation Server - Chat Demo                           │
│  Ask questions about your simulation data using natural language│
├────────────┬────────────────────────────────────────────────────┤
│            │                                                    │
│  SIDEBAR   │              MAIN CHAT AREA                        │
│            │                                                    │
│  Server    │  ┌──────────────────────────────────────────────┐ │
│  Status    │  │ 👤 User: What's the population growth rate?  │ │
│            │  └──────────────────────────────────────────────┘ │
│  🟢 healthy│                                                    │
│            │  ┌──────────────────────────────────────────────┐ │
│  Database: │  │ 🤖 Assistant: Let me analyze that...         │ │
│  connected │  │                                              │ │
│            │  │  🔧 Tool: analyze_population_dynamics        │ │
│  Cache:    │  │     ✅ Success (23.4ms)                      │ │
│  Enabled   │  │                                              │ │
│  (15 items)│  │  📈 [Interactive Chart]                      │ │
│  Hit: 85%  │  │                                              │ │
│            │  │  The population grew by 70%...              │ │
│  Tools:    │  └──────────────────────────────────────────────┘ │
│  25/25     │                                                    │
│            │  ┌──────────────────────────────────────────────┐ │
│  ━━━━━━━━━━│  │ 💬 Ask about your simulation data...         │ │
│            │  └──────────────────────────────────────────────┘ │
│  Example   │                                                    │
│  Queries   │                                                    │
│            │                                                    │
│  [List all │                                                    │
│   sims]    │                                                    │
│            │                                                    │
│  [Growth   │                                                    │
│   rate?]   │                                                    │
│            │                                                    │
│  [Top 5    │                                                    │
│   agents]  │                                                    │
│            │                                                    │
│  ...       │                                                    │
│            │                                                    │
│  [🗑️ Clear│                                                    │
│   Chat]    │                                                    │
│            │                                                    │
└────────────┴────────────────────────────────────────────────────┘
```

## 📊 Example Interactions

### 1. Simple Query

**User Input:**
```
List all available simulations
```

**Agent Response:**
```
🤖 Assistant:
I'll retrieve the list of simulations for you.

🔧 Tool: list_simulations
   Input: {"limit": 100, "offset": 0}
   ✅ Success (8.2ms)
   
   📊 Found 3 simulations:
   
   [Data Table showing:]
   simulation_id | status    | total_steps | total_agents
   sim_001      | completed | 1000        | 177
   sim_002      | completed | 1000        | 145  
   sim_003      | running   | 523         | 89

There are 3 simulations in the database. Two are completed
and one is still running.
```

### 2. Analysis with Visualization

**User Input:**
```
Analyze population dynamics and show a chart
```

**Agent Response:**
```
🤖 Assistant:
Let me analyze the population dynamics for you.

🔧 Tool: analyze_population_dynamics
   Input: {
     "simulation_id": "sim_001",
     "include_chart": true
   }
   ✅ Success (23.4ms)
   
   📈 Population Dynamics Chart
   [Interactive Plotly Line Chart]
   - X-axis: Step Number (0-1000)
   - Y-axis: Agent Count
   - Lines: Total Agents, Births, Deaths
   
   📊 Summary:
   • Growth Rate: +70%
   • Peak Population: 89 agents (step 456)
   • Final Population: 32 agents
   • Total Births: 145
   • Total Deaths: 113

The simulation shows strong initial growth with a 70% 
increase, peaking at step 456 with 89 agents. The 
population then declined to 32 agents by the end.
```

### 3. Agent Deep Dive

**User Input:**
```
Show me the top 5 agents that survived the longest
```

**Agent Response:**
```
🤖 Assistant:
I'll find the longest-surviving agents for you.

🔧 Tool: query_agents
   Input: {
     "simulation_id": "sim_001",
     "limit": 100
   }
   ✅ Success (7.1ms)
   
🔧 Tool: analyze_survival_rates
   Input: {
     "simulation_id": "sim_001", 
     "group_by": "generation"
   }
   ✅ Success (18.3ms)

Top 5 Longest-Surviving Agents:

┌──────────┬────────┬────────────┬───────────┬──────────┐
│ agent_id │ type   │ generation │ lifespan  │ status   │
├──────────┼────────┼────────────┼───────────┼──────────┤
│ A_089    │ system │     2      │ 892 steps │ died     │
│ A_034    │ system │     1      │ 856 steps │ died     │
│ A_121    │ indep. │     3      │ 823 steps │ died     │
│ A_067    │ system │     2      │ 789 steps │ alive    │
│ A_012    │ system │     1      │ 745 steps │ died     │
└──────────┴────────┴────────────┴───────────┴──────────┘

The longest-surviving agent (A_089) lived for 892 steps
across generation 2. Interestingly, 4 out of 5 top
survivors are system-type agents.
```

### 4. Multi-Tool Agentic Workflow

**User Input:**
```
Were there any critical events or population crashes?
```

**Agent Response:**
```
🤖 Assistant:
Let me analyze critical events in the simulation.

🔧 Tool: identify_critical_events
   Input: {
     "simulation_id": "sim_001",
     "threshold_percent": 5.0
   }
   ✅ Success (49.2ms)
   
🔧 Tool: analyze_population_dynamics
   Input: {
     "simulation_id": "sim_001",
     "start_step": 450,
     "end_step": 500
   }
   ✅ Success (12.1ms)

📊 Critical Events Detected: 22 events

Major Events:
1. 🔴 POPULATION_CRASH (Step 467)
   - Severity: HIGH
   - Population dropped from 89 → 67 (-24.7%)
   
2. ⚠️  MASS_DEATH_EVENT (Step 468)
   - 15 agents died in single step
   
3. 📉 POPULATION_DECLINE (Steps 470-490)
   - Sustained 20-step decline
   - Lost 23 additional agents

4. ✅ GENERATION_MILESTONE (Step 234)
   - Generation 3 emerged
   
The simulation experienced a major population crash at
step 467, losing nearly 25% of the population. This was
followed by a mass death event and continued decline.
```

## 🎯 UI Components

### Expandable Tool Results

```
┌─────────────────────────────────────────────────────┐
│ 🔧 Tool: analyze_population_dynamics           [▼]  │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Input Parameters:                                  │
│  {                                                  │
│    "simulation_id": "sim_001",                      │
│    "include_chart": true                            │
│  }                                                  │
│                                                     │
│  ✅ Success (23.4ms)                                │
│                                                     │
│  📈 [Interactive Plotly Chart]                      │
│     [Chart shows population over time]              │
│                                                     │
│  📊 Data:                                           │
│  {                                                  │
│    "population_summary": {                          │
│      "total_growth_rate_percent": 70.2,             │
│      "peak_population": 89,                         │
│      ...                                            │
│    }                                                │
│  }                                                  │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Interactive Charts

```
Population Dynamics Over Time
┌─────────────────────────────────────────────┐
│  100 ┤                    ╭─╮               │
│      │                   ╱   ╰╮              │
│   80 ┤                 ╱      ╰╮            │
│      │               ╱          ╰╮          │
│   60 ┤             ╱              ╰╮        │
│      │           ╱                  ╰╮      │
│   40 ┤        ╭╯                     ╰──╮   │
│      │      ╱                            ╰─ │
│   20 ┤   ╭─╯                               │
│      │ ╭─╯                                  │
│    0 ┼─┴─────────────────────────────────── │
│      0    200   400   600   800  1000      │
│                  Step Number                │
│                                             │
│  ━ Total Agents  ⋯ Births  ⋯ Deaths        │
│                                             │
│  [Pan] [Zoom] [Reset] [Download]           │
└─────────────────────────────────────────────┘
```

### Data Tables

```
┌─────────────────────────────────────────────────────┐
│  Agent Data                           [↕ Sort] [🔍] │
├──────────┬────────┬────────────┬───────────┬────────┤
│ agent_id │ type   │ generation │ birth     │ death  │
├──────────┼────────┼────────────┼───────────┼────────┤
│ A_001    │ system │     0      │     0     │  234   │
│ A_002    │ system │     0      │     0     │  456   │
│ A_003    │ indep. │     0      │     0     │  189   │
│ A_004    │ system │     1      │    12     │  789   │
│ ...      │  ...   │    ...     │   ...     │  ...   │
├──────────┴────────┴────────────┴───────────┴────────┤
│  Showing 10 of 177 agents                           │
│  [◀ Prev] Page 1 of 18 [Next ▶]                    │
└─────────────────────────────────────────────────────┘
```

## 🎨 Color Scheme

### Status Indicators
- 🟢 Green: Healthy, Success, Connected
- 🔴 Red: Error, Unhealthy, Failed
- 🟡 Yellow: Warning, Degraded
- ⚪ Gray: Neutral, Info

### Message Types
- 👤 User: Blue background
- 🤖 Assistant: Light gray background
- 🔧 Tool: White with border

### Charts
- **Total Agents**: Blue (#1f77b4)
- **Births**: Green (#2ca02c) - dotted
- **Deaths**: Red (#d62728) - dotted
- **Resources**: Orange (#ff7f0e)

## 🔄 Workflow Examples

### Simple Workflow
```
User Query
    ↓
Claude Analyzes
    ↓
Single Tool Call
    ↓
Display Results
```

### Complex Workflow (Agentic)
```
User: "Compare survival across generations"
    ↓
Claude: Analyzes intent
    ↓
Tool 1: list_simulations (get sim_id)
    ↓
Tool 2: analyze_survival_rates (group_by=generation)
    ↓
Tool 3: compare_generations (detailed comparison)
    ↓
Claude: Synthesizes results
    ↓
Display: Combined analysis with insights
```

## 💡 Tips for Best Results

### 1. Be Specific
❌ "Show me data"
✅ "Show me population dynamics for sim_001"

### 2. Ask Follow-ups
✅ "What caused that population crash?"
✅ "Show me the agents that died in that period"

### 3. Use Examples
✅ Click example queries in sidebar
✅ Modify and resubmit

### 4. Explore Tools
✅ Expand tool result sections
✅ Review JSON data
✅ Check execution times

### 5. Visualize
✅ Request charts: "...and show a chart"
✅ Explore interactive features
✅ Download charts (Plotly menu)

## 🚀 Quick Actions

### In Sidebar
- Click **Server Status** → See health
- Click **Example Query** → Auto-submit
- Click **Clear Chat** → Reset conversation

### In Chat
- Click **Tool Section** → Expand/collapse
- Hover **Chart** → See data points
- Click **JSON** → Expand/collapse

### In Results
- Click **Table Header** → Sort column
- Drag **Chart** → Pan view
- Scroll **Chart** → Zoom in/out

---

**Note**: This is a visual guide. Actual interface will have Streamlit's
modern, responsive design with smooth interactions and animations.

**Try it yourself**: `streamlit run streamlit_demo.py`
