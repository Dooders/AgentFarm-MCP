"""Agent-related database models.

This module contains models for agents, agent states, and agent actions.
"""

from typing import Any, Dict, Optional

from sqlalchemy import JSON, Boolean, Column, Float, ForeignKey, Index, Integer, String
from sqlalchemy.orm import relationship

from .base import Base


class AgentModel(Base):
    """Represents a simulation agent and its core attributes.

    This model stores the fundamental properties of agents in the simulation,
    including their lifecycle data, physical attributes, and genetic information.

    Attributes
    ----------
    agent_id : str
        Unique identifier for the agent
    birth_time : int
        Step number when the agent was created
    death_time : Optional[int]
        Step number when the agent died (None if still alive)
    agent_type : str
        Type/category of the agent (e.g., 'system', 'independent', 'control')
    position_x : float
        X-coordinate of agent's position
    position_y : float
        Y-coordinate of agent's position
    initial_resources : float
        Starting resource level of the agent
    starting_health : float
        Maximum health capacity of the agent
    starvation_counter : int
        Counter for consecutive steps agent has had zero resources
    genome_id : str
        Unique identifier for agent's genetic code
    generation : int
        Generational number in evolutionary lineage
    action_weights : Dict[str, float]
        Dictionary of action names to their weights/probabilities

    Relationships
    ------------
    states : List[AgentState]
        History of agent states over time
    actions : List[AgentAction]
        History of actions taken by the agent
    health_incidents : List[HealthIncident]
        Record of health-affecting events
    learning_experiences : List[LearningExperience]
        History of learning events and outcomes
    targeted_actions : List[AgentAction]
        Actions where this agent is the target
    """

    __tablename__ = "agents"
    __table_args__ = (
        Index("idx_agents_agent_type", "agent_type"),
        Index("idx_agents_birth_time", "birth_time"),
        Index("idx_agents_death_time", "death_time"),
    )

    simulation_id = Column(String(64), ForeignKey("simulations.simulation_id"))
    agent_id = Column(String(64), primary_key=True)
    birth_time = Column(Integer)
    death_time = Column(Integer)
    agent_type = Column(String(50))
    position_x = Column(Float(precision=6))
    position_y = Column(Float(precision=6))
    initial_resources = Column(Float(precision=6))
    starting_health = Column(Float(precision=4))
    starvation_counter = Column(Integer)
    genome_id = Column(String(64))
    generation = Column(Integer)
    action_weights = Column(JSON, nullable=True)

    # Relationships
    states = relationship("AgentStateModel", back_populates="agent")
    actions = relationship(
        "ActionModel",
        back_populates="agent",
        foreign_keys="[ActionModel.agent_id]",
        primaryjoin="AgentModel.agent_id==ActionModel.agent_id",
    )
    health_incidents = relationship("HealthIncident", back_populates="agent")
    learning_experiences = relationship("LearningExperienceModel", back_populates="agent")
    targeted_actions = relationship(
        "ActionModel",
        foreign_keys="[ActionModel.action_target_id]",
        primaryjoin="AgentModel.agent_id==ActionModel.action_target_id",
        backref="target",
        overlaps="targeted_by",
    )


class AgentStateModel(Base):
    """Tracks the state of an agent at a specific simulation step.

    This model captures the complete state of an agent at each time step,
    including position, resources, health, and cumulative metrics.

    Attributes
    ----------
    id : str
        Unique identifier for the state record
    step_number : int
        Simulation step this state represents
    agent_id : str
        ID of the agent this state belongs to
    position_x : float
        Current X-coordinate position
    position_y : float
        Current Y-coordinate position
    position_z : float
        Current Z-coordinate position
    resource_level : float
        Current resource amount held by agent
    current_health : float
        Current health level
    starting_health : float
        Maximum possible health
    starvation_counter : int
        Consecutive steps with zero resources (for starvation tracking)
    is_defending : bool
        Whether agent is in defensive stance
    total_reward : float
        Cumulative reward received
    age : int
        Number of steps agent has existed

    Relationships
    ------------
    agent : Agent
        The agent this state belongs to

    Methods
    -------
    as_dict() -> Dict[str, Any]
        Convert state to dictionary format for serialization
    """

    __tablename__ = "agent_states"
    __table_args__ = (
        Index("idx_agent_states_agent_id", "agent_id"),
        Index("idx_agent_states_step_number", "step_number"),
        Index("idx_agent_states_agent_step", "agent_id", "step_number"),
        {"sqlite_autoincrement": False},
    )

    id = Column(String(128), primary_key=True, nullable=False)
    simulation_id = Column(String(64), ForeignKey("simulations.simulation_id"))
    step_number = Column(Integer)
    agent_id = Column(String(64), ForeignKey("agents.agent_id"))
    position_x = Column(Float)
    position_y = Column(Float)
    position_z = Column(Float)
    resource_level = Column(Float)
    current_health = Column(Float)
    starting_health = Column(Float(precision=4))
    starvation_counter = Column(Integer)
    is_defending = Column(Boolean)
    total_reward = Column(Float)
    age = Column(Integer)

    agent = relationship("AgentModel", back_populates="states")

    def __init__(self, **kwargs: Any) -> None:
        """Initialize agent state with auto-generated ID."""
        # Generate id before initializing other attributes
        if "agent_id" in kwargs and "step_number" in kwargs:
            sim_id = kwargs.get("simulation_id")
            if sim_id:
                kwargs["id"] = f"{sim_id}:{kwargs['agent_id']}-{kwargs['step_number']}"
            else:
                kwargs["id"] = f"{kwargs['agent_id']}-{kwargs['step_number']}"
        elif "id" not in kwargs:
            raise ValueError("Both agent_id and step_number are required to create AgentStateModel")
        super().__init__(**kwargs)

    @staticmethod
    def generate_id(agent_id: str, step_number: int, simulation_id: str | None = None) -> str:
        """Generate a unique ID for an agent state.

        Args:
            agent_id: Agent identifier
            step_number: Simulation step number
            simulation_id: Optional simulation identifier

        Returns:
            Unique state ID
        """
        # Generate a unique ID by combining components
        if simulation_id:
            return f"{simulation_id}:{agent_id}-{step_number}"
        return f"{agent_id}-{step_number}"

    def as_dict(self) -> Dict[str, Any]:
        """Convert agent state to dictionary.

        Returns:
            Dictionary representation of agent state
        """
        return {
            "agent_id": self.agent_id,
            "step_number": self.step_number,
            "position_x": self.position_x,
            "position_y": self.position_y,
            "position_z": self.position_z,
            "resource_level": self.resource_level,
            "current_health": self.current_health,
            "starting_health": self.starting_health,
            "starvation_counter": self.starvation_counter,
            "is_defending": self.is_defending,
            "total_reward": self.total_reward,
            "age": self.age,
        }


