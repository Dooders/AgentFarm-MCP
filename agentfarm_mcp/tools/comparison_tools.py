"""Comparison tools for multi-simulation analysis and parameter impact studies."""

from typing import Dict, List, Optional

import numpy as np
from pydantic import BaseModel, Field

from ..models.database_models import Simulation, SimulationStepModel
from .base import ToolBase
from ..utils.exceptions import SimulationNotFoundError, ValidationError


class CompareSimulationsParams(BaseModel):
    """Parameters for comparing simulations."""

    simulation_ids: List[str] = Field(
        ..., min_length=2, max_length=10, description="List of simulation IDs to compare (2-10)"
    )
    metrics: Optional[List[str]] = Field(
        None,
        description="Metrics to compare (e.g., 'total_agents', 'average_reward'). Uses defaults if not specified.",
    )


class CompareSimulationsTool(ToolBase):
    """Compare metrics across multiple simulations."""

    @property
    def name(self) -> str:
        return "compare_simulations"

    @property
    def description(self) -> str:
        return """
        Compare metrics across multiple simulations.
        
        Returns comparative analysis including:
        - Statistics for each simulation (mean, std, min, max)
        - Pairwise differences
        - Ranking by metrics
        - Parameter differences
        
        Use this to:
        - Compare experiment outcomes
        - Identify best-performing configurations
        - Understand parameter impacts
        - Validate hypotheses
        """

    @property
    def parameters_schema(self):
        return CompareSimulationsParams

    def execute(self, **params):
        """Execute simulation comparison."""

        def query_func(session):
            # Validate all simulations exist
            for sim_id in params["simulation_ids"]:
                if not self.db.validate_simulation_exists(sim_id):
                    raise SimulationNotFoundError(sim_id)

            # Default metrics if not specified
            metrics_to_compare = params.get("metrics") or [
                "total_agents",
                "average_agent_health",
                "average_reward",
                "births",
                "deaths",
            ]

            results = {}
            simulation_info = {}

            # Get metrics for each simulation
            for sim_id in params["simulation_ids"]:
                # Get simulation metadata
                sim = session.query(Simulation).filter_by(simulation_id=sim_id).first()
                simulation_info[sim_id] = {
                    "status": sim.status,
                    "parameters": sim.parameters,
                }

                # Get step metrics
                steps = (
                    session.query(SimulationStepModel)
                    .filter(SimulationStepModel.simulation_id == sim_id)
                    .all()
                )

                sim_stats = {}
                for metric in metrics_to_compare:
                    # Extract values for this metric
                    values = []
                    for step in steps:
                        val = getattr(step, metric, None)
                        if val is not None:
                            values.append(val)

                    if values:
                        sim_stats[metric] = {
                            "mean": float(np.mean(values)),
                            "std": float(np.std(values)),
                            "min": float(np.min(values)),
                            "max": float(np.max(values)),
                            "final": values[-1] if values else None,
                            "initial": values[0] if values else None,
                        }
                    else:
                        sim_stats[metric] = None

                results[sim_id] = sim_stats

            # Calculate pairwise comparisons
            comparisons = self._calculate_pairwise_differences(
                results, params["simulation_ids"], metrics_to_compare
            )

            # Rank simulations by each metric
            rankings = self._rank_simulations(results, metrics_to_compare)

            return {
                "simulations": results,
                "simulation_info": simulation_info,
                "pairwise_comparisons": comparisons,
                "rankings": rankings,
                "metrics_compared": metrics_to_compare,
                "simulation_count": len(params["simulation_ids"]),
            }

        return self.db.execute_query(query_func)

    def _calculate_pairwise_differences(
        self, results: Dict, sim_ids: List[str], metrics: List[str]
    ) -> Dict:
        """Calculate differences between simulation pairs."""
        differences = {}

        for i, sim1 in enumerate(sim_ids):
            for sim2 in sim_ids[i + 1 :]:
                pair_key = f"{sim1}_vs_{sim2}"
                pair_diff = {}

                for metric in metrics:
                    if results[sim1].get(metric) and results[sim2].get(metric):
                        mean_diff = (
                            results[sim1][metric]["mean"] - results[sim2][metric]["mean"]
                        )
                        pair_diff[metric] = {
                            "mean_difference": round(mean_diff, 4),
                            "percent_difference": (
                                round((mean_diff / results[sim2][metric]["mean"]) * 100, 2)
                                if results[sim2][metric]["mean"] != 0
                                else None
                            ),
                        }

                differences[pair_key] = pair_diff

        return differences

    def _rank_simulations(self, results: Dict, metrics: List[str]) -> Dict:
        """Rank simulations by each metric."""
        rankings = {}

        for metric in metrics:
            # Get mean values for this metric
            sim_means = []
            for sim_id, stats in results.items():
                if stats.get(metric):
                    sim_means.append((sim_id, stats[metric]["mean"]))

            # Sort by mean (descending)
            sim_means.sort(key=lambda x: x[1], reverse=True)

            rankings[metric] = [
                {"rank": i + 1, "simulation_id": sim_id, "value": round(value, 4)}
                for i, (sim_id, value) in enumerate(sim_means)
            ]

        return rankings


