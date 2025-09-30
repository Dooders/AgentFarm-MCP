"""Unit tests for custom exceptions."""

import pytest

from agentfarm_mcp.utils.exceptions import (
    AgentNotFoundError,
    CacheError,
    ConfigurationError,
    ConnectionError,
    DatabaseError,
    ExperimentNotFoundError,
    MCPException,
    PermissionError,
    QueryExecutionError,
    QueryTimeoutError,
    ResourceLimitError,
    ResultTooLargeError,
    SimulationNotFoundError,
    ToolNotFoundError,
    ValidationError,
)


def test_mcp_exception_basic():
    """Test base MCPException."""
    exc = MCPException("Test error")

    assert str(exc) == "Test error"
    assert exc.message == "Test error"
    assert exc.details == {}


def test_mcp_exception_with_details():
    """Test MCPException with details."""
    exc = MCPException("Test error", details={"key": "value"})

    assert exc.details == {"key": "value"}


def test_database_error():
    """Test DatabaseError."""
    exc = DatabaseError("Database connection failed")

    assert isinstance(exc, MCPException)
    assert str(exc) == "Database connection failed"


def test_validation_error():
    """Test ValidationError."""
    exc = ValidationError("Invalid parameter")

    assert isinstance(exc, MCPException)
    assert str(exc) == "Invalid parameter"


def test_query_timeout_error():
    """Test QueryTimeoutError with timeout info."""
    exc = QueryTimeoutError(timeout=30, query="SELECT * FROM agents")

    assert isinstance(exc, DatabaseError)
    assert exc.details["timeout"] == 30
    assert exc.details["query"] == "SELECT * FROM agents"
    assert "30 seconds" in str(exc)


def test_query_timeout_error_without_query():
    """Test QueryTimeoutError without query string."""
    exc = QueryTimeoutError(timeout=30)

    assert exc.details["timeout"] == 30
    assert "query" not in exc.details


def test_simulation_not_found_error():
    """Test SimulationNotFoundError."""
    exc = SimulationNotFoundError("sim_123")

    assert isinstance(exc, DatabaseError)
    assert exc.simulation_id == "sim_123"
    assert exc.details["simulation_id"] == "sim_123"
    assert "sim_123" in str(exc)


def test_experiment_not_found_error():
    """Test ExperimentNotFoundError."""
    exc = ExperimentNotFoundError("exp_456")

    assert isinstance(exc, DatabaseError)
    assert exc.experiment_id == "exp_456"
    assert exc.details["experiment_id"] == "exp_456"
    assert "exp_456" in str(exc)


def test_result_too_large_error():
    """Test ResultTooLargeError."""
    exc = ResultTooLargeError(size=15000, max_size=10000)

    assert isinstance(exc, MCPException)
    assert exc.size == 15000
    assert exc.max_size == 10000
    assert exc.details["size"] == 15000
    assert exc.details["max_size"] == 10000
    assert "15000" in str(exc)
    assert "10000" in str(exc)


def test_cache_error():
    """Test CacheError."""
    exc = CacheError("Cache operation failed")

    assert isinstance(exc, MCPException)
    assert str(exc) == "Cache operation failed"


def test_tool_not_found_error():
    """Test ToolNotFoundError."""
    exc = ToolNotFoundError("nonexistent_tool")

    assert isinstance(exc, MCPException)
    assert exc.tool_name == "nonexistent_tool"
    assert exc.details["tool_name"] == "nonexistent_tool"
    assert "nonexistent_tool" in str(exc)


def test_configuration_error():
    """Test ConfigurationError."""
    exc = ConfigurationError("Invalid configuration")

    assert isinstance(exc, MCPException)
    assert str(exc) == "Invalid configuration"


def test_agent_not_found_error():
    """Test AgentNotFoundError."""
    exc = AgentNotFoundError("agent_123", "sim_456")

    assert isinstance(exc, DatabaseError)
    assert exc.agent_id == "agent_123"
    assert exc.simulation_id == "sim_456"
    assert exc.details["agent_id"] == "agent_123"
    assert exc.details["simulation_id"] == "sim_456"
    assert "agent_123" in str(exc)
    assert "sim_456" in str(exc)


def test_connection_error():
    """Test ConnectionError."""
    exc = ConnectionError("Database connection failed", database_type="sqlite")

    assert isinstance(exc, DatabaseError)
    assert exc.database_type == "sqlite"
    assert exc.details["database_type"] == "sqlite"
    assert "sqlite" in str(exc)


