"""Unit tests for analysis tools."""

import pytest

from mcp.tools.analysis_tools import (
    AnalyzeAgentPerformanceTool,
    AnalyzePopulationDynamicsTool,
    AnalyzeReproductionTool,
    AnalyzeResourceEfficiencyTool,
    AnalyzeSocialPatternsTool,
    AnalyzeSurvivalRatesTool,
    IdentifyCriticalEventsTool,
)


@pytest.fixture
def analyze_population_tool(services):
    """Create AnalyzePopulationDynamicsTool instance."""
    db_service, cache_service = services
    return AnalyzePopulationDynamicsTool(db_service, cache_service)


@pytest.fixture
def analyze_survival_tool(services):
    """Create AnalyzeSurvivalRatesTool instance."""
    db_service, cache_service = services
    return AnalyzeSurvivalRatesTool(db_service, cache_service)


@pytest.fixture
def analyze_resource_tool(services):
    """Create AnalyzeResourceEfficiencyTool instance."""
    db_service, cache_service = services
    return AnalyzeResourceEfficiencyTool(db_service, cache_service)


@pytest.fixture
def analyze_agent_tool(services):
    """Create AnalyzeAgentPerformanceTool instance."""
    db_service, cache_service = services
    return AnalyzeAgentPerformanceTool(db_service, cache_service)


@pytest.fixture
def identify_events_tool(services):
    """Create IdentifyCriticalEventsTool instance."""
    db_service, cache_service = services
    return IdentifyCriticalEventsTool(db_service, cache_service)


@pytest.fixture
def analyze_social_tool(services):
    """Create AnalyzeSocialPatternsTool instance."""
    db_service, cache_service = services
    return AnalyzeSocialPatternsTool(db_service, cache_service)


@pytest.fixture
def analyze_reproduction_tool(services):
    """Create AnalyzeReproductionTool instance."""
    db_service, cache_service = services
    return AnalyzeReproductionTool(db_service, cache_service)


# AnalyzePopulationDynamicsTool Tests


def test_analyze_population_basic(analyze_population_tool, test_simulation_id):
    """Test basic population analysis."""
    result = analyze_population_tool(simulation_id=test_simulation_id)

    assert result["success"] is True
    assert "population_summary" in result["data"]
    assert "by_type" in result["data"]
    assert "time_series" in result["data"]


def test_analyze_population_summary_fields(analyze_population_tool, test_simulation_id):
    """Test population summary contains expected fields."""
    result = analyze_population_tool(simulation_id=test_simulation_id)

    summary = result["data"]["population_summary"]

    assert "initial_population" in summary
    assert "final_population" in summary
    assert "peak_population" in summary
    assert "peak_step" in summary
    assert "average_population" in summary
    assert "total_births" in summary
    assert "total_deaths" in summary
    assert "total_growth_rate_percent" in summary


def test_analyze_population_by_type(analyze_population_tool, test_simulation_id):
    """Test population breakdown by type."""
    result = analyze_population_tool(simulation_id=test_simulation_id)

    by_type = result["data"]["by_type"]

    assert "system" in by_type
    assert "independent" in by_type
    assert "control" in by_type

    # Each type should have statistics
    for agent_type in ["system", "independent", "control"]:
        assert "peak" in by_type[agent_type]
        assert "average" in by_type[agent_type]
        assert "final" in by_type[agent_type]


def test_analyze_population_step_range(analyze_population_tool, test_simulation_id):
    """Test population analysis with step range."""
    result = analyze_population_tool(
        simulation_id=test_simulation_id, start_step=10, end_step=50
    )

    assert result["success"] is True
    assert result["data"]["step_range"]["start"] == 10
    assert result["data"]["step_range"]["end"] == 50
    assert result["data"]["step_range"]["count"] == 41  # 10-50 inclusive


def test_analyze_population_with_chart(analyze_population_tool, test_simulation_id):
    """Test chart generation."""
    result = analyze_population_tool(
        simulation_id=test_simulation_id, include_chart=True
    )

    assert result["success"] is True
    assert "chart" in result["data"]
    assert isinstance(result["data"]["chart"], str)
    assert len(result["data"]["chart"]) > 0


