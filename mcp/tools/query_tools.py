"""Query tools for retrieving simulation data with flexible filtering."""

from typing import Optional

from pydantic import BaseModel, Field

from ..models.database_models import (
    ActionModel,
    AgentModel,
    AgentStateModel,
    InteractionModel,
    ResourceModel,
    SimulationStepModel,
)
from .base import ToolBase
from ..utils.exceptions import SimulationNotFoundError


class QueryAgentsParams(BaseModel):
    """Parameters for query_agents tool."""

    simulation_id: str = Field(..., description="Simulation ID to query")
    agent_type: Optional[str] = Field(None, description="Filter by agent type")
    generation: Optional[int] = Field(None, ge=0, description="Filter by generation number")
    alive_only: bool = Field(False, description="Return only living agents")
    limit: int = Field(100, ge=1, le=1000, description="Maximum results to return")
    offset: int = Field(0, ge=0, description="Pagination offset")


class QueryAgentsTool(ToolBase):
    """Query agents with flexible filtering options."""

    @property
    def name(self) -> str:
        return "query_agents"

    @property
    def description(self) -> str:
        return """
        Query agents from a simulation with flexible filtering options.
        
        Returns agent data including:
        - Agent ID, type, and generation
        - Birth and death times
        - Initial resources and health
        - Position and genome information
        
        Use this to:
        - List all agents in a simulation
        - Find agents of specific types or generations
        - Identify living vs. dead agents
        - Get agent details for further analysis
        """

    @property
    def parameters_schema(self):
        return QueryAgentsParams

    def execute(self, **params):
        """Execute agent query."""
        # Validate simulation exists
        if not self.db.validate_simulation_exists(params["simulation_id"]):
            raise SimulationNotFoundError(params["simulation_id"])

        def query_func(session):
            # Build query
            query = session.query(AgentModel).filter(
                AgentModel.simulation_id == params["simulation_id"]
            )

            # Apply filters
            if params.get("agent_type"):
                query = query.filter(AgentModel.agent_type == params["agent_type"])

            if params.get("generation") is not None:
                query = query.filter(AgentModel.generation == params["generation"])

            if params.get("alive_only"):
                query = query.filter(AgentModel.death_time.is_(None))

            # Get total count
            total = query.count()

            # Apply pagination
            query = query.limit(params["limit"]).offset(params["offset"])

            # Execute and serialize
            agents = query.all()
            results = [
                {
                    "agent_id": a.agent_id,
                    "agent_type": a.agent_type,
                    "generation": a.generation,
                    "birth_time": a.birth_time,
                    "death_time": a.death_time,
                    "position": {"x": a.position_x, "y": a.position_y},
                    "initial_resources": a.initial_resources,
                    "starting_health": a.starting_health,
                    "starvation_counter": a.starvation_counter,
                    "genome_id": a.genome_id,
                }
                for a in agents
            ]

            return {
                "agents": results,
                "total_count": total,
                "returned_count": len(results),
                "limit": params["limit"],
                "offset": params["offset"],
            }

        return self.db.execute_query(query_func)


class QueryActionsParams(BaseModel):
    """Parameters for query_actions tool."""

    simulation_id: str = Field(..., description="Simulation ID to query")
    agent_id: Optional[str] = Field(None, description="Filter by agent ID")
    action_type: Optional[str] = Field(None, description="Filter by action type")
    start_step: Optional[int] = Field(None, ge=0, description="Start step (inclusive)")
    end_step: Optional[int] = Field(None, ge=0, description="End step (inclusive)")
    limit: int = Field(100, ge=1, le=1000, description="Maximum results to return")
    offset: int = Field(0, ge=0, description="Pagination offset")


