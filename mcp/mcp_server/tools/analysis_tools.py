"""Analysis tools for advanced simulation data analysis and insights."""

from typing import List, Optional

import numpy as np
from mcp_server.models.database_models import (
    AgentModel,
    ReproductionEventModel,
    SimulationStepModel,
    SocialInteractionModel,
)
from mcp_server.tools.base import ToolBase
from mcp_server.utils.exceptions import SimulationNotFoundError
from pydantic import BaseModel, Field


class AnalyzePopulationDynamicsParams(BaseModel):
    """Parameters for population dynamics analysis."""

    simulation_id: str = Field(..., description="Simulation ID to analyze")
    start_step: Optional[int] = Field(None, ge=0, description="Start step (inclusive)")
    end_step: Optional[int] = Field(None, ge=0, description="End step (inclusive)")
    include_chart: bool = Field(False, description="Include ASCII chart visualization")


class AnalyzePopulationDynamicsTool(ToolBase):
    """Analyze population dynamics over time."""

    # Chart configuration constants
    MAX_CHART_DATA_POINTS = 50
    CHART_HEIGHT = 10

    @property
    def name(self) -> str:
        return "analyze_population_dynamics"

    @property
    def description(self) -> str:
        return """
        Analyze how agent populations evolve over simulation time.
        
        Returns comprehensive population analysis including:
        - Total population trends
        - Breakdown by agent type
        - Birth and death rates
        - Population growth rate
        - Peak population metrics
        - Optional ASCII chart visualization
        
        Use this to:
        - Understand population trends
        - Identify population crashes or booms
        - Compare different agent types' success
        - Detect critical demographic events
        """

    @property
    def parameters_schema(self):
        return AnalyzePopulationDynamicsParams

    def execute(self, **params):
        """Execute population dynamics analysis."""
        if not self.db.validate_simulation_exists(params["simulation_id"]):
            raise SimulationNotFoundError(params["simulation_id"])

        def query_func(session):
            # Build query for simulation steps
            query = session.query(SimulationStepModel).filter(
                SimulationStepModel.simulation_id == params["simulation_id"]
            )

            # Apply step range filters
            if params.get("start_step") is not None:
                query = query.filter(SimulationStepModel.step_number >= params["start_step"])
            if params.get("end_step") is not None:
                query = query.filter(SimulationStepModel.step_number <= params["end_step"])

            query = query.order_by(SimulationStepModel.step_number)
            steps = query.all()

            if not steps:
                return {"error": "No data found for specified range"}

            # Extract time series data
            step_numbers = [s.step_number for s in steps]
            total_agents = [s.total_agents for s in steps]
            system_agents = [s.system_agents or 0 for s in steps]
            independent_agents = [s.independent_agents or 0 for s in steps]
            control_agents = [s.control_agents or 0 for s in steps]
            births = [s.births for s in steps]
            deaths = [s.deaths for s in steps]

            # Calculate statistics
            peak_population = max(total_agents)
            peak_step = step_numbers[total_agents.index(peak_population)]
            final_population = total_agents[-1]
            initial_population = total_agents[0]

            # Growth rate calculation
            if initial_population > 0:
                total_growth_rate = (
                    (final_population - initial_population) / initial_population
                ) * 100
            else:
                total_growth_rate = 0

            result = {
                "step_range": {
                    "start": step_numbers[0],
                    "end": step_numbers[-1],
                    "count": len(steps),
                },
                "population_summary": {
                    "initial_population": initial_population,
                    "final_population": final_population,
                    "peak_population": peak_population,
                    "peak_step": peak_step,
                    "average_population": float(np.mean(total_agents)),
                    "population_std": float(np.std(total_agents)),
                    "total_growth_rate_percent": round(total_growth_rate, 2),
                    "total_births": sum(births),
                    "total_deaths": sum(deaths),
                    "net_change": sum(births) - sum(deaths),
                },
                "by_type": {
                    "system": {
                        "peak": max(system_agents),
                        "average": float(np.mean(system_agents)),
                        "final": system_agents[-1],
                    },
                    "independent": {
                        "peak": max(independent_agents),
                        "average": float(np.mean(independent_agents)),
                        "final": independent_agents[-1],
                    },
                    "control": {
                        "peak": max(control_agents),
                        "average": float(np.mean(control_agents)),
                        "final": control_agents[-1],
                    },
                },
                "time_series": {
                    "steps": step_numbers,
                    "total_agents": total_agents,
                    "system_agents": system_agents,
                    "independent_agents": independent_agents,
                    "control_agents": control_agents,
                    "births": births,
                    "deaths": deaths,
                },
            }

            # Add simple ASCII chart if requested
            if params.get("include_chart"):
                result["chart"] = self._create_simple_chart(step_numbers, total_agents)

            return result

        return self.db.execute_query(query_func)

    def _create_simple_chart(self, steps: List[int], values: List[int]) -> str:
        """Create a simple ASCII chart."""
        if not values:
            return "No data to chart"

        # Sample data if too many points
        if len(values) > self.MAX_CHART_DATA_POINTS:
            step_size = len(values) // self.MAX_CHART_DATA_POINTS
            steps = steps[::step_size]
            values = values[::step_size]

        max_val = max(values)
        min_val = min(values)
        height = self.CHART_HEIGHT

        chart_lines = []
        chart_lines.append(f"\nPopulation Over Time (Max: {max_val}, Min: {min_val})")
        chart_lines.append("-" * 60)

        # Create chart
        for h in range(height, -1, -1):
            line = []
            threshold = min_val + (max_val - min_val) * h / height
            for val in values:
                if val >= threshold:
                    line.append("█")
                else:
                    line.append(" ")
            chart_lines.append("".join(line))

        chart_lines.append("-" * 60)
        chart_lines.append(f"Step: {steps[0]}" + " " * 40 + f"{steps[-1]}")

        return "\n".join(chart_lines)