def test_connection_error_with_details():
    """Test ConnectionError with additional details."""
    exc = ConnectionError(
        "Connection timeout",
        database_type="postgresql",
        details={"host": "localhost", "port": 5432},
    )

    assert exc.database_type == "postgresql"
    assert exc.details["database_type"] == "postgresql"
    assert exc.details["host"] == "localhost"
    assert exc.details["port"] == 5432


def test_query_execution_error():
    """Test QueryExecutionError."""
    exc = QueryExecutionError("Query failed", query="SELECT * FROM agents")

    assert isinstance(exc, DatabaseError)
    assert exc.query == "SELECT * FROM agents"
    assert exc.details["query"] == "SELECT * FROM agents"
    assert "SELECT * FROM agents" in str(exc)


def test_query_execution_error_with_operation():
    """Test QueryExecutionError with operation context."""
    exc = QueryExecutionError(
        "Query failed", query="SELECT * FROM agents", details={"operation": "agent_lookup"}
    )

    assert exc.query == "SELECT * FROM agents"
    assert exc.details["query"] == "SELECT * FROM agents"
    assert exc.details["operation"] == "agent_lookup"


def test_permission_error():
    """Test PermissionError."""
    exc = PermissionError("Access denied", operation="write")

    assert isinstance(exc, MCPException)
    assert exc.operation == "write"
    assert exc.details["operation"] == "write"
    assert "write" in str(exc)


def test_permission_error_with_details():
    """Test PermissionError with additional details."""
    exc = PermissionError(
        "Access denied", operation="delete", details={"resource": "simulation", "user": "guest"}
    )

    assert exc.operation == "delete"
    assert exc.details["operation"] == "delete"
    assert exc.details["resource"] == "simulation"
    assert exc.details["user"] == "guest"


def test_resource_limit_error():
    """Test ResourceLimitError."""
    exc = ResourceLimitError("Memory limit exceeded", limit_type="memory", limit_value="1GB")

    assert isinstance(exc, MCPException)
    assert exc.limit_type == "memory"
    assert exc.limit_value == "1GB"
    assert exc.details["limit_type"] == "memory"
    assert exc.details["limit_value"] == "1GB"
    assert "memory" in str(exc)
    assert "1GB" in str(exc)


def test_resource_limit_error_with_details():
    """Test ResourceLimitError with additional details."""
    exc = ResourceLimitError(
        "CPU limit exceeded",
        limit_type="cpu",
        limit_value="80%",
        details={"current_usage": "85%", "process": "analysis_tool"},
    )

    assert exc.limit_type == "cpu"
    assert exc.limit_value == "80%"
    assert exc.details["limit_type"] == "cpu"
    assert exc.details["limit_value"] == "80%"
    assert exc.details["current_usage"] == "85%"
    assert exc.details["process"] == "analysis_tool"


def test_exception_inheritance():
    """Test exception inheritance hierarchy."""
    # DatabaseError inherits from MCPException
    assert issubclass(DatabaseError, MCPException)

    # QueryTimeoutError inherits from DatabaseError
    assert issubclass(QueryTimeoutError, DatabaseError)
    assert issubclass(QueryTimeoutError, MCPException)

    # SimulationNotFoundError inherits from DatabaseError
    assert issubclass(SimulationNotFoundError, DatabaseError)

    # New exceptions inherit correctly
    assert issubclass(AgentNotFoundError, DatabaseError)
    assert issubclass(ConnectionError, DatabaseError)
    assert issubclass(QueryExecutionError, DatabaseError)
    assert issubclass(PermissionError, MCPException)
    assert issubclass(ResourceLimitError, MCPException)


def test_exceptions_are_catchable():
    """Test that exceptions can be caught properly."""
    # Catch as MCPException
    try:
        raise SimulationNotFoundError("sim_999")
    except MCPException as e:
        assert isinstance(e, SimulationNotFoundError)

    # Catch as DatabaseError
    try:
        raise QueryTimeoutError(timeout=30)
    except DatabaseError as e:
        assert isinstance(e, QueryTimeoutError)

    # Catch new exceptions
    try:
        raise AgentNotFoundError("agent_123", "sim_456")
    except DatabaseError as e:
        assert isinstance(e, AgentNotFoundError)

    try:
        raise ConnectionError("Connection failed", database_type="sqlite")
    except DatabaseError as e:
        assert isinstance(e, ConnectionError)

    try:
        raise PermissionError("Access denied", operation="write")
    except MCPException as e:
        assert isinstance(e, PermissionError)
