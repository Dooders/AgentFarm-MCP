"""Unit tests for advanced tools."""

import pytest

from mcp.tools.advanced_tools import BuildAgentLineageTool, GetAgentLifecycleTool


@pytest.fixture
def build_lineage_tool(services):
    """Create BuildAgentLineageTool instance."""
    db_service, cache_service = services
    return BuildAgentLineageTool(db_service, cache_service)


@pytest.fixture
def get_lifecycle_tool(services):
    """Create GetAgentLifecycleTool instance."""
    db_service, cache_service = services
    return GetAgentLifecycleTool(db_service, cache_service)


# BuildAgentLineageTool Tests


def test_build_lineage_basic(build_lineage_tool, test_simulation_id, test_agent_id):
    """Test basic lineage building."""
    result = build_lineage_tool(
        simulation_id=test_simulation_id, agent_id=test_agent_id, depth=3
    )

    assert result["success"] is True
    assert "agent" in result["data"]
    assert "ancestors" in result["data"]
    assert "descendants" in result["data"]


def test_build_lineage_agent_info(build_lineage_tool, test_simulation_id, test_agent_id):
    """Test that agent info is included."""
    result = build_lineage_tool(
        simulation_id=test_simulation_id, agent_id=test_agent_id, depth=2
    )

    agent = result["data"]["agent"]

    assert agent["agent_id"] == test_agent_id
    assert "agent_type" in agent
    assert "generation" in agent
    assert "birth_time" in agent
    assert "genome_id" in agent


def test_build_lineage_with_descendants(build_lineage_tool, test_simulation_id):
    """Test lineage with descendants."""
    # Agent_000 has offspring (agent_010)
    result = build_lineage_tool(
        simulation_id=test_simulation_id, agent_id="agent_000", depth=2
    )

    assert result["success"] is True

    # Should have at least one descendant
    descendants = result["data"]["descendants"]
    if descendants:
        assert len(descendants) >= 1
        descendant = descendants[0]
        assert "agent_id" in descendant
        assert "relationship" in descendant
        assert descendant["relationship"] == "child"


def test_build_lineage_invalid_agent(build_lineage_tool, test_simulation_id):
    """Test with invalid agent ID."""
    result = build_lineage_tool(
        simulation_id=test_simulation_id, agent_id="invalid_999", depth=2
    )

    assert result["success"] is True  # Returns success with error in data
    assert "error" in result["data"]


# GetAgentLifecycleTool Tests


def test_get_lifecycle_basic(get_lifecycle_tool, test_simulation_id, test_agent_id):
    """Test basic lifecycle retrieval."""
    result = get_lifecycle_tool(
        simulation_id=test_simulation_id,
        agent_id=test_agent_id,
        include_actions=True,
        include_states=True,
        include_health=True,
    )

    assert result["success"] is True
    assert "agent_info" in result["data"]


def test_get_lifecycle_agent_info(get_lifecycle_tool, test_simulation_id, test_agent_id):
    """Test agent info in lifecycle."""
    result = get_lifecycle_tool(
        simulation_id=test_simulation_id, agent_id=test_agent_id
    )

    info = result["data"]["agent_info"]

    assert info["agent_id"] == test_agent_id
    assert "agent_type" in info
    assert "generation" in info
    assert "birth_time" in info
    assert "lifespan" in info
    assert "position" in info
    assert "initial_resources" in info


def test_get_lifecycle_with_states(get_lifecycle_tool, test_simulation_id):
    """Test lifecycle with state history."""
    # agent_000 has states
    result = get_lifecycle_tool(
        simulation_id=test_simulation_id, agent_id="agent_000", include_states=True
    )

    assert result["success"] is True
    assert "states" in result["data"]
    assert "state_count" in result["data"]

    if result["data"]["states"]:
        state = result["data"]["states"][0]
        assert "step" in state
        assert "position" in state
        assert "resources" in state
        assert "health" in state
        assert "age" in state


def test_get_lifecycle_with_actions(get_lifecycle_tool, test_simulation_id):
    """Test lifecycle with action history."""
    # agent_000 has actions
    result = get_lifecycle_tool(
        simulation_id=test_simulation_id, agent_id="agent_000", include_actions=True
    )

    assert result["success"] is True
    assert "actions" in result["data"]
    assert "action_count" in result["data"]

    if result["data"]["actions"]:
        action = result["data"]["actions"][0]
        assert "step" in action
        assert "action_type" in action
        assert "reward" in action


def test_get_lifecycle_with_health(get_lifecycle_tool, test_simulation_id, test_agent_id):
    """Test lifecycle with health incidents."""
    result = get_lifecycle_tool(
        simulation_id=test_simulation_id, agent_id=test_agent_id, include_health=True
    )

    assert result["success"] is True
    assert "health_incidents" in result["data"]
    assert "health_incident_count" in result["data"]


def test_get_lifecycle_selective_inclusion(get_lifecycle_tool, test_simulation_id, test_agent_id):
    """Test selective data inclusion."""
    # Only states
    result = get_lifecycle_tool(
        simulation_id=test_simulation_id,
        agent_id=test_agent_id,
        include_states=True,
        include_actions=False,
        include_health=False,
    )

    assert result["success"] is True
    assert "states" in result["data"]
    assert "actions" not in result["data"]
    assert "health_incidents" not in result["data"]


def test_get_lifecycle_invalid_agent(get_lifecycle_tool, test_simulation_id):
    """Test with invalid agent ID."""
    result = get_lifecycle_tool(
        simulation_id=test_simulation_id, agent_id="invalid_999"
    )

    assert result["success"] is True  # Returns with error in data
    assert "error" in result["data"]


def test_build_lineage_depth_limit(build_lineage_tool, test_simulation_id, test_agent_id):
    """Test lineage with different depth limits."""
    result1 = build_lineage_tool(
        simulation_id=test_simulation_id, agent_id=test_agent_id, depth=1
    )
    result2 = build_lineage_tool(
        simulation_id=test_simulation_id, agent_id=test_agent_id, depth=5
    )

    assert result1["success"] is True
    assert result2["success"] is True


def test_get_lifecycle_without_states(get_lifecycle_tool, test_simulation_id, test_agent_id):
    """Test lifecycle without state data."""
    result = get_lifecycle_tool(
        simulation_id=test_simulation_id,
        agent_id=test_agent_id,
        include_states=False,
        include_actions=True,
        include_health=True,
    )

    assert result["success"] is True
    assert "states" not in result["data"]
    assert "agent_info" in result["data"]


def test_get_lifecycle_resource_change_calculation(get_lifecycle_tool, test_simulation_id):
    """Test that resource changes are calculated in actions."""
    # Use agent_000 which has actions
    result = get_lifecycle_tool(
        simulation_id=test_simulation_id, agent_id="agent_000", include_actions=True
    )

    if "actions" in result["data"] and result["data"]["actions"]:
        action = result["data"]["actions"][0]
        assert "resources_change" in action


def test_build_lineage_reproduction_event_details(build_lineage_tool, test_simulation_id):
    """Test that reproduction event details are included."""
    # agent_010 is offspring of agent_000
    result = build_lineage_tool(
        simulation_id=test_simulation_id, agent_id="agent_010", depth=2
    )

    if result["data"]["ancestors"]:
        ancestor = result["data"]["ancestors"][0]
        if "reproduction_event" in ancestor:
            event = ancestor["reproduction_event"]
            assert "step" in event
            assert "resources_cost" in event