class AnalyzeSurvivalRatesParams(BaseModel):
    """Parameters for survival rate analysis."""

    simulation_id: str = Field(..., description="Simulation ID to analyze")
    group_by: str = Field("generation", description="Group by 'generation' or 'agent_type'")


class AnalyzeSurvivalRatesTool(ToolBase):
    """Analyze agent survival rates by cohort."""

    @property
    def name(self) -> str:
        return "analyze_survival_rates"

    @property
    def description(self) -> str:
        return """
        Analyze agent survival rates grouped by generation or agent type.
        
        Returns survival analysis including:
        - Survival rates by cohort
        - Average lifespan statistics
        - Death causes (if available)
        - Cohort comparison
        
        Use this to:
        - Compare survival across generations
        - Identify which agent types survive longer
        - Detect survival patterns
        - Analyze evolutionary fitness
        """

    @property
    def parameters_schema(self):
        return AnalyzeSurvivalRatesParams

    def execute(self, **params):
        """Execute survival rate analysis."""
        if not self.db.validate_simulation_exists(params["simulation_id"]):
            raise SimulationNotFoundError(params["simulation_id"])

        def query_func(session):
            # Get all agents
            agents = (
                session.query(AgentModel)
                .filter(AgentModel.simulation_id == params["simulation_id"])
                .all()
            )

            if not agents:
                return {"error": "No agents found"}

            # Group by specified field
            group_field = params["group_by"]
            groups = {}

            for agent in agents:
                if group_field == "generation":
                    key = agent.generation
                elif group_field == "agent_type":
                    key = agent.agent_type
                else:
                    key = "all"

                if key not in groups:
                    groups[key] = {"alive": 0, "dead": 0, "lifespans": []}

                if agent.death_time is None:
                    groups[key]["alive"] += 1
                else:
                    groups[key]["dead"] += 1
                    lifespan = agent.death_time - agent.birth_time
                    groups[key]["lifespans"].append(lifespan)

            # Calculate statistics for each group
            results = {}
            for key, data in groups.items():
                total = data["alive"] + data["dead"]
                survival_rate = (data["alive"] / total * 100) if total > 0 else 0

                if data["lifespans"]:
                    avg_lifespan = float(np.mean(data["lifespans"]))
                    median_lifespan = float(np.median(data["lifespans"]))
                    max_lifespan = max(data["lifespans"])
                    min_lifespan = min(data["lifespans"])
                else:
                    avg_lifespan = median_lifespan = max_lifespan = min_lifespan = None

                results[str(key)] = {
                    "total_agents": total,
                    "alive": data["alive"],
                    "dead": data["dead"],
                    "survival_rate_percent": round(survival_rate, 2),
                    "average_lifespan": round(avg_lifespan, 2) if avg_lifespan else None,
                    "median_lifespan": median_lifespan,
                    "max_lifespan": max_lifespan,
                    "min_lifespan": min_lifespan,
                }

            return {
                "grouped_by": group_field,
                "cohorts": results,
                "summary": {
                    "total_groups": len(results),
                    "total_agents": sum(r["total_agents"] for r in results.values()),
                    "overall_survival_rate": round(
                        sum(r["alive"] for r in results.values())
                        / sum(r["total_agents"] for r in results.values())
                        * 100,
                        2,
                    ),
                },
            }

        return self.db.execute_query(query_func)