class CompareParametersParams(BaseModel):
    """Parameters for parameter comparison tool."""

    parameter_name: str = Field(..., description="Name of parameter to compare")
    simulation_ids: Optional[List[str]] = Field(
        None, description="Optional list of specific simulation IDs to compare"
    )
    outcome_metric: str = Field(
        "total_agents",
        description="Metric to use for measuring outcomes (default: total_agents)",
    )
    limit: int = Field(20, ge=2, le=100, description="Maximum simulations to analyze")


class CompareParametersTool(ToolBase):
    """Analyze how a specific parameter impacts simulation outcomes."""

    @property
    def name(self) -> str:
        return "compare_parameters"

    @property
    def description(self) -> str:
        return """
        Analyze the impact of a specific parameter on simulation outcomes.
        
        Returns parameter impact analysis including:
        - Grouping of simulations by parameter value
        - Outcome metrics for each group
        - Statistical comparison across groups
        - Correlation analysis
        
        Use this to:
        - Test hypotheses about parameter effects
        - Identify optimal parameter values
        - Understand parameter sensitivity
        - Guide experiment design
        """

    @property
    def parameters_schema(self):
        return CompareParametersParams

    def execute(self, **params):
        """Execute parameter comparison."""

        def query_func(session):
            # Get simulations to compare
            query = session.query(Simulation)

            if params.get("simulation_ids"):
                query = query.filter(Simulation.simulation_id.in_(params["simulation_ids"]))

            query = query.limit(params["limit"])
            simulations = query.all()

            if len(simulations) < 2:
                raise ValidationError("Need at least 2 simulations for comparison")

            # Group simulations by parameter value
            parameter_groups = {}
            param_name = params["parameter_name"]

            for sim in simulations:
                # Extract parameter value
                param_value = sim.parameters.get(param_name)
                if param_value is None:
                    continue

                # Convert to string key for grouping
                param_key = str(param_value)

                if param_key not in parameter_groups:
                    parameter_groups[param_key] = []

                parameter_groups[param_key].append(sim.simulation_id)

            if len(parameter_groups) < 2:
                return {
                    "message": f"All simulations have the same value for '{param_name}' or parameter not found"
                }

            # Get outcome metrics for each group
            outcome_metric = params["outcome_metric"]
            group_outcomes = {}

            for param_value, sim_ids in parameter_groups.items():
                outcomes = []

                for sim_id in sim_ids:
                    # Get final or average value of outcome metric
                    steps = (
                        session.query(SimulationStepModel)
                        .filter(SimulationStepModel.simulation_id == sim_id)
                        .all()
                    )

                    if steps:
                        values = [
                            getattr(step, outcome_metric)
                            for step in steps
                            if getattr(step, outcome_metric) is not None
                        ]
                        if values:
                            outcomes.append(
                                {
                                    "simulation_id": sim_id,
                                    "mean": float(np.mean(values)),
                                    "final": values[-1],
                                }
                            )

                if outcomes:
                    group_outcomes[param_value] = {
                        "simulation_count": len(outcomes),
                        "simulations": outcomes,
                        "group_mean": float(np.mean([o["mean"] for o in outcomes])),
                        "group_std": float(np.std([o["mean"] for o in outcomes]))
                        if len(outcomes) > 1
                        else 0,
                        "best_simulation": max(outcomes, key=lambda x: x["mean"]),
                        "worst_simulation": min(outcomes, key=lambda x: x["mean"]),
                    }

            return {
                "parameter": param_name,
                "outcome_metric": outcome_metric,
                "parameter_values": list(parameter_groups.keys()),
                "groups": group_outcomes,
                "total_simulations_analyzed": len(simulations),
                "groups_count": len(parameter_groups),
            }

        return self.db.execute_query(query_func)


