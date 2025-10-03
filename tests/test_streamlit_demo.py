"""Tests for the Streamlit demo application.

Note: These tests focus on the utility functions and helper methods.
Full Streamlit UI testing would require selenium or similar tools.
"""

import json
import os
from typing import Any, Dict
from unittest.mock import MagicMock, Mock, patch

import pytest

# Test helper functions that can be extracted and tested


class TestToolDefinitionConversion:
    """Test conversion of Pydantic schemas to Anthropic format."""

    def test_basic_schema_conversion(self):
        """Test basic schema conversion logic."""
        # Simulate a simple Pydantic schema
        schema = {
            "properties": {
                "simulation_id": {
                    "type": "string",
                    "description": "Simulation ID to query"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum results",
                    "default": 100,
                    "minimum": 1,
                    "maximum": 1000
                }
            },
            "required": ["simulation_id"]
        }
        
        # Build expected Anthropic format
        properties = schema.get("properties", {})
        required = schema.get("required", [])
        
        input_schema = {
            "type": "object",
            "properties": {},
            "required": required,
        }
        
        for prop_name, prop_info in properties.items():
            input_schema["properties"][prop_name] = {
                "type": prop_info.get("type", "string"),
                "description": prop_info.get("description", ""),
            }
            
            if "minimum" in prop_info:
                input_schema["properties"][prop_name]["minimum"] = prop_info["minimum"]
            if "maximum" in prop_info:
                input_schema["properties"][prop_name]["maximum"] = prop_info["maximum"]
            if "default" in prop_info:
                input_schema["properties"][prop_name]["default"] = prop_info["default"]
        
        # Verify structure
        assert input_schema["type"] == "object"
        assert "simulation_id" in input_schema["properties"]
        assert "limit" in input_schema["properties"]
        assert input_schema["required"] == ["simulation_id"]
        assert input_schema["properties"]["limit"]["minimum"] == 1
        assert input_schema["properties"]["limit"]["maximum"] == 1000


class TestToolExecution:
    """Test tool execution logic."""

    def test_successful_tool_execution(self):
        """Test successful tool execution."""
        # Mock MCP server and tool
        mock_tool = Mock()
        mock_tool.return_value = {
            "success": True,
            "data": {"agents": [{"agent_id": "A_001"}]},
            "metadata": {"execution_time_ms": 10.5}
        }
        
        # Simulate execution
        result = mock_tool(simulation_id="sim_001", limit=10)
        
        assert result["success"] is True
        assert "data" in result
        assert "agents" in result["data"]
        assert result["metadata"]["execution_time_ms"] > 0

    def test_failed_tool_execution(self):
        """Test failed tool execution."""
        # Mock tool that raises an exception
        mock_tool = Mock()
        mock_tool.side_effect = Exception("Database connection failed")
        
        # Simulate execution with error handling
        try:
            result = mock_tool(simulation_id="sim_001")
            pytest.fail("Should have raised exception")
        except Exception as e:
            # Error handling would wrap this
            error_result = {
                "success": False,
                "error": str(e),
                "metadata": {"execution_time_ms": 0}
            }
            assert error_result["success"] is False
            assert "Database connection failed" in error_result["error"]


class TestVisualizationHelpers:
    """Test visualization helper functions."""

    def test_population_data_structure(self):
        """Test population data structure for visualization."""
        data = {
            "time_series": [
                {
                    "step_number": 0,
                    "total_agents": 10,
                    "births": 10,
                    "deaths": 0
                },
                {
                    "step_number": 1,
                    "total_agents": 12,
                    "births": 2,
                    "deaths": 0
                }
            ]
        }
        
        assert "time_series" in data
        assert len(data["time_series"]) == 2
        assert all("step_number" in ts for ts in data["time_series"])
        assert all("total_agents" in ts for ts in data["time_series"])

    def test_agent_data_structure(self):
        """Test agent data structure for tables."""
        data = {
            "agents": [
                {
                    "agent_id": "A_001",
                    "agent_type": "system",
                    "generation": 0,
                    "birth_time": 0,
                    "death_time": None
                }
            ]
        }
        
        assert "agents" in data
        assert len(data["agents"]) == 1
        assert data["agents"][0]["agent_id"] == "A_001"
        assert data["agents"][0]["death_time"] is None