def test_analyze_population_without_chart(analyze_population_tool, test_simulation_id):
    """Test analysis without chart."""
    result = analyze_population_tool(
        simulation_id=test_simulation_id, include_chart=False
    )

    assert result["success"] is True
    assert "chart" not in result["data"]


# AnalyzeSurvivalRatesTool Tests


def test_analyze_survival_by_generation(analyze_survival_tool, test_simulation_id):
    """Test survival analysis by generation."""
    result = analyze_survival_tool(simulation_id=test_simulation_id, group_by="generation")

    assert result["success"] is True
    assert result["data"]["grouped_by"] == "generation"
    assert "cohorts" in result["data"]
    assert "summary" in result["data"]


def test_analyze_survival_by_agent_type(analyze_survival_tool, test_simulation_id):
    """Test survival analysis by agent type."""
    result = analyze_survival_tool(simulation_id=test_simulation_id, group_by="agent_type")

    assert result["success"] is True
    assert result["data"]["grouped_by"] == "agent_type"


def test_analyze_survival_cohort_structure(analyze_survival_tool, test_simulation_id):
    """Test cohort data structure."""
    result = analyze_survival_tool(simulation_id=test_simulation_id, group_by="generation")

    cohorts = result["data"]["cohorts"]

    # At least one cohort should exist
    if cohorts:
        cohort_key = list(cohorts.keys())[0]
        cohort = cohorts[cohort_key]

        assert "total_agents" in cohort
        assert "alive" in cohort
        assert "dead" in cohort
        assert "survival_rate_percent" in cohort


def test_analyze_survival_summary(analyze_survival_tool, test_simulation_id):
    """Test survival summary."""
    result = analyze_survival_tool(simulation_id=test_simulation_id, group_by="generation")

    summary = result["data"]["summary"]

    assert "total_groups" in summary
    assert "total_agents" in summary
    assert "overall_survival_rate" in summary


# AnalyzeResourceEfficiencyTool Tests


def test_analyze_resource_efficiency_basic(analyze_resource_tool, test_simulation_id):
    """Test basic resource efficiency analysis."""
    result = analyze_resource_tool(simulation_id=test_simulation_id)

    assert result["success"] is True
    assert "resource_summary" in result["data"]
    assert "agent_resource_metrics" in result["data"]


def test_analyze_resource_summary_fields(analyze_resource_tool, test_simulation_id):
    """Test resource summary fields."""
    result = analyze_resource_tool(simulation_id=test_simulation_id)

    summary = result["data"]["resource_summary"]

    assert "initial_total_resources" in summary
    assert "final_total_resources" in summary
    assert "peak_total_resources" in summary
    assert "average_total_resources" in summary
    assert "total_consumed" in summary


# AnalyzeAgentPerformanceTool Tests


def test_analyze_agent_performance_basic(analyze_agent_tool, test_simulation_id, test_agent_id):
    """Test basic agent performance analysis."""
    result = analyze_agent_tool(simulation_id=test_simulation_id, agent_id=test_agent_id)

    assert result["success"] is True
    assert result["data"]["agent_id"] == test_agent_id


def test_analyze_agent_performance_fields(analyze_agent_tool, test_simulation_id, test_agent_id):
    """Test agent performance fields."""
    result = analyze_agent_tool(simulation_id=test_simulation_id, agent_id=test_agent_id)

    data = result["data"]

    assert "agent_id" in data
    assert "agent_type" in data
    assert "generation" in data
    assert "status" in data
    assert "lifespan" in data
    assert "performance_metrics" in data


def test_analyze_agent_performance_invalid_agent(analyze_agent_tool, test_simulation_id):
    """Test with invalid agent ID."""
    result = analyze_agent_tool(simulation_id=test_simulation_id, agent_id="invalid_999")

    assert result["success"] is True  # Returns success with error message
    assert "error" in result["data"]


# IdentifyCriticalEventsTool Tests