class RankConfigurationsParams(BaseModel):
    """Parameters for ranking configurations."""

    metric_name: str = Field(
        "total_agents", description="Metric to rank by (e.g., 'total_agents', 'average_reward')"
    )
    aggregation: str = Field(
        "mean",
        description="Aggregation method: 'mean', 'final', 'max', 'min'",
    )
    limit: int = Field(20, ge=1, le=100, description="Maximum simulations to rank")
    status_filter: Optional[str] = Field(None, description="Filter by simulation status")


class RankConfigurationsTool(ToolBase):
    """Rank simulations by performance metrics."""

    @property
    def name(self) -> str:
        return "rank_configurations"

    @property
    def description(self) -> str:
        return """
        Rank simulations by a specific performance metric.
        
        Returns ranked list including:
        - Simulation IDs ordered by performance
        - Metric values for each simulation
        - Configuration parameters
        - Statistical summaries
        
        Use this to:
        - Identify best configurations
        - Find optimal parameter settings
        - Compare experiment results
        - Guide parameter tuning
        """

    @property
    def parameters_schema(self):
        return RankConfigurationsParams

    def execute(self, **params):
        """Execute configuration ranking."""

        def query_func(session):
            # Get simulations
            query = session.query(Simulation)

            if params.get("status_filter"):
                query = query.filter(Simulation.status == params["status_filter"])

            query = query.limit(params["limit"])
            simulations = query.all()

            if not simulations:
                return {"message": "No simulations found"}

            metric_name = params["metric_name"]
            aggregation = params["aggregation"]

            # Calculate metric value for each simulation
            sim_scores = []

            for sim in simulations:
                steps = (
                    session.query(SimulationStepModel)
                    .filter(SimulationStepModel.simulation_id == sim.simulation_id)
                    .all()
                )

                if not steps:
                    continue

                # Extract metric values
                values = [
                    getattr(step, metric_name)
                    for step in steps
                    if getattr(step, metric_name, None) is not None
                ]

                if not values:
                    continue

                # Apply aggregation
                if aggregation == "mean":
                    score = float(np.mean(values))
                elif aggregation == "final":
                    score = float(values[-1])
                elif aggregation == "max":
                    score = float(np.max(values))
                elif aggregation == "min":
                    score = float(np.min(values))
                else:
                    score = float(np.mean(values))

                sim_scores.append(
                    {
                        "simulation_id": sim.simulation_id,
                        "score": round(score, 4),
                        "status": sim.status,
                        "parameters": sim.parameters,
                        "steps_analyzed": len(steps),
                    }
                )

            # Sort by score (descending)
            sim_scores.sort(key=lambda x: x["score"], reverse=True)

            # Add ranks
            for i, entry in enumerate(sim_scores):
                entry["rank"] = i + 1

            return {
                "metric": metric_name,
                "aggregation": aggregation,
                "rankings": sim_scores,
                "total_ranked": len(sim_scores),
                "best_simulation": sim_scores[0] if sim_scores else None,
                "worst_simulation": sim_scores[-1] if sim_scores else None,
                "statistics": {
                    "mean_score": float(np.mean([s["score"] for s in sim_scores]))
                    if sim_scores
                    else None,
                    "std_score": float(np.std([s["score"] for s in sim_scores]))
                    if sim_scores
                    else None,
                    "score_range": {
                        "min": sim_scores[-1]["score"] if sim_scores else None,
                        "max": sim_scores[0]["score"] if sim_scores else None,
                    },
                },
            }

        return self.db.execute_query(query_func)