class AnalyzeResourceEfficiencyParams(BaseModel):
    """Parameters for resource efficiency analysis."""

    simulation_id: str = Field(..., description="Simulation ID to analyze")
    start_step: Optional[int] = Field(None, ge=0, description="Start step (inclusive)")
    end_step: Optional[int] = Field(None, ge=0, description="End step (inclusive)")


class AnalyzeResourceEfficiencyTool(ToolBase):
    """Analyze resource utilization efficiency."""

    @property
    def name(self) -> str:
        return "analyze_resource_efficiency"

    @property
    def description(self) -> str:
        return """
        Analyze resource utilization and efficiency metrics.
        
        Returns efficiency analysis including:
        - Resource consumption trends
        - Efficiency ratios over time
        - Resource distribution metrics
        - Agent resource holdings
        
        Use this to:
        - Understand resource usage patterns
        - Identify resource bottlenecks
        - Measure efficiency improvements
        - Detect resource scarcity events
        """

    @property
    def parameters_schema(self):
        return AnalyzeResourceEfficiencyParams

    def execute(self, **params):
        """Execute resource efficiency analysis."""
        if not self.db.validate_simulation_exists(params["simulation_id"]):
            raise SimulationNotFoundError(params["simulation_id"])

        def query_func(session):
            # Get simulation steps with resource metrics
            query = session.query(SimulationStepModel).filter(
                SimulationStepModel.simulation_id == params["simulation_id"]
            )

            if params.get("start_step") is not None:
                query = query.filter(SimulationStepModel.step_number >= params["start_step"])
            if params.get("end_step") is not None:
                query = query.filter(SimulationStepModel.step_number <= params["end_step"])

            query = query.order_by(SimulationStepModel.step_number)
            steps = query.all()

            if not steps:
                return {"error": "No data found"}

            # Extract resource metrics
            total_resources = [s.total_resources for s in steps]
            avg_agent_resources = [s.average_agent_resources for s in steps]
            efficiency = [s.resource_efficiency for s in steps if s.resource_efficiency]
            entropy = [
                s.resource_distribution_entropy for s in steps if s.resource_distribution_entropy
            ]
            consumed = [s.resources_consumed or 0 for s in steps]

            # Calculate statistics
            result = {
                "step_range": {"start": steps[0].step_number, "end": steps[-1].step_number},
                "resource_summary": {
                    "initial_total_resources": total_resources[0],
                    "final_total_resources": total_resources[-1],
                    "peak_total_resources": max(total_resources),
                    "average_total_resources": float(np.mean(total_resources)),
                    "total_consumed": sum(consumed),
                },
                "agent_resource_metrics": {
                    "peak_avg_per_agent": max(avg_agent_resources),
                    "average_per_agent": float(np.mean(avg_agent_resources)),
                    "final_avg_per_agent": avg_agent_resources[-1],
                },
            }

            if efficiency:
                result["efficiency_metrics"] = {
                    "average_efficiency": float(np.mean(efficiency)),
                    "peak_efficiency": max(efficiency),
                    "final_efficiency": efficiency[-1],
                }

            if entropy:
                result["distribution_metrics"] = {
                    "average_entropy": float(np.mean(entropy)),
                    "peak_entropy": max(entropy),
                    "final_entropy": entropy[-1],
                }

            return result

        return self.db.execute_query(query_func)


