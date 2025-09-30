"""Tests for database URL builder."""

import pytest
from unittest.mock import Mock

from agentfarm_mcp.config import DatabaseConfig
from agentfarm_mcp.services.database_url_builder import (
    DatabaseURLBuilder,
    SQLiteURLBuilder,
    PostgreSQLURLBuilder,
    DatabaseURLBuilderFactory,
    detect_database_type,
)


class TestSQLiteURLBuilder:
    """Test the SQLiteURLBuilder."""

    @pytest.fixture
    def sqlite_config(self):
        """Create a SQLite database configuration."""
        return DatabaseConfig(
            path="sqlite:///test/database.sqlite",
            database_type="sqlite",
            pool_size=5,
            query_timeout=30,
            read_only=True
        )

    @pytest.fixture
    def sqlite_builder(self):
        """Create a SQLiteURLBuilder instance."""
        return SQLiteURLBuilder()

    def test_sqlite_url_builder_inheritance(self, sqlite_builder):
        """Test that SQLiteURLBuilder inherits from DatabaseURLBuilder."""
        assert isinstance(sqlite_builder, DatabaseURLBuilder)

    def test_sqlite_build_url(self, sqlite_builder, sqlite_config):
        """Test SQLite URL building."""
        url = sqlite_builder.build_url(sqlite_config)
        
        assert url.startswith("sqlite:///")
        assert "file:" in url
        assert "/test/database.sqlite" in url
        assert "mode=ro" in url
        assert "uri=true" in url

    def test_sqlite_build_url_absolute_path(self, sqlite_builder):
        """Test SQLite URL building with absolute path."""
        config = DatabaseConfig(
            path="sqlite:///absolute/path/to/db.sqlite",
            database_type="sqlite",
            read_only=True
        )
        
        url = sqlite_builder.build_url(config)
        
        assert url.startswith("sqlite:///")
        assert "file:" in url
        assert "/absolute/path/to/db.sqlite" in url
        assert "mode=ro" in url

    def test_sqlite_build_url_read_write(self, sqlite_builder):
        """Test SQLite URL building in read-write mode."""
        config = DatabaseConfig(
            path="/test/db.sqlite",
            database_type="sqlite",
            read_only=False
        )
        
        url = sqlite_builder.build_url(config)
        
        assert url.startswith("sqlite:///")
        assert "mode=rw" in url

    def test_sqlite_get_connect_args(self, sqlite_builder, sqlite_config):
        """Test SQLite connection arguments."""
        connect_args = sqlite_builder.get_connect_args(sqlite_config)
        
        assert "timeout" in connect_args
        assert connect_args["timeout"] == 30
        assert "check_same_thread" in connect_args
        assert connect_args["check_same_thread"] is False
        assert "uri" in connect_args
        assert connect_args["uri"] is True

    def test_sqlite_get_connect_args_defaults(self, sqlite_builder):
        """Test SQLite connection arguments with defaults."""
        config = DatabaseConfig(
            path="/test/db.sqlite",
            database_type="sqlite"
        )
        
        connect_args = sqlite_builder.get_connect_args(config)
        
        assert "timeout" in connect_args
        assert connect_args["timeout"] == 30  # Default
        assert "check_same_thread" in connect_args
        assert "uri" in connect_args


