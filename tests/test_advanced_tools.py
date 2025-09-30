#!/usr/bin/env python3
"""Test advanced tools."""

from agentfarm_mcp.config import MCPConfig
from agentfarm_mcp.server import SimulationMCPServer


def print_section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print('='*70)


def test_advanced_tools():
    """Test the 2 advanced tools."""
    
    # Initialize server
    print_section("SERVER INITIALIZATION")
    config = MCPConfig.from_db_path("simulation.db")
    server = SimulationMCPServer(config)
    print(f"✓ Server initialized with {len(server.list_tools())} tools")
    
    # Get simulation and agent for testing
    list_sims = server.get_tool("list_simulations")
    sims_result = list_sims(limit=1)
    sim_id = sims_result['data']['simulations'][0]['simulation_id']
    
    query_agents = server.get_tool("query_agents")
    agents_result = query_agents(simulation_id=sim_id, limit=1)
    agent_id = agents_result['data']['agents'][0]['agent_id']
    
    print(f"✓ Using simulation: {sim_id}")
    print(f"✓ Using agent: {agent_id}")
    
    # Test 1: Get Agent Lifecycle
    print_section("1. GET AGENT LIFECYCLE")
    lifecycle_tool = server.get_tool("get_agent_lifecycle")
    
    result = lifecycle_tool(
        simulation_id=sim_id,
        agent_id=agent_id,
        include_actions=True,
        include_states=True,
        include_health=True
    )
    
    print(f"✓ Success: {result['success']}")
    print(f"✓ Execution time: {result['metadata']['execution_time_ms']:.2f}ms")
    
    if result['success']:
        info = result['data']['agent_info']
        print(f"\nAgent Information:")
        print(f"  ID: {info['agent_id']}")
        print(f"  Type: {info['agent_type']}")
        print(f"  Generation: {info['generation']}")
        print(f"  Birth: {info['birth_time']}")
        print(f"  Death: {info['death_time']}")
        print(f"  Lifespan: {info['lifespan']}")
        print(f"  Genome: {info['genome_id']}")
        
        if 'states' in result['data']:
            states = result['data']['states']
            print(f"\n✓ States: {result['data']['state_count']} records")
            if states:
                first = states[0]
                last = states[-1]
                print(f"  First (step {first['step']}): Resources={first['resources']}, Health={first['health']}")
                print(f"  Last (step {last['step']}): Resources={last['resources']}, Health={last['health']}")
        
        if 'actions' in result['data']:
            actions = result['data']['actions']
            print(f"\n✓ Actions: {result['data']['action_count']} total")
            if actions:
                # Count action types
                action_types = {}
                for action in actions:
                    atype = action['action_type']
                    action_types[atype] = action_types.get(atype, 0) + 1
                
                print(f"  Action distribution:")
                for atype, count in sorted(action_types.items(), key=lambda x: x[1], reverse=True)[:5]:
                    print(f"    {atype}: {count}")
        
        if 'health_incidents' in result['data']:
            incidents = result['data']['health_incidents']
            print(f"\n✓ Health incidents: {result['data']['health_incident_count']}")
            if incidents:
                for incident in incidents[:3]:
                    print(f"  Step {incident['step']}: {incident['cause']} (damage: {incident['damage']})")
    
    # Test 2: Build Agent Lineage
    print_section("2. BUILD AGENT LINEAGE")
    lineage_tool = server.get_tool("build_agent_lineage")
    
    result = lineage_tool(
        simulation_id=sim_id,
        agent_id=agent_id,
        depth=3
    )
    
    print(f"✓ Success: {result['success']}")
    print(f"✓ Execution time: {result['metadata']['execution_time_ms']:.2f}ms")
    
    if result['success']:
        agent_info = result['data']['agent']
        print(f"\nTarget Agent:")
        print(f"  ID: {agent_info['agent_id']}")
        print(f"  Generation: {agent_info['generation']}")
        print(f"  Type: {agent_info['agent_type']}")
        
        ancestors = result['data']['ancestors']
        print(f"\n✓ Ancestors found: {len(ancestors)}")
        if ancestors:
            for i, ancestor in enumerate(ancestors):
                print(f"  Ancestor {i+1}: {ancestor['agent_id']} (Gen {ancestor['generation']})")
                if 'reproduction_event' in ancestor:
                    event = ancestor['reproduction_event']
                    print(f"    Reproduced at step {event['step']}, cost: {event['resources_cost']}")
        else:
            print("  (No ancestors - Generation 0 agent)")
        
        descendants = result['data']['descendants']
        print(f"\n✓ Descendants found: {len(descendants)}")
        if descendants:
            for i, descendant in enumerate(descendants[:5]):
                print(f"  Descendant {i+1}: {descendant['agent_id']} (Gen {descendant['generation']})")
                if 'reproduction_event' in descendant:
                    event = descendant['reproduction_event']
                    print(f"    Born at step {event['step']}, given: {event['resources_given']}")
        else:
            print("  (No descendants yet)")
    
    # Summary
    print_section("SUMMARY")
    print("Advanced tools tested:")
    print("  ✓ get_agent_lifecycle - Complete agent history")
    print("  ✓ build_agent_lineage - Family tree construction")
    
    print(f"\n🎉 Total tools now available: {len(server.list_tools())}")
    print("  - 4 Metadata tools")
    print("  - 6 Query tools")
    print("  - 7 Analysis tools")
    print("  - 4 Comparison tools")
    print("  - 2 Advanced tools")
    
    server.close()


if __name__ == "__main__":
    test_advanced_tools()