def test_identify_critical_events_basic(identify_events_tool, test_simulation_id):
    """Test basic event identification."""
    result = identify_events_tool(simulation_id=test_simulation_id, threshold_percent=10.0)

    assert result["success"] is True
    assert "events" in result["data"]
    assert "summary" in result["data"]


def test_identify_critical_events_threshold(identify_events_tool, test_simulation_id):
    """Test that threshold affects detection."""
    # High threshold - fewer events
    result_high = identify_events_tool(
        simulation_id=test_simulation_id, threshold_percent=50.0
    )

    # Low threshold - more events
    result_low = identify_events_tool(simulation_id=test_simulation_id, threshold_percent=5.0)

    assert result_high["success"] is True
    assert result_low["success"] is True

    # Lower threshold should detect more or equal events
    assert len(result_low["data"]["events"]) >= len(result_high["data"]["events"])


def test_identify_critical_events_structure(identify_events_tool, test_simulation_id):
    """Test event structure."""
    result = identify_events_tool(simulation_id=test_simulation_id, threshold_percent=5.0)

    if result["data"]["events"]:
        event = result["data"]["events"][0]
        assert "type" in event
        assert "step" in event
        assert "description" in event
        assert "severity" in event


# AnalyzeSocialPatternsTool Tests


def test_analyze_social_patterns_basic(analyze_social_tool, test_simulation_id):
    """Test social pattern analysis."""
    result = analyze_social_tool(simulation_id=test_simulation_id, limit=100)

    assert result["success"] is True
    # May or may not have interactions depending on simulation


# AnalyzeReproductionTool Tests


def test_analyze_reproduction_basic(analyze_reproduction_tool, test_simulation_id):
    """Test reproduction analysis."""
    result = analyze_reproduction_tool(simulation_id=test_simulation_id)

    assert result["success"] is True
    # We created one reproduction event
    if "total_attempts" in result["data"]:
        assert result["data"]["total_attempts"] >= 1


def test_analyze_reproduction_with_events(analyze_reproduction_tool, test_simulation_id):
    """Test reproduction analysis with events."""
    result = analyze_reproduction_tool(simulation_id=test_simulation_id)

    if "total_attempts" in result["data"]:
        data = result["data"]
        assert "successful" in data
        assert "failed" in data
        assert "success_rate_percent" in data
        assert "resource_analysis" in data


def test_analyze_population_no_data(analyze_population_tool):
    """Test population analysis with no data."""
    # Create a simulation with no steps
    result = analyze_population_tool(
        simulation_id="test_sim_001", start_step=9999, end_step=10000
    )

    assert result["success"] is True
    if "error" in result["data"]:
        assert "No data found" in result["data"]["error"]


def test_analyze_survival_no_agents(analyze_survival_tool):
    """Test survival analysis with simulation that has no agents."""
    # test_sim_004 has no agents
    result = analyze_survival_tool(simulation_id="test_sim_004", group_by="generation")

    assert result["success"] is True
    if "error" in result["data"]:
        assert "No agents" in result["data"]["error"]


def test_analyze_resource_step_range(analyze_resource_tool, test_simulation_id):
    """Test resource efficiency with step range."""
    result = analyze_resource_tool(
        simulation_id=test_simulation_id, start_step=0, end_step=50
    )

    assert result["success"] is True
    assert result["data"]["step_range"]["start"] == 0
    assert result["data"]["step_range"]["end"] == 50


def test_identify_events_high_threshold(identify_events_tool, test_simulation_id):
    """Test event detection with very high threshold."""
    result = identify_events_tool(simulation_id=test_simulation_id, threshold_percent=99.0)

    assert result["success"] is True
    # Very high threshold should detect fewer or no events
    assert "events" in result["data"]


def test_identify_events_summary_structure(identify_events_tool, test_simulation_id):
    """Test event summary structure."""
    result = identify_events_tool(simulation_id=test_simulation_id, threshold_percent=10.0)

    assert "summary" in result["data"]
    summary = result["data"]["summary"]
    assert "total_events" in summary