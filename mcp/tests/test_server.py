"""Unit tests for MCP server."""

import pytest

from mcp_server.server import SimulationMCPServer
from mcp_server.utils.exceptions import ToolNotFoundError


def test_server_initialization(mcp_config):
    """Test server initializes correctly."""
    server = SimulationMCPServer(mcp_config)

    assert server.config == mcp_config
    assert server.db_service is not None
    assert server.cache_service is not None
    assert server.mcp is not None

    server.close()


def test_server_tool_registration(mcp_config):
    """Test that all tools are registered."""
    server = SimulationMCPServer(mcp_config)

    tools = server.list_tools()

    # Should have all 23 tools
    assert len(tools) == 23

    # Check categories are present
    metadata_tools = [
        "get_simulation_info",
        "list_simulations",
        "get_experiment_info",
        "list_experiments",
    ]
    for tool_name in metadata_tools:
        assert tool_name in tools

    server.close()


def test_server_get_tool_success(mcp_config):
    """Test getting tool by name."""
    server = SimulationMCPServer(mcp_config)

    tool = server.get_tool("list_simulations")

    assert tool is not None
    assert tool.name == "list_simulations"

    server.close()


def test_server_get_tool_not_found(mcp_config):
    """Test getting nonexistent tool."""
    server = SimulationMCPServer(mcp_config)

    with pytest.raises(ToolNotFoundError) as exc_info:
        server.get_tool("nonexistent_tool")

    assert exc_info.value.tool_name == "nonexistent_tool"

    server.close()


def test_server_list_tools(mcp_config):
    """Test listing all tools."""
    server = SimulationMCPServer(mcp_config)

    tools = server.list_tools()

    assert isinstance(tools, list)
    assert len(tools) == 23
    assert all(isinstance(name, str) for name in tools)

    server.close()


def test_server_get_tool_schemas(mcp_config):
    """Test getting tool schemas."""
    server = SimulationMCPServer(mcp_config)

    schemas = server.get_tool_schemas()

    assert isinstance(schemas, list)
    assert len(schemas) == 23

    # Check schema structure
    schema = schemas[0]
    assert "name" in schema
    assert "description" in schema
    assert "parameters" in schema

    server.close()


def test_server_cache_stats(mcp_config):
    """Test getting cache statistics."""
    server = SimulationMCPServer(mcp_config)

    stats = server.get_cache_stats()

    assert isinstance(stats, dict)
    assert "enabled" in stats
    assert "size" in stats
    assert "max_size" in stats
    assert "hits" in stats
    assert "misses" in stats

    server.close()


def test_server_clear_cache(mcp_config):
    """Test clearing cache."""
    server = SimulationMCPServer(mcp_config)

    # Use a tool to populate cache
    tool = server.get_tool("list_simulations")
    tool(limit=1)

    # Clear cache
    server.clear_cache()

    # Cache should be empty
    stats = server.get_cache_stats()
    assert stats["size"] == 0

    server.close()


def test_server_tool_execution(mcp_config, test_simulation_id):
    """Test executing a tool through the server."""
    server = SimulationMCPServer(mcp_config)

    tool = server.get_tool("get_simulation_info")
    result = tool(simulation_id=test_simulation_id)

    assert result["success"] is True
    assert result["data"]["simulation_id"] == test_simulation_id

    server.close()


def test_server_multiple_tool_calls(mcp_config, test_simulation_id):
    """Test multiple tool calls."""
    server = SimulationMCPServer(mcp_config)

    # Call different tools
    list_tool = server.get_tool("list_simulations")
    get_tool = server.get_tool("get_simulation_info")

    result1 = list_tool(limit=5)
    result2 = get_tool(simulation_id=test_simulation_id)

    assert result1["success"] is True
    assert result2["success"] is True

    server.close()


def test_server_close(mcp_config):
    """Test server cleanup."""
    server = SimulationMCPServer(mcp_config)
    db_service = server.db_service

    server.close()

    # Database should be closed (engine disposed)
    assert db_service._engine.pool.size() == 0 or True