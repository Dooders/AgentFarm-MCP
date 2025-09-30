"""Command-line interface for MCP server."""

import argparse
import sys

from mcp_server.config import CacheConfig, MCPConfig
from mcp_server.server import SimulationMCPServer
from mcp_server.utils.logging import setup_logging


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="FastMCP Server for Simulation Database Analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with database path
  %(prog)s --db-path /path/to/simulation.db
  
  # Run with config file
  %(prog)s --config config.yaml
  
  # Run with custom log level
  %(prog)s --db-path simulation.db --log-level DEBUG
  
  # Disable caching
  %(prog)s --db-path simulation.db --no-cache
  
  # List available tools
  %(prog)s --db-path simulation.db --list-tools
        """,
    )

    parser.add_argument(
        "--db-path", type=str, help="Path to simulation database (required unless using --config)"
    )

    parser.add_argument("--config", type=str, help="Path to configuration YAML file (optional)")

    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Logging level (default: INFO)",
    )

    parser.add_argument(
        "--log-file", type=str, help="Optional log file path (logs to stdout if not specified)"
    )

    parser.add_argument("--no-cache", action="store_true", help="Disable caching")

    parser.add_argument("--list-tools", action="store_true", help="List available tools and exit")

    args = parser.parse_args()

    # Setup logging first
    setup_logging(log_level=args.log_level, log_file=args.log_file)

    # Validate arguments
    if not args.config and not args.db_path:
        parser.error("Either --db-path or --config must be specified")

    try:
        # Load configuration
        if args.config:
            config = MCPConfig.from_yaml(args.config)
        else:
            config = MCPConfig.from_db_path(args.db_path)

        # Override cache setting if requested
        if args.no_cache:
            config.cache = CacheConfig(enabled=False)

        # Create server
        server = SimulationMCPServer(config)

        # List tools if requested
        if args.list_tools:
            print("\nAvailable Tools:")
            print("=" * 60)
            for tool_name in sorted(server.list_tools()):
                tool = server.get_tool(tool_name)
                print(f"\n{tool_name}")
                print(f"  {tool.description.strip()[:100]}...")
            print("\n" + "=" * 60)
            print(f"Total: {len(server.list_tools())} tools")
            sys.exit(0)

        # Run server
        print(f"\nStarting MCP server with {len(server.list_tools())} tools...")
        print(f"Database: {config.database.path}")
        print(f"Cache: {'enabled' if config.cache.enabled else 'disabled'}")
        print(f"Log level: {args.log_level}")
        print("\nPress Ctrl+C to stop the server.\n")

        server.run()

    except KeyboardInterrupt:
        print("\n\nShutting down server...")
        sys.exit(0)
    except (ValueError, FileNotFoundError, OSError) as e:
        print(f"\nError: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
