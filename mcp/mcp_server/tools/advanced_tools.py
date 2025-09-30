"""Advanced tools for specialized analysis."""

from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from mcp_server.models.database_models import AgentModel, ReproductionEventModel
from mcp_server.tools.base import ToolBase
from mcp_server.utils.exceptions import SimulationNotFoundError


class BuildAgentLineageParams(BaseModel):
    """Parameters for building agent lineage."""

    simulation_id: str = Field(..., description="Simulation ID to query")
    agent_id: str = Field(..., description="Agent ID to build lineage for")
    depth: int = Field(
        3, ge=1, le=10, description="How many generations to trace (ancestors and descendants)"
    )


class BuildAgentLineageTool(ToolBase):
    """Build family tree for an agent."""

    @property
    def name(self) -> str:
        return "build_agent_lineage"

    @property
    def description(self) -> str:
        return """
        Build a family tree showing an agent's ancestors and descendants.
        
        Returns lineage information including:
        - Parent-child relationships
        - Agent attributes at each node
        - Generation depth
        - Reproduction success
        
        Use this to:
        - Trace agent ancestry
        - Understand genetic lineages
        - Identify successful family lines
        - Track evolutionary paths
        """

    @property
    def parameters_schema(self):
        return BuildAgentLineageParams

    def execute(self, **params):
        """Execute lineage building."""
        if not self.db.validate_simulation_exists(params["simulation_id"]):
            raise SimulationNotFoundError(params["simulation_id"])

        def query_func(session):
            # Get the target agent
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

            # Build lineage
            lineage = {
                "agent": self._agent_to_dict(agent),
                "ancestors": self._get_ancestors(session, params["simulation_id"], agent, params["depth"]),
                "descendants": self._get_descendants(
                    session, params["simulation_id"], agent, params["depth"]
                ),
            }

            return lineage

        return self.db.execute_query(query_func)

    def _agent_to_dict(self, agent: AgentModel) -> Dict:
        """Convert agent to dictionary."""
        return {
            "agent_id": agent.agent_id,
            "agent_type": agent.agent_type,
            "generation": agent.generation,
            "birth_time": agent.birth_time,
            "death_time": agent.death_time,
            "genome_id": agent.genome_id,
        }

    def _get_ancestors(
        self, session, simulation_id: str, agent: AgentModel, depth: int
    ) -> List[Dict]:
        """Get ancestors of an agent."""
        if depth <= 0:
            return []

        ancestors = []

        # Find parent through reproduction events
        birth_event = (
            session.query(ReproductionEventModel)
            .filter(
                ReproductionEventModel.simulation_id == simulation_id,
                ReproductionEventModel.offspring_id == agent.agent_id,
                ReproductionEventModel.success == True,
            )
            .first()
        )

        if birth_event:
            parent = (
                session.query(AgentModel)
                .filter(
                    AgentModel.simulation_id == simulation_id,
                    AgentModel.agent_id == birth_event.parent_id,
                )
                .first()
            )

            if parent:
                ancestor_info = self._agent_to_dict(parent)
                ancestor_info["relationship"] = "parent"
                ancestor_info["reproduction_event"] = {
                    "step": birth_event.step_number,
                    "resources_cost": birth_event.parent_resources_before
                    - birth_event.parent_resources_after,
                }

                # Recursively get parent's ancestors
                if depth > 1:
                    ancestor_info["ancestors"] = self._get_ancestors(
                        session, simulation_id, parent, depth - 1
                    )

                ancestors.append(ancestor_info)

        return ancestors

    def _get_descendants(
        self, session, simulation_id: str, agent: AgentModel, depth: int
    ) -> List[Dict]:
        """Get descendants of an agent."""
        if depth <= 0:
            return []

        descendants = []

        # Find offspring through reproduction events
        reproduction_events = (
            session.query(ReproductionEventModel)
            .filter(
                ReproductionEventModel.simulation_id == simulation_id,
                ReproductionEventModel.parent_id == agent.agent_id,
                ReproductionEventModel.success == True,
            )
            .all()
        )

        for event in reproduction_events:
            offspring = (
                session.query(AgentModel)
                .filter(
                    AgentModel.simulation_id == simulation_id,
                    AgentModel.agent_id == event.offspring_id,
                )
                .first()
            )

            if offspring:
                descendant_info = self._agent_to_dict(offspring)
                descendant_info["relationship"] = "child"
                descendant_info["reproduction_event"] = {
                    "step": event.step_number,
                    "resources_given": event.offspring_initial_resources,
                }

                # Recursively get offspring's descendants
                if depth > 1:
                    descendant_info["descendants"] = self._get_descendants(
                        session, simulation_id, offspring, depth - 1
                    )

                descendants.append(descendant_info)

        return descendants


