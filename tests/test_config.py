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

    # Mock load_dotenv to prevent loading .env file
    from unittest.mock import patch
    with patch('dotenv.load_dotenv'):
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


def test_database_config_connection_string_validation():
    """Test connection string validation."""
    # Valid connection strings
    valid_strings = [
        "postgresql://user:pass@localhost:5432/db",
        "postgres://user:pass@localhost:5432/db",
        "mysql://user:pass@localhost:3306/db",
        "sqlite:///path/to/db.sqlite"
    ]
    
    for conn_str in valid_strings:
        config = DatabaseConfig(path=conn_str)
        assert config.path == conn_str

    # Invalid connection strings
    invalid_strings = [
        "invalid://",
        "postgresql://",
        "://user:pass@localhost:5432/db",
        "postgresql://user:pass@localhost:5432/db://extra"
    ]
    
    for conn_str in invalid_strings:
        with pytest.raises(Exception, match="Invalid connection string format"):
            DatabaseConfig(path=conn_str)


def test_database_config_database_type_validation():
    """Test database type validation."""
    # Valid types
    valid_types = ["sqlite", "postgresql", "postgres"]
    for db_type in valid_types:
        config = DatabaseConfig(path="test.db", database_type=db_type)
        assert config.database_type == db_type.lower()

    # Case insensitive
    config = DatabaseConfig(path="test.db", database_type="SQLITE")
    assert config.database_type == "sqlite"

    # Invalid type
    with pytest.raises(ValueError, match="Unsupported database type"):
        DatabaseConfig(path="test.db", database_type="mysql")


def test_database_config_ssl_mode_validation():
    """Test SSL mode validation for PostgreSQL."""
    # Valid SSL modes
    valid_modes = ["disable", "allow", "prefer", "require", "verify-ca", "verify-full"]
    for ssl_mode in valid_modes:
        config = DatabaseConfig(
            path="postgresql://user:pass@localhost:5432/db",
            database_type="postgresql",
            sslmode=ssl_mode
        )
        assert config.sslmode == ssl_mode.lower()

    # Case insensitive
    config = DatabaseConfig(
        path="postgresql://user:pass@localhost:5432/db",
        database_type="postgresql",
        sslmode="REQUIRE"
    )
    assert config.sslmode == "require"

    # Invalid SSL mode
    with pytest.raises(ValueError, match="Invalid SSL mode"):
        DatabaseConfig(
            path="postgresql://user:pass@localhost:5432/db",
            database_type="postgresql",
            sslmode="invalid"
        )


def test_database_config_postgresql_validation():
    """Test PostgreSQL-specific validation."""
    # Valid PostgreSQL config with connection string
    config = DatabaseConfig(
        path="postgresql://user:pass@localhost:5432/db",
        database_type="postgresql"
    )
    assert config.database_type == "postgresql"

    # Valid PostgreSQL config with individual parameters
    config = DatabaseConfig(
        path="",
        database_type="postgresql",
        host="localhost",
        database="testdb"
    )
    assert config.host == "localhost"
    assert config.database == "testdb"

    # Invalid PostgreSQL config - missing host
    with pytest.raises(ValueError, match="PostgreSQL host is required"):
        DatabaseConfig(
            path="",
            database_type="postgresql",
            host="",  # Explicitly set to empty
            database="testdb"
        )

    # Invalid PostgreSQL config - missing database
    with pytest.raises(ValueError, match="PostgreSQL database name is required"):
        DatabaseConfig(
            path="",
            database_type="postgresql",
            host="localhost",
            database=""  # Explicitly set to empty
        )


def test_database_config_improved_error_messages(tmp_path):
    """Test improved error messages for missing files."""
    # Test with directory that exists but file doesn't
    test_dir = tmp_path / "test_dir"
    test_dir.mkdir()
    test_file = test_dir / "nonexistent.db"
    
    with pytest.raises(ValueError) as exc_info:
        DatabaseConfig(path=str(test_file))
    
    error_msg = str(exc_info.value)
    assert "Database file not found" in error_msg
    assert "Directory exists" in error_msg
    assert "Available files" in error_msg

    # Test with directory that doesn't exist
    nonexistent_dir = tmp_path / "nonexistent_dir"
    nonexistent_file = nonexistent_dir / "test.db"
    
    with pytest.raises(ValueError) as exc_info:
        DatabaseConfig(path=str(nonexistent_file))
    
    error_msg = str(exc_info.value)
    assert "Database file not found" in error_msg
    assert "Directory does not exist" in error_msg
    assert "Please check the path" in error_msg


def test_database_config_empty_file(tmp_path):
    """Test that empty files are rejected."""
    empty_file = tmp_path / "empty.db"
    empty_file.touch()  # Create empty file
    
    with pytest.raises(ValueError, match="Database file is empty"):
        DatabaseConfig(path=str(empty_file))


def test_database_config_port_validation():
    """Test port validation for PostgreSQL."""
    # Valid ports
    valid_ports = [1, 5432, 65535]
    for port in valid_ports:
        config = DatabaseConfig(
            path="",
            database_type="postgresql",
            host="localhost",
            database="testdb",
            port=port
        )
        assert config.port == port

    # Invalid ports
    invalid_ports = [0, -1, 65536, 70000]
    for port in invalid_ports:
        with pytest.raises(ValueError):
            DatabaseConfig(
                path="",
                database_type="postgresql",
                host="localhost",
                database="testdb",
                port=port
            )


def test_database_config_postgresql_defaults():
    """Test PostgreSQL configuration defaults."""
    config = DatabaseConfig(
        path="postgresql://user:pass@localhost:5432/db",
        database_type="postgresql"
    )
    
    assert config.host == "localhost"  # Default
    assert config.port == 5432  # Default
    assert config.database == "simulation"  # Default
    assert config.sslmode == "prefer"  # Default


def test_database_config_sqlite_with_postgresql_fields():
    """Test that SQLite config ignores PostgreSQL-specific fields."""
    config = DatabaseConfig(
        path="test.db",
        database_type="sqlite",
        host="should_be_ignored",
        port=9999,
        database="should_be_ignored",
        username="should_be_ignored",
        password="should_be_ignored",
        sslmode="should_be_ignored"
    )
    
    # These fields should be set but not validated for SQLite
    assert config.host == "should_be_ignored"
    assert config.port == 9999
    assert config.database == "should_be_ignored"
    assert config.username == "should_be_ignored"
    assert config.password == "should_be_ignored"
    assert config.sslmode == "should_be_ignored"