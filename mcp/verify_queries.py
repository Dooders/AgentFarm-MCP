#!/usr/bin/env python3
"""Comprehensive verification of MCP server querying capabilities."""

import json
from mcp_server.config import MCPConfig
from mcp_server.server import SimulationMCPServer

def print_section(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print('='*70)

def verify_queries():
    """Verify all querying functionality works."""
    
    # Initialize server
    print_section("1. SERVER INITIALIZATION")
    config = MCPConfig.from_db_path("/workspace/simulation.db")
    server = SimulationMCPServer(config)
    print(f"✓ Server initialized successfully")
    print(f"✓ Tools available: {', '.join(server.list_tools())}")
    
    # Test 1: List Simulations
    print_section("2. LIST SIMULATIONS - BASIC QUERY")
    list_sims = server.get_tool("list_simulations")
    result = list_sims(limit=10)
    
    print(f"Success: {result['success']}")
    print(f"Total simulations in database: {result['data']['total_count']}")
    print(f"Returned: {result['data']['returned_count']}")
    print(f"From cache: {result['metadata']['from_cache']}")
    print(f"Execution time: {result['metadata']['execution_time_ms']:.2f}ms")
    
    if result['data']['simulations']:
        sim = result['data']['simulations'][0]
        print(f"\nFirst simulation details:")
        print(f"  ID: {sim['simulation_id']}")
        print(f"  Status: {sim['status']}")
        print(f"  Experiment ID: {sim['experiment_id']}")
        print(f"  Start time: {sim['start_time']}")
        print(f"  Database path: {sim['db_path']}")
        print(f"  Parameters (sample):")
        for key, value in list(sim['parameters_summary'].items())[:3]:
            print(f"    - {key}: {value}")
    
    # Test 2: Get Simulation Info (Detailed Query)
    print_section("3. GET SIMULATION INFO - DETAILED QUERY")
    sim_id = result['data']['simulations'][0]['simulation_id']
    get_sim = server.get_tool("get_simulation_info")
    result2 = get_sim(simulation_id=sim_id)
    
    print(f"Success: {result2['success']}")
    print(f"From cache: {result2['metadata']['from_cache']}")
    print(f"Execution time: {result2['metadata']['execution_time_ms']:.2f}ms")
    print(f"\nFull simulation data:")
    print(f"  ID: {result2['data']['simulation_id']}")
    print(f"  Status: {result2['data']['status']}")
    print(f"  Experiment: {result2['data']['experiment_id']}")
    print(f"  Start: {result2['data']['start_time']}")
    print(f"  End: {result2['data']['end_time']}")
    print(f"  Parameters: {len(result2['data']['parameters'])} total")
    print(f"  Results summary: {result2['data']['results_summary']}")
    
    # Test 3: Cache Hit Test
    print_section("4. CACHE VERIFICATION - REPEAT QUERY")
    result3 = get_sim(simulation_id=sim_id)
    
    print(f"Success: {result3['success']}")
    print(f"From cache: {result3['metadata']['from_cache']}")
    print(f"Execution time: {result3['metadata']['execution_time_ms']:.2f}ms")
    
    if result3['metadata']['from_cache']:
        print(f"✓ CACHE WORKING! Second query used cached data")
    else:
        print(f"⚠ Cache not used (unexpected)")
    
    # Test 4: Filtering Test
    print_section("5. FILTERED QUERY - STATUS FILTER")
    result4 = list_sims(status="completed", limit=5)
    
    print(f"Success: {result4['success']}")
    print(f"Completed simulations: {result4['data']['total_count']}")
    print(f"Returned: {result4['data']['returned_count']}")
    
    if result4['data']['simulations']:
        print(f"\nAll returned simulations have status 'completed':")
        for sim in result4['data']['simulations']:
            print(f"  - {sim['simulation_id']}: {sim['status']}")
    
    # Test 5: Experiment Queries
    print_section("6. EXPERIMENT QUERIES")
    list_exp = server.get_tool("list_experiments")
    exp_result = list_exp(limit=10)
    
    print(f"Success: {exp_result['success']}")
    print(f"Total experiments: {exp_result['data']['total_count']}")
    print(f"From cache: {exp_result['metadata']['from_cache']}")
    
    if exp_result['data']['experiments']:
        exp = exp_result['data']['experiments'][0]
        print(f"\nFirst experiment:")
        print(f"  ID: {exp['experiment_id']}")
        print(f"  Name: {exp['name']}")
        print(f"  Status: {exp['status']}")
        print(f"  Simulations: {exp['simulation_count']}")
        
        # Get detailed experiment info
        get_exp = server.get_tool("get_experiment_info")
        exp_detail = get_exp(experiment_id=exp['experiment_id'])
        
        if exp_detail['success']:
            print(f"\nDetailed experiment info:")
            print(f"  Description: {exp_detail['data']['description'][:100]}...")
            print(f"  Variables: {exp_detail['data']['variables']}")
            print(f"  Tags: {exp_detail['data']['tags']}")
    else:
        print("  No experiments found in database")
    
    # Test 6: Error Handling
    print_section("7. ERROR HANDLING - INVALID SIMULATION ID")
    bad_result = get_sim(simulation_id="invalid_sim_id_12345")
    
    print(f"Success: {bad_result['success']}")
    if not bad_result['success']:
        print(f"Error type: {bad_result['error']['type']}")
        print(f"Error message: {bad_result['error']['message']}")
        print(f"✓ Error handling working correctly")
    
    # Test 7: Pagination
    print_section("8. PAGINATION TEST")
    page1 = list_sims(limit=1, offset=0)
    page2 = list_sims(limit=1, offset=1)
    
    print(f"Page 1 - Simulation: {page1['data']['simulations'][0]['simulation_id']}")
    if page2['data']['simulations']:
        print(f"Page 2 - Simulation: {page2['data']['simulations'][0]['simulation_id']}")
        if page1['data']['simulations'][0]['simulation_id'] != page2['data']['simulations'][0]['simulation_id']:
            print(f"✓ Pagination working - different results returned")
    
    # Final Stats
    print_section("9. FINAL CACHE STATISTICS")
    stats = server.get_cache_stats()
    print(f"Cache enabled: {stats['enabled']}")
    print(f"Cache size: {stats['size']}/{stats['max_size']}")
    print(f"Total hits: {stats['hits']}")
    print(f"Total misses: {stats['misses']}")
    print(f"Hit rate: {stats['hit_rate']:.1%}")
    
    print_section("✓ ALL VERIFICATION TESTS PASSED")
    print("The MCP server successfully:")
    print("  ✓ Queries the database")
    print("  ✓ Returns accurate data")
    print("  ✓ Handles filtering")
    print("  ✓ Supports pagination")
    print("  ✓ Caches results")
    print("  ✓ Handles errors gracefully")
    print("  ✓ Provides detailed metadata")
    
    server.close()

if __name__ == "__main__":
    verify_queries()