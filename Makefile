.PHONY: help install install-dev setup test lint format type-check pre-commit clean docker-up docker-down benchmark

# Default target
help:
	@echo "AgentFarm MCP - Development Commands"
	@echo ""
	@echo "Setup:"
	@echo "  make install          Install production dependencies"
	@echo "  make install-dev      Install development dependencies"
	@echo "  make setup            Full development setup (install + pre-commit)"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint             Run linting (ruff)"
	@echo "  make format           Format code (black + isort)"
	@echo "  make type-check       Run type checking (mypy)"
	@echo "  make pre-commit       Run all pre-commit hooks"
	@echo "  make security         Run security checks (bandit)"
	@echo ""
	@echo "Testing:"
	@echo "  make test             Run all tests"
	@echo "  make test-cov         Run tests with coverage report"
	@echo "  make test-unit        Run unit tests only"
	@echo "  make test-integration Run integration tests only"
	@echo ""
	@echo "Performance:"
	@echo "  make benchmark        Run performance benchmarks"
	@echo ""
	@echo "Development:"
	@echo "  make run-dev          Run server in development mode"
	@echo "  make docker-up        Start Docker services (PostgreSQL, Redis)"
	@echo "  make docker-down      Stop Docker services"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean            Remove generated files and caches"
	@echo "  make clean-cache      Clear Redis and in-memory caches"

# Installation
install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"
	pip install -r requirements.txt

setup: install-dev
	pre-commit install
	@echo "✅ Development environment setup complete!"
	@echo "Run 'make test' to verify installation"

# Code Quality
lint:
	ruff check agentfarm_mcp/ --fix
	@echo "✅ Linting complete"

format:
	black agentfarm_mcp/ tests/
	isort agentfarm_mcp/ tests/
	@echo "✅ Code formatting complete"

type-check:
	mypy agentfarm_mcp/
	@echo "✅ Type checking complete"

pre-commit:
	pre-commit run --all-files
	@echo "✅ All pre-commit checks passed"

security:
	bandit -r agentfarm_mcp/ -c pyproject.toml
	@echo "✅ Security checks complete"

# Testing
test:
	pytest -v
	@echo "✅ All tests passed"

test-cov:
	pytest -v --cov=agentfarm_mcp --cov-report=html --cov-report=term
	@echo "✅ Coverage report generated in htmlcov/"

test-unit:
	pytest tests/ -v -m "not integration"
	@echo "✅ Unit tests passed"

test-integration:
	pytest tests/integration/ -v
	@echo "✅ Integration tests passed"

# Performance
benchmark:
	@echo "Running performance benchmarks..."
	@python -m pytest tests/ -v -k benchmark --benchmark-only
	@echo "✅ Benchmarks complete"

# Development
run-dev:
	@echo "Starting MCP server in development mode..."
	python -m agentfarm_mcp.cli --config config.dev.yaml

docker-up:
	@echo "Starting Docker services (PostgreSQL + Redis)..."
	docker-compose up -d
	@echo "✅ Services running:"
	@echo "  PostgreSQL: localhost:5432"
	@echo "  Redis: localhost:6379"

docker-down:
	@echo "Stopping Docker services..."
	docker-compose down
	@echo "✅ Services stopped"

# Cleanup
clean:
	@echo "Cleaning generated files..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/
	rm -rf dist/
	rm -rf build/
	@echo "✅ Cleanup complete"

clean-cache:
	@echo "Clearing application caches..."
	@python -c "import redis; r = redis.Redis(host='localhost', port=6379, db=0); r.flushdb(); print('Redis cache cleared')" 2>/dev/null || echo "Redis not available"
	@echo "✅ Cache cleanup complete"

# Quick development cycle
dev: format lint type-check test
	@echo "✅ Development cycle complete - ready to commit!"

# CI/CD simulation
ci: pre-commit test-cov
	@echo "✅ CI checks passed"
