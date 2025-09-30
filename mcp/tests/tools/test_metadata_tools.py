"""Unit tests for metadata tools."""

import pytest

from mcp.tools.metadata_tools import (
    GetExperimentInfoTool,
    GetSimulationInfoTool,
    ListExperimentsTool,
    ListSimulationsTool,
)
from mcp.utils.exceptions import ExperimentNotFoundError, SimulationNotFoundError


@pytest.fixture
def list_simulations_tool(services):
    """Create ListSimulationsTool instance."""
    db_service, cache_service = services
    return ListSimulationsTool(db_service, cache_service)


@pytest.fixture
def get_simulation_info_tool(services):
    """Create GetSimulationInfoTool instance."""
    db_service, cache_service = services
    return GetSimulationInfoTool(db_service, cache_service)


@pytest.fixture
def list_experiments_tool(services):
    """Create ListExperimentsTool instance."""
    db_service, cache_service = services
    return ListExperimentsTool(db_service, cache_service)


@pytest.fixture
def get_experiment_info_tool(services):
    """Create GetExperimentInfoTool instance."""
    db_service, cache_service = services
    return GetExperimentInfoTool(db_service, cache_service)


# ListSimulationsTool Tests


def test_list_simulations_basic(list_simulations_tool):
    """Test basic simulation listing."""
    result = list_simulations_tool()

    assert result["success"] is True
    assert "simulations" in result["data"]
    assert result["data"]["total_count"] >= 5  # We created 5 test simulations
    assert result["data"]["returned_count"] <= result["data"]["limit"]


def test_list_simulations_with_limit(list_simulations_tool):
    """Test listing with limit."""
    result = list_simulations_tool(limit=2)

    assert result["success"] is True
    assert result["data"]["returned_count"] <= 2
    assert result["data"]["limit"] == 2


def test_list_simulations_with_offset(list_simulations_tool):
    """Test pagination with offset."""
    result1 = list_simulations_tool(limit=1, offset=0)
    result2 = list_simulations_tool(limit=1, offset=1)

    assert result1["success"] is True
    assert result2["success"] is True

    if (
        result1["data"]["simulations"]
        and result2["data"]["simulations"]
        and result1["data"]["total_count"] > 1
    ):
        # Different simulations should be returned
        sim1_id = result1["data"]["simulations"][0]["simulation_id"]
        sim2_id = result2["data"]["simulations"][0]["simulation_id"]
        assert sim1_id != sim2_id


def test_list_simulations_filter_by_status(list_simulations_tool):
    """Test filtering by status."""
    result = list_simulations_tool(status="completed")

    assert result["success"] is True
    # All returned simulations should have status="completed"
    for sim in result["data"]["simulations"]:
        assert sim["status"] == "completed"


def test_list_simulations_filter_by_experiment(list_simulations_tool):
    """Test filtering by experiment ID."""
    result = list_simulations_tool(experiment_id="test_exp_001")

    assert result["success"] is True
    # All returned simulations should have this experiment_id
    for sim in result["data"]["simulations"]:
        assert sim["experiment_id"] == "test_exp_001"


def test_list_simulations_response_structure(list_simulations_tool):
    """Test response structure is correct."""
    result = list_simulations_tool(limit=1)

    assert "simulations" in result["data"]
    assert "total_count" in result["data"]
    assert "returned_count" in result["data"]
    assert "limit" in result["data"]
    assert "offset" in result["data"]

    if result["data"]["simulations"]:
        sim = result["data"]["simulations"][0]
        assert "simulation_id" in sim
        assert "status" in sim
        assert "experiment_id" in sim
        assert "start_time" in sim
        assert "parameters_summary" in sim


# GetSimulationInfoTool Tests


def test_get_simulation_info_success(get_simulation_info_tool, test_simulation_id):
    """Test getting simulation info successfully."""
    result = get_simulation_info_tool(simulation_id=test_simulation_id)

    assert result["success"] is True
    assert result["data"]["simulation_id"] == test_simulation_id
    assert "status" in result["data"]
    assert "parameters" in result["data"]
    assert "db_path" in result["data"]


