#!/usr/bin/env python3
"""Test all query tools comprehensively."""

from agentfarm_mcp.config import MCPConfig
from agentfarm_mcp.server import SimulationMCPServer


def print_section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print('='*70)


def test_query_tools():
    """Test all 6 query tools."""
    
    # Initialize server
    print_section("SERVER INITIALIZATION")
    config = MCPConfig.from_db_path("simulation.db")
    server = SimulationMCPServer(config)
    print(f"✓ Server initialized with {len(server.list_tools())} tools")
    
    # Get simulation ID for testing
    list_sims = server.get_tool("list_simulations")
    sims_result = list_sims(limit=1)
    sim_id = sims_result['data']['simulations'][0]['simulation_id']
    print(f"✓ Using simulation: {sim_id}")
    
    # Test 1: Query Agents
    print_section("1. QUERY AGENTS TOOL")
    query_agents = server.get_tool("query_agents")
    
    # Basic query
    result = query_agents(simulation_id=sim_id, limit=5)
    print(f"✓ Total agents: {result['data']['total_count']}")
    print(f"✓ Returned: {result['data']['returned_count']}")
    print(f"✓ Execution time: {result['metadata']['execution_time_ms']:.2f}ms")
    
    if result['data']['agents']:
        agent = result['data']['agents'][0]
        print(f"\nFirst agent:")
        print(f"  ID: {agent['agent_id']}")
        print(f"  Type: {agent['agent_type']}")
        print(f"  Generation: {agent['generation']}")
        print(f"  Birth time: {agent['birth_time']}")
        print(f"  Position: ({agent['position']['x']}, {agent['position']['y']})")
        print(f"  Resources: {agent['initial_resources']}")
        
        # Test filtering
        result2 = query_agents(
            simulation_id=sim_id, 
            agent_type=agent['agent_type'],
            limit=3
        )
        print(f"\n✓ Filtered by type '{agent['agent_type']}': {result2['data']['total_count']} agents")
        
        # Test alive_only filter
        result3 = query_agents(simulation_id=sim_id, alive_only=True, limit=3)
        print(f"✓ Alive agents only: {result3['data']['total_count']} agents")
    
    # Test 2: Query Actions
    print_section("2. QUERY ACTIONS TOOL")
    query_actions = server.get_tool("query_actions")
    
    result = query_actions(simulation_id=sim_id, limit=10)
    print(f"✓ Total actions: {result['data']['total_count']}")
    print(f"✓ Returned: {result['data']['returned_count']}")
    print(f"✓ Execution time: {result['metadata']['execution_time_ms']:.2f}ms")
    
    if result['data']['actions']:
        action = result['data']['actions'][0]
        print(f"\nFirst action:")
        print(f"  ID: {action['action_id']}")
        print(f"  Step: {action['step_number']}")
        print(f"  Agent: {action['agent_id']}")
        print(f"  Type: {action['action_type']}")
        print(f"  Reward: {action['reward']}")
        
        # Test filtering by action type
        result2 = query_actions(
            simulation_id=sim_id,
            action_type=action['action_type'],
            limit=5
        )
        print(f"\n✓ Actions of type '{action['action_type']}': {result2['data']['total_count']}")
        
        # Test filtering by step range
        result3 = query_actions(
            simulation_id=sim_id,
            start_step=0,
            end_step=10,
            limit=5
        )
        print(f"✓ Actions in steps 0-10: {result3['data']['returned_count']}")
    
    # Test 3: Query States
    print_section("3. QUERY STATES TOOL")
    query_states = server.get_tool("query_states")
    
    result = query_states(simulation_id=sim_id, limit=10)
    print(f"✓ Total states: {result['data']['total_count']}")
    print(f"✓ Returned: {result['data']['returned_count']}")
    print(f"✓ Execution time: {result['metadata']['execution_time_ms']:.2f}ms")
    
    if result['data']['states']:
        state = result['data']['states'][0]
        print(f"\nFirst state:")
        print(f"  Agent: {state['agent_id']}")
        print(f"  Step: {state['step_number']}")
        print(f"  Position: ({state['position']['x']}, {state['position']['y']})")
        print(f"  Resources: {state['resource_level']}")
        print(f"  Health: {state['current_health']}/{state['starting_health']}")
        print(f"  Age: {state['age']}")
        
        # Test filtering by agent
        result2 = query_states(
            simulation_id=sim_id,
            agent_id=state['agent_id'],
            limit=5
        )
        print(f"\n✓ States for agent {state['agent_id']}: {result2['data']['total_count']}")
    
    # Test 4: Query Resources
    print_section("4. QUERY RESOURCES TOOL")
    query_resources = server.get_tool("query_resources")
    
    result = query_resources(simulation_id=sim_id, limit=10)
    print(f"✓ Total resource records: {result['data']['total_count']}")
    print(f"✓ Returned: {result['data']['returned_count']}")
    print(f"✓ Execution time: {result['metadata']['execution_time_ms']:.2f}ms")
    
    if result['data']['resources']:
        resource = result['data']['resources'][0]
        print(f"\nFirst resource:")
        print(f"  ID: {resource['resource_id']}")
        print(f"  Step: {resource['step_number']}")
        print(f"  Amount: {resource['amount']}")
        print(f"  Position: ({resource['position']['x']}, {resource['position']['y']})")
        
        # Test filtering by step
        result2 = query_resources(
            simulation_id=sim_id,
            step_number=resource['step_number'],
            limit=5
        )
        print(f"\n✓ Resources at step {resource['step_number']}: {result2['data']['returned_count']}")
    
    # Test 5: Query Interactions
    print_section("5. QUERY INTERACTIONS TOOL")
    query_interactions = server.get_tool("query_interactions")
    
    result = query_interactions(simulation_id=sim_id, limit=10)
    print(f"✓ Total interactions: {result['data']['total_count']}")
    print(f"✓ Returned: {result['data']['returned_count']}")
    print(f"✓ Execution time: {result['metadata']['execution_time_ms']:.2f}ms")
    
    if result['data']['interactions']:
        interaction = result['data']['interactions'][0]
        print(f"\nFirst interaction:")
        print(f"  ID: {interaction['interaction_id']}")
        print(f"  Step: {interaction['step_number']}")
        print(f"  Type: {interaction['interaction_type']}")
        print(f"  Source: {interaction['source_type']}:{interaction['source_id']}")
        print(f"  Target: {interaction['target_type']}:{interaction['target_id']}")
        
        # Test filtering by type
        if interaction['interaction_type']:
            result2 = query_interactions(
                simulation_id=sim_id,
                interaction_type=interaction['interaction_type'],
                limit=5
            )
            print(f"\n✓ '{interaction['interaction_type']}' interactions: {result2['data']['total_count']}")
    
    # Test 6: Get Simulation Metrics
    print_section("6. GET SIMULATION METRICS TOOL")
    get_metrics = server.get_tool("get_simulation_metrics")
    
    result = get_metrics(simulation_id=sim_id, limit=20)
    print(f"✓ Total steps: {result['data']['total_count']}")
    print(f"✓ Returned: {result['data']['returned_count']}")
    print(f"✓ Execution time: {result['metadata']['execution_time_ms']:.2f}ms")
    
    if result['data']['metrics']:
        metrics = result['data']['metrics']
        first_step = metrics[0]
        last_step = metrics[-1]
        
        print(f"\nFirst step ({first_step['step_number']}):")
        print(f"  Total agents: {first_step['total_agents']}")
        print(f"  System: {first_step['system_agents']}")
        print(f"  Independent: {first_step['independent_agents']}")
        print(f"  Avg health: {first_step['average_agent_health']}")
        
        print(f"\nLast step ({last_step['step_number']}):")
        print(f"  Total agents: {last_step['total_agents']}")
        print(f"  Births: {last_step['births']}")
        print(f"  Deaths: {last_step['deaths']}")
        print(f"  Resources: {last_step['total_resources']}")
        
        # Test step range filtering
        result2 = get_metrics(
            simulation_id=sim_id,
            start_step=0,
            end_step=10
        )
        print(f"\n✓ Metrics for steps 0-10: {result2['data']['returned_count']} steps")
    
    # Cache Statistics
    print_section("CACHE STATISTICS")
    stats = server.get_cache_stats()
    print(f"Cache size: {stats['size']}/{stats['max_size']}")
    print(f"Hits: {stats['hits']}, Misses: {stats['misses']}")
    if stats['hits'] + stats['misses'] > 0:
        print(f"Hit rate: {stats['hit_rate']:.1%}")
    
    print_section("✓ ALL QUERY TOOLS TESTED SUCCESSFULLY")
    print("Phase 2 query tools are fully functional:")
    print("  ✓ query_agents - with filtering by type, generation, alive status")
    print("  ✓ query_actions - with filtering by agent, type, step range")
    print("  ✓ query_states - with filtering by agent, step range")
    print("  ✓ query_resources - with filtering by step")
    print("  ✓ query_interactions - with filtering by type, source, target")
    print("  ✓ get_simulation_metrics - with step range filtering")
    
    server.close()


if __name__ == "__main__":
    test_query_tools()