class CompareGenerationsParams(BaseModel):
    """Parameters for generation comparison."""

    simulation_id: str = Field(..., description="Simulation ID to analyze")
    max_generations: int = Field(10, ge=1, le=50, description="Maximum generations to compare")


class CompareGenerationsTool(ToolBase):
    """Compare performance across generations within a simulation."""

    @property
    def name(self) -> str:
        return "compare_generations"

    @property
    def description(self) -> str:
        return """
        Compare agent performance across different generations.
        
        Returns generation comparison including:
        - Agent count per generation
        - Survival rates by generation
        - Average lifespan by generation
        - Performance trends
        
        Use this to:
        - Track evolutionary progress
        - Identify successful generations
        - Understand generational fitness
        - Detect evolutionary trends
        """

    @property
    def parameters_schema(self):
        return CompareGenerationsParams

    def execute(self, **params):
        """Execute generation comparison."""
        if not self.db.validate_simulation_exists(params["simulation_id"]):
            raise SimulationNotFoundError(params["simulation_id"])

        def query_func(session):
            from ..models.database_models import AgentModel

            # Get agents grouped by generation
            agents = (
                session.query(AgentModel)
                .filter(AgentModel.simulation_id == params["simulation_id"])
                .all()
            )

            if not agents:
                return {"message": "No agents found"}

            # Group by generation
            generations = {}
            for agent in agents:
                gen = agent.generation
                if gen not in generations:
                    generations[gen] = {
                        "agents": [],
                        "alive": 0,
                        "dead": 0,
                        "lifespans": [],
                    }

                generations[gen]["agents"].append(agent.agent_id)

                if agent.death_time is None:
                    generations[gen]["alive"] += 1
                else:
                    generations[gen]["dead"] += 1
                    lifespan = agent.death_time - agent.birth_time
                    generations[gen]["lifespans"].append(lifespan)

            # Calculate statistics for each generation
            generation_stats = {}
            for gen in sorted(generations.keys())[: params["max_generations"]]:
                data = generations[gen]
                total = data["alive"] + data["dead"]

                stats = {
                    "generation": gen,
                    "total_agents": total,
                    "alive": data["alive"],
                    "dead": data["dead"],
                    "survival_rate_percent": round((data["alive"] / total * 100), 2)
                    if total > 0
                    else 0,
                }

                if data["lifespans"]:
                    stats["lifespan_stats"] = {
                        "mean": round(float(np.mean(data["lifespans"])), 2),
                        "median": float(np.median(data["lifespans"])),
                        "min": min(data["lifespans"]),
                        "max": max(data["lifespans"]),
                    }

                generation_stats[gen] = stats

            return {
                "total_generations": len(generations),
                "generations_analyzed": len(generation_stats),
                "generations": generation_stats,
                "summary": {
                    "total_agents": sum(g["total_agents"] for g in generation_stats.values()),
                    "best_survival_generation": max(
                        generation_stats.items(), key=lambda x: x[1]["survival_rate_percent"]
                    )[0]
                    if generation_stats
                    else None,
                },
            }

        return self.db.execute_query(query_func)