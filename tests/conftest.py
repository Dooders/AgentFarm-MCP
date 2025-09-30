"""Shared fixtures for pytest tests."""

import pytest
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from agentfarm_mcp.config import CacheConfig, DatabaseConfig, MCPConfig, ServerConfig
from agentfarm_mcp.models.database_models import (
    ActionModel,
    AgentModel,
    AgentStateModel,
    Base,
    ExperimentModel,
    ReproductionEventModel,
    ResourceModel,
    Simulation,
    SimulationStepModel,
    SocialInteractionModel,
    InteractionModel,
)
from agentfarm_mcp.services.cache_service import CacheService
from agentfarm_mcp.services.database_service import DatabaseService


@pytest.fixture(scope="session")
def test_db_path(tmp_path_factory):
    """Create a temporary database for testing."""
    db_path = tmp_path_factory.mktemp("data") / "test.db"
    return db_path


@pytest.fixture(scope="session")
def test_db_with_data(test_db_path):
    """Create and populate test database with sample data."""
    engine = create_engine(f"sqlite:///{test_db_path}")
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Create test experiments
        exp1 = ExperimentModel(
            experiment_id="test_exp_001",
            name="Test Experiment 1",
            description="A test experiment",
            hypothesis="Testing hypothesis",
            status="running",
            tags=["test", "experiment"],
            variables={"param1": "value1"},
        )
        session.add(exp1)

        # Create test simulations
        for i in range(5):
            sim = Simulation(
                simulation_id=f"test_sim_{i:03d}",
                experiment_id="test_exp_001" if i < 3 else None,
                status="completed" if i % 2 == 0 else "running",
                parameters={
                    "agents": 100 + i * 10,
                    "resources": 1000,
                    "seed": 42 + i,
                    "simulation_steps": 1000,
                },
                results_summary={"final_agents": 90 + i * 5} if i % 2 == 0 else None,
                simulation_db_path=str(test_db_path),
            )
            session.add(sim)

            # Add detailed data for first simulation only
            if i == 0:
                # Add agents
                for j in range(20):
                    agent_type = "system" if j % 3 == 0 else "independent"
                    generation = j // 5
                    death_time = 50 + j * 10 if j % 2 == 0 else None

                    agent = AgentModel(
                        simulation_id=sim.simulation_id,
                        agent_id=f"agent_{j:03d}",
                        agent_type=agent_type,
                        birth_time=generation * 10,
                        death_time=death_time,
                        generation=generation,
                        position_x=float(j * 5),
                        position_y=float(j * 3),
                        initial_resources=50.0,
                        starting_health=100.0,
                        starvation_counter=0,
                        genome_id=f"genome_{j % 3}",
                    )
                    session.add(agent)

                    # Add states for first 5 agents
                    if j < 5:
                        for step in range(0, 100, 10):
                            state = AgentStateModel(
                                simulation_id=sim.simulation_id,
                                agent_id=agent.agent_id,
                                step_number=step,
                                position_x=float(j * 5 + step * 0.1),
                                position_y=float(j * 3 + step * 0.05),
                                position_z=0.0,
                                resource_level=50.0 - step * 0.2,
                                current_health=100.0 - step * 0.1,
                                starting_health=100.0,
                                starvation_counter=0,
                                is_defending=False,
                                total_reward=float(step * 0.5),
                                age=step,
                            )
                            session.add(state)

                    # Add actions for first 3 agents
                    if j < 3:
                        for step in range(0, 50, 5):
                            action = ActionModel(
                                simulation_id=sim.simulation_id,
                                agent_id=agent.agent_id,
                                step_number=step,
                                action_type=["move", "gather", "attack"][step % 3],
                                resources_before=50.0,
                                resources_after=55.0,
                                reward=10.0,
                                details="test action",
                            )
                            session.add(action)

                # Add simulation steps
                for step in range(100):
                    step_data = SimulationStepModel(
                        simulation_id=sim.simulation_id,
                        step_number=step,
                        total_agents=20 - (step // 20),
                        system_agents=7 - (step // 30),
                        independent_agents=13 - (step // 20),
                        control_agents=0,
                        total_resources=1000.0 - step * 5.0,
                        average_agent_resources=50.0 - step * 0.3,
                        births=1 if step % 10 == 0 else 0,
                        deaths=1 if step % 20 == 0 else 0,
                        current_max_generation=step // 30,
                        average_agent_health=100.0 - step * 0.1,
                        average_agent_age=step // 2,
                        average_reward=float(step * 0.5),
                        combat_encounters=step // 5,
                        successful_attacks=step // 10,
                        resources_shared=float(step * 0.2),
                        resource_efficiency=0.8 - step * 0.001,
                        resource_distribution_entropy=0.5 + step * 0.001,
                        resources_shared_this_step=1.0,
                        combat_encounters_this_step=0,
                        successful_attacks_this_step=0,
                        genetic_diversity=0.7,
                        dominant_genome_ratio=0.3,
                        resources_consumed=float(step * 2.0),
                    )
                    session.add(step_data)

                # Add resources
                for res_id in range(10):
                    for step in [0, 50, 99]:
                        resource = ResourceModel(
                            simulation_id=sim.simulation_id,
                            step_number=step,
                            resource_id=res_id,
                            amount=100.0 - step * 0.5,
                            position_x=float(res_id * 10),
                            position_y=float(res_id * 5),
                        )
                        session.add(resource)

                # Add interactions
                for step in range(0, 50, 5):
                    interaction = InteractionModel(
                        simulation_id=sim.simulation_id,
                        step_number=step,
                        source_type="agent",
                        source_id="agent_000",
                        target_type="resource",
                        target_id="resource_0",
                        interaction_type="gather",
                        action_type="gather",
                        details={"amount": 5.0},
                    )
                    session.add(interaction)

                # Add reproduction events
                repro_event = ReproductionEventModel(
                    simulation_id=sim.simulation_id,
                    step_number=20,
                    parent_id="agent_000",
                    offspring_id="agent_010",
                    success=True,
                    parent_resources_before=60.0,
                    parent_resources_after=40.0,
                    offspring_initial_resources=20.0,
                    parent_generation=0,
                    offspring_generation=1,
                    parent_position_x=0.0,
                    parent_position_y=0.0,
                )
                session.add(repro_event)

                # Add social interaction
                social = SocialInteractionModel(
                    simulation_id=sim.simulation_id,
                    step_number=15,
                    initiator_id="agent_000",
                    recipient_id="agent_001",
                    interaction_type="cooperation",
                    subtype="resource_sharing",
                    outcome="successful",
                    resources_transferred=5.0,
                    distance=2.5,
                    initiator_resources_before=50.0,
                    initiator_resources_after=45.0,
                    recipient_resources_before=30.0,
                    recipient_resources_after=35.0,
                )
                session.add(social)

        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

    return test_db_path


@pytest.fixture
def db_config(test_db_with_data):
    """Create database config for tests."""
    return DatabaseConfig(path=str(test_db_with_data))


@pytest.fixture
def cache_config():
    """Create cache config for tests."""
    return CacheConfig(max_size=10, ttl_seconds=60, enabled=True)


@pytest.fixture
def server_config():
    """Create server config for tests."""
    return ServerConfig(max_result_size=10000, default_limit=100, log_level="INFO")


@pytest.fixture
def mcp_config(db_config, cache_config, server_config):
    """Create complete MCP config for tests."""
    return MCPConfig(database=db_config, cache=cache_config, server=server_config)


@pytest.fixture
def db_service(db_config):
    """Create database service for tests."""
    service = DatabaseService(db_config)
    yield service
    service.close()


@pytest.fixture
def cache_service(cache_config):
    """Create cache service for tests."""
    return CacheService(cache_config)


@pytest.fixture
def services(db_service, cache_service):
    """Provide both services as a tuple."""
    return db_service, cache_service


@pytest.fixture
def test_simulation_id():
    """Return test simulation ID."""
    return "test_sim_000"


@pytest.fixture
def test_agent_id():
    """Return test agent ID."""
    return "agent_000"