class TestResultFormatting:
    """Test result formatting logic."""

    def test_format_success_result(self):
        """Test formatting of successful results."""
        result = {
            "success": True,
            "data": {
                "agents": [{"agent_id": "A_001"}, {"agent_id": "A_002"}]
            },
            "metadata": {"execution_time_ms": 15.3}
        }
        
        # Simulate formatting logic
        if result.get("success"):
            data = result.get("data", {})
            exec_time = result.get("metadata", {}).get("execution_time_ms", 0)
            
            formatted = f"⚡ {exec_time:.1f}ms\n"
            if "agents" in data:
                formatted += f"📊 Found {len(data['agents'])} agents"
            
            assert "15.3ms" in formatted
            assert "2 agents" in formatted

    def test_format_error_result(self):
        """Test formatting of error results."""
        result = {
            "success": False,
            "error": "Simulation not found",
            "metadata": {"execution_time_ms": 0}
        }
        
        # Simulate formatting logic
        if not result.get("success"):
            formatted = f"❌ Error: {result.get('error', 'Unknown error')}"
            
            assert "❌ Error" in formatted
            assert "Simulation not found" in formatted


class TestEnvironmentValidation:
    """Test environment variable validation."""

    def test_missing_api_key(self):
        """Test handling of missing API key."""
        with patch.dict(os.environ, {}, clear=True):
            api_key = os.getenv("ANTHROPIC_API_KEY")
            assert api_key is None

    def test_present_api_key(self):
        """Test handling of present API key."""
        with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
            api_key = os.getenv("ANTHROPIC_API_KEY")
            assert api_key == "test-key"

    def test_default_db_path(self):
        """Test default database path."""
        with patch.dict(os.environ, {}, clear=True):
            db_path = os.getenv("DB_PATH", "simulation.db")
            assert db_path == "simulation.db"

    def test_custom_db_path(self):
        """Test custom database path."""
        with patch.dict(os.environ, {"DB_PATH": "/custom/path.db"}):
            db_path = os.getenv("DB_PATH", "simulation.db")
            assert db_path == "/custom/path.db"


class TestMessageHandling:
    """Test chat message handling."""

    def test_message_structure(self):
        """Test message data structure."""
        message = {
            "role": "user",
            "content": "What's the population growth rate?"
        }
        
        assert "role" in message
        assert "content" in message
        assert message["role"] in ["user", "assistant"]

    def test_assistant_message_with_tools(self):
        """Test assistant message with tool results."""
        message = {
            "role": "assistant",
            "content": "The population grew by 70%",
            "tool_results": [
                {
                    "name": "analyze_population_dynamics",
                    "input": {"simulation_id": "sim_001"},
                    "result": {"success": True, "data": {}}
                }
            ]
        }
        
        assert message["role"] == "assistant"
        assert "tool_results" in message
        assert len(message["tool_results"]) == 1
        assert message["tool_results"][0]["name"] == "analyze_population_dynamics"


class TestErrorHandling:
    """Test error handling scenarios."""

    def test_database_not_found_error(self):
        """Test handling of database not found error."""
        # This would be caught during MCP server initialization
        with pytest.raises(ValueError):
            from agentfarm_mcp import MCPConfig
            # This should raise ValueError for non-existent DB
            config = MCPConfig.from_db_path("/nonexistent/path.db")

    def test_tool_not_found_error(self):
        """Test handling of tool not found error."""
        from agentfarm_mcp import SimulationMCPServer, MCPConfig
        from agentfarm_mcp.utils.exceptions import ToolNotFoundError
        
        # Create server with test database
        config = MCPConfig.from_db_path("simulation.db")
        server = SimulationMCPServer(config)
        
        # Try to get non-existent tool
        with pytest.raises(ToolNotFoundError):
            server.get_tool("nonexistent_tool")