class GetAgentLifecycleParams(BaseModel):
    """Parameters for getting complete agent lifecycle."""

    simulation_id: str = Field(..., description="Simulation ID to query")
    agent_id: str = Field(..., description="Agent ID to analyze")
    include_actions: bool = Field(True, description="Include action history")
    include_states: bool = Field(True, description="Include state history")
    include_health: bool = Field(True, description="Include health incidents")


class GetAgentLifecycleTool(ToolBase):
    """Get complete agent lifecycle with all data."""

    @property
    def name(self) -> str:
        return "get_agent_lifecycle"

    @property
    def description(self) -> str:
        return """
        Get complete lifecycle data for a specific agent.
        
        Returns comprehensive agent history including:
        - Basic agent information
        - Complete state history
        - All actions taken
        - Health incidents
        - Reproduction events
        
        Use this to:
        - Deep-dive into agent behavior
        - Debug agent issues
        - Understand agent strategies
        - Analyze complete agent story
        """

    @property
    def parameters_schema(self):
        return GetAgentLifecycleParams

    def execute(self, **params):
        """Execute agent lifecycle retrieval."""
        if not self.db.validate_simulation_exists(params["simulation_id"]):
            raise SimulationNotFoundError(params["simulation_id"])

        def query_func(session):
            from mcp_server.models.database_models import (
                ActionModel,
                AgentStateModel,
                HealthIncident,
            )

            # Get agent
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

            result = {
                "agent_info": {
                    "agent_id": agent.agent_id,
                    "agent_type": agent.agent_type,
                    "generation": agent.generation,
                    "birth_time": agent.birth_time,
                    "death_time": agent.death_time,
                    "lifespan": (
                        agent.death_time - agent.birth_time
                        if agent.death_time
                        else None
                    ),
                    "position": {"x": agent.position_x, "y": agent.position_y},
                    "initial_resources": agent.initial_resources,
                    "starting_health": agent.starting_health,
                    "genome_id": agent.genome_id,
                }
            }

            # Get states if requested
            if params.get("include_states"):
                states = (
                    session.query(AgentStateModel)
                    .filter(AgentStateModel.agent_id == params["agent_id"])
                    .order_by(AgentStateModel.step_number)
                    .all()
                )

                result["states"] = [
                    {
                        "step": s.step_number,
                        "position": {"x": s.position_x, "y": s.position_y, "z": s.position_z},
                        "resources": s.resource_level,
                        "health": s.current_health,
                        "age": s.age,
                        "reward": s.total_reward,
                    }
                    for s in states
                ]
                result["state_count"] = len(states)

            # Get actions if requested
            if params.get("include_actions"):
                actions = (
                    session.query(ActionModel)
                    .filter(ActionModel.agent_id == params["agent_id"])
                    .order_by(ActionModel.step_number)
                    .all()
                )

                result["actions"] = [
                    {
                        "step": a.step_number,
                        "action_type": a.action_type,
                        "target": a.action_target_id,
                        "reward": a.reward,
                        "resources_change": (
                            a.resources_after - a.resources_before
                            if a.resources_after and a.resources_before
                            else None
                        ),
                    }
                    for a in actions
                ]
                result["action_count"] = len(actions)

            # Get health incidents if requested
            if params.get("include_health"):
                incidents = (
                    session.query(HealthIncident)
                    .filter(HealthIncident.agent_id == params["agent_id"])
                    .order_by(HealthIncident.step_number)
                    .all()
                )

                result["health_incidents"] = [
                    {
                        "step": h.step_number,
                        "cause": h.cause,
                        "health_before": h.health_before,
                        "health_after": h.health_after,
                        "damage": h.health_before - h.health_after
                        if h.health_before and h.health_after
                        else None,
                    }
                    for h in incidents
                ]
                result["health_incident_count"] = len(incidents)

            return result

        return self.db.execute_query(query_func)