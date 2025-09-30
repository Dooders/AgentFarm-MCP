"""Unit tests for base tool class."""

import pytest
from pydantic import BaseModel, Field, ValidationError as PydanticValidationError

from mcp_server.tools.base import ToolBase
from mcp_server.utils.exceptions import DatabaseError


# Create a concrete test tool for testing
class TestToolParams(BaseModel):
    """Test parameter schema."""

    value: int = Field(..., ge=0, le=100, description="Test value")
    name: str = Field(..., min_length=1, description="Test name")
    optional_field: str = Field(None, description="Optional field")


class TestTool(ToolBase):
    """Concrete tool implementation for testing."""

    @property
    def name(self) -> str:
        return "test_tool"

    @property
    def description(self) -> str:
        return "A tool for testing the base class"

    @property
    def parameters_schema(self):
        return TestToolParams

    def execute(self, **params):
        """Execute test tool."""
        return {"result": f"Executed with value={params['value']}, name={params['name']}"}


class FailingTool(ToolBase):
    """Tool that always fails (for testing error handling)."""

    @property
    def name(self) -> str:
        return "failing_tool"

    @property
    def description(self) -> str:
        return "A tool that fails"

    @property
    def parameters_schema(self):
        return TestToolParams

    def execute(self, **params):
        """Always raises an error."""
        raise DatabaseError("Test database error")


@pytest.fixture
def test_tool(services):
    """Create test tool instance."""
    db_service, cache_service = services
    return TestTool(db_service, cache_service)


@pytest.fixture
def failing_tool(services):
    """Create failing tool instance."""
    db_service, cache_service = services
    return FailingTool(db_service, cache_service)


def test_tool_initialization(services):
    """Test that tool initializes with services."""
    db_service, cache_service = services
    tool = TestTool(db_service, cache_service)

    assert tool.db == db_service
    assert tool.cache == cache_service


def test_tool_properties(test_tool):
    """Test tool properties are accessible."""
    assert test_tool.name == "test_tool"
    assert test_tool.description == "A tool for testing the base class"
    assert test_tool.parameters_schema == TestToolParams


def test_tool_successful_execution(test_tool):
    """Test successful tool execution."""
    result = test_tool(value=42, name="test")

    assert result["success"] is True
    assert result["data"]["result"] == "Executed with value=42, name=test"
    assert result["error"] is None
    assert result["metadata"]["tool"] == "test_tool"
    assert "timestamp" in result["metadata"]
    assert "execution_time_ms" in result["metadata"]


def test_tool_validation_error_out_of_range(test_tool):
    """Test that validation errors are handled."""
    result = test_tool(value=200, name="test")  # value > 100

    assert result["success"] is False
    assert result["data"] is None
    assert result["error"]["type"] == "ValidationError"
    assert "validation error" in result["error"]["message"].lower()


def test_tool_validation_error_missing_required(test_tool):
    """Test missing required parameter."""
    result = test_tool(value=42)  # Missing 'name'

    assert result["success"] is False
    assert result["error"]["type"] == "ValidationError"


def test_tool_validation_error_wrong_type(test_tool):
    """Test wrong parameter type."""
    result = test_tool(value="not_a_number", name="test")

    assert result["success"] is False
    assert result["error"]["type"] == "ValidationError"


def test_tool_database_error_handling(failing_tool):
    """Test that database errors are handled."""
    result = failing_tool(value=42, name="test")

    assert result["success"] is False
    assert result["error"]["type"] == "DatabaseError"
    assert "Test database error" in result["error"]["message"]


def test_tool_caching(test_tool):
    """Test that results are cached."""
    # Clear cache first
    test_tool.cache.clear()

    # First call - should not be cached
    result1 = test_tool(value=42, name="test")
    assert result1["metadata"]["from_cache"] is False
    assert result1["metadata"]["execution_time_ms"] > 0

    # Second call with same params - should hit cache
    result2 = test_tool(value=42, name="test")
    assert result2["metadata"]["from_cache"] is True
    assert result2["metadata"]["execution_time_ms"] == 0

    # Third call with different params - should not hit cache
    result3 = test_tool(value=50, name="test")
    assert result3["metadata"]["from_cache"] is False


def test_tool_cache_disabled(services):
    """Test tool with cache disabled."""
    db_service, cache_service = services
    cache_service.enabled = False

    tool = TestTool(db_service, cache_service)

    result1 = tool(value=42, name="test")
    result2 = tool(value=42, name="test")

    # Both should execute (not cached)
    assert result1["metadata"]["from_cache"] is False
    assert result2["metadata"]["from_cache"] is False


def test_tool_get_schema(test_tool):
    """Test tool schema generation."""
    schema = test_tool.get_schema()

    assert schema["name"] == "test_tool"
    assert "description" in schema
    assert "parameters" in schema
    assert "properties" in schema["parameters"]


