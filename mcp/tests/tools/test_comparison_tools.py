"""Unit tests for comparison tools."""

import pytest

from mcp_server.tools.comparison_tools import (
    CompareGenerationsTool,
    CompareParametersTool,
    CompareSimulationsTool,
    RankConfigurationsTool,
)


@pytest.fixture
def compare_simulations_tool(services):
    """Create CompareSimulationsTool instance."""
    db_service, cache_service = services
    return CompareSimulationsTool(db_service, cache_service)


@pytest.fixture
def compare_parameters_tool(services):
    """Create CompareParametersTool instance."""
    db_service, cache_service = services
    return CompareParametersTool(db_service, cache_service)


@pytest.fixture
def rank_configurations_tool(services):
    """Create RankConfigurationsTool instance."""
    db_service, cache_service = services
    return RankConfigurationsTool(db_service, cache_service)


@pytest.fixture
def compare_generations_tool(services):
    """Create CompareGenerationsTool instance."""
    db_service, cache_service = services
    return CompareGenerationsTool(db_service, cache_service)


# CompareSimulationsTool Tests


def test_compare_simulations_basic(compare_simulations_tool):
    """Test basic simulation comparison."""
    result = compare_simulations_tool(simulation_ids=["test_sim_000", "test_sim_001"])

    assert result["success"] is True
    assert result["data"]["simulation_count"] == 2
    assert "simulations" in result["data"]
    assert "pairwise_comparisons" in result["data"]
    assert "rankings" in result["data"]


def test_compare_simulations_validation_min_sims(compare_simulations_tool):
    """Test that at least 2 simulations are required."""
    result = compare_simulations_tool(simulation_ids=["test_sim_000"])

    # Should fail validation (min 2 simulations)
    assert result["success"] is False


def test_compare_simulations_custom_metrics(compare_simulations_tool):
    """Test comparing specific metrics."""
    result = compare_simulations_tool(
        simulation_ids=["test_sim_000", "test_sim_001"],
        metrics=["total_agents", "births"],
    )

    assert result["success"] is True
    assert result["data"]["metrics_compared"] == ["total_agents", "births"]


def test_compare_simulations_rankings(compare_simulations_tool):
    """Test that rankings are generated."""
    result = compare_simulations_tool(simulation_ids=["test_sim_000", "test_sim_001"])

    rankings = result["data"]["rankings"]

    # Should have rankings for each metric
    for metric in result["data"]["metrics_compared"]:
        assert metric in rankings
        # Each ranking should be a list
        assert isinstance(rankings[metric], list)


# CompareParametersTool Tests


def test_compare_parameters_basic(compare_parameters_tool):
    """Test basic parameter comparison."""
    result = compare_parameters_tool(parameter_name="agents", outcome_metric="total_agents")

    assert result["success"] is True or "message" in result["data"]


def test_compare_parameters_with_sim_ids(compare_parameters_tool):
    """Test parameter comparison with specific simulations."""
    result = compare_parameters_tool(
        parameter_name="seed",
        simulation_ids=["test_sim_000", "test_sim_001", "test_sim_002"],
        outcome_metric="total_agents",
    )

    # May succeed or indicate not enough variance
    assert "parameter" in result["data"] or "message" in result["data"]


def test_compare_parameters_response_structure(compare_parameters_tool):
    """Test response structure when groups found."""
    result = compare_parameters_tool(parameter_name="agents", outcome_metric="total_agents")

    if "groups" in result["data"]:
        assert "parameter" in result["data"]
        assert "outcome_metric" in result["data"]
        assert "groups_count" in result["data"]


# RankConfigurationsTool Tests


def test_rank_configurations_basic(rank_configurations_tool):
    """Test basic configuration ranking."""
    result = rank_configurations_tool(metric_name="total_agents", aggregation="mean")

    assert result["success"] is True
    assert "rankings" in result["data"]
    assert "metric" in result["data"]
    assert "aggregation" in result["data"]


def test_rank_configurations_aggregation_methods(rank_configurations_tool):
    """Test different aggregation methods."""
    for aggregation in ["mean", "final", "max", "min"]:
        result = rank_configurations_tool(
            metric_name="total_agents", aggregation=aggregation, limit=5
        )

        assert result["success"] is True
        assert result["data"]["aggregation"] == aggregation


def test_rank_configurations_response_structure(rank_configurations_tool):
    """Test ranking response structure."""
    result = rank_configurations_tool(metric_name="total_agents")

    if result["data"]["rankings"]:
        ranking = result["data"]["rankings"][0]

        assert "rank" in ranking
        assert "simulation_id" in ranking
        assert "score" in ranking
        assert "status" in ranking
        assert "parameters" in ranking
        assert "steps_analyzed" in ranking


def test_rank_configurations_statistics(rank_configurations_tool):
    """Test that statistics are calculated."""
    result = rank_configurations_tool(metric_name="total_agents")

    assert "statistics" in result["data"]
    stats = result["data"]["statistics"]

    if result["data"]["total_ranked"] > 0:
        assert "mean_score" in stats
        assert "std_score" in stats
        assert "score_range" in stats


def test_rank_configurations_status_filter(rank_configurations_tool):
    """Test filtering by status."""
    result = rank_configurations_tool(
        metric_name="total_agents", status_filter="completed", limit=10
    )

    assert result["success"] is True
    # All ranked should have completed status
    for ranking in result["data"]["rankings"]:
        assert ranking["status"] == "completed"


# CompareGenerationsTool Tests


def test_compare_generations_basic(compare_generations_tool, test_simulation_id):
    """Test basic generation comparison."""
    result = compare_generations_tool(simulation_id=test_simulation_id, max_generations=5)

    assert result["success"] is True
    assert "generations" in result["data"]
    assert "total_generations" in result["data"]


def test_compare_generations_structure(compare_generations_tool, test_simulation_id):
    """Test generation comparison structure."""
    result = compare_generations_tool(simulation_id=test_simulation_id)

    if result["data"]["total_generations"] > 0:
        generations = result["data"]["generations"]
        gen_key = list(generations.keys())[0]
        gen_data = generations[gen_key]

        assert "generation" in gen_data
        assert "total_agents" in gen_data
        assert "alive" in gen_data
        assert "dead" in gen_data
        assert "survival_rate_percent" in gen_data


def test_compare_generations_summary(compare_generations_tool, test_simulation_id):
    """Test generation comparison summary."""
    result = compare_generations_tool(simulation_id=test_simulation_id)

    summary = result["data"]["summary"]

    assert "total_agents" in summary
    assert "best_survival_generation" in summary


def test_compare_generations_max_limit(compare_generations_tool, test_simulation_id):
    """Test max generations limit."""
    result = compare_generations_tool(simulation_id=test_simulation_id, max_generations=2)

    assert result["success"] is True
    assert result["data"]["generations_analyzed"] <= 2