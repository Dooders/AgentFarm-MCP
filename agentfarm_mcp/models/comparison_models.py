"""Comparison and analysis-related models.

This module contains data classes and utilities for simulation comparison.
"""

import statistics
from dataclasses import dataclass
from typing import Any, Dict

from deepdiff import DeepDiff

from .simulation_models import Simulation, SimulationStepModel


@dataclass
class SimulationDifference:
    """Represents differences between two simulations.

    Attributes
    ----------
    metadata_diff : Dict[str, tuple]
        Differences in basic metadata fields, with (sim1_value, sim2_value) tuples
    parameter_diff : Dict
        Differences in simulation parameters (from DeepDiff)
    results_diff : Dict
        Differences in results summary (from DeepDiff)
    step_metrics_diff : Dict[str, Dict[str, float]]
        Statistical differences in step metrics (min, max, mean, etc.)
    """

    metadata_diff: Dict[str, tuple]
    parameter_diff: Dict
    results_diff: Dict
    step_metrics_diff: Dict[str, Dict[str, float]]


class SimulationComparison:
    """Utility class for comparing two simulations.

    This class provides methods to compare different aspects of two simulations,
    including metadata, parameters, results, and step metrics.
    """

    def __init__(self, sim1: Simulation, sim2: Simulation) -> None:
        """Initialize with two simulations to compare.

        Parameters
        ----------
        sim1 : Simulation
            First simulation to compare
        sim2 : Simulation
            Second simulation to compare
        """
        self.sim1 = sim1
        self.sim2 = sim2

    def _compare_metadata(self) -> Dict[str, tuple]:
        """Compare basic metadata fields between simulations.

        Returns:
            Dictionary of metadata differences
        """
        metadata_fields = ["status", "simulation_db_path"]
        differences = {}

        for field in metadata_fields:
            val1 = getattr(self.sim1, field)
            val2 = getattr(self.sim2, field)
            if val1 != val2:
                differences[field] = (val1, val2)

        # Compare timestamps
        start_time1: Any = self.sim1.start_time
        start_time2: Any = self.sim2.start_time
        if start_time1 != start_time2:
            differences["start_time"] = (start_time1, start_time2)

        end_time1: Any = self.sim1.end_time
        end_time2: Any = self.sim2.end_time
        if end_time1 != end_time2:
            differences["end_time"] = (end_time1, end_time2)

        return differences

    def _compare_parameters(self) -> Dict:
        """Compare simulation parameters using DeepDiff.

        Returns:
            Dictionary of parameter differences
        """
        return DeepDiff(self.sim1.parameters, self.sim2.parameters, ignore_order=True)

    def _compare_results(self) -> Dict:
        """Compare results summaries using DeepDiff.

        Returns:
            Dictionary of results differences
        """
        return DeepDiff(self.sim1.results_summary, self.sim2.results_summary, ignore_order=True)

    def _compare_step_metrics(self, session: Any) -> Dict[str, Dict[str, float]]:
        """Compare statistical summaries of step metrics.

        Parameters
        ----------
        session : Session
            SQLAlchemy database session

        Returns
        -------
        Dict[str, Dict[str, float]]
            Dictionary mapping metric names to their statistical differences
        """
        metrics = {
            "total_agents": [],
            "births": [],
            "deaths": [],
            "average_agent_health": [],
            "average_reward": [],
            "combat_encounters": [],
            "resources_consumed": [],
        }

        differences = {}

        # Get step data for both simulations
        for sim_id, metric_list in [
            (self.sim1.simulation_id, "_sim1_metrics"),
            (self.sim2.simulation_id, "_sim2_metrics"),
        ]:
            steps = (
                session.query(SimulationStepModel)
                .filter(SimulationStepModel.simulation_id == sim_id)
                .all()
            )

            setattr(
                self,
                metric_list,
                {metric: [getattr(step, metric) for step in steps] for metric in metrics},
            )

        # Compare statistics for each metric
        for metric in metrics:
            sim1_values = getattr(self, "_sim1_metrics")[metric]
            sim2_values = getattr(self, "_sim2_metrics")[metric]

            if sim1_values and sim2_values:  # Only compare if both have data
                differences[metric] = {
                    "mean_diff": statistics.mean(sim1_values) - statistics.mean(sim2_values),
                    "max_diff": max(sim1_values) - max(sim2_values),
                    "min_diff": min(sim1_values) - min(sim2_values),
                    "std_diff": statistics.stdev(sim1_values) - statistics.stdev(sim2_values),
                }

        return differences

    def compare(self, session: Any) -> SimulationDifference:
        """Perform full comparison between simulations.

        Parameters
        ----------
        session : Session
            SQLAlchemy session for database queries

        Returns
        -------
        SimulationDifference
            Object containing all differences between the simulations
        """
        return SimulationDifference(
            metadata_diff=self._compare_metadata(),
            parameter_diff=self._compare_parameters(),
            results_diff=self._compare_results(),
            step_metrics_diff=self._compare_step_metrics(session),
        )
