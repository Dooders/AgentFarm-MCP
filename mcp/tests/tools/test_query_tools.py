"""Unit tests for query tools."""

import pytest

from mcp.tools.query_tools import (
    GetSimulationMetricsTool,
    QueryActionsTool,
    QueryAgentsTool,
    QueryInteractionsTool,
    QueryResourcesTool,
    QueryStatesTool,
)


@pytest.fixture
def query_agents_tool(services):
    """Create QueryAgentsTool instance."""
    db_service, cache_service = services
    return QueryAgentsTool(db_service, cache_service)


@pytest.fixture
def query_actions_tool(services):
    """Create QueryActionsTool instance."""
    db_service, cache_service = services
    return QueryActionsTool(db_service, cache_service)


@pytest.fixture
def query_states_tool(services):
    """Create QueryStatesTool instance."""
    db_service, cache_service = services
    return QueryStatesTool(db_service, cache_service)


@pytest.fixture
def query_resources_tool(services):
    """Create QueryResourcesTool instance."""
    db_service, cache_service = services
    return QueryResourcesTool(db_service, cache_service)


@pytest.fixture
def query_interactions_tool(services):
    """Create QueryInteractionsTool instance."""
    db_service, cache_service = services
    return QueryInteractionsTool(db_service, cache_service)


@pytest.fixture
def get_simulation_metrics_tool(services):
    """Create GetSimulationMetricsTool instance."""
    db_service, cache_service = services
    return GetSimulationMetricsTool(db_service, cache_service)


# QueryAgentsTool Tests


def test_query_agents_basic(query_agents_tool, test_simulation_id):
    """Test basic agent query."""
    result = query_agents_tool(simulation_id=test_simulation_id, limit=10)

    assert result["success"] is True
    assert "agents" in result["data"]
    assert result["data"]["total_count"] == 20  # We created 20 agents
    assert len(result["data"]["agents"]) <= 10


def test_query_agents_filter_by_type(query_agents_tool, test_simulation_id):
    """Test filtering agents by type."""
    result = query_agents_tool(
        simulation_id=test_simulation_id, agent_type="system", limit=20
    )

    assert result["success"] is True
    # All returned agents should be system type
    for agent in result["data"]["agents"]:
        assert agent["agent_type"] == "system"


def test_query_agents_filter_by_generation(query_agents_tool, test_simulation_id):
    """Test filtering agents by generation."""
    result = query_agents_tool(simulation_id=test_simulation_id, generation=0, limit=20)

    assert result["success"] is True
    for agent in result["data"]["agents"]:
        assert agent["generation"] == 0


def test_query_agents_alive_only(query_agents_tool, test_simulation_id):
    """Test filtering for alive agents only."""
    result = query_agents_tool(simulation_id=test_simulation_id, alive_only=True, limit=20)

    assert result["success"] is True
    for agent in result["data"]["agents"]:
        assert agent["death_time"] is None


def test_query_agents_response_structure(query_agents_tool, test_simulation_id):
    """Test agent response structure."""
    result = query_agents_tool(simulation_id=test_simulation_id, limit=1)

    assert result["success"] is True

    if result["data"]["agents"]:
        agent = result["data"]["agents"][0]
        assert "agent_id" in agent
        assert "agent_type" in agent
        assert "generation" in agent
        assert "birth_time" in agent
        assert "death_time" in agent
        assert "position" in agent
        assert "x" in agent["position"]
        assert "y" in agent["position"]
        assert "initial_resources" in agent
        assert "starting_health" in agent
        assert "genome_id" in agent


def test_query_agents_invalid_simulation(query_agents_tool):
    """Test querying invalid simulation."""
    result = query_agents_tool(simulation_id="invalid_999", limit=10)

    assert result["success"] is False
    # SimulationNotFoundError is wrapped in DatabaseError by the error handling
    assert "DatabaseError" in result["error"]["type"] or "SimulationNotFoundError" in result["error"]["type"]
    assert "not found" in result["error"]["message"].lower()


# QueryActionsTool Tests


def test_query_actions_basic(query_actions_tool, test_simulation_id):
    """Test basic action query."""
    result = query_actions_tool(simulation_id=test_simulation_id, limit=10)

    assert result["success"] is True
    assert "actions" in result["data"]
    assert result["data"]["total_count"] >= 1


