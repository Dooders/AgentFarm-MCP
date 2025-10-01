"""Database service for MCP server."""

from collections.abc import Callable, Generator
from contextlib import contextmanager
from typing import Any, TypeVar

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import QueuePool
from structlog import get_logger

from ..config import DatabaseConfig
from ..models.database_models import Simulation
from ..utils.exceptions import ConnectionError as MCPConnectionError
from ..utils.exceptions import (
    DatabaseError,
    QueryExecutionError,
    QueryTimeoutError,
    SimulationNotFoundError,
)
from .database_url_builder import DatabaseURLBuilderFactory, detect_database_type

logger = get_logger(__name__)

T = TypeVar("T")


class DatabaseService:
    """Service for database operations with connection management.

    This service provides a clean interface for database operations with:
    - Connection pooling
    - Session management
    - Error handling
    - Read-only enforcement
    - Query timeout support
    """

    def __init__(self, config: DatabaseConfig):
        """Initialize database service.

        Args:
            config: Database configuration

        Raises:
            DatabaseError: If database initialization fails
        """
        self.config = config
        self._engine = None
        self._SessionFactory = None
        self._initialize_engine()

    def _initialize_engine(self):
        """Initialize SQLAlchemy engine and session factory."""
        try:
            # Detect database type and create appropriate URL builder
            db_type = detect_database_type(self.config)
            url_builder = DatabaseURLBuilderFactory.create_builder(db_type)

            # Build database URL and connection arguments
            db_url = url_builder.build_url(self.config)
            connect_args = url_builder.get_connect_args(self.config)

            # Create engine with connection pooling
            self._engine = create_engine(
                db_url,
                poolclass=QueuePool,
                pool_size=self.config.pool_size,
                max_overflow=2,
                pool_pre_ping=True,  # Verify connections before use
                connect_args=connect_args,
                echo=False,  # Set to True for SQL debugging
            )

            # Create session factory
            self._SessionFactory = sessionmaker(bind=self._engine, expire_on_commit=False)

            logger.info(
                "Database service initialized: %s (type=%s, read_only=%s)",
                self.config.path,
                db_type,
                self.config.read_only,
            )

        except Exception as exc:
            logger.error("Failed to initialize database: %s", exc)
            db_type = detect_database_type(self.config)
            raise MCPConnectionError(
                f"Database initialization failed: {exc}", database_type=db_type
            ) from exc

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Provide a transactional scope for database operations.

        Yields:
            SQLAlchemy Session

        Raises:
            DatabaseError: If session operations fail

        Example:
            >>> with db_service.get_session() as session:
            ...     agents = session.query(AgentModel).all()
        """
        session = self._SessionFactory()
        try:
            yield session
            # Read-only mode, no commit needed
            if not self.config.read_only:
                session.commit()
        except Exception as exc:
            session.rollback()
            logger.error("database_session_error", error=str(exc), exc_info=exc)
            raise QueryExecutionError(f"Query execution failed: {exc}") from exc
        finally:
            session.close()

    def execute_query(self, query_func: Callable[[Session], T]) -> T:
        """Execute a query function with error handling.

        Args:
            query_func: Function that takes a session and returns results

        Returns:
            Query results

        Raises:
            DatabaseError: If query execution fails
            QueryTimeoutError: If query exceeds timeout

        Example:
            >>> def my_query(session: Session) -> int:
            ...     return session.query(AgentModel).count()
            >>> count = db_service.execute_query(my_query)
        """
        with self.get_session() as session:
            try:
                # Note: SQLite doesn't support statement-level timeouts natively
                # For production with PostgreSQL, you would set statement_timeout here
                result = query_func(session)
                return result

            except QueryTimeoutError:
                raise
            except Exception as exc:
                logger.error("query_execution_error", error=str(exc), exc_info=exc)
                raise QueryExecutionError(f"Query failed: {exc}") from exc

    def validate_simulation_exists(self, simulation_id: str) -> bool:
        """Check if simulation exists in database.

        Args:
            simulation_id: Simulation ID to check

        Returns:
            True if simulation exists, False otherwise

        Example:
            >>> if db_service.validate_simulation_exists("sim_001"):
            ...     print("Simulation exists")
        """

        def check_exists(session: Session) -> bool:
            return (
                session.query(Simulation).filter_by(simulation_id=simulation_id).first() is not None
            )

        try:
            return self.execute_query(check_exists)
        except DatabaseError:
            return False

    def get_simulation(self, simulation_id: str) -> Simulation:
        """Get simulation by ID.

        Args:
            simulation_id: Simulation ID

        Returns:
            Simulation model instance

        Raises:
            SimulationNotFoundError: If simulation doesn't exist

        Example:
            >>> sim = db_service.get_simulation("sim_001")
            >>> print(sim.status)
        """

        def get_sim(session: Session) -> Simulation:
            sim = session.query(Simulation).filter_by(simulation_id=simulation_id).first()

            if not sim:
                raise SimulationNotFoundError(simulation_id)

            return sim

        return self.execute_query(get_sim)

    def close(self):
        """Close database connections and dispose of engine.

        Example:
            >>> db_service.close()
        """
        if self._engine:
            self._engine.dispose()
            logger.info("Database service closed")