def test_get_simulation_info_not_found(get_simulation_info_tool):
    """Test getting nonexistent simulation."""
    result = get_simulation_info_tool(simulation_id="nonexistent_999")

    assert result["success"] is False
    assert result["error"]["type"] == "DatabaseError"
    assert "not found" in result["error"]["message"].lower()


def test_get_simulation_info_caching(get_simulation_info_tool, test_simulation_id):
    """Test that results are cached."""
    get_simulation_info_tool.cache.clear()

    result1 = get_simulation_info_tool(simulation_id=test_simulation_id)
    result2 = get_simulation_info_tool(simulation_id=test_simulation_id)

    assert result1["metadata"]["from_cache"] is False
    assert result2["metadata"]["from_cache"] is True


def test_get_simulation_info_response_fields(get_simulation_info_tool, test_simulation_id):
    """Test all expected fields are in response."""
    result = get_simulation_info_tool(simulation_id=test_simulation_id)

    assert result["success"] is True
    data = result["data"]

    # Check all required fields
    assert "simulation_id" in data
    assert "experiment_id" in data
    assert "status" in data
    assert "start_time" in data
    assert "end_time" in data
    assert "parameters" in data
    assert "results_summary" in data
    assert "db_path" in data


# ListExperimentsTool Tests


def test_list_experiments_basic(list_experiments_tool):
    """Test basic experiment listing."""
    result = list_experiments_tool()

    assert result["success"] is True
    assert "experiments" in result["data"]
    assert result["data"]["total_count"] >= 1  # At least one test experiment


def test_list_experiments_with_limit(list_experiments_tool):
    """Test listing experiments with limit."""
    result = list_experiments_tool(limit=1)

    assert result["success"] is True
    assert result["data"]["returned_count"] <= 1


def test_list_experiments_filter_by_status(list_experiments_tool):
    """Test filtering experiments by status."""
    result = list_experiments_tool(status="running")

    assert result["success"] is True
    for exp in result["data"]["experiments"]:
        assert exp["status"] == "running"


def test_list_experiments_response_structure(list_experiments_tool):
    """Test experiment response structure."""
    result = list_experiments_tool()

    if result["data"]["experiments"]:
        exp = result["data"]["experiments"][0]
        assert "experiment_id" in exp
        assert "name" in exp
        assert "status" in exp
        assert "simulation_count" in exp
        assert "tags" in exp


# GetExperimentInfoTool Tests


def test_get_experiment_info_success(get_experiment_info_tool):
    """Test getting experiment info."""
    result = get_experiment_info_tool(experiment_id="test_exp_001")

    assert result["success"] is True
    assert result["data"]["experiment_id"] == "test_exp_001"
    assert result["data"]["name"] == "Test Experiment 1"
    assert "simulation_count" in result["data"]


def test_get_experiment_info_not_found(get_experiment_info_tool):
    """Test getting nonexistent experiment."""
    result = get_experiment_info_tool(experiment_id="nonexistent_exp_999")

    assert result["success"] is False
    assert result["error"]["type"] == "DatabaseError"


def test_get_experiment_info_includes_simulation_count(get_experiment_info_tool):
    """Test that simulation count is included."""
    result = get_experiment_info_tool(experiment_id="test_exp_001")

    assert result["success"] is True
    assert "simulation_count" in result["data"]
    assert result["data"]["simulation_count"] >= 3  # We linked 3 simulations


def test_get_experiment_info_response_fields(get_experiment_info_tool):
    """Test all expected fields in experiment info."""
    result = get_experiment_info_tool(experiment_id="test_exp_001")

    assert result["success"] is True
    data = result["data"]

    assert "experiment_id" in data
    assert "name" in data
    assert "description" in data
    assert "hypothesis" in data
    assert "status" in data
    assert "variables" in data
    assert "tags" in data
    assert "simulation_count" in data


# Test validation errors


def test_tool_validates_limit_range(list_simulations_tool):
    """Test that limit is validated."""
    # Too small
    result = list_simulations_tool(limit=0)
    assert result["success"] is False

    # Too large
    result = list_simulations_tool(limit=2000)
    assert result["success"] is False


def test_tool_validates_offset_range(list_simulations_tool):
    """Test that offset is validated."""
    # Negative offset
    result = list_simulations_tool(offset=-1)
    assert result["success"] is False

    # Valid offset
    result = list_simulations_tool(offset=0)
    assert result["success"] is True