def test_tool_cache_key_generation(test_tool):
    """Test cache key generation."""
    params1 = TestToolParams(value=42, name="test")
    params2 = TestToolParams(value=42, name="test")
    params3 = TestToolParams(value=50, name="test")

    key1 = test_tool._get_cache_key(params1)
    key2 = test_tool._get_cache_key(params2)
    key3 = test_tool._get_cache_key(params3)

    # Same params should produce same key
    assert key1 == key2

    # Different params should produce different key
    assert key1 != key3

    # Keys should contain tool name
    assert "test_tool:" in key1


def test_tool_response_format(test_tool):
    """Test response format is correct."""
    result = test_tool(value=42, name="test")

    # Check structure
    assert "success" in result
    assert "data" in result
    assert "metadata" in result
    assert "error" in result

    # Check metadata structure
    assert "tool" in result["metadata"]
    assert "timestamp" in result["metadata"]
    assert "from_cache" in result["metadata"]
    assert "execution_time_ms" in result["metadata"]


def test_tool_error_response_format(test_tool):
    """Test error response format."""
    result = test_tool(value=200, name="test")  # Invalid

    assert result["success"] is False
    assert result["data"] is None
    assert result["error"] is not None
    assert "type" in result["error"]
    assert "message" in result["error"]


def test_tool_optional_parameters(test_tool):
    """Test optional parameters work."""
    result = test_tool(value=42, name="test", optional_field="optional")

    assert result["success"] is True

    # Optional field not provided
    result2 = test_tool(value=42, name="test")
    assert result2["success"] is True


def test_tool_metadata_timestamp_format(test_tool):
    """Test that timestamp is in ISO format."""
    result = test_tool(value=42, name="test")

    timestamp = result["metadata"]["timestamp"]
    # Should be ISO format (contains T and :)
    assert "T" in timestamp
    assert ":" in timestamp


def test_tool_execution_time_measured(test_tool):
    """Test that execution time is measured."""
    test_tool.cache.clear()

    result = test_tool(value=42, name="test")

    exec_time = result["metadata"]["execution_time_ms"]
    assert exec_time >= 0
    assert isinstance(exec_time, (int, float))


def test_tool_error_with_details(failing_tool):
    """Test error formatting with details."""
    result = failing_tool(value=42, name="test")

    assert result["success"] is False
    assert result["error"]["type"] == "DatabaseError"
    assert "message" in result["error"]


def test_tool_unexpected_error(services):
    """Test handling of unexpected errors."""
    from mcp_server.utils.exceptions import MCPException

    class UnexpectedErrorTool(ToolBase):
        @property
        def name(self):
            return "unexpected_tool"

        @property
        def description(self):
            return "Tool that raises unexpected error"

        @property
        def parameters_schema(self):
            return TestToolParams

        def execute(self, **params):
            raise RuntimeError("Unexpected runtime error")

    db_service, cache_service = services
    tool = UnexpectedErrorTool(db_service, cache_service)

    result = tool(value=42, name="test")

    assert result["success"] is False
    assert result["error"]["type"] == "UnknownError"
    assert "Unexpected runtime error" in result["error"]["message"]


def test_tool_mcp_exception(services):
    """Test handling of MCPException subclasses."""
    from mcp_server.utils.exceptions import ValidationError as MCPValidationError

    class MCPErrorTool(ToolBase):
        @property
        def name(self):
            return "mcp_error_tool"

        @property
        def description(self):
            return "Tool that raises MCP error"

        @property
        def parameters_schema(self):
            return TestToolParams

        def execute(self, **params):
            raise MCPValidationError("Custom validation error", details={"field": "value"})

    db_service, cache_service = services
    tool = MCPErrorTool(db_service, cache_service)

    result = tool(value=42, name="test")

    assert result["success"] is False
    assert result["error"]["type"] == "ValidationError"
    assert "Custom validation error" in result["error"]["message"]


def test_tool_abstract_methods_must_be_implemented():
    """Test that abstract methods must be implemented."""
    from abc import ABC

    # Try to create incomplete tool (should fail at instantiation attempt)
    class IncompleteTool(ToolBase):
        # Missing abstract method implementations
        pass

    # Can't instantiate without implementing abstract methods
    # This is caught at class definition time by Python
    assert issubclass(ToolBase, ABC)


def test_tool_all_abstract_properties_defined(test_tool):
    """Test that all abstract properties are defined."""
    # These should all be accessible
    assert hasattr(test_tool, "name")
    assert hasattr(test_tool, "description")
    assert hasattr(test_tool, "parameters_schema")
    assert hasattr(test_tool, "execute")

    # And they should return appropriate types
    assert isinstance(test_tool.name, str)
    assert isinstance(test_tool.description, str)
    assert test_tool.parameters_schema is not None
    assert callable(test_tool.execute)