class TestPostgreSQLURLBuilder:
    """Test the PostgreSQLURLBuilder."""

    @pytest.fixture
    def postgres_config(self):
        """Create a PostgreSQL database configuration."""
        return DatabaseConfig(
            path="postgresql://user:pass@localhost:5432/dbname",
            database_type="postgresql",
            host="localhost",
            port=5432,
            database="dbname",
            username="user",
            password="pass",
            sslmode="prefer",
            pool_size=5,
            query_timeout=30,
            read_only=True
        )

    @pytest.fixture
    def postgres_builder(self):
        """Create a PostgreSQLURLBuilder instance."""
        return PostgreSQLURLBuilder()

    def test_postgres_url_builder_inheritance(self, postgres_builder):
        """Test that PostgreSQLURLBuilder inherits from DatabaseURLBuilder."""
        assert isinstance(postgres_builder, DatabaseURLBuilder)

    def test_postgres_build_url_connection_string(self, postgres_builder, postgres_config):
        """Test PostgreSQL URL building with connection string."""
        url = postgres_builder.build_url(postgres_config)
        
        assert url == "postgresql://user:pass@localhost:5432/dbname"

    def test_postgres_build_url_individual_params(self, postgres_builder):
        """Test PostgreSQL URL building with individual parameters."""
        config = DatabaseConfig(
            path="",  # Empty path to use individual params
            database_type="postgresql",
            host="example.com",
            port=5433,
            database="testdb",
            username="testuser",
            password="testpass",
            sslmode="require"
        )
        
        url = postgres_builder.build_url(config)
        
        assert url == "postgresql://testuser:testpass@example.com:5433/testdb"

    def test_postgres_build_url_no_password(self, postgres_builder):
        """Test PostgreSQL URL building without password."""
        config = DatabaseConfig(
            path="",
            database_type="postgresql",
            host="localhost",
            port=5432,
            database="testdb",
            username="testuser",
            password=None,
            sslmode="prefer"
        )
        
        url = postgres_builder.build_url(config)
        
        assert url == "postgresql://testuser@localhost:5432/testdb"

    def test_postgres_build_url_default_port(self, postgres_builder):
        """Test PostgreSQL URL building with default port."""
        config = DatabaseConfig(
            path="",
            database_type="postgresql",
            host="localhost",
            port=5432,  # Default port
            database="testdb",
            username="testuser",
            password="testpass"
        )
        
        url = postgres_builder.build_url(config)
        
        assert url == "postgresql://testuser:testpass@localhost:5432/testdb"

    def test_postgres_get_connect_args(self, postgres_builder, postgres_config):
        """Test PostgreSQL connection arguments."""
        connect_args = postgres_builder.get_connect_args(postgres_config)
        
        assert "sslmode" in connect_args
        assert connect_args["sslmode"] == "prefer"

    def test_postgres_get_connect_args_different_ssl_mode(self, postgres_builder):
        """Test PostgreSQL connection arguments with different SSL mode."""
        config = DatabaseConfig(
            path="postgresql://user:pass@localhost:5432/db",
            database_type="postgresql",
            sslmode="require"
        )
        
        connect_args = postgres_builder.get_connect_args(config)
        
        assert "sslmode" in connect_args
        assert connect_args["sslmode"] == "require"


class TestDatabaseURLBuilderFactory:
    """Test the DatabaseURLBuilderFactory."""

    def test_create_sqlite_builder(self):
        """Test creating a SQLite URL builder."""
        builder = DatabaseURLBuilderFactory.create_builder("sqlite")
        
        assert isinstance(builder, SQLiteURLBuilder)

    def test_create_postgresql_builder(self):
        """Test creating a PostgreSQL URL builder."""
        builder = DatabaseURLBuilderFactory.create_builder("postgresql")
        
        assert isinstance(builder, PostgreSQLURLBuilder)

    def test_create_postgres_builder(self):
        """Test creating a PostgreSQL URL builder with 'postgres' alias."""
        builder = DatabaseURLBuilderFactory.create_builder("postgres")
        
        assert isinstance(builder, PostgreSQLURLBuilder)

    def test_create_unsupported_builder(self):
        """Test creating an unsupported database type."""
        with pytest.raises(ValueError, match="Unsupported database type"):
            DatabaseURLBuilderFactory.create_builder("mysql")

    def test_create_builder_case_insensitive(self):
        """Test that builder creation is case insensitive."""
        builder1 = DatabaseURLBuilderFactory.create_builder("SQLITE")
        builder2 = DatabaseURLBuilderFactory.create_builder("sqlite")
        
        assert isinstance(builder1, SQLiteURLBuilder)
        assert isinstance(builder2, SQLiteURLBuilder)


