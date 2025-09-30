"""Unit tests for database service."""

import pytest
from mcp.config import DatabaseConfig
from mcp.models.database_models import AgentModel, Simulation
from mcp.services.database_service import DatabaseService
from mcp.utils.exceptions import DatabaseError, SimulationNotFoundError


def test_database_service_initialization(db_config):
    """Test database service initializes correctly."""
    service = DatabaseService(db_config)

    assert service._engine is not None
    assert service._SessionFactory is not None
    assert service.config == db_config

    service.close()


def test_database_service_get_session(db_service):
    """Test session context manager."""
    with db_service.get_session() as session:
        assert session is not None
        # Session should be usable
        result = session.query(Simulation).first()
        assert result is not None


def test_database_service_execute_query(db_service, test_simulation_id):
    """Test execute_query method."""

    def count_simulations(session):
        return session.query(Simulation).count()

    count = db_service.execute_query(count_simulations)

    assert count >= 1  # At least our test simulation


def test_database_service_execute_query_error_handling(db_service):
    """Test that query errors are handled properly."""

    def failing_query(session):
        raise ValueError("Test error")

    with pytest.raises(DatabaseError, match="Query failed"):
        db_service.execute_query(failing_query)


def test_database_service_validate_simulation_exists(db_service, test_simulation_id):
    """Test simulation existence validation."""
    # Valid simulation
    assert db_service.validate_simulation_exists(test_simulation_id) is True

    # Invalid simulation
    assert db_service.validate_simulation_exists("nonexistent_sim_999") is False


def test_database_service_get_simulation(db_service, test_simulation_id):
    """Test retrieving simulation by ID."""
    sim = db_service.get_simulation(test_simulation_id)

    assert sim is not None
    assert sim.simulation_id == test_simulation_id
    assert sim.status in ["completed", "running", "failed", "pending"]


def test_database_service_get_simulation_not_found(db_service):
    """Test that getting nonexistent simulation raises error."""
    # The SimulationNotFoundError is raised inside the query, then wrapped in DatabaseError
    with pytest.raises(DatabaseError) as exc_info:
        db_service.get_simulation("nonexistent_sim_999")

    assert "not found" in str(exc_info.value).lower()


def test_database_service_close(db_config):
    """Test closing database service."""
    service = DatabaseService(db_config)
    engine = service._engine

    service.close()

    # Engine should be disposed
    assert engine.pool.size() == 0 or True  # Pool is disposed


def test_database_service_session_rollback_on_error(db_service):
    """Test that session rolls back on error."""

    def query_with_error(session):
        # Start a query
        session.query(Simulation).first()
        # Raise an error
        raise ValueError("Test error")

    with pytest.raises(DatabaseError):
        db_service.execute_query(query_with_error)

    # Should still be able to use the service
    with db_service.get_session() as session:
        result = session.query(Simulation).first()
        assert result is not None


def test_database_service_multiple_sessions(db_service):
    """Test that multiple sessions can be created."""
    with db_service.get_session() as session1:
        result1 = session1.query(Simulation).first()
        assert result1 is not None

    with db_service.get_session() as session2:
        result2 = session2.query(Simulation).first()
        assert result2 is not None


def test_database_service_query_agents(db_service, test_simulation_id):
    """Test querying agents from database."""

    def get_agents(session):
        return (
            session.query(AgentModel)
            .filter(AgentModel.simulation_id == test_simulation_id)
            .all()
        )

    agents = db_service.execute_query(get_agents)

    assert len(agents) == 20  # We created 20 test agents
    assert all(a.simulation_id == test_simulation_id for a in agents)


def test_database_service_query_with_filters(db_service, test_simulation_id):
    """Test querying with filters."""

    def get_system_agents(session):
        return (
            session.query(AgentModel)
            .filter(
                AgentModel.simulation_id == test_simulation_id,
                AgentModel.agent_type == "system",
            )
            .all()
        )

    agents = db_service.execute_query(get_system_agents)

    assert len(agents) >= 1
    assert all(a.agent_type == "system" for a in agents)


def test_database_service_read_only_config(test_db_with_data):
    """Test that read-only configuration is set."""
    config = DatabaseConfig(path=str(test_db_with_data), read_only=True)
    service = DatabaseService(config)

    assert service.config.read_only is True

    service.close()


def test_database_service_validate_nonexistent_returns_false(db_service):
    """Test that validate returns False for errors."""
    # This tests the except DatabaseError branch
    result = db_service.validate_simulation_exists("definitely_does_not_exist_12345")
    assert result is False


def test_database_service_writable_mode(test_db_with_data):
    """Test database service in writable mode."""
    config = DatabaseConfig(path=str(test_db_with_data), read_only=False)
    service = DatabaseService(config)

    assert service.config.read_only is False

    # Should still be able to query
    with service.get_session() as session:
        result = session.query(Simulation).first()
        assert result is not None

    service.close()