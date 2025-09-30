"""Main MCP server implementation."""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP

from .config import MCPConfig
from .services.cache_service import CacheService
from .services.database_service import DatabaseService
from .tools.advanced_tools import BuildAgentLineageTool, GetAgentLifecycleTool
from .tools.analysis_tools import (
    AnalyzeAgentPerformanceTool,
    AnalyzePopulationDynamicsTool,
    AnalyzeReproductionTool,
    AnalyzeResourceEfficiencyTool,
    AnalyzeSocialPatternsTool,
    AnalyzeSurvivalRatesTool,
    IdentifyCriticalEventsTool,
)
from .tools.base import ToolBase
from .tools.comparison_tools import (
    CompareGenerationsTool,
    CompareParametersTool,
    CompareSimulationsTool,
    RankConfigurationsTool,
)
from .tools.health_tools import HealthCheckTool, SystemInfoTool
from .tools.metadata_tools import (
    GetExperimentInfoTool,
    GetSimulationInfoTool,
    ListExperimentsTool,
    ListSimulationsTool,
)
from .tools.query_tools import (
    GetSimulationMetricsTool,
    QueryActionsTool,
    QueryAgentsTool,
    QueryInteractionsTool,
    QueryResourcesTool,
    QueryStatesTool,
)
from .utils.exceptions import ToolNotFoundError

logger = logging.getLogger(__name__)


class SimulationMCPServer:
    """Main MCP server for simulation database analysis."""

    def __init__(self, config: MCPConfig):
        """Initialize MCP server.

        Args:
            config: Server configuration
        """
        self.config = config

        # Initialize services
        self.db_service = DatabaseService(config.database)
        self.cache_service = CacheService(config.cache)

        # Initialize FastMCP
        self.mcp = FastMCP("simulation-analysis")

        # Tool registry
        self._tools: Dict[str, ToolBase] = {}

        # Register all tools
        self._register_tools()

        logger.info("MCP server initialized")

    def _register_tools(self):
        """Register all MCP tools."""
        # Define all tools to register
        tool_classes = [
            # Metadata tools
            GetSimulationInfoTool,
            ListSimulationsTool,
            GetExperimentInfoTool,
            ListExperimentsTool,
            # Query tools
            QueryAgentsTool,
            QueryActionsTool,
            QueryStatesTool,
            QueryResourcesTool,
            QueryInteractionsTool,
            GetSimulationMetricsTool,
            # Analysis tools
            AnalyzePopulationDynamicsTool,
            AnalyzeSurvivalRatesTool,
            AnalyzeResourceEfficiencyTool,
            AnalyzeAgentPerformanceTool,
            IdentifyCriticalEventsTool,
            AnalyzeSocialPatternsTool,
            AnalyzeReproductionTool,
            # Comparison tools
            CompareSimulationsTool,
            CompareParametersTool,
            RankConfigurationsTool,
            CompareGenerationsTool,
            # Advanced tools
            BuildAgentLineageTool,
            GetAgentLifecycleTool,
            # Health and monitoring tools
            HealthCheckTool,
            SystemInfoTool,
        ]

        # Instantiate and register each tool
        for tool_class in tool_classes:
            tool = tool_class(self.db_service, self.cache_service)
            self._tools[tool.name] = tool

            # Register with FastMCP
            self._register_tool_with_mcp(tool)

            logger.info("Registered tool: %s", tool.name)

    def _register_tool_with_mcp(self, tool: ToolBase):
        """Register a tool with FastMCP.

        Args:
            tool: Tool instance to register
        """
        # Get the parameter schema to create proper function signature
        schema = tool.parameters_schema
        schema_fields = schema.model_fields

        # Create a function with specific parameters based on the schema
        def create_tool_function(tool_instance, fields):
            # Create function signature dynamically
            import inspect
            from typing import get_type_hints

            # Build parameter list for the function signature
            params = []
            for field_name, field_info in fields.items():
                # Get the default value
                default = field_info.default if field_info.default is not ... else None
                if default is None and field_info.default_factory is not None:
                    default = field_info.default_factory()

                # Add parameter to signature
                if default is ...:
                    # Required parameter
                    params.append(
                        inspect.Parameter(field_name, inspect.Parameter.POSITIONAL_OR_KEYWORD)
                    )
                else:
                    # Optional parameter with default
                    params.append(
                        inspect.Parameter(
                            field_name, inspect.Parameter.POSITIONAL_OR_KEYWORD, default=default
                        )
                    )

            # Create function signature
            sig = inspect.Signature(params)

            def tool_func(*args, **kwargs):
                """Tool function with proper signature."""
                # Bind arguments to signature
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()

                # Call the tool with the bound arguments
                return tool_instance(**bound_args.arguments)

            # Set the signature on the function
            tool_func.__signature__ = sig
            tool_func.__name__ = tool_instance.name
            tool_func.__doc__ = tool_instance.description

            return tool_func

        # Create the tool function with proper signature
        tool_func = create_tool_function(tool, schema_fields)

        # Register with FastMCP
        self.mcp.tool()(tool_func)

    def get_tool(self, name: str) -> Optional[ToolBase]:
        """Get tool by name.

        Args:
            name: Tool name

        Returns:
            Tool instance or None

        Raises:
            ToolNotFoundError: If tool doesn't exist
        """
        tool = self._tools.get(name)
        if tool is None:
            raise ToolNotFoundError(name)
        return tool

    def list_tools(self) -> List[str]:
        """List all registered tools.

        Returns:
            List of tool names
        """
        return list(self._tools.keys())

    def get_tool_schemas(self) -> List[Dict]:
        """Get schemas for all registered tools.

        Returns:
            List of tool schema dictionaries
        """
        return [tool.get_schema() for tool in self._tools.values()]

    def get_cache_stats(self) -> dict:
        """Get cache statistics.

        Returns:
            Cache statistics dictionary
        """
        return self.cache_service.get_stats()

    def clear_cache(self):
        """Clear all cached data."""
        self.cache_service.clear()
        logger.info("Cache cleared")

    def run(self, **kwargs):
        """Start the MCP server.

        Args:
            **kwargs: Additional arguments for FastMCP.run()
        """
        logger.info("Starting MCP server with %d tools", len(self._tools))
        self.mcp.run(**kwargs)

    def health_check(self) -> Dict[str, Any]:
        """Check server health status.

        Returns:
            Health status dictionary with component status

        Example:
            >>> health = server.health_check()
            >>> print(f"Status: {health['status']}")
        """
        health_info = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "components": {},
        }

        # Check database connection
        try:
            with self.db_service.get_session() as session:
                from sqlalchemy import text

                session.execute(text("SELECT 1"))
            health_info["components"]["database"] = "connected"
        except (ConnectionError, TimeoutError, OSError) as e:
            health_info["components"]["database"] = f"error: {str(e)}"
            health_info["status"] = "unhealthy"

        # Check cache status
        try:
            stats = self.cache_service.get_stats()
            health_info["components"]["cache"] = {
                "enabled": stats["enabled"],
                "size": stats["size"],
                "hit_rate": stats["hit_rate"],
            }
        except (ConnectionError, TimeoutError, OSError) as e:
            health_info["components"]["cache"] = f"error: {str(e)}"

        # Tool registry status
        health_info["components"]["tools"] = {
            "registered": len(self._tools),
            "expected": 25,  # Updated to include health tools
        }

        # Overall health
        if health_info["components"]["tools"]["registered"] != 25:
            health_info["status"] = "degraded"

        return health_info

    def close(self):
        """Shutdown server and cleanup resources."""
        self.db_service.close()
        logger.info("MCP server shutdown complete")