class AnalyzeAgentPerformanceParams(BaseModel):
    """Parameters for agent performance analysis."""

    simulation_id: str = Field(..., description="Simulation ID to analyze")
    agent_id: str = Field(..., description="Agent ID to analyze")


class AnalyzeAgentPerformanceTool(ToolBase):
    """Analyze individual agent performance."""

    @property
    def name(self) -> str:
        return "analyze_agent_performance"

    @property
    def description(self) -> str:
        return """
        Analyze the performance of a specific agent.
        
        Returns performance analysis including:
        - Lifespan and survival
        - Total rewards accumulated
        - Resource acquisition
        - Action distribution
        - Health trajectory
        
        Use this to:
        - Evaluate individual agent success
        - Identify successful strategies
        - Compare agent behaviors
        - Debug agent issues
        """

    @property
    def parameters_schema(self):
        return AnalyzeAgentPerformanceParams

    def execute(self, **params):
        """Execute agent performance analysis."""
        if not self.db.validate_simulation_exists(params["simulation_id"]):
            raise SimulationNotFoundError(params["simulation_id"])

        def query_func(session):
            # Get agent info
            agent = (
                session.query(AgentModel)
                .filter(
                    AgentModel.simulation_id == params["simulation_id"],
                    AgentModel.agent_id == params["agent_id"],
                )
                .first()
            )

            if not agent:
                return {"error": f"Agent {params['agent_id']} not found"}

            # Calculate lifespan
            if agent.death_time is not None:
                lifespan = agent.death_time - agent.birth_time
                status = "dead"
            else:
                # Get current step to estimate lifespan
                latest_step = (
                    session.query(SimulationStepModel)
                    .filter(SimulationStepModel.simulation_id == params["simulation_id"])
                    .order_by(SimulationStepModel.step_number.desc())
                    .first()
                )
                lifespan = latest_step.step_number - agent.birth_time if latest_step else 0
                status = "alive"

            result = {
                "agent_id": agent.agent_id,
                "agent_type": agent.agent_type,
                "generation": agent.generation,
                "status": status,
                "lifespan": lifespan,
                "birth_time": agent.birth_time,
                "death_time": agent.death_time,
                "performance_metrics": {
                    "initial_resources": agent.initial_resources,
                    "starting_health": agent.starting_health,
                    "genome_id": agent.genome_id,
                },
            }

            return result

        return self.db.execute_query(query_func)


class IdentifyCriticalEventsParams(BaseModel):
    """Parameters for critical events identification."""

    simulation_id: str = Field(..., description="Simulation ID to analyze")
    threshold_percent: float = Field(
        10.0, ge=0, le=100, description="Population change threshold percentage"
    )


