# 🚀 Quick Start Guide - Improved Codebase

This guide helps you get started with the improved AgentFarm MCP codebase.

## 📋 Prerequisites

- Python 3.8+
- Docker (optional, for PostgreSQL/Redis)
- Git

## 🎯 Quick Setup (5 minutes)

### 1. Clone and Install

```bash
# Install dependencies and setup development environment
make setup

# Or manually:
pip install -r requirements.txt
pre-commit install
```

### 2. Configure Environment

```bash
# Copy development config
cp agentfarm_mcp/config.example.dev.yaml config.dev.yaml

# Edit if needed (default settings work for SQLite)
vim config.dev.yaml
```

### 3. Verify Installation

```bash
# Run tests
make test

# Run type checking
make type-check

# Run linting
make lint
```

## 🏃 Running the Server

### Development Mode (SQLite + In-Memory Cache)

```bash
# Using the Makefile
make run-dev

# Or directly
python -m agentfarm_mcp.cli --config config.dev.yaml
```

### With Docker Services (PostgreSQL + Redis)

```bash
# Start PostgreSQL and Redis
make docker-up

# Configure for PostgreSQL (edit config.dev.yaml):
database:
  database_type: "postgresql"
  host: "localhost"
  port: 5432
  database: "agentfarm_simulations"
  username: "agentfarm"
  password: "devpassword"

cache:
  backend: "redis"
  redis_host: "localhost"
  redis_port: 6379

# Run server
make run-dev
```

## 🧪 Development Workflow

### Code Quality Checks

```bash
# Format code
make format

# Run linting with auto-fix
make lint

# Type checking
make type-check

# Run all checks (format, lint, type-check, test)
make dev

# Run pre-commit hooks manually
make pre-commit
```

### Testing

```bash
# All tests
make test

# With coverage report
make test-cov

# Unit tests only
make test-unit

# Integration tests only
make test-integration
```

## 📊 Using New Features

### Structured Logging

```python
from agentfarm_mcp.utils.structured_logging import (
    setup_structured_logging,
    get_structured_logger,
    LogContext,
)

# Setup (in main)
setup_structured_logging(log_level="DEBUG", dev_mode=True)

# Get logger
logger = get_structured_logger(__name__)

# Log with context
logger.info(
    "query_executed",
    query_type="agents",
    simulation_id="sim_123",
    duration_ms=45.2,
    result_count=156,
)

# Automatic context binding
with LogContext(request_id="abc-123"):
    logger.info("processing")  # Includes request_id
```

### Redis Caching

```python
from agentfarm_mcp.services.redis_cache_service import (
    RedisCacheService,
    RedisCacheConfig,
)

# Configure
config = RedisCacheConfig(
    enabled=True,
    host="localhost",
    port=6379,
    ttl_seconds=300,
)

# Use cache
cache = RedisCacheService(config)
key = cache.generate_key("query_agents", {"limit": 100})

result = cache.get(key)
if result is None:
    result = fetch_from_database()
    cache.set(key, result)

# Check performance
stats = cache.get_stats()
print(f"Hit rate: {stats['hit_rate']:.1%}")
```

### Modular Models

```python
# Old way (still works)
from agentfarm_mcp.models.database_models import AgentModel, Simulation

# New modular way
from agentfarm_mcp.models.agent_models import AgentModel
from agentfarm_mcp.models.simulation_models import Simulation
from agentfarm_mcp.models.interaction_models import SocialInteractionModel
```

## 🐳 Docker Services

### Start Services

```bash
# PostgreSQL + Redis
make docker-up

# With optional web UIs (PgAdmin + Redis Commander)
docker-compose --profile tools up -d
```

Access web UIs:
- **PgAdmin**: http://localhost:8080 (admin@agentfarm.dev / admin)
- **Redis Commander**: http://localhost:8081

### Stop Services

```bash
make docker-down
```

## 📈 Performance Benchmarking

```bash
# Run benchmarks
make benchmark

# Or manually test cache performance
python scripts/benchmark_cache.py --queries 1000
```

## 🔧 Configuration Examples

### Development (SQLite + Memory)
```yaml
database:
  path: "simulation.db"
  database_type: "sqlite"
  
cache:
  backend: "memory"
  
server:
  log_level: "DEBUG"
  environment: "development"
```

