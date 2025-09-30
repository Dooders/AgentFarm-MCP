"""End-to-end integration tests."""

import pytest

from mcp.config import MCPConfig
from mcp.server import SimulationMCPServer


def test_full_analysis_workflow(mcp_config, test_simulation_id):
    """Test complete analysis workflow from start to finish."""
    server = SimulationMCPServer(mcp_config)

    # 1. List simulations
    list_tool = server.get_tool("list_simulations")
    result = list_tool()
    assert result["success"] is True
    assert len(result["data"]["simulations"]) > 0

    # 2. Get simulation info
    info_tool = server.get_tool("get_simulation_info")
    result = info_tool(simulation_id=test_simulation_id)
    assert result["success"] is True
    assert result["data"]["simulation_id"] == test_simulation_id

    # 3. Analyze population
    pop_tool = server.get_tool("analyze_population_dynamics")
    result = pop_tool(simulation_id=test_simulation_id)
    assert result["success"] is True
    assert "population_summary" in result["data"]

    # 4. Query agents
    agent_tool = server.get_tool("query_agents")
    result = agent_tool(simulation_id=test_simulation_id, limit=10)
    assert result["success"] is True
    assert len(result["data"]["agents"]) > 0

    server.close()


def test_error_handling_workflow(mcp_config):
    """Test that errors are handled gracefully throughout workflow."""
    server = SimulationMCPServer(mcp_config)

    # Try to get info for nonexistent simulation
    info_tool = server.get_tool("get_simulation_info")
    result = info_tool(simulation_id="nonexistent_sim_999")

    assert result["success"] is False
    assert "error" in result
    assert result["error"] is not None

    server.close()


def test_caching_workflow(mcp_config, test_simulation_id):
    """Test that caching works across multiple tool calls."""
    server = SimulationMCPServer(mcp_config)

    tool = server.get_tool("query_agents")

    # Clear cache first
    server.clear_cache()

    # First call - not cached
    result1 = tool(simulation_id=test_simulation_id, limit=5)
    assert result1["metadata"]["from_cache"] is False

    # Second call - should be cached
    result2 = tool(simulation_id=test_simulation_id, limit=5)
    assert result2["metadata"]["from_cache"] is True

    # Different params - not cached
    result3 = tool(simulation_id=test_simulation_id, limit=10)
    assert result3["metadata"]["from_cache"] is False

    server.close()


def test_multi_tool_workflow(mcp_config, test_simulation_id):
    """Test chaining multiple tool calls."""
    server = SimulationMCPServer(mcp_config)

    # Get agents
    agent_tool = server.get_tool("query_agents")
    agents_result = agent_tool(simulation_id=test_simulation_id, limit=1)
    assert agents_result["success"] is True

    # Get agent ID from result
    agent_id = agents_result["data"]["agents"][0]["agent_id"]

    # Use agent ID in performance analysis
    perf_tool = server.get_tool("analyze_agent_performance")
    perf_result = perf_tool(simulation_id=test_simulation_id, agent_id=agent_id)
    assert perf_result["success"] is True
    assert perf_result["data"]["agent_id"] == agent_id

    # Get complete lifecycle
    lifecycle_tool = server.get_tool("get_agent_lifecycle")
    lifecycle_result = lifecycle_tool(simulation_id=test_simulation_id, agent_id=agent_id)
    assert lifecycle_result["success"] is True

    server.close()


def test_comparison_workflow(mcp_config):
    """Test comparison workflow with multiple simulations."""
    server = SimulationMCPServer(mcp_config)

    # Get list of simulations
    list_tool = server.get_tool("list_simulations")
    sims = list_tool(limit=10)

    if sims["data"]["total_count"] >= 2:
        sim_ids = [s["simulation_id"] for s in sims["data"]["simulations"][:2]]

        # Compare simulations
        compare_tool = server.get_tool("compare_simulations")
        result = compare_tool(simulation_ids=sim_ids)

        assert result["success"] is True
        assert result["data"]["simulation_count"] == 2

    # Rank configurations
    rank_tool = server.get_tool("rank_configurations")
    result = rank_tool(metric_name="total_agents", aggregation="mean")

    assert result["success"] is True
    assert "rankings" in result["data"]

    server.close()


def test_generation_analysis_workflow(mcp_config, test_simulation_id):
    """Test generation analysis workflow."""
    server = SimulationMCPServer(mcp_config)

    # Get survival rates by generation
    survival_tool = server.get_tool("analyze_survival_rates")
    survival_result = survival_tool(simulation_id=test_simulation_id, group_by="generation")

    assert survival_result["success"] is True

    # Compare generations
    compare_gen_tool = server.get_tool("compare_generations")
    compare_result = compare_gen_tool(simulation_id=test_simulation_id)

    assert compare_result["success"] is True

    server.close()


def test_event_detection_workflow(mcp_config, test_simulation_id):
    """Test event detection and analysis workflow."""
    server = SimulationMCPServer(mcp_config)

    # Get simulation metrics
    metrics_tool = server.get_tool("get_simulation_metrics")
    metrics_result = metrics_tool(simulation_id=test_simulation_id, limit=100)

    assert metrics_result["success"] is True

    # Identify critical events
    events_tool = server.get_tool("identify_critical_events")
    events_result = events_tool(simulation_id=test_simulation_id, threshold_percent=10.0)

    assert events_result["success"] is True
    assert "events" in events_result["data"]

    server.close()


def test_cache_persistence_across_tools(mcp_config, test_simulation_id):
    """Test that cache works across different tool calls."""
    server = SimulationMCPServer(mcp_config)

    server.clear_cache()
    initial_stats = server.get_cache_stats()
    assert initial_stats["size"] == 0

    # Call multiple tools
    tools_to_test = [
        ("list_simulations", {}),
        ("get_simulation_info", {"simulation_id": test_simulation_id}),
        ("query_agents", {"simulation_id": test_simulation_id, "limit": 5}),
    ]

    for tool_name, params in tools_to_test:
        tool = server.get_tool(tool_name)
        result = tool(**params)
        assert result["success"] is True

    # Cache should have entries
    final_stats = server.get_cache_stats()
    assert final_stats["size"] > 0

    server.close()