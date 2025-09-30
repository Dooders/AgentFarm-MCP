"""Configuration management for MCP server."""

from pathlib import Path

from pydantic import BaseModel, Field, field_validator


class DatabaseConfig(BaseModel):
    """Database configuration."""

    path: str = Field(..., description="Path to database file")
    pool_size: int = Field(5, ge=1, le=20, description="Connection pool size")
    query_timeout: int = Field(30, ge=5, le=300, description="Query timeout in seconds")
    read_only: bool = Field(True, description="Read-only access mode")

    @field_validator("path")
    @classmethod
    def validate_path_exists(cls, v: str) -> str:
        """Ensure database file exists."""
        path = Path(v)
        if not path.exists():
            raise ValueError(f"Database file not found: {v}")
        if not path.is_file():
            raise ValueError(f"Database path is not a file: {v}")
        return str(path.absolute())


class CacheConfig(BaseModel):
    """Cache configuration."""

    max_size: int = Field(100, ge=0, le=1000, description="Maximum cache entries")
    ttl_seconds: int = Field(300, ge=0, description="Time to live in seconds")
    enabled: bool = Field(True, description="Enable caching")


class ServerConfig(BaseModel):
    """Server configuration."""

    max_result_size: int = Field(10000, ge=100, le=100000, description="Maximum results per query")
    default_limit: int = Field(100, ge=10, le=1000, description="Default pagination limit")
    log_level: str = Field("INFO", description="Logging level")

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"Invalid log level: {v}. Must be one of {', '.join(valid_levels)}")
        return v_upper


class MCPConfig(BaseModel):
    """Main MCP server configuration."""

    database: DatabaseConfig
    cache: CacheConfig = Field(default_factory=CacheConfig)
    server: ServerConfig = Field(default_factory=ServerConfig)

    @classmethod
    def from_db_path(
        cls, db_path: str, cache: CacheConfig = None, server: ServerConfig = None
    ) -> "MCPConfig":
        """Create config from database path with optional overrides.

        Args:
            db_path: Path to the database file
            cache: Optional cache configuration override
            server: Optional server configuration override

        Returns:
            MCPConfig instance

        Example:
            >>> config = MCPConfig.from_db_path(
            ...     "/path/to/db.sqlite",
            ...     cache=CacheConfig(enabled=False)
            ... )
        """
        return cls(
            database=DatabaseConfig(path=db_path),
            cache=cache or CacheConfig(),
            server=server or ServerConfig(),
        )

    @classmethod
    def from_yaml(cls, yaml_path: str) -> "MCPConfig":
        """Load configuration from YAML file.

        Args:
            yaml_path: Path to YAML configuration file

        Returns:
            MCPConfig instance

        Example:
            >>> config = MCPConfig.from_yaml("config.yaml")
        """
        import yaml

        yaml_file = Path(yaml_path)
        if not yaml_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {yaml_path}")

        with open(yaml_file, encoding="utf-8") as f:
            data = yaml.safe_load(f)

        return cls(**data)

    @classmethod
    def from_env(cls) -> "MCPConfig":
        """Load configuration from environment variables.

        Environment variables:
            DB_PATH: Database file path
            DB_POOL_SIZE: Connection pool size
            DB_QUERY_TIMEOUT: Query timeout in seconds
            DB_READ_ONLY: Read-only mode (true/false)
            CACHE_ENABLED: Enable caching (true/false)
            CACHE_MAX_SIZE: Maximum cache entries
            CACHE_TTL_SECONDS: Cache TTL in seconds
            MAX_RESULT_SIZE: Maximum result size
            DEFAULT_LIMIT: Default pagination limit
            LOG_LEVEL: Logging level

        Returns:
            MCPConfig instance

        Example:
            >>> config = MCPConfig.from_env()
        """
        import os

        from dotenv import load_dotenv

        load_dotenv()

        def get_bool(key: str, default: bool) -> bool:
            """Get boolean from environment variable."""
            value = os.getenv(key)
            if value is None:
                return default
            return value.lower() in ("true", "1", "yes", "on")

        def get_int(key: str, default: int) -> int:
            """Get integer from environment variable."""
            value = os.getenv(key)
            if value is None:
                return default
            return int(value)

        db_path = os.getenv("DB_PATH")
        if not db_path:
            raise ValueError("DB_PATH environment variable is required")

        return cls(
            database=DatabaseConfig(
                path=db_path,
                pool_size=get_int("DB_POOL_SIZE", 5),
                query_timeout=get_int("DB_QUERY_TIMEOUT", 30),
                read_only=get_bool("DB_READ_ONLY", True),
            ),
            cache=CacheConfig(
                enabled=get_bool("CACHE_ENABLED", True),
                max_size=get_int("CACHE_MAX_SIZE", 100),
                ttl_seconds=get_int("CACHE_TTL_SECONDS", 300),
            ),
            server=ServerConfig(
                max_result_size=get_int("MAX_RESULT_SIZE", 10000),
                default_limit=get_int("DEFAULT_LIMIT", 100),
                log_level=os.getenv("LOG_LEVEL", "INFO"),
            ),
        )