def test_query_actions_filter_by_agent(query_actions_tool, test_simulation_id, test_agent_id):
    """Test filtering actions by agent."""
    result = query_actions_tool(
        simulation_id=test_simulation_id, agent_id=test_agent_id, limit=20
    )

    assert result["success"] is True
    for action in result["data"]["actions"]:
        assert action["agent_id"] == test_agent_id


def test_query_actions_filter_by_type(query_actions_tool, test_simulation_id):
    """Test filtering actions by type."""
    result = query_actions_tool(
        simulation_id=test_simulation_id, action_type="move", limit=20
    )

    assert result["success"] is True
    for action in result["data"]["actions"]:
        assert action["action_type"] == "move"


def test_query_actions_step_range(query_actions_tool, test_simulation_id):
    """Test filtering by step range."""
    result = query_actions_tool(
        simulation_id=test_simulation_id, start_step=10, end_step=30, limit=20
    )

    assert result["success"] is True
    for action in result["data"]["actions"]:
        assert 10 <= action["step_number"] <= 30


# QueryStatesTool Tests


def test_query_states_basic(query_states_tool, test_simulation_id):
    """Test basic state query."""
    result = query_states_tool(simulation_id=test_simulation_id, limit=10)

    assert result["success"] is True
    assert "states" in result["data"]


def test_query_states_filter_by_agent(query_states_tool, test_simulation_id, test_agent_id):
    """Test filtering states by agent."""
    result = query_states_tool(
        simulation_id=test_simulation_id, agent_id=test_agent_id, limit=20
    )

    assert result["success"] is True
    for state in result["data"]["states"]:
        assert state["agent_id"] == test_agent_id


def test_query_states_step_range(query_states_tool, test_simulation_id):
    """Test filtering states by step range."""
    result = query_states_tool(
        simulation_id=test_simulation_id, start_step=0, end_step=50, limit=50
    )

    assert result["success"] is True
    for state in result["data"]["states"]:
        assert 0 <= state["step_number"] <= 50


def test_query_states_response_structure(query_states_tool, test_simulation_id):
    """Test state response structure."""
    result = query_states_tool(simulation_id=test_simulation_id, limit=1)

    if result["data"]["states"]:
        state = result["data"]["states"][0]
        assert "agent_id" in state
        assert "step_number" in state
        assert "position" in state
        assert "resource_level" in state
        assert "current_health" in state
        assert "age" in state


# QueryResourcesTool Tests


def test_query_resources_basic(query_resources_tool, test_simulation_id):
    """Test basic resource query."""
    result = query_resources_tool(simulation_id=test_simulation_id, limit=10)

    assert result["success"] is True
    assert "resources" in result["data"]


def test_query_resources_filter_by_step(query_resources_tool, test_simulation_id):
    """Test filtering resources by specific step."""
    result = query_resources_tool(simulation_id=test_simulation_id, step_number=0, limit=20)

    assert result["success"] is True
    for resource in result["data"]["resources"]:
        assert resource["step_number"] == 0


def test_query_resources_step_range(query_resources_tool, test_simulation_id):
    """Test filtering by step range."""
    result = query_resources_tool(
        simulation_id=test_simulation_id, start_step=0, end_step=50, limit=50
    )

    assert result["success"] is True
    for resource in result["data"]["resources"]:
        assert 0 <= resource["step_number"] <= 50


# QueryInteractionsTool Tests


def test_query_interactions_basic(query_interactions_tool, test_simulation_id):
    """Test basic interaction query."""
    result = query_interactions_tool(simulation_id=test_simulation_id, limit=10)

    assert result["success"] is True
    assert "interactions" in result["data"]


def test_query_interactions_filter_by_type(query_interactions_tool, test_simulation_id):
    """Test filtering interactions by type."""
    result = query_interactions_tool(
        simulation_id=test_simulation_id, interaction_type="gather", limit=20
    )

    assert result["success"] is True
    for interaction in result["data"]["interactions"]:
        assert interaction["interaction_type"] == "gather"


def test_query_interactions_filter_by_source(query_interactions_tool, test_simulation_id):
    """Test filtering by source entity."""
    result = query_interactions_tool(
        simulation_id=test_simulation_id, source_id="agent_000", limit=20
    )

    assert result["success"] is True
    for interaction in result["data"]["interactions"]:
        assert interaction["source_id"] == "agent_000"


