"""Metadata tools for querying simulation and experiment information."""

from typing import Optional

from pydantic import BaseModel, Field

from mcp_server.models.database_models import ExperimentModel, Simulation
from mcp_server.tools.base import ToolBase
from mcp_server.utils.exceptions import ExperimentNotFoundError, SimulationNotFoundError


class GetSimulationInfoParams(BaseModel):
    """Parameters for get_simulation_info tool."""

    simulation_id: str = Field(..., description="Simulation ID to query")


class GetSimulationInfoTool(ToolBase):
    """Get detailed information about a specific simulation."""

    @property
    def name(self) -> str:
        return "get_simulation_info"

    @property
    def description(self) -> str:
        return """
        Get detailed information about a specific simulation.
        
        Returns simulation metadata including:
        - Simulation ID and status
        - Start and end times
        - Configuration parameters
        - Results summary
        - Associated experiment ID
        - Database path
        
        Use this to:
        - Get overview of a specific simulation
        - Check simulation status and duration
        - Review configuration parameters
        - Access results summary
        """

    @property
    def parameters_schema(self):
        return GetSimulationInfoParams

    def execute(self, **params):
        """Execute simulation info retrieval."""

        def query_func(session):
            sim = (
                session.query(Simulation)
                .filter_by(simulation_id=params["simulation_id"])
                .first()
            )

            if not sim:
                raise SimulationNotFoundError(params["simulation_id"])

            return {
                "simulation_id": sim.simulation_id,
                "experiment_id": sim.experiment_id,
                "status": sim.status,
                "start_time": sim.start_time.isoformat() if sim.start_time else None,
                "end_time": sim.end_time.isoformat() if sim.end_time else None,
                "parameters": sim.parameters,
                "results_summary": sim.results_summary,
                "db_path": sim.simulation_db_path,
            }

        return self.db.execute_query(query_func)


class ListSimulationsParams(BaseModel):
    """Parameters for list_simulations tool."""

    status: Optional[str] = Field(None, description="Filter by status (e.g., 'completed', 'running')")
    experiment_id: Optional[str] = Field(None, description="Filter by experiment ID")
    limit: int = Field(100, ge=1, le=1000, description="Maximum results to return")
    offset: int = Field(0, ge=0, description="Pagination offset")


class ListSimulationsTool(ToolBase):
    """List all simulations with optional filtering."""

    @property
    def name(self) -> str:
        return "list_simulations"

    @property
    def description(self) -> str:
        return """
        List all simulations in the database with optional filtering.
        
        Returns simulation metadata including:
        - Simulation ID
        - Status (completed, running, failed, pending)
        - Start and end times
        - Parameter summary
        - Experiment association
        
        Use this to:
        - Get overview of all simulations
        - Find simulations by status
        - Filter by experiment
        - Navigate available simulation data
        """

    @property
    def parameters_schema(self):
        return ListSimulationsParams

    def execute(self, **params):
        """Execute simulation listing."""

        def query_func(session):
            # Build query
            query = session.query(Simulation)

            # Apply filters
            if params.get("status"):
                query = query.filter(Simulation.status == params["status"])

            if params.get("experiment_id"):
                query = query.filter(Simulation.experiment_id == params["experiment_id"])

            # Get total count
            total = query.count()

            # Apply pagination
            query = query.limit(params["limit"]).offset(params["offset"])

            # Execute
            simulations = query.all()

            # Serialize
            results = [
                {
                    "simulation_id": s.simulation_id,
                    "experiment_id": s.experiment_id,
                    "status": s.status,
                    "start_time": s.start_time.isoformat() if s.start_time else None,
                    "end_time": s.end_time.isoformat() if s.end_time else None,
                    "parameters_summary": (
                        {k: v for k, v in list(s.parameters.items())[:5]}
                        if s.parameters
                        else {}
                    ),
                    "db_path": s.simulation_db_path,
                }
                for s in simulations
            ]

            return {
                "simulations": results,
                "total_count": total,
                "returned_count": len(results),
                "limit": params["limit"],
                "offset": params["offset"],
            }

        return self.db.execute_query(query_func)


class GetExperimentInfoParams(BaseModel):
    """Parameters for get_experiment_info tool."""

    experiment_id: str = Field(..., description="Experiment ID to query")


class GetExperimentInfoTool(ToolBase):
    """Get detailed information about a specific experiment."""

    @property
    def name(self) -> str:
        return "get_experiment_info"

    @property
    def description(self) -> str:
        return """
        Get detailed information about a specific research experiment.
        
        Returns experiment metadata including:
        - Experiment ID, name, and description
        - Hypothesis being tested
        - Variables being manipulated
        - Status and dates
        - Results summary
        - Count of associated simulations
        
        Use this to:
        - Understand experiment design
        - Review hypothesis and variables
        - Check experiment status
        - See number of simulations
        """

    @property
    def parameters_schema(self):
        return GetExperimentInfoParams

    def execute(self, **params):
        """Execute experiment info retrieval."""

        def query_func(session):
            exp = (
                session.query(ExperimentModel)
                .filter_by(experiment_id=params["experiment_id"])
                .first()
            )

            if not exp:
                raise ExperimentNotFoundError(params["experiment_id"])

            # Count associated simulations
            sim_count = (
                session.query(Simulation)
                .filter_by(experiment_id=exp.experiment_id)
                .count()
            )

            return {
                "experiment_id": exp.experiment_id,
                "name": exp.name,
                "description": exp.description,
                "hypothesis": exp.hypothesis,
                "creation_date": exp.creation_date.isoformat() if exp.creation_date else None,
                "last_updated": exp.last_updated.isoformat() if exp.last_updated else None,
                "status": exp.status,
                "tags": exp.tags,
                "variables": exp.variables,
                "results_summary": exp.results_summary,
                "notes": exp.notes,
                "simulation_count": sim_count,
            }

        return self.db.execute_query(query_func)


class ListExperimentsParams(BaseModel):
    """Parameters for list_experiments tool."""

    status: Optional[str] = Field(None, description="Filter by status")
    limit: int = Field(100, ge=1, le=1000, description="Maximum results to return")
    offset: int = Field(0, ge=0, description="Pagination offset")


class ListExperimentsTool(ToolBase):
    """List all experiments with optional filtering."""

    @property
    def name(self) -> str:
        return "list_experiments"

    @property
    def description(self) -> str:
        return """
        List all research experiments with optional filtering.
        
        Returns experiment metadata including:
        - Experiment ID and name
        - Status
        - Creation and update dates
        - Tags
        - Simulation count
        
        Use this to:
        - Browse all experiments
        - Filter by status (planned, running, completed, analyzed)
        - Find experiments by tags
        - Get experiment overview
        """

    @property
    def parameters_schema(self):
        return ListExperimentsParams

    def execute(self, **params):
        """Execute experiment listing."""

        def query_func(session):
            # Build query
            query = session.query(ExperimentModel)

            # Apply filters
            if params.get("status"):
                query = query.filter(ExperimentModel.status == params["status"])

            # Get total count
            total = query.count()

            # Apply pagination
            query = query.limit(params["limit"]).offset(params["offset"])

            # Execute
            experiments = query.all()

            # Count simulations for each experiment
            results = []
            for exp in experiments:
                sim_count = (
                    session.query(Simulation)
                    .filter_by(experiment_id=exp.experiment_id)
                    .count()
                )

                results.append(
                    {
                        "experiment_id": exp.experiment_id,
                        "name": exp.name,
                        "status": exp.status,
                        "creation_date": (
                            exp.creation_date.isoformat() if exp.creation_date else None
                        ),
                        "last_updated": (
                            exp.last_updated.isoformat() if exp.last_updated else None
                        ),
                        "tags": exp.tags,
                        "simulation_count": sim_count,
                    }
                )

            return {
                "experiments": results,
                "total_count": total,
                "returned_count": len(results),
                "limit": params["limit"],
                "offset": params["offset"],
            }

        return self.db.execute_query(query_func)