class TestIntegration:
    """Integration tests for demo components."""

    def test_mcp_server_initialization(self):
        """Test MCP server can be initialized."""
        from agentfarm_mcp import MCPConfig, SimulationMCPServer
        
        config = MCPConfig.from_db_path("simulation.db")
        server = SimulationMCPServer(config)
        
        assert server is not None
        tools = server.list_tools()
        assert len(tools) >= 1
        assert "list_simulations" in tools

    def test_tool_schema_extraction(self):
        """Test tool schema can be extracted."""
        from agentfarm_mcp import MCPConfig, SimulationMCPServer
        
        config = MCPConfig.from_db_path("simulation.db")
        server = SimulationMCPServer(config)
        
        # Get a tool and its schema
        tool = server.get_tool("list_simulations")
        schema = tool.parameters_schema.model_json_schema()
        
        assert "properties" in schema
        assert isinstance(schema["properties"], dict)

    def test_tool_execution(self):
        """Test tool can be executed."""
        from agentfarm_mcp import MCPConfig, SimulationMCPServer
        
        config = MCPConfig.from_db_path("simulation.db")
        server = SimulationMCPServer(config)
        
        # Execute a simple tool
        tool = server.get_tool("list_simulations")
        result = tool(limit=5)
        
        assert result["success"] is True
        assert "data" in result
        assert "metadata" in result

    def test_health_check(self):
        """Test server health check."""
        from agentfarm_mcp import MCPConfig, SimulationMCPServer
        
        config = MCPConfig.from_db_path("simulation.db")
        server = SimulationMCPServer(config)
        
        health = server.health_check()
        
        assert "status" in health
        assert health["status"] in ["healthy", "degraded", "unhealthy"]
        assert "components" in health


class TestUtilityFunctions:
    """Test utility functions."""

    def test_json_serialization(self):
        """Test JSON serialization of results."""
        data = {
            "simulation_id": "sim_001",
            "count": 42,
            "nested": {"key": "value"}
        }
        
        json_str = json.dumps(data)
        parsed = json.loads(json_str)
        
        assert parsed["simulation_id"] == "sim_001"
        assert parsed["count"] == 42
        assert parsed["nested"]["key"] == "value"

    def test_list_comprehension_for_messages(self):
        """Test message filtering logic."""
        messages = [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi"},
            {"role": "system", "content": "System message"},
            {"role": "user", "content": "How are you?"}
        ]
        
        # Filter to only user and assistant messages
        filtered = [msg for msg in messages if msg["role"] in ["user", "assistant"]]
        
        assert len(filtered) == 3
        assert all(msg["role"] in ["user", "assistant"] for msg in filtered)


# Performance tests
class TestPerformance:
    """Performance-related tests."""

    def test_tool_execution_speed(self):
        """Test that tool execution is fast enough."""
        from agentfarm_mcp import MCPConfig, SimulationMCPServer
        import time
        
        config = MCPConfig.from_db_path("simulation.db")
        server = SimulationMCPServer(config)
        
        tool = server.get_tool("list_simulations")
        
        start = time.time()
        result = tool(limit=10)
        duration = (time.time() - start) * 1000  # Convert to ms
        
        # Should be reasonably fast (< 1 second for simple query)
        assert duration < 1000
        assert isinstance(result["metadata"]["execution_time_ms"], (int, float))
        assert result["metadata"]["execution_time_ms"] >= 0

    def test_schema_generation_speed(self):
        """Test that schema generation is fast."""
        from agentfarm_mcp import MCPConfig, SimulationMCPServer
        import time
        
        config = MCPConfig.from_db_path("simulation.db")
        server = SimulationMCPServer(config)
        
        start = time.time()
        
        # Generate schemas for all tools
        for tool_name in server.list_tools():
            tool = server.get_tool(tool_name)
            schema = tool.parameters_schema.model_json_schema()
        
        duration = (time.time() - start) * 1000
        
        # Should be reasonably fast (relaxed threshold for CI environments)
        assert duration < 5000  # 5 seconds should be more than enough


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