class TestDetectDatabaseType:
    """Test the detect_database_type function."""

    def test_detect_sqlite_from_path(self):
        """Test detecting SQLite from file path."""
        config = DatabaseConfig(
            path="/path/to/database.sqlite",
            database_type="sqlite"
        )
        
        db_type = detect_database_type(config)
        assert db_type == "sqlite"

    def test_detect_sqlite_from_connection_string(self):
        """Test detecting SQLite from connection string."""
        config = DatabaseConfig(
            path="sqlite:///path/to/database.sqlite",
            database_type="sqlite"
        )
        
        db_type = detect_database_type(config)
        assert db_type == "sqlite"

    def test_detect_postgresql_from_connection_string(self):
        """Test detecting PostgreSQL from connection string."""
        config = DatabaseConfig(
            path="postgresql://user:pass@localhost:5432/db",
            database_type="postgresql"
        )
        
        db_type = detect_database_type(config)
        assert db_type == "postgresql"

    def test_detect_postgres_from_connection_string(self):
        """Test detecting PostgreSQL from 'postgres' connection string."""
        config = DatabaseConfig(
            path="postgres://user:pass@localhost:5432/db",
            database_type="postgresql"
        )
        
        db_type = detect_database_type(config)
        assert db_type == "postgresql"

    def test_detect_from_database_type_field(self):
        """Test detecting from database_type field when path is ambiguous."""
        config = DatabaseConfig(
            path="some_ambiguous_path",
            database_type="postgresql"
        )
        
        db_type = detect_database_type(config)
        assert db_type == "postgresql"

    def test_detect_sqlite_default(self):
        """Test that SQLite is the default when type is ambiguous."""
        config = DatabaseConfig(
            path="some_ambiguous_path",
            database_type="sqlite"
        )
        
        db_type = detect_database_type(config)
        assert db_type == "sqlite"


class TestDatabaseURLBuilderIntegration:
    """Integration tests for the database URL builder system."""

    def test_sqlite_full_workflow(self):
        """Test complete SQLite workflow."""
        config = DatabaseConfig(
            path="/test/database.sqlite",
            database_type="sqlite",
            read_only=True,
            query_timeout=60
        )
        
        # Detect database type
        db_type = detect_database_type(config)
        assert db_type == "sqlite"
        
        # Create builder
        builder = DatabaseURLBuilderFactory.create_builder(db_type)
        assert isinstance(builder, SQLiteURLBuilder)
        
        # Build URL
        url = builder.build_url(config)
        assert url.startswith("sqlite:///")
        assert "mode=ro" in url
        
        # Get connection args
        connect_args = builder.get_connect_args(config)
        assert connect_args["timeout"] == 60
        assert connect_args["uri"] is True

    def test_postgresql_full_workflow(self):
        """Test complete PostgreSQL workflow."""
        config = DatabaseConfig(
            path="postgresql://user:pass@localhost:5432/testdb",
            database_type="postgresql",
            sslmode="require"
        )
        
        # Detect database type
        db_type = detect_database_type(config)
        assert db_type == "postgresql"
        
        # Create builder
        builder = DatabaseURLBuilderFactory.create_builder(db_type)
        assert isinstance(builder, PostgreSQLURLBuilder)
        
        # Build URL
        url = builder.build_url(config)
        assert url == "postgresql://user:pass@localhost:5432/testdb"
        
        # Get connection args
        connect_args = builder.get_connect_args(config)
        assert connect_args["sslmode"] == "require"

    def test_postgresql_individual_params_workflow(self):
        """Test PostgreSQL workflow with individual parameters."""
        config = DatabaseConfig(
            path="",  # Empty to use individual params
            database_type="postgresql",
            host="db.example.com",
            port=5433,
            database="production",
            username="prod_user",
            password="secret",
            sslmode="verify-full"
        )
        
        # Detect database type
        db_type = detect_database_type(config)
        assert db_type == "postgresql"
        
        # Create builder
        builder = DatabaseURLBuilderFactory.create_builder(db_type)
        assert isinstance(builder, PostgreSQLURLBuilder)
        
        # Build URL
        url = builder.build_url(config)
        assert url == "postgresql://prod_user:secret@db.example.com:5433/production"
        
        # Get connection args
        connect_args = builder.get_connect_args(config)
        assert connect_args["sslmode"] == "verify-full"
