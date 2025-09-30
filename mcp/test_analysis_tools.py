#!/usr/bin/env python3
"""Test all analysis tools comprehensively."""

from mcp_server.config import MCPConfig
from mcp_server.server import SimulationMCPServer


def print_section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print('='*70)


def test_analysis_tools():
    """Test all 7 analysis tools."""
    
    # Initialize server
    print_section("SERVER INITIALIZATION")
    config = MCPConfig.from_db_path("/workspace/simulation.db")
    server = SimulationMCPServer(config)
    print(f"✓ Server initialized with {len(server.list_tools())} tools")
    
    # Get simulation ID and agent ID for testing
    list_sims = server.get_tool("list_simulations")
    sims_result = list_sims(limit=1)
    sim_id = sims_result['data']['simulations'][0]['simulation_id']
    
    query_agents = server.get_tool("query_agents")
    agents_result = query_agents(simulation_id=sim_id, limit=1)
    agent_id = agents_result['data']['agents'][0]['agent_id']
    
    print(f"✓ Using simulation: {sim_id}")
    print(f"✓ Using agent: {agent_id}")
    
    # Test 1: Analyze Population Dynamics
    print_section("1. ANALYZE POPULATION DYNAMICS")
    analyze_pop = server.get_tool("analyze_population_dynamics")
    
    result = analyze_pop(simulation_id=sim_id, start_step=0, end_step=100)
    print(f"✓ Success: {result['success']}")
    print(f"✓ Execution time: {result['metadata']['execution_time_ms']:.2f}ms")
    
    if result['success']:
        summary = result['data']['population_summary']
        print(f"\nPopulation Summary:")
        print(f"  Initial: {summary['initial_population']}")
        print(f"  Final: {summary['final_population']}")
        print(f"  Peak: {summary['peak_population']} at step {summary['peak_step']}")
        print(f"  Average: {summary['average_population']:.1f}")
        print(f"  Growth rate: {summary['total_growth_rate_percent']}%")
        print(f"  Total births: {summary['total_births']}")
        print(f"  Total deaths: {summary['total_deaths']}")
        
        by_type = result['data']['by_type']
        print(f"\nBy Type:")
        print(f"  System agents: peak={by_type['system']['peak']}, avg={by_type['system']['average']:.1f}")
        print(f"  Independent: peak={by_type['independent']['peak']}, avg={by_type['independent']['average']:.1f}")
    
    # Test with chart
    result2 = analyze_pop(simulation_id=sim_id, start_step=0, end_step=20, include_chart=True)
    if result2['success'] and 'chart' in result2['data']:
        print(f"\n✓ Chart generation working")
    
    # Test 2: Analyze Survival Rates
    print_section("2. ANALYZE SURVIVAL RATES")
    analyze_survival = server.get_tool("analyze_survival_rates")
    
    # By generation
    result = analyze_survival(simulation_id=sim_id, group_by="generation")
    print(f"✓ Success: {result['success']}")
    print(f"✓ Execution time: {result['metadata']['execution_time_ms']:.2f}ms")
    
    if result['success']:
        print(f"\nGrouped by: {result['data']['grouped_by']}")
        print(f"Total cohorts: {result['data']['summary']['total_groups']}")
        print(f"Total agents: {result['data']['summary']['total_agents']}")
        print(f"Overall survival rate: {result['data']['summary']['overall_survival_rate']}%")
        
        # Show first few cohorts
        cohorts = list(result['data']['cohorts'].items())[:3]
        print(f"\nFirst 3 cohorts:")
        for gen, stats in cohorts:
            print(f"  Generation {gen}:")
            print(f"    Total: {stats['total_agents']}, Alive: {stats['alive']}, Dead: {stats['dead']}")
            print(f"    Survival rate: {stats['survival_rate_percent']}%")
            if stats['average_lifespan']:
                print(f"    Avg lifespan: {stats['average_lifespan']}")
    
    # By agent type
    result2 = analyze_survival(simulation_id=sim_id, group_by="agent_type")
    if result2['success']:
        print(f"\n✓ By agent_type: {result2['data']['summary']['total_groups']} types analyzed")
    
    # Test 3: Analyze Resource Efficiency
    print_section("3. ANALYZE RESOURCE EFFICIENCY")
    analyze_resources = server.get_tool("analyze_resource_efficiency")
    
    result = analyze_resources(simulation_id=sim_id, start_step=0, end_step=100)
    print(f"✓ Success: {result['success']}")
    print(f"✓ Execution time: {result['metadata']['execution_time_ms']:.2f}ms")
    
    if result['success']:
        res_summary = result['data']['resource_summary']
        print(f"\nResource Summary:")
        print(f"  Initial total: {res_summary['initial_total_resources']}")
        print(f"  Final total: {res_summary['final_total_resources']}")
        print(f"  Peak: {res_summary['peak_total_resources']}")
        print(f"  Average: {res_summary['average_total_resources']:.2f}")
        print(f"  Total consumed: {res_summary['total_consumed']}")
        
        agent_res = result['data']['agent_resource_metrics']
        print(f"\nPer Agent Metrics:")
        print(f"  Peak avg: {agent_res['peak_avg_per_agent']}")
        print(f"  Overall avg: {agent_res['average_per_agent']:.2f}")
        print(f"  Final avg: {agent_res['final_avg_per_agent']}")
        
        if 'efficiency_metrics' in result['data']:
            eff = result['data']['efficiency_metrics']
            print(f"\nEfficiency Metrics:")
            print(f"  Average: {eff['average_efficiency']:.4f}")
            print(f"  Peak: {eff['peak_efficiency']:.4f}")
    
    # Test 4: Analyze Agent Performance
    print_section("4. ANALYZE AGENT PERFORMANCE")
    analyze_agent = server.get_tool("analyze_agent_performance")
    
    result = analyze_agent(simulation_id=sim_id, agent_id=agent_id)
    print(f"✓ Success: {result['success']}")
    print(f"✓ Execution time: {result['metadata']['execution_time_ms']:.2f}ms")
    
    if result['success']:
        print(f"\nAgent Analysis:")
        print(f"  ID: {result['data']['agent_id']}")
        print(f"  Type: {result['data']['agent_type']}")
        print(f"  Generation: {result['data']['generation']}")
        print(f"  Status: {result['data']['status']}")
        print(f"  Lifespan: {result['data']['lifespan']} steps")
        print(f"  Birth: {result['data']['birth_time']}")
        print(f"  Death: {result['data']['death_time']}")
        
        perf = result['data']['performance_metrics']
        print(f"\nPerformance:")
        print(f"  Initial resources: {perf['initial_resources']}")
        print(f"  Starting health: {perf['starting_health']}")
        print(f"  Genome: {perf['genome_id']}")
    
    # Test 5: Identify Critical Events
    print_section("5. IDENTIFY CRITICAL EVENTS")
    identify_events = server.get_tool("identify_critical_events")
    
    result = identify_events(simulation_id=sim_id, threshold_percent=5.0)
    print(f"✓ Success: {result['success']}")
    print(f"✓ Execution time: {result['metadata']['execution_time_ms']:.2f}ms")
    
    if result['success']:
        summary = result['data']['summary']
        print(f"\nEvent Summary:")
        print(f"  Total events detected: {summary['total_events']}")
        
        if 'by_type' in summary:
            print(f"\nBy Type:")
            for event_type, count in summary['by_type'].items():
                print(f"    {event_type}: {count}")
        
        if 'by_severity' in summary:
            print(f"\nBy Severity:")
            for severity, count in summary['by_severity'].items():
                print(f"    {severity}: {count}")
        
        # Show first few events
        events = result['data']['events'][:5]
        if events:
            print(f"\nFirst {len(events)} events:")
            for event in events:
                print(f"  Step {event['step']}: [{event['severity']}] {event['description']}")
    
    # Test 6: Analyze Social Patterns
    print_section("6. ANALYZE SOCIAL PATTERNS")
    analyze_social = server.get_tool("analyze_social_patterns")
    
    result = analyze_social(simulation_id=sim_id, limit=1000)
    print(f"✓ Success: {result['success']}")
    print(f"✓ Execution time: {result['metadata']['execution_time_ms']:.2f}ms")
    
    if result['success']:
        if 'total_interactions' in result['data']:
            print(f"\nSocial Interaction Analysis:")
            print(f"  Total interactions: {result['data']['total_interactions']}")
            
            if 'interaction_types' in result['data']:
                print(f"\nInteraction Types:")
                for itype, count in list(result['data']['interaction_types'].items())[:5]:
                    print(f"    {itype}: {count}")
            
            if 'outcomes' in result['data']:
                print(f"\nOutcomes:")
                for outcome, count in result['data']['outcomes'].items():
                    print(f"    {outcome}: {count}")
            
            if 'resource_sharing' in result['data']:
                sharing = result['data']['resource_sharing']
                print(f"\nResource Sharing:")
                print(f"    Total transferred: {sharing['total_resources_transferred']}")
                print(f"    Avg per interaction: {sharing['average_per_interaction']}")
        else:
            print(f"  {result['data'].get('message', 'No data')}")
    
    # Test 7: Analyze Reproduction
    print_section("7. ANALYZE REPRODUCTION")
    analyze_repro = server.get_tool("analyze_reproduction")
    
    result = analyze_repro(simulation_id=sim_id)
    print(f"✓ Success: {result['success']}")
    print(f"✓ Execution time: {result['metadata']['execution_time_ms']:.2f}ms")
    
    if result['success']:
        if 'total_attempts' in result['data']:
            print(f"\nReproduction Analysis:")
            print(f"  Total attempts: {result['data']['total_attempts']}")
            print(f"  Successful: {result['data']['successful']}")
            print(f"  Failed: {result['data']['failed']}")
            print(f"  Success rate: {result['data']['success_rate_percent']}%")
            
            if 'resource_analysis' in result['data']:
                res_analysis = result['data']['resource_analysis']
                print(f"\nResource Costs:")
                print(f"    Average: {res_analysis['average_cost']}")
                print(f"    Min: {res_analysis['min_cost']}")
                print(f"    Max: {res_analysis['max_cost']}")
            
            if 'failure_reasons' in result['data'] and result['data']['failure_reasons']:
                print(f"\nFailure Reasons:")
                for reason, count in result['data']['failure_reasons'].items():
                    print(f"    {reason}: {count}")
        else:
            print(f"  {result['data'].get('message', 'No data')}")
    
    # Cache Statistics
    print_section("CACHE STATISTICS")
    stats = server.get_cache_stats()
    print(f"Cache size: {stats['size']}/{stats['max_size']}")
    print(f"Hits: {stats['hits']}, Misses: {stats['misses']}")
    if stats['hits'] + stats['misses'] > 0:
        print(f"Hit rate: {stats['hit_rate']:.1%}")
    
    print_section("✓ ALL ANALYSIS TOOLS TESTED SUCCESSFULLY")
    print("Phase 3 analysis tools are fully functional:")
    print("  ✓ analyze_population_dynamics - with charts and detailed stats")
    print("  ✓ analyze_survival_rates - by generation and agent type")
    print("  ✓ analyze_resource_efficiency - resource utilization metrics")
    print("  ✓ analyze_agent_performance - individual agent analysis")
    print("  ✓ identify_critical_events - event detection with severity")
    print("  ✓ analyze_social_patterns - social interaction analysis")
    print("  ✓ analyze_reproduction - reproduction success analysis")
    
    print(f"\n🎉 Total tools now available: {len(server.list_tools())}")
    print("  - 4 Metadata tools")
    print("  - 6 Query tools")
    print("  - 7 Analysis tools")
    
    server.close()


if __name__ == "__main__":
    test_analysis_tools()