"""Unit tests for configuration module."""

from pathlib import Path

import pytest
from agentfarm_mcp.config import CacheConfig, DatabaseConfig, MCPConfig, ServerConfig


def test_database_config_valid(test_db_with_data):
    """Test creating valid database configuration."""
    config = DatabaseConfig(path=str(test_db_with_data))

    assert config.path == str(Path(test_db_with_data).absolute())
    assert config.pool_size == 5  # default
    assert config.query_timeout == 30  # default
    assert config.read_only is True  # default


def test_database_config_custom_values(test_db_with_data):
    """Test database config with custom values."""
    config = DatabaseConfig(
        path=str(test_db_with_data), pool_size=10, query_timeout=60, read_only=False
    )

    assert config.pool_size == 10
    assert config.query_timeout == 60
    assert config.read_only is False


def test_database_config_validation_nonexistent_file():
    """Test that config validates database file exists."""
    with pytest.raises(ValueError, match="Database file not found"):
        DatabaseConfig(path="/nonexistent/path/to/database.db")


def test_database_config_validation_pool_size():
    """Test pool size validation."""
    with pytest.raises(ValueError):
        DatabaseConfig(path="test.db", pool_size=0)  # Too small

    with pytest.raises(ValueError):
        DatabaseConfig(path="test.db", pool_size=25)  # Too large


def test_database_config_validation_timeout():
    """Test timeout validation."""
    with pytest.raises(ValueError):
        DatabaseConfig(path="test.db", query_timeout=2)  # Too small

    with pytest.raises(ValueError):
        DatabaseConfig(path="test.db", query_timeout=500)  # Too large


def test_cache_config_defaults():
    """Test cache config with defaults."""
    config = CacheConfig()

    assert config.max_size == 100
    assert config.ttl_seconds == 300
    assert config.enabled is True


def test_cache_config_custom():
    """Test cache config with custom values."""
    config = CacheConfig(max_size=50, ttl_seconds=120, enabled=False)

    assert config.max_size == 50
    assert config.ttl_seconds == 120
    assert config.enabled is False


def test_cache_config_validation():
    """Test cache config validation."""
    with pytest.raises(ValueError):
        CacheConfig(max_size=-1)  # Negative

    with pytest.raises(ValueError):
        CacheConfig(max_size=2000)  # Too large

    with pytest.raises(ValueError):
        CacheConfig(ttl_seconds=-1)  # Negative


def test_server_config_defaults():
    """Test server config with defaults."""
    config = ServerConfig()

    assert config.max_result_size == 10000
    assert config.default_limit == 100
    assert config.log_level == "INFO"


def test_server_config_custom():
    """Test server config with custom values."""
    config = ServerConfig(max_result_size=5000, default_limit=50, log_level="DEBUG")

    assert config.max_result_size == 5000
    assert config.default_limit == 50
    assert config.log_level == "DEBUG"


def test_server_config_log_level_validation():
    """Test log level validation."""
    # Valid levels
    for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
        config = ServerConfig(log_level=level)
        assert config.log_level == level

    # Case insensitive
    config = ServerConfig(log_level="debug")
    assert config.log_level == "DEBUG"

    # Invalid level
    with pytest.raises(ValueError, match="Invalid log level"):
        ServerConfig(log_level="INVALID")


def test_mcp_config_from_db_path(test_db_with_data):
    """Test creating MCP config from database path."""
    config = MCPConfig.from_db_path(str(test_db_with_data))

    assert config.database.path == str(Path(test_db_with_data).absolute())
    assert config.cache.enabled is True  # default
    assert config.server.max_result_size == 10000  # default


def test_mcp_config_from_db_path_with_overrides(test_db_with_data):
    """Test MCP config with overrides."""
    config = MCPConfig.from_db_path(str(test_db_with_data), cache=CacheConfig(enabled=False))

    assert config.cache.enabled is False
    assert config.database.path == str(Path(test_db_with_data).absolute())