class ActionModel(Base):
    """Record of an action taken by an agent during simulation.

    This model tracks individual actions performed by agents, including the type of action,
    target (if any), position changes, resource changes, and resulting rewards.

    Attributes
    ----------
    action_id : int
        Unique identifier for the action
    step_number : int
        Simulation step when the action occurred
    agent_id : str
        ID of the agent that performed the action
    action_type : str
        Type of action performed (e.g., 'move', 'attack', 'share')
    action_target_id : Optional[str]
        ID of the target agent, if the action involved another agent
    state_before_id : Optional[str]
        Reference to agent's state before the action
    state_after_id : Optional[str]
        Reference to agent's state after the action
    resources_before : float
        Agent's resource level before the action
    resources_after : float
        Agent's resource level after the action
    reward : float
        Reward received for the action
    details : Optional[str]
        JSON string containing additional action details

    Relationships
    ------------
    agent : Agent
        The agent that performed the action
    state_before : Optional[AgentState]
        The agent's state before the action
    state_after : Optional[AgentState]
        The agent's state after the action
    """

    __tablename__ = "agent_actions"
    __table_args__ = (
        Index("idx_agent_actions_step_number", "step_number"),
        Index("idx_agent_actions_agent_id", "agent_id"),
        Index("idx_agent_actions_action_type", "action_type"),
    )

    action_id = Column(Integer, primary_key=True)
    simulation_id = Column(String(64), ForeignKey("simulations.simulation_id"))
    step_number = Column(Integer, nullable=False)
    agent_id = Column(String(64), ForeignKey("agents.agent_id"), nullable=False)
    action_type = Column(String(20), nullable=False)
    action_target_id = Column(String(64), ForeignKey("agents.agent_id"), nullable=True)
    state_before_id = Column(String(128), ForeignKey("agent_states.id"), nullable=True)
    state_after_id = Column(String(128), ForeignKey("agent_states.id"), nullable=True)
    resources_before = Column(Float(precision=6), nullable=True)
    resources_after = Column(Float(precision=6), nullable=True)
    reward = Column(Float(precision=6), nullable=True)
    details = Column(String(1024), nullable=True)

    agent = relationship("AgentModel", back_populates="actions", foreign_keys=[agent_id])
    state_before = relationship("AgentStateModel", foreign_keys=[state_before_id])
    state_after = relationship("AgentStateModel", foreign_keys=[state_after_id])


class LearningExperienceModel(Base):
    """Learning experience records for agents."""

    __tablename__ = "learning_experiences"
    __table_args__ = (
        Index("idx_learning_experiences_step_number", "step_number"),
        Index("idx_learning_experiences_agent_id", "agent_id"),
        Index("idx_learning_experiences_module_type", "module_type"),
    )

    experience_id = Column(Integer, primary_key=True)
    simulation_id = Column(String(64), ForeignKey("simulations.simulation_id"))
    step_number = Column(Integer)
    agent_id = Column(String(64), ForeignKey("agents.agent_id"))
    module_type = Column(String(50))
    module_id = Column(String(64))
    action_taken = Column(Integer)
    action_taken_mapped = Column(String(20))
    reward = Column(Float(precision=6))

    agent = relationship("AgentModel", back_populates="learning_experiences")


class HealthIncident(Base):
    """Health incident records for agents."""

    __tablename__ = "health_incidents"
    __table_args__ = (
        Index("idx_health_incidents_step_number", "step_number"),
        Index("idx_health_incidents_agent_id", "agent_id"),
    )

    incident_id = Column(Integer, primary_key=True)
    simulation_id = Column(String(64), ForeignKey("simulations.simulation_id"))
    step_number = Column(Integer, nullable=False)
    agent_id = Column(String(64), ForeignKey("agents.agent_id"), nullable=False)
    health_before = Column(Float(precision=4))
    health_after = Column(Float(precision=4))
    cause = Column(String(50), nullable=False)
    details = Column(String(512))

    agent = relationship("AgentModel", back_populates="health_incidents")