class IdentifyCriticalEventsTool(ToolBase):
    """Identify critical events in simulation."""

    @property
    def name(self) -> str:
        return "identify_critical_events"

    @property
    def description(self) -> str:
        return """
        Identify significant events during simulation.
        
        Detects critical events such as:
        - Population crashes (>threshold% decline)
        - Population booms (>threshold% growth)
        - Resource depletion events
        - Mass death events
        - Generation milestones
        
        Use this to:
        - Find turning points in simulation
        - Identify crisis moments
        - Detect emergent behaviors
        - Analyze simulation stability
        """

    @property
    def parameters_schema(self):
        return IdentifyCriticalEventsParams

    def execute(self, **params):
        """Execute critical events identification."""
        if not self.db.validate_simulation_exists(params["simulation_id"]):
            raise SimulationNotFoundError(params["simulation_id"])

        def query_func(session):
            # Get simulation steps
            steps = (
                session.query(SimulationStepModel)
                .filter(SimulationStepModel.simulation_id == params["simulation_id"])
                .order_by(SimulationStepModel.step_number)
                .all()
            )

            if len(steps) < 2:
                return {"events": [], "summary": "Insufficient data"}

            events = []
            threshold = params["threshold_percent"]

            # Detect population changes
            for i in range(1, len(steps)):
                prev_pop = steps[i - 1].total_agents
                curr_pop = steps[i].total_agents

                if prev_pop > 0:
                    change_percent = ((curr_pop - prev_pop) / prev_pop) * 100

                    if change_percent <= -threshold:
                        events.append(
                            {
                                "type": "population_crash",
                                "step": steps[i].step_number,
                                "description": f"Population dropped {abs(change_percent):.1f}% ({prev_pop} → {curr_pop})",
                                "severity": "high" if abs(change_percent) > 30 else "medium",
                            }
                        )
                    elif change_percent >= threshold:
                        events.append(
                            {
                                "type": "population_boom",
                                "step": steps[i].step_number,
                                "description": f"Population grew {change_percent:.1f}% ({prev_pop} → {curr_pop})",
                                "severity": "medium",
                            }
                        )

                # Detect mass death events
                if steps[i].deaths > 10:  # Arbitrary threshold
                    events.append(
                        {
                            "type": "mass_death",
                            "step": steps[i].step_number,
                            "description": f"{steps[i].deaths} deaths in single step",
                            "severity": "high" if steps[i].deaths > 20 else "medium",
                        }
                    )

                # Detect generation milestones
                if i > 0 and steps[i].current_max_generation > steps[i - 1].current_max_generation:
                    events.append(
                        {
                            "type": "new_generation",
                            "step": steps[i].step_number,
                            "description": f"Generation {steps[i].current_max_generation} reached",
                            "severity": "low",
                        }
                    )

            return {
                "events": events,
                "summary": {
                    "total_events": len(events),
                    "by_type": {
                        event_type: len([e for e in events if e["type"] == event_type])
                        for event_type in set(e["type"] for e in events)
                    },
                    "by_severity": {
                        severity: len([e for e in events if e["severity"] == severity])
                        for severity in set(e["severity"] for e in events)
                    },
                },
            }

        return self.db.execute_query(query_func)


class AnalyzeSocialPatternsParams(BaseModel):
    """Parameters for social pattern analysis."""

    simulation_id: str = Field(..., description="Simulation ID to analyze")
    limit: int = Field(1000, ge=1, le=10000, description="Max interactions to analyze")


