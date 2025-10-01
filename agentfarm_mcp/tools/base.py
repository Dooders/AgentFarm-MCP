"""Base class for all MCP tools."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

from pydantic import BaseModel
from pydantic import ValidationError as PydanticValidationError
from structlog import get_logger

from ..services.cache_service import CacheService
from ..services.database_service import DatabaseService
from ..utils.exceptions import DatabaseError, MCPException

logger = get_logger(__name__)


class ToolBase(ABC):
    """Base class for all MCP tools.

    Provides common functionality:
    - Parameter validation via Pydantic
    - Response formatting
    - Error handling
    - Caching integration
    - Logging
    """

    def __init__(self, db_service: DatabaseService, cache_service: CacheService | Any) -> None:
        """Initialize tool with required services.

        Args:
            db_service: Database service instance
            cache_service: Cache service instance (CacheService or RedisCacheService)
        """
        self.db = db_service
        self.cache = cache_service

    # Abstract properties that subclasses must implement

    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name for registration and logging."""

    @property
    @abstractmethod
    def description(self) -> str:
        """Detailed description for LLM consumption."""

    @property
    @abstractmethod
    def parameters_schema(self) -> type[BaseModel]:
        """Pydantic schema for parameter validation."""

    @abstractmethod
    def execute(self, **params: Any) -> Any:
        """Execute the tool with validated parameters.

        Args:
            **params: Validated parameters from schema

        Returns:
            Tool execution result
        """

    # Concrete methods

    def __call__(self, **params: Any) -> dict[str, Any]:
        """Validate and execute tool with error handling.

        This is the main entry point for tool execution.

        Args:
            **params: Raw parameters from MCP request

        Returns:
            Structured response dictionary
        """
        start_time = datetime.now()

        try:
            # Validate parameters using Pydantic schema
            validated_params = self.parameters_schema(**params)

            # Check cache if enabled
            cache_key = self._get_cache_key(validated_params)
            cached_result = self.cache.get(cache_key)

            if cached_result is not None:
                logger.info("tool_cache_hit", tool=self.name)
                return self._format_response(
                    data=cached_result, from_cache=True, execution_time_ms=0
                )

            # Execute tool
            logger.info("tool_executing", tool=self.name, params=params)
            result = self.execute(**validated_params.model_dump())

            # Cache result
            self.cache.set(cache_key, result)

            # Calculate execution time
            execution_time = (datetime.now() - start_time).total_seconds() * 1000

            logger.info("tool_executed", tool=self.name, execution_time_ms=execution_time)
            return self._format_response(
                data=result, from_cache=False, execution_time_ms=execution_time
            )

        except PydanticValidationError as e:
            logger.warning("tool_validation_error", tool=self.name, error=str(e))
            return self._format_error("ValidationError", str(e), e.errors())

        except DatabaseError as e:
            logger.error("tool_database_error", tool=self.name, error=str(e))
            return self._format_error("DatabaseError", str(e), getattr(e, "details", None))

        except MCPException as e:
            logger.error("tool_mcp_error", tool=self.name, error=str(e), error_type=type(e).__name__)
            return self._format_error(type(e).__name__, str(e), getattr(e, "details", None))

        except (ValueError, TypeError, AttributeError, KeyError, RuntimeError) as e:
            logger.error("tool_unexpected_error", tool=self.name, error=str(e), exc_info=e)
            return self._format_error("UnknownError", str(e))

    def _format_response(
        self, data: Any, from_cache: bool = False, execution_time_ms: float = 0
    ) -> dict[str, Any]:
        """Format successful response.

        Args:
            data: Result data
            from_cache: Whether result came from cache
            execution_time_ms: Execution time in milliseconds

        Returns:
            Formatted response dictionary
        """
        return {
            "success": True,
            "data": data,
            "metadata": {
                "tool": self.name,
                "timestamp": datetime.now().isoformat(),
                "from_cache": from_cache,
                "execution_time_ms": execution_time_ms,
            },
            "error": None,
        }

    def _format_error(
        self, error_type: str, message: str, details: Any | None = None
    ) -> dict[str, Any]:
        """Format error response.

        Args:
            error_type: Type of error
            message: Error message
            details: Optional additional error details

        Returns:
            Formatted error response
        """
        error_dict: dict[str, Any] = {
            "type": error_type,
            "message": message,
        }

        if details:
            error_dict["details"] = details

        return {
            "success": False,
            "data": None,
            "metadata": {
                "tool": self.name,
                "timestamp": datetime.now().isoformat(),
            },
            "error": error_dict,
        }

    def _get_cache_key(self, params: BaseModel) -> str:
        """Generate cache key from parameters.

        Args:
            params: Validated parameters

        Returns:
            Cache key string
        """
        return CacheService.generate_key(self.name, params.model_dump())

    def get_schema(self) -> dict[str, Any]:
        """Get tool schema for MCP registration.

        Returns:
            Tool schema dictionary for FastMCP
        """
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters_schema.model_json_schema(),
        }
