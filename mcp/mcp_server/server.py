"""Main MCP server implementation."""

import logging
from typing import Dict, List, Optional

from fastmcp import FastMCP

from mcp_server.config import MCPConfig
from mcp_server.services.cache_service import CacheService
from mcp_server.services.database_service import DatabaseService
from mcp_server.tools.base import ToolBase
from mcp_server.tools.metadata_tools import (
    GetExperimentInfoTool,
    GetSimulationInfoTool,
    ListExperimentsTool,
    ListSimulationsTool,
)
from mcp_server.utils.exceptions import ToolNotFoundError

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
        ]

        # Instantiate and register each tool
        for tool_class in tool_classes:
            tool = tool_class(self.db_service, self.cache_service)
            self._tools[tool.name] = tool

            # Register with FastMCP
            self._register_tool_with_mcp(tool)

            logger.info(f"Registered tool: {tool.name}")

    def _register_tool_with_mcp(self, tool: ToolBase):
        """Register a tool with FastMCP.

        Args:
            tool: Tool instance to register
        """
        # Create a uniquely named function for each tool
        # This avoids FastMCP warnings about duplicate tool names
        def make_tool_wrapper(t):
            def wrapper(request: t.parameters_schema) -> dict:  # type: ignore
                """Execute the tool."""
                return t(**request.model_dump())
            wrapper.__name__ = t.name
            wrapper.__doc__ = t.description
            return wrapper
        
        tool_wrapper = make_tool_wrapper(tool)
        self.mcp.tool()(tool_wrapper)

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
        logger.info(f"Starting MCP server with {len(self._tools)} tools")
        self.mcp.run(**kwargs)

    def close(self):
        """Shutdown server and cleanup resources."""
        self.db_service.close()
        logger.info("MCP server shutdown complete")