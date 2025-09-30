"""Database URL builder for multiple backend support."""

import logging
from abc import ABC, abstractmethod
from typing import Dict, Any
from urllib.parse import quote_plus

from ..config import DatabaseConfig

logger = logging.getLogger(__name__)


class DatabaseURLBuilder(ABC):
    """Abstract base class for database URL builders."""

    @abstractmethod
    def build_url(self, config: DatabaseConfig) -> str:
        """Build database URL from configuration.

        Args:
            config: Database configuration

        Returns:
            Database URL string
        """

    @abstractmethod
    def get_connect_args(self, config: DatabaseConfig) -> Dict[str, Any]:
        """Get connection arguments for the database.

        Args:
            config: Database configuration

        Returns:
            Dictionary of connection arguments
        """


class SQLiteURLBuilder(DatabaseURLBuilder):
    """SQLite database URL builder."""

    def build_url(self, config: DatabaseConfig) -> str:
        """Build SQLite database URL."""
        if config.read_only:
            # Use SQLite URI format to enforce read-only mode
            return f"sqlite:///file:{config.path}?mode=ro&uri=true"
        else:
            # For read-write mode, use URI format with mode=rw
            return f"sqlite:///file:{config.path}?mode=rw&uri=true"

    def get_connect_args(self, config: DatabaseConfig) -> Dict[str, Any]:
        """Get SQLite connection arguments."""
        connect_args = {
            "timeout": config.query_timeout,
            "check_same_thread": False,
        }
        
        if config.read_only:
            connect_args["uri"] = True
            
        return connect_args


class PostgreSQLURLBuilder(DatabaseURLBuilder):
    """PostgreSQL database URL builder."""

    def build_url(self, config: DatabaseConfig) -> str:
        """Build PostgreSQL database URL."""
        # If path is a connection string, return it as-is
        if config.path.startswith(('postgresql://', 'postgres://')):
            return config.path
        
        # For PostgreSQL, we expect additional config fields
        host = getattr(config, 'host', 'localhost')
        port = getattr(config, 'port', 5432)
        database = getattr(config, 'database', 'simulation')
        username = getattr(config, 'username', None)
        password = getattr(config, 'password', None)
        
        if username and password:
            return f"postgresql://{quote_plus(username)}:{quote_plus(password)}@{host}:{port}/{database}"
        elif username:
            return f"postgresql://{quote_plus(username)}@{host}:{port}/{database}"
        else:
            return f"postgresql://{host}:{port}/{database}"

    def get_connect_args(self, config: DatabaseConfig) -> Dict[str, Any]:
        """Get PostgreSQL connection arguments."""
        connect_args = {}
        
        # Add SSL settings if configured
        if hasattr(config, 'sslmode'):
            connect_args['sslmode'] = config.sslmode
            
        return connect_args


class DatabaseURLBuilderFactory:
    """Factory for creating database URL builders."""

    _builders = {
        'sqlite': SQLiteURLBuilder,
        'postgresql': PostgreSQLURLBuilder,
        'postgres': PostgreSQLURLBuilder,
    }

    @classmethod
    def create_builder(cls, database_type: str) -> DatabaseURLBuilder:
        """Create a database URL builder for the specified type.

        Args:
            database_type: Type of database ('sqlite', 'postgresql', etc.)

        Returns:
            Database URL builder instance

        Raises:
            ValueError: If database type is not supported
        """
        builder_class = cls._builders.get(database_type.lower())
        if not builder_class:
            supported_types = ', '.join(cls._builders.keys())
            raise ValueError(f"Unsupported database type: {database_type}. Supported types: {supported_types}")
        
        return builder_class()

    @classmethod
    def get_supported_types(cls) -> list[str]:
        """Get list of supported database types.

        Returns:
            List of supported database type names
        """
        return list(cls._builders.keys())

    @classmethod
    def register_builder(cls, database_type: str, builder_class: type[DatabaseURLBuilder]):
        """Register a new database URL builder.

        Args:
            database_type: Database type name
            builder_class: Builder class to register
        """
        cls._builders[database_type.lower()] = builder_class
        logger.info("Registered database URL builder for type: %s", database_type)


def detect_database_type(config: DatabaseConfig) -> str:
    """Detect database type from configuration.

    Args:
        config: Database configuration

    Returns:
        Detected database type
    """
    # Check if path looks like a connection string
    if config.path.startswith(('postgresql://', 'postgres://', 'mysql://', 'sqlite://')):
        db_type = config.path.split('://')[0]
        # Normalize 'postgres' to 'postgresql'
        if db_type == 'postgres':
            return 'postgresql'
        return db_type
    
    # Check for database type attribute
    if hasattr(config, 'database_type'):
        return config.database_type
    
    # Default to SQLite for file paths
    return 'sqlite'
