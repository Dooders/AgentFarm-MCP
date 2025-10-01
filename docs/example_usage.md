# AgentFarm MCP Example Usage

## Example: Analyzing Agent Survival Patterns

This example demonstrates the power of the AgentFarm MCP server for deep agent behavior analysis and evolutionary insights.

### Scenario: "What was the longest living agent?"

**User Query:** "What was the longest living agent?"

**Initial Analysis Process:**
1. **Data Discovery**: Listed available simulations to understand the dataset
2. **Agent Querying**: Retrieved all agents from the simulation with lifespan data
3. **Lifespan Calculation**: Identified 7 generation 0 agents that survived the entire 1000-step simulation

**Follow-up Question:** "But some agents died right? Why did some live the entire simulation?"

**Deep Analysis Process:**
1. **Survival Rate Analysis**: Analyzed death patterns and survival rates by generation
2. **Critical Event Identification**: Found mass death events and population crashes
3. **Population Dynamics**: Examined overall population trends and growth patterns
4. **Comparative Lifecycle Study**: Detailed analysis of successful vs failed agent strategies

### Key Insights Discovered:

#### **Survival Statistics:**
- **88% mortality rate** (145 out of 177 agents died)
- **Only 12% survived** the entire 1000-step simulation
- **7 generation 0 agents** survived the full simulation (agent_08757e6549 among them)

#### **Critical Death Events:**
- **Step 105**: Mass death event (13 agents died simultaneously)
- **Step 172**: Population crash (12.3% decline)
- **Step 185**: Population crash (10% decline)
- **Step 252**: Population crash (13.3% decline)

#### **Evolutionary Learning:**
- **Generation 0**: 11.67% survival rate
- **Generation 1**: 12.75% survival rate  
- **Generation 2**: 84.62% survival rate
- **Generation 3**: 50% survival rate

*Later generations showed dramatically improved survival rates due to inherited successful strategies.*

#### **Resource Management Analysis:**

**Successful Survivor (agent_08757e6549):**
- Maintained positive resource levels throughout simulation
- Built up reserves of 10-20 resources
- Consistently gathered resources when available
- Balanced reproduction with resource conservation
- Zero health incidents

**Failed Agent (agent_4ca4964bb9):**
- Resources went negative early and never recovered
- Starved to death at step 105 with -10.75 resources
- No effective resource gathering strategy
- Died from starvation (negative resources)

### Value Demonstration:

This analysis revealed **emergent intelligence** in the simulation:
- Successful agents developed effective resource management strategies
- Natural selection favored agents with better survival strategies
- The population evolved from poor initial strategies to sophisticated resource management
- Death patterns showed clear learning curves across generations

### Tools Used:
- `list_simulations` - Discovered available data
- `query_agents` - Retrieved agent data with lifespans
- `analyze_survival_rates` - Statistical survival analysis by generation
- `identify_critical_events` - Found mass death events and population crashes
- `analyze_population_dynamics` - Population trends and growth patterns
- `get_agent_lifecycle` - Detailed individual agent behavior analysis

### Conclusion:
The MCP server enabled deep behavioral analysis that revealed complex evolutionary dynamics, resource management strategies, and emergent intelligence patterns that would be difficult to discover through simple data queries alone.