def test_mcp_config_from_yaml(tmp_path, test_db_with_data):
    """Test loading config from YAML file."""
    # Convert Windows path to forward slashes for YAML compatibility
    db_path = str(test_db_with_data).replace("\\", "/")
    yaml_content = f"""
database:
  path: "{db_path}"
  pool_size: 3
  query_timeout: 20
  read_only: true

cache:
  enabled: false
  max_size: 50
  ttl_seconds: 120

server:
  max_result_size: 5000
  default_limit: 50
  log_level: "WARNING"
"""

    yaml_file = tmp_path / "test_config.yaml"
    yaml_file.write_text(yaml_content)

    config = MCPConfig.from_yaml(str(yaml_file))

    assert config.database.pool_size == 3
    assert config.database.query_timeout == 20
    assert config.cache.enabled is False
    assert config.cache.max_size == 50
    assert config.server.log_level == "WARNING"


def test_mcp_config_from_yaml_nonexistent():
    """Test that loading from nonexistent YAML fails."""
    with pytest.raises(FileNotFoundError):
        MCPConfig.from_yaml("/nonexistent/config.yaml")


def test_mcp_config_from_env(test_db_with_data, monkeypatch):
    """Test loading config from environment variables."""
    # Set environment variables
    monkeypatch.setenv("DB_PATH", str(test_db_with_data))
    monkeypatch.setenv("DB_POOL_SIZE", "7")
    monkeypatch.setenv("DB_QUERY_TIMEOUT", "45")
    monkeypatch.setenv("DB_READ_ONLY", "false")
    monkeypatch.setenv("CACHE_ENABLED", "false")
    monkeypatch.setenv("CACHE_MAX_SIZE", "75")
    monkeypatch.setenv("CACHE_TTL_SECONDS", "200")
    monkeypatch.setenv("MAX_RESULT_SIZE", "8000")
    monkeypatch.setenv("DEFAULT_LIMIT", "80")
    monkeypatch.setenv("LOG_LEVEL", "ERROR")

    config = MCPConfig.from_env()

    assert config.database.pool_size == 7
    assert config.database.query_timeout == 45
    assert config.database.read_only is False
    assert config.cache.enabled is False
    assert config.cache.max_size == 75
    assert config.cache.ttl_seconds == 200
    assert config.server.max_result_size == 8000
    assert config.server.default_limit == 80
    assert config.server.log_level == "ERROR"


def test_mcp_config_from_env_missing_db_path(monkeypatch):
    """Test that from_env requires DB_PATH."""
    monkeypatch.delenv("DB_PATH", raising=False)

    with pytest.raises(ValueError, match="DB_PATH environment variable is required"):
        MCPConfig.from_env()


def test_mcp_config_from_env_bool_parsing(test_db_with_data, monkeypatch):
    """Test boolean parsing from environment variables."""
    monkeypatch.setenv("DB_PATH", str(test_db_with_data))

    # Test various true values
    for true_val in ["true", "True", "1", "yes", "YES", "on"]:
        monkeypatch.setenv("CACHE_ENABLED", true_val)
        config = MCPConfig.from_env()
        assert config.cache.enabled is True

    # Test false values
    for false_val in ["false", "False", "0", "no", "off"]:
        monkeypatch.setenv("CACHE_ENABLED", false_val)
        config = MCPConfig.from_env()
        assert config.cache.enabled is False


def test_mcp_config_defaults(test_db_with_data):
    """Test that MCP config has sensible defaults."""
    config = MCPConfig.from_db_path(str(test_db_with_data))

    # Database defaults
    assert config.database.pool_size == 5
    assert config.database.query_timeout == 30
    assert config.database.read_only is True

    # Cache defaults
    assert config.cache.enabled is True
    assert config.cache.max_size == 100
    assert config.cache.ttl_seconds == 300

    # Server defaults
    assert config.server.max_result_size == 10000
    assert config.server.default_limit == 100
    assert config.server.log_level == "INFO"


def test_database_config_path_is_directory(tmp_path):
    """Test that config rejects directory as path."""
    directory = tmp_path / "some_dir"
    directory.mkdir()

    with pytest.raises(ValueError, match="not a file"):
        DatabaseConfig(path=str(directory))
