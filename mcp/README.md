# MCP Simulation Analysis Server

FastMCP server for querying and analyzing simulation databases with LLM agents.

## Quick Start

```bash
# Install
pip install -e .

# Run server
mcp-server --db-path /path/to/simulation.db

# With config file
mcp-server --config config.yaml
```

## Features

- 20+ specialized tools for simulation analysis
- Read-only database access for safety
- Smart caching for performance
- Comprehensive error handling
- Built-in validation via Pydantic schemas

## Documentation

See [docs/](docs/) for full documentation.

## Configuration

Copy `.env.example` to `.env` and configure:
- Database path
- Cache settings
- Query limits
- Logging level

## Development

```bash
# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=mcp_server --cov-report=html
```

## License

MIT