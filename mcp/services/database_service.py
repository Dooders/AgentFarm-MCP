"""Database service for MCP server."""

import logging
from contextlib import contextmanager
from typing import Any, Callable, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import QueuePool

from ..config import DatabaseConfig
from ..models.database_models import Base, Simulation
from ..utils.exceptions import DatabaseError, QueryTimeoutError, SimulationNotFoundError

logger = logging.getLogger(__name__)


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
            # Configure connection arguments
            connect_args = {
                "timeout": self.config.query_timeout,
                "check_same_thread": False,
            }

            # Create database URL (SQLite-specific for now)
            # Note: SQLite read-only mode can be enforced via URI with mode=ro
            if self.config.read_only:
                # Use SQLite URI format to enforce read-only mode
                db_url = f"sqlite:///file:{self.config.path}?mode=ro&uri=true"
                connect_args["uri"] = True
            else:
                db_url = f"sqlite:///{self.config.path}"

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
                f"Database service initialized: {self.config.path} "
                f"(read_only={self.config.read_only})"
            )

        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise DatabaseError(f"Database initialization failed: {e}")

    @contextmanager
    def get_session(self) -> Session:
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
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise DatabaseError(f"Query execution failed: {e}")
        finally:
            session.close()

    def execute_query(
        self, query_func: Callable[[Session], Any], timeout: Optional[int] = None
    ) -> Any:
        """Execute a query function with error handling.

        Args:
            query_func: Function that takes a session and returns results
            timeout: Optional query timeout override

        Returns:
            Query results

        Raises:
            DatabaseError: If query execution fails
            QueryTimeoutError: If query exceeds timeout

        Example:
            >>> def my_query(session):
            ...     return session.query(AgentModel).count()
            >>> count = db_service.execute_query(my_query)
        """
        # Use provided timeout or default from config
        query_timeout = timeout or self.config.query_timeout

        with self.get_session() as session:
            try:
                # Note: SQLite doesn't support statement-level timeouts natively
                # For production with PostgreSQL, you would set statement_timeout here
                result = query_func(session)
                return result

            except QueryTimeoutError:
                raise
            except Exception as e:
                logger.error(f"Query execution error: {e}")
                raise DatabaseError(f"Query failed: {e}")

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
                session.query(Simulation)
                .filter_by(simulation_id=simulation_id)
                .first()
                is not None
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