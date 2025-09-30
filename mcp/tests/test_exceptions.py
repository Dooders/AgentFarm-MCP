"""Unit tests for custom exceptions."""

import pytest

from mcp.utils.exceptions import (
    CacheError,
    ConfigurationError,
    DatabaseError,
    ExperimentNotFoundError,
    MCPException,
    QueryTimeoutError,
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


def test_exception_inheritance():
    """Test exception inheritance hierarchy."""
    # DatabaseError inherits from MCPException
    assert issubclass(DatabaseError, MCPException)

    # QueryTimeoutError inherits from DatabaseError
    assert issubclass(QueryTimeoutError, DatabaseError)
    assert issubclass(QueryTimeoutError, MCPException)

    # SimulationNotFoundError inherits from DatabaseError
    assert issubclass(SimulationNotFoundError, DatabaseError)


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