### Staging (PostgreSQL + Redis)
```yaml
database:
  database_type: "postgresql"
  host: "db.staging.example.com"
  database: "simulations"
  username: "${DB_USERNAME}"
  password: "${DB_PASSWORD}"
  
cache:
  backend: "redis"
  redis_host: "redis.staging.example.com"
  
server:
  log_level: "INFO"
  environment: "staging"
  json_logs: true
```

### Production
```yaml
database:
  database_type: "postgresql"
  host: "db.prod.example.com"
  sslmode: "require"
  pool_size: 20
  
cache:
  backend: "redis"
  redis_host: "redis.prod.example.com"
  redis_password: "${REDIS_PASSWORD}"
  ttl_seconds: 600
  
server:
  log_level: "INFO"
  environment: "production"
  json_logs: true
  structured_logging: true
```

## 🛠️ Common Tasks

### Add Type Hints to New Code

```python
from typing import List, Dict, Optional

def process_agents(
    simulation_id: str,
    limit: int = 100,
    filters: Optional[Dict[str, str]] = None
) -> List[Dict[str, Any]]:
    """Process agents with type-safe parameters."""
    # Implementation
    pass
```

### Create a New Model

```python
# In agentfarm_mcp/models/custom_models.py
from sqlalchemy import Column, Integer, String
from .base import Base

class CustomModel(Base):
    """Your model docstring."""
    
    __tablename__ = "custom"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
```

Then export in `__init__.py`:
```python
from .custom_models import CustomModel

__all__ = ["CustomModel"]
```

### Add a New Tool

```python
from typing import Optional
from pydantic import BaseModel, Field
from .base import ToolBase

class MyToolParams(BaseModel):
    """Parameters for my_tool."""
    simulation_id: str = Field(..., description="Simulation ID")
    limit: int = Field(100, ge=1, le=1000, description="Result limit")

class MyTool(ToolBase):
    """My custom tool."""
    
    @property
    def name(self) -> str:
        return "my_tool"
    
    @property
    def description(self) -> str:
        return "Description of what this tool does"
    
    @property
    def parameters_schema(self):
        return MyToolParams
    
    def execute(self, **params):
        """Execute the tool logic."""
        # Implementation
        pass
```

## 🚨 Troubleshooting

### Pre-commit Hooks Failing

```bash
# Update hooks
pre-commit autoupdate

# Clean and reinstall
pre-commit clean
pre-commit install
```

### Type Checking Errors

```bash
# Install missing type stubs
pip install types-PyYAML types-redis

# Run with verbose output
mypy agentfarm_mcp/ --show-error-codes
```

### Redis Connection Issues

```bash
# Check if Redis is running
docker ps | grep redis

# Test connection
redis-cli -h localhost -p 6379 ping

# Restart Redis
docker-compose restart redis
```

### Database Connection Issues

```bash
# Check PostgreSQL
docker ps | grep postgres

# Test connection
psql -h localhost -U agentfarm -d agentfarm_simulations

# View logs
docker logs agentfarm_postgres
```

## 📚 Next Steps

1. **Read the full improvements documentation**: [IMPROVEMENTS.md](IMPROVEMENTS.md)
2. **Explore the codebase**: Start with `agentfarm_mcp/server.py`
3. **Run examples**: Check `demo_all_tools.py`
4. **Add your features**: Follow the type-safe patterns
5. **Contribute**: Use pre-commit hooks and write tests

## 🤝 Getting Help

- **Documentation**: See [IMPROVEMENTS.md](IMPROVEMENTS.md) for detailed explanations
- **API Reference**: Check [docs/API_REFERENCE.md](docs/API_REFERENCE.md)
- **Issues**: Report bugs and request features on GitHub

## ✅ Checklist for New Developers

- [ ] Clone repository
- [ ] Run `make setup`
- [ ] Run `make test` to verify
- [ ] Copy and edit config file
- [ ] Start Docker services (if using PostgreSQL/Redis)
- [ ] Run `make run-dev`
- [ ] Install IDE extensions (Python, MyPy, Ruff)
- [ ] Configure IDE to use pre-commit hooks
- [ ] Read [IMPROVEMENTS.md](IMPROVEMENTS.md)
- [ ] Try the examples in `demo_all_tools.py`

Happy coding! 🎉