class AnalyzeSocialPatternsTool(ToolBase):
    """Analyze social interaction patterns."""

    @property
    def name(self) -> str:
        return "analyze_social_patterns"

    @property
    def description(self) -> str:
        return """
        Analyze social interaction patterns between agents.
        
        Returns social analysis including:
        - Interaction type distribution
        - Most social agents
        - Cooperation vs competition rates
        - Resource sharing patterns
        
        Use this to:
        - Understand social dynamics
        - Identify cooperation patterns
        - Detect social hierarchies
        - Analyze group behaviors
        """

    @property
    def parameters_schema(self):
        return AnalyzeSocialPatternsParams

    def execute(self, **params):
        """Execute social pattern analysis."""
        if not self.db.validate_simulation_exists(params["simulation_id"]):
            raise SimulationNotFoundError(params["simulation_id"])

        def query_func(session):
            # Get social interactions
            interactions = (
                session.query(SocialInteractionModel)
                .filter(SocialInteractionModel.simulation_id == params["simulation_id"])
                .limit(params["limit"])
                .all()
            )

            if not interactions:
                return {"message": "No social interactions found"}

            # Analyze interaction types
            type_counts = {}
            outcome_counts = {}
            total_resources_shared = 0

            for interaction in interactions:
                # Count interaction types
                itype = interaction.interaction_type
                type_counts[itype] = type_counts.get(itype, 0) + 1

                # Count outcomes
                outcome = interaction.outcome
                outcome_counts[outcome] = outcome_counts.get(outcome, 0) + 1

                # Sum resources transferred
                if interaction.resources_transferred:
                    total_resources_shared += interaction.resources_transferred

            return {
                "total_interactions": len(interactions),
                "interaction_types": type_counts,
                "outcomes": outcome_counts,
                "resource_sharing": {
                    "total_resources_transferred": round(total_resources_shared, 2),
                    "average_per_interaction": (
                        round(total_resources_shared / len(interactions), 2) if interactions else 0
                    ),
                },
            }

        return self.db.execute_query(query_func)


class AnalyzeReproductionParams(BaseModel):
    """Parameters for reproduction analysis."""

    simulation_id: str = Field(..., description="Simulation ID to analyze")


class AnalyzeReproductionTool(ToolBase):
    """Analyze reproduction success rates and patterns."""

    @property
    def name(self) -> str:
        return "analyze_reproduction"

    @property
    def description(self) -> str:
        return """
        Analyze reproduction attempts and success rates.
        
        Returns reproduction analysis including:
        - Success/failure rates
        - Resource costs
        - Generation progression
        - Failure reasons
        
        Use this to:
        - Evaluate reproductive fitness
        - Understand population growth
        - Identify reproduction barriers
        - Analyze evolutionary success
        """

    @property
    def parameters_schema(self):
        return AnalyzeReproductionParams

    def execute(self, **params):
        """Execute reproduction analysis."""
        if not self.db.validate_simulation_exists(params["simulation_id"]):
            raise SimulationNotFoundError(params["simulation_id"])

        def query_func(session):
            # Get reproduction events
            events = (
                session.query(ReproductionEventModel)
                .filter(ReproductionEventModel.simulation_id == params["simulation_id"])
                .all()
            )

            if not events:
                return {"message": "No reproduction events found"}

            successful = [e for e in events if e.success]
            failed = [e for e in events if not e.success]

            # Analyze success rates
            total_events = len(events)
            success_rate = (len(successful) / total_events * 100) if total_events > 0 else 0

            # Analyze resource costs
            resource_costs = [
                e.parent_resources_before - e.parent_resources_after for e in successful
            ]
            avg_cost = float(np.mean(resource_costs)) if resource_costs else 0

            # Analyze failure reasons
            failure_reasons = {}
            for event in failed:
                reason = event.failure_reason or "unknown"
                failure_reasons[reason] = failure_reasons.get(reason, 0) + 1

            return {
                "total_attempts": total_events,
                "successful": len(successful),
                "failed": len(failed),
                "success_rate_percent": round(success_rate, 2),
                "resource_analysis": {
                    "average_cost": round(avg_cost, 2),
                    "min_cost": min(resource_costs) if resource_costs else None,
                    "max_cost": max(resource_costs) if resource_costs else None,
                },
                "failure_reasons": failure_reasons,
                "generation_progression": {
                    "max_offspring_generation": (
                        max(e.offspring_generation for e in successful if e.offspring_generation)
                        if successful
                        else None
                    )
                },
            }

        return self.db.execute_query(query_func)
