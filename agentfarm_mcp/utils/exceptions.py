"""Custom exceptions for MCP server."""

from typing import Any, Dict, Optional


class MCPException(Exception):
    """Base exception for MCP server.

    All custom exceptions should inherit from this class.
    """

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """Initialize exception with message and optional details.

        Args:
            message: Error message
            details: Optional dictionary with additional error context
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}


class DatabaseError(MCPException):
    """Database-related errors.

    Raised when database operations fail, including connection issues,
    query errors, or transaction failures.
    """


class ValidationError(MCPException):
    """Parameter validation errors.

    Raised when input parameters fail validation checks.
    """


class QueryTimeoutError(DatabaseError):
    """Query exceeded timeout limit.

    Raised when a database query takes longer than the configured timeout.
    """

    def __init__(self, timeout: int, query: Optional[str] = None):
        """Initialize with timeout information.

        Args:
            timeout: Timeout duration in seconds
            query: Optional query that timed out
        """
        message = f"Query exceeded timeout of {timeout} seconds"
        details = {"timeout": timeout}
        if query:
            details["query"] = query
        super().__init__(message, details)


class SimulationNotFoundError(DatabaseError):
    """Requested simulation does not exist.

    Raised when attempting to access a simulation that doesn't exist
    in the database.
    """

    def __init__(self, simulation_id: str):
        """Initialize with simulation ID.

        Args:
            simulation_id: ID of the simulation that was not found
        """
        self.simulation_id = simulation_id
        message = f"Simulation not found: {simulation_id}"
        details = {"simulation_id": simulation_id}
        super().__init__(message, details)


class ExperimentNotFoundError(DatabaseError):
    """Requested experiment does not exist.

    Raised when attempting to access an experiment that doesn't exist
    in the database.
    """

    def __init__(self, experiment_id: str):
        """Initialize with experiment ID.

        Args:
            experiment_id: ID of the experiment that was not found
        """
        self.experiment_id = experiment_id
        message = f"Experiment not found: {experiment_id}"
        details = {"experiment_id": experiment_id}
        super().__init__(message, details)


class ResultTooLargeError(MCPException):
    """Query result exceeds maximum size.

    Raised when a query would return more results than the configured limit.
    """

    def __init__(self, size: int, max_size: int):
        """Initialize with size information.

        Args:
            size: Actual result size
            max_size: Maximum allowed size
        """
        self.size = size
        self.max_size = max_size
        message = f"Result size ({size}) exceeds maximum ({max_size}). Use pagination."
        details = {"size": size, "max_size": max_size}
        super().__init__(message, details)


class CacheError(MCPException):
    """Cache-related errors.

    Raised when cache operations fail.
    """


class ToolNotFoundError(MCPException):
    """Requested tool does not exist.

    Raised when attempting to access a tool that hasn't been registered.
    """

    def __init__(self, tool_name: str):
        """Initialize with tool name.

        Args:
            tool_name: Name of the tool that was not found
        """
        self.tool_name = tool_name
        message = f"Tool not found: {tool_name}"
        details = {"tool_name": tool_name}
        super().__init__(message, details)


class ConfigurationError(MCPException):
    """Configuration-related errors.

    Raised when configuration is invalid or missing required values.
    """
