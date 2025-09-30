#!/usr/bin/env python3
"""Simple test script to verify the MCP server works."""

import sys
from agentfarm_mcp.config import MCPConfig
from agentfarm_mcp.server import SimulationMCPServer

def test_server():
    """Test the MCP server with basic operations."""
    print("Testing MCP Server...")
    print("=" * 60)
    
    # Initialize server
    print("\n1. Initializing server...")
    config = MCPConfig.from_db_path("simulation.db")
    server = SimulationMCPServer(config)
    print(f"   ✓ Server initialized with {len(server.list_tools())} tools")
    
    # List tools
    print("\n2. Listing tools...")
    tools = server.list_tools()
    for tool_name in tools:
        print(f"   - {tool_name}")
    
    # Test list_simulations tool
    print("\n3. Testing list_simulations tool...")
    try:
        list_sim_tool = server.get_tool("list_simulations")
        result = list_sim_tool(limit=5)
        
        if result["success"]:
            print(f"   ✓ Found {result['data']['total_count']} simulations")
            print(f"   ✓ Returned {result['data']['returned_count']} results")
            if result['data']['simulations']:
                sim = result['data']['simulations'][0]
                print(f"   ✓ First simulation: {sim['simulation_id']}")
        else:
            print(f"   ✗ Error: {result['error']}")
    except Exception as e:
        print(f"   ✗ Error testing tool: {e}")
    
    # Test get_simulation_info tool
    print("\n4. Testing get_simulation_info tool...")
    try:
        get_sim_tool = server.get_tool("get_simulation_info")
        
        # First get a simulation ID to test with
        list_sim_tool = server.get_tool("list_simulations")
        list_result = list_sim_tool(limit=1)
        
        if list_result["success"] and list_result['data']['simulations']:
            sim_id = list_result['data']['simulations'][0]['simulation_id']
            
            result = get_sim_tool(simulation_id=sim_id)
            
            if result["success"]:
                print(f"   ✓ Got info for simulation: {result['data']['simulation_id']}")
                print(f"   ✓ Status: {result['data']['status']}")
                print(f"   ✓ Cached: {result['metadata']['from_cache']}")
                print(f"   ✓ Execution time: {result['metadata']['execution_time_ms']:.2f}ms")
                
                # Test cache by calling again
                result2 = get_sim_tool(simulation_id=sim_id)
                if result2["metadata"]["from_cache"]:
                    print(f"   ✓ Cache working! Second call used cache")
            else:
                print(f"   ✗ Error: {result['error']}")
        else:
            print("   ⚠ No simulations found to test with")
    except Exception as e:
        print(f"   ✗ Error testing tool: {e}")
    
    # Test cache stats
    print("\n5. Testing cache statistics...")
    stats = server.get_cache_stats()
    print(f"   - Cache enabled: {stats['enabled']}")
    print(f"   - Cache size: {stats['size']}/{stats['max_size']}")
    print(f"   - Hits: {stats['hits']}, Misses: {stats['misses']}")
    if stats['hits'] + stats['misses'] > 0:
        print(f"   - Hit rate: {stats['hit_rate']:.1%}")
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    
    # Cleanup
    server.close()

if __name__ == "__main__":
    try:
        test_server()
    except Exception as e:
        print(f"\nFatal error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)