# GetSimulationMetricsTool Tests


def test_get_simulation_metrics_basic(get_simulation_metrics_tool, test_simulation_id):
    """Test basic metrics query."""
    result = get_simulation_metrics_tool(simulation_id=test_simulation_id, limit=50)

    assert result["success"] is True
    assert "metrics" in result["data"]
    assert result["data"]["total_count"] == 100  # We created 100 steps


def test_get_simulation_metrics_step_range(get_simulation_metrics_tool, test_simulation_id):
    """Test filtering metrics by step range."""
    result = get_simulation_metrics_tool(
        simulation_id=test_simulation_id, start_step=10, end_step=20, limit=50
    )

    assert result["success"] is True
    assert result["data"]["returned_count"] == 11  # Steps 10-20 inclusive
    for metric in result["data"]["metrics"]:
        assert 10 <= metric["step_number"] <= 20


def test_get_simulation_metrics_response_structure(get_simulation_metrics_tool, test_simulation_id):
    """Test metrics response structure."""
    result = get_simulation_metrics_tool(simulation_id=test_simulation_id, limit=1)

    if result["data"]["metrics"]:
        metric = result["data"]["metrics"][0]
        # Check key fields
        assert "step_number" in metric
        assert "total_agents" in metric
        assert "births" in metric
        assert "deaths" in metric
        assert "total_resources" in metric
        assert "average_agent_health" in metric


# Test pagination across all query tools


@pytest.mark.parametrize(
    "tool_fixture,params",
    [
        ("query_agents_tool", {}),
        ("query_actions_tool", {}),
        ("query_states_tool", {}),
        ("query_resources_tool", {}),
        ("query_interactions_tool", {}),
        ("get_simulation_metrics_tool", {}),
    ],
)
def test_pagination_consistency(tool_fixture, params, test_simulation_id, request):
    """Test that pagination works consistently across all query tools."""
    tool = request.getfixturevalue(tool_fixture)

    result = tool(simulation_id=test_simulation_id, limit=5, offset=0, **params)

    assert result["success"] is True
    assert result["data"]["limit"] == 5
    assert result["data"]["offset"] == 0
    assert result["data"]["returned_count"] <= 5


# Additional edge case tests


def test_query_actions_with_target(query_actions_tool, test_simulation_id):
    """Test that actions include target information."""
    result = query_actions_tool(simulation_id=test_simulation_id, limit=5)

    assert result["success"] is True
    # Just verify the field exists
    for action in result["data"]["actions"]:
        assert "action_target_id" in action


def test_query_states_full_data(query_states_tool, test_simulation_id):
    """Test that states include all fields."""
    result = query_states_tool(simulation_id=test_simulation_id, limit=1)

    if result["data"]["states"]:
        state = result["data"]["states"][0]
        # Verify all position fields
        assert "x" in state["position"]
        assert "y" in state["position"]
        assert "z" in state["position"]
        # Verify all numeric fields
        assert isinstance(state["resource_level"], (int, float))
        assert isinstance(state["age"], int)


def test_query_resources_step_number_vs_range(query_resources_tool, test_simulation_id):
    """Test that step_number takes precedence over range."""
    result = query_resources_tool(
        simulation_id=test_simulation_id,
        step_number=0,
        start_step=10,
        end_step=20,
        limit=20,
    )

    assert result["success"] is True
    # When step_number is specified, it should override range
    for resource in result["data"]["resources"]:
        assert resource["step_number"] == 0


def test_query_interactions_step_range(query_interactions_tool, test_simulation_id):
    """Test interactions with step range."""
    result = query_interactions_tool(
        simulation_id=test_simulation_id, start_step=0, end_step=25, limit=20
    )

    assert result["success"] is True
    for interaction in result["data"]["interactions"]:
        assert 0 <= interaction["step_number"] <= 25


def test_get_simulation_metrics_ordering(get_simulation_metrics_tool, test_simulation_id):
    """Test that metrics are ordered by step number."""
    result = get_simulation_metrics_tool(simulation_id=test_simulation_id, limit=20)

    assert result["success"] is True

    # Check ordering
    steps = result["data"]["metrics"]
    if len(steps) > 1:
        for i in range(len(steps) - 1):
            assert steps[i]["step_number"] <= steps[i + 1]["step_number"]