class QueryActionsTool(ToolBase):
    """Query agent actions with filtering options."""

    @property
    def name(self) -> str:
        return "query_actions"

    @property
    def description(self) -> str:
        return """
        Retrieve action logs from a simulation with flexible filtering.
        
        Returns action data including:
        - Action type and step number
        - Agent ID and target (if applicable)
        - Resources before and after
        - Reward received
        - Action details
        
        Use this to:
        - Analyze agent behavior patterns
        - Track specific action types
        - Study resource changes
        - Examine rewards and outcomes
        """

    @property
    def parameters_schema(self):
        return QueryActionsParams

    def execute(self, **params):
        """Execute action query."""
        # Validate simulation exists
        if not self.db.validate_simulation_exists(params["simulation_id"]):
            raise SimulationNotFoundError(params["simulation_id"])

        def query_func(session):
            # Build query
            query = session.query(ActionModel).filter(
                ActionModel.simulation_id == params["simulation_id"]
            )

            # Apply filters
            if params.get("agent_id"):
                query = query.filter(ActionModel.agent_id == params["agent_id"])

            if params.get("action_type"):
                query = query.filter(ActionModel.action_type == params["action_type"])

            if params.get("start_step") is not None:
                query = query.filter(ActionModel.step_number >= params["start_step"])

            if params.get("end_step") is not None:
                query = query.filter(ActionModel.step_number <= params["end_step"])

            # Order by step number
            query = query.order_by(ActionModel.step_number)

            # Get total count
            total = query.count()

            # Apply pagination
            query = query.limit(params["limit"]).offset(params["offset"])

            # Execute and serialize
            actions = query.all()
            results = [
                {
                    "action_id": a.action_id,
                    "step_number": a.step_number,
                    "agent_id": a.agent_id,
                    "action_type": a.action_type,
                    "action_target_id": a.action_target_id,
                    "resources_before": a.resources_before,
                    "resources_after": a.resources_after,
                    "reward": a.reward,
                    "details": a.details,
                }
                for a in actions
            ]

            return {
                "actions": results,
                "total_count": total,
                "returned_count": len(results),
                "limit": params["limit"],
                "offset": params["offset"],
            }

        return self.db.execute_query(query_func)


class QueryStatesParams(BaseModel):
    """Parameters for query_states tool."""

    simulation_id: str = Field(..., description="Simulation ID to query")
    agent_id: Optional[str] = Field(None, description="Filter by agent ID")
    start_step: Optional[int] = Field(None, ge=0, description="Start step (inclusive)")
    end_step: Optional[int] = Field(None, ge=0, description="End step (inclusive)")
    limit: int = Field(100, ge=1, le=1000, description="Maximum results to return")
    offset: int = Field(0, ge=0, description="Pagination offset")


class QueryStatesTool(ToolBase):
    """Query agent states over time."""

    @property
    def name(self) -> str:
        return "query_states"

    @property
    def description(self) -> str:
        return """
        Get agent state data over time with flexible filtering.
        
        Returns state data including:
        - Position (x, y, z coordinates)
        - Resource level
        - Current and starting health
        - Starvation counter
        - Defensive status
        - Total reward and age
        
        Use this to:
        - Track agent movement over time
        - Monitor resource accumulation
        - Analyze health changes
        - Study agent lifecycle progression
        """

    @property
    def parameters_schema(self):
        return QueryStatesParams

    def execute(self, **params):
        """Execute state query."""
        # Validate simulation exists
        if not self.db.validate_simulation_exists(params["simulation_id"]):
            raise SimulationNotFoundError(params["simulation_id"])

        def query_func(session):
            # Build query
            query = session.query(AgentStateModel).filter(
                AgentStateModel.simulation_id == params["simulation_id"]
            )

            # Apply filters
            if params.get("agent_id"):
                query = query.filter(AgentStateModel.agent_id == params["agent_id"])

            if params.get("start_step") is not None:
                query = query.filter(AgentStateModel.step_number >= params["start_step"])

            if params.get("end_step") is not None:
                query = query.filter(AgentStateModel.step_number <= params["end_step"])

            # Order by step number
            query = query.order_by(AgentStateModel.step_number)

            # Get total count
            total = query.count()

            # Apply pagination
            query = query.limit(params["limit"]).offset(params["offset"])

            # Execute and serialize
            states = query.all()
            results = [
                {
                    "agent_id": s.agent_id,
                    "step_number": s.step_number,
                    "position": {"x": s.position_x, "y": s.position_y, "z": s.position_z},
                    "resource_level": s.resource_level,
                    "current_health": s.current_health,
                    "starting_health": s.starting_health,
                    "starvation_counter": s.starvation_counter,
                    "is_defending": s.is_defending,
                    "total_reward": s.total_reward,
                    "age": s.age,
                }
                for s in states
            ]

            return {
                "states": results,
                "total_count": total,
                "returned_count": len(results),
                "limit": params["limit"],
                "offset": params["offset"],
            }

        return self.db.execute_query(query_func)


class QueryResourcesParams(BaseModel):
    """Parameters for query_resources tool."""

    simulation_id: str = Field(..., description="Simulation ID to query")
    step_number: Optional[int] = Field(None, ge=0, description="Filter by specific step")
    start_step: Optional[int] = Field(None, ge=0, description="Start step (inclusive)")
    end_step: Optional[int] = Field(None, ge=0, description="End step (inclusive)")
    limit: int = Field(100, ge=1, le=1000, description="Maximum results to return")
    offset: int = Field(0, ge=0, description="Pagination offset")


class QueryResourcesTool(ToolBase):
    """Query resource states in the environment."""

    @property
    def name(self) -> str:
        return "query_resources"

    @property
    def description(self) -> str:
        return """
        Fetch resource states from the simulation environment.
        
        Returns resource data including:
        - Resource ID and amount
        - Position (x, y coordinates)
        - Step number
        
        Use this to:
        - Track resource distribution
        - Monitor resource depletion
        - Analyze resource positioning
        - Study resource-agent interactions
        """

    @property
    def parameters_schema(self):
        return QueryResourcesParams

    def execute(self, **params):
        """Execute resource query."""
        # Validate simulation exists
        if not self.db.validate_simulation_exists(params["simulation_id"]):
            raise SimulationNotFoundError(params["simulation_id"])

        def query_func(session):
            # Build query
            query = session.query(ResourceModel).filter(
                ResourceModel.simulation_id == params["simulation_id"]
            )

            # Apply filters
            if params.get("step_number") is not None:
                query = query.filter(ResourceModel.step_number == params["step_number"])
            else:
                if params.get("start_step") is not None:
                    query = query.filter(ResourceModel.step_number >= params["start_step"])

                if params.get("end_step") is not None:
                    query = query.filter(ResourceModel.step_number <= params["end_step"])

            # Order by step number
            query = query.order_by(ResourceModel.step_number)

            # Get total count
            total = query.count()

            # Apply pagination
            query = query.limit(params["limit"]).offset(params["offset"])

            # Execute and serialize
            resources = query.all()
            results = [
                {
                    "resource_id": r.resource_id,
                    "step_number": r.step_number,
                    "amount": r.amount,
                    "position": {"x": r.position_x, "y": r.position_y},
                }
                for r in resources
            ]

            return {
                "resources": results,
                "total_count": total,
                "returned_count": len(results),
                "limit": params["limit"],
                "offset": params["offset"],
            }

        return self.db.execute_query(query_func)


class QueryInteractionsParams(BaseModel):
    """Parameters for query_interactions tool."""

    simulation_id: str = Field(..., description="Simulation ID to query")
    interaction_type: Optional[str] = Field(
        None, description="Filter by interaction type (e.g., 'share', 'attack')"
    )
    source_id: Optional[str] = Field(None, description="Filter by source entity ID")
    target_id: Optional[str] = Field(None, description="Filter by target entity ID")
    start_step: Optional[int] = Field(None, ge=0, description="Start step (inclusive)")
    end_step: Optional[int] = Field(None, ge=0, description="End step (inclusive)")
    limit: int = Field(100, ge=1, le=1000, description="Maximum results to return")
    offset: int = Field(0, ge=0, description="Pagination offset")


class QueryInteractionsTool(ToolBase):
    """Query interaction data between entities."""

    @property
    def name(self) -> str:
        return "query_interactions"

    @property
    def description(self) -> str:
        return """
        Retrieve interaction data between agents and resources.
        
        Returns interaction data including:
        - Source and target entity information
        - Interaction type and action type
        - Step number and timestamp
        - Details about the interaction
        
        Use this to:
        - Analyze agent-agent interactions
        - Study agent-resource interactions
        - Track interaction patterns
        - Examine social behaviors
        """

    @property
    def parameters_schema(self):
        return QueryInteractionsParams

    def execute(self, **params):
        """Execute interaction query."""
        # Validate simulation exists
        if not self.db.validate_simulation_exists(params["simulation_id"]):
            raise SimulationNotFoundError(params["simulation_id"])

        def query_func(session):
            # Build query
            query = session.query(InteractionModel).filter(
                InteractionModel.simulation_id == params["simulation_id"]
            )

            # Apply filters
            if params.get("interaction_type"):
                query = query.filter(
                    InteractionModel.interaction_type == params["interaction_type"]
                )

            if params.get("source_id"):
                query = query.filter(InteractionModel.source_id == params["source_id"])

            if params.get("target_id"):
                query = query.filter(InteractionModel.target_id == params["target_id"])

            if params.get("start_step") is not None:
                query = query.filter(InteractionModel.step_number >= params["start_step"])

            if params.get("end_step") is not None:
                query = query.filter(InteractionModel.step_number <= params["end_step"])

            # Order by step number
            query = query.order_by(InteractionModel.step_number)

            # Get total count
            total = query.count()

            # Apply pagination
            query = query.limit(params["limit"]).offset(params["offset"])

            # Execute and serialize
            interactions = query.all()
            results = [
                {
                    "interaction_id": i.interaction_id,
                    "step_number": i.step_number,
                    "source_type": i.source_type,
                    "source_id": i.source_id,
                    "target_type": i.target_type,
                    "target_id": i.target_id,
                    "interaction_type": i.interaction_type,
                    "action_type": i.action_type,
                    "details": i.details,
                    "timestamp": i.timestamp.isoformat() if i.timestamp else None,
                }
                for i in interactions
            ]

            return {
                "interactions": results,
                "total_count": total,
                "returned_count": len(results),
                "limit": params["limit"],
                "offset": params["offset"],
            }

        return self.db.execute_query(query_func)


class GetSimulationMetricsParams(BaseModel):
    """Parameters for get_simulation_metrics tool."""

    simulation_id: str = Field(..., description="Simulation ID to query")
    start_step: Optional[int] = Field(None, ge=0, description="Start step (inclusive)")
    end_step: Optional[int] = Field(None, ge=0, description="End step (inclusive)")
    limit: int = Field(1000, ge=1, le=10000, description="Maximum results to return")
    offset: int = Field(0, ge=0, description="Pagination offset")


class GetSimulationMetricsTool(ToolBase):
    """Get step-level simulation metrics."""

    @property
    def name(self) -> str:
        return "get_simulation_metrics"

    @property
    def description(self) -> str:
        return """
        Get detailed step-by-step simulation metrics.
        
        Returns metrics including:
        - Population counts (total, by type)
        - Births and deaths
        - Resource metrics
        - Agent health and rewards
        - Combat and social interactions
        - Genetic diversity metrics
        
        Use this to:
        - Analyze simulation progression
        - Track population dynamics
        - Monitor resource usage
        - Study emergent behaviors
        - Generate time-series data
        """

    @property
    def parameters_schema(self):
        return GetSimulationMetricsParams

    def execute(self, **params):
        """Execute metrics query."""
        # Validate simulation exists
        if not self.db.validate_simulation_exists(params["simulation_id"]):
            raise SimulationNotFoundError(params["simulation_id"])

        def query_func(session):
            # Build query
            query = session.query(SimulationStepModel).filter(
                SimulationStepModel.simulation_id == params["simulation_id"]
            )

            # Apply filters
            if params.get("start_step") is not None:
                query = query.filter(SimulationStepModel.step_number >= params["start_step"])

            if params.get("end_step") is not None:
                query = query.filter(SimulationStepModel.step_number <= params["end_step"])

            # Order by step number
            query = query.order_by(SimulationStepModel.step_number)

            # Get total count
            total = query.count()

            # Apply pagination
            query = query.limit(params["limit"]).offset(params["offset"])

            # Execute and serialize
            steps = query.all()
            results = [
                {
                    "step_number": s.step_number,
                    "total_agents": s.total_agents,
                    "system_agents": s.system_agents,
                    "independent_agents": s.independent_agents,
                    "control_agents": s.control_agents,
                    "total_resources": s.total_resources,
                    "average_agent_resources": s.average_agent_resources,
                    "births": s.births,
                    "deaths": s.deaths,
                    "current_max_generation": s.current_max_generation,
                    "resource_efficiency": s.resource_efficiency,
                    "resource_distribution_entropy": s.resource_distribution_entropy,
                    "average_agent_health": s.average_agent_health,
                    "average_agent_age": s.average_agent_age,
                    "average_reward": s.average_reward,
                    "combat_encounters": s.combat_encounters,
                    "successful_attacks": s.successful_attacks,
                    "resources_shared": s.resources_shared,
                    "genetic_diversity": s.genetic_diversity,
                    "dominant_genome_ratio": s.dominant_genome_ratio,
                    "resources_consumed": s.resources_consumed,
                }
                for s in steps
            ]

            return {
                "metrics": results,
                "total_count": total,
                "returned_count": len(results),
                "limit": params["limit"],
                "offset": params["offset"],
            }

        return self.db.execute_query(query_func)