"""Interaction and event-related database models.

This module contains models for interactions, reproduction events, and social behaviors.
"""

from datetime import datetime, timezone
from typing import Any, Dict

from sqlalchemy import JSON, Boolean, Column, DateTime, Float, ForeignKey, Index, Integer, String
from sqlalchemy.orm import relationship

from .base import Base


class InteractionModel(Base):
    """Generic interaction edges between nodes in the environment.

    This table captures interactions as edges between source and target nodes
    (e.g., agent->agent, agent->resource) with consistent metadata for
    downstream analytics and visualization.
    """

    __tablename__ = "interactions"
    __table_args__ = (
        Index("idx_interactions_step_number", "step_number"),
        Index("idx_interactions_source", "source_type", "source_id"),
        Index("idx_interactions_target", "target_type", "target_id"),
        Index("idx_interactions_type", "interaction_type"),
    )

    interaction_id = Column(Integer, primary_key=True)
    simulation_id = Column(String(64), ForeignKey("simulations.simulation_id"))
    step_number = Column(Integer, nullable=False)

    # Source node
    source_type = Column(String(32), nullable=False)  # e.g., 'agent', 'resource'
    source_id = Column(String(64), nullable=False)

    # Target node
    target_type = Column(String(32), nullable=False)  # e.g., 'agent', 'resource'
    target_id = Column(String(64), nullable=False)

    # Semantics
    interaction_type = Column(
        String(50), nullable=False
    )  # e.g., 'share', 'attack', 'gather', 'reproduce'
    action_type = Column(String(50), nullable=True)
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)


class ReproductionEventModel(Base):
    """Records reproduction attempts and outcomes in the simulation.

    This model tracks both successful and failed reproduction attempts,
    including details about the parent agent, resources involved, and
    any offspring created.

    Attributes
    ----------
    event_id : int
        Unique identifier for the reproduction event
    step_number : int
        Simulation step when the reproduction attempt occurred
    parent_id : str
        ID of the agent attempting reproduction
    offspring_id : Optional[str]
        ID of the created offspring (if successful)
    success : bool
        Whether the reproduction attempt succeeded
    parent_resources_before : float
        Parent's resource level before reproduction
    parent_resources_after : float
        Parent's resource level after reproduction
    offspring_initial_resources : float
        Resources given to offspring (if successful)
    failure_reason : Optional[str]
        Reason for failed reproduction attempt
    parent_generation : int
        Generation number of parent agent
    offspring_generation : Optional[int]
        Generation number of offspring (if successful)
    parent_position_x : float
        X-coordinate where reproduction occurred
    parent_position_y : float
        Y-coordinate where reproduction occurred
    timestamp : DateTime
        When the event occurred

    Relationships
    ------------
    parent : Agent
        The agent that attempted reproduction
    offspring : Optional[Agent]
        The newly created agent (if successful)
    """

    __tablename__ = "reproduction_events"
    __table_args__ = (
        Index("idx_reproduction_events_step_number", "step_number"),
        Index("idx_reproduction_events_parent_id", "parent_id"),
        Index("idx_reproduction_events_success", "success"),
    )

    event_id = Column(Integer, primary_key=True)
    simulation_id = Column(String(64), ForeignKey("simulations.simulation_id"))
    step_number = Column(Integer, nullable=False)
    parent_id = Column(String(64), ForeignKey("agents.agent_id"), nullable=False)
    offspring_id = Column(String(64), ForeignKey("agents.agent_id"), nullable=True)
    success = Column(Boolean, nullable=False)
    parent_resources_before = Column(Float(precision=6), nullable=False)
    parent_resources_after = Column(Float(precision=6), nullable=False)
    offspring_initial_resources = Column(Float(precision=6), nullable=True)
    failure_reason = Column(String(255), nullable=True)
    parent_generation = Column(Integer, nullable=False)
    offspring_generation = Column(Integer, nullable=True)
    parent_position_x = Column(Float, nullable=False)
    parent_position_y = Column(Float, nullable=False)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    parent = relationship("AgentModel", foreign_keys=[parent_id], backref="reproduction_attempts")
    offspring = relationship("AgentModel", foreign_keys=[offspring_id], backref="creation_event")

    def as_dict(self) -> Dict[str, Any]:
        """Convert reproduction event to dictionary format.

        Returns:
            Dictionary representation of reproduction event
        """
        return {
            "step_number": self.step_number,
            "parent_id": self.parent_id,
            "offspring_id": self.offspring_id,
            "success": self.success,
            "parent_resources_before": self.parent_resources_before,
            "parent_resources_after": self.parent_resources_after,
            "offspring_initial_resources": self.offspring_initial_resources,
            "failure_reason": self.failure_reason,
            "parent_generation": self.parent_generation,
            "offspring_generation": self.offspring_generation,
            "parent_position": (self.parent_position_x, self.parent_position_y),
            "timestamp": self.timestamp,
        }


class SocialInteractionModel(Base):
    """Records social interactions between agents in the simulation.

    This model tracks various types of social interactions between agents,
    including cooperation, competition, resource sharing, territory defense,
    and group formation behaviors.

    Attributes
    ----------
    interaction_id : int
        Unique identifier for the social interaction
    step_number : int
        Simulation step when the interaction occurred
    initiator_id : str
        ID of the agent that initiated the interaction
    recipient_id : str
        ID of the agent that received/responded to the interaction
    interaction_type : str
        Type of social interaction (e.g., 'cooperation', 'competition', 'group_formation')
    subtype : str
        Specific subtype of the interaction (e.g., 'resource_sharing', 'territory_defense')
    outcome : str
        Outcome of the interaction (e.g., 'successful', 'rejected', 'conflict')
    resources_transferred : float
        Amount of resources exchanged during the interaction (if applicable)
    distance : float
        Distance between agents during the interaction
    initiator_resources_before : float
        Initiator's resource level before the interaction
    initiator_resources_after : float
        Initiator's resource level after the interaction
    recipient_resources_before : float
        Recipient's resource level before the interaction
    recipient_resources_after : float
        Recipient's resource level after the interaction
    group_id : str
        Identifier for the group/cluster if this interaction involves group behavior
    details : dict
        Additional interaction-specific details stored as JSON
    timestamp : DateTime
        When the interaction occurred

    Relationships
    ------------
    initiator : Agent
        The agent that initiated the interaction
    recipient : Agent
        The agent that received/responded to the interaction
    """

    __tablename__ = "social_interactions"
    __table_args__ = (
        Index("idx_social_interactions_step_number", "step_number"),
        Index("idx_social_interactions_initiator_id", "initiator_id"),
        Index("idx_social_interactions_recipient_id", "recipient_id"),
        Index("idx_social_interactions_interaction_type", "interaction_type"),
    )

    interaction_id = Column(Integer, primary_key=True)
    simulation_id = Column(String(64), ForeignKey("simulations.simulation_id"))
    step_number = Column(Integer, nullable=False)
    initiator_id = Column(String(64), ForeignKey("agents.agent_id"), nullable=False)
    recipient_id = Column(String(64), ForeignKey("agents.agent_id"), nullable=False)
    interaction_type = Column(String(50), nullable=False)
    subtype = Column(String(50), nullable=True)
    outcome = Column(String(50), nullable=False)
    resources_transferred = Column(Float(precision=6), nullable=True)
    distance = Column(Float, nullable=True)
    initiator_resources_before = Column(Float(precision=6), nullable=True)
    initiator_resources_after = Column(Float(precision=6), nullable=True)
    recipient_resources_before = Column(Float(precision=6), nullable=True)
    recipient_resources_after = Column(Float(precision=6), nullable=True)
    group_id = Column(String(64), nullable=True)
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)

    # Relationships
    initiator = relationship(
        "AgentModel", foreign_keys=[initiator_id], backref="initiated_interactions"
    )
    recipient = relationship(
        "AgentModel", foreign_keys=[recipient_id], backref="received_interactions"
    )

    def as_dict(self) -> Dict[str, Any]:
        """Convert social interaction to dictionary format.

        Returns:
            Dictionary representation of social interaction
        """
        return {
            "step_number": self.step_number,
            "initiator_id": self.initiator_id,
            "recipient_id": self.recipient_id,
            "interaction_type": self.interaction_type,
            "subtype": self.subtype,
            "outcome": self.outcome,
            "resources_transferred": self.resources_transferred,
            "distance": self.distance,
            "initiator_resources_before": self.initiator_resources_before,
            "initiator_resources_after": self.initiator_resources_after,
            "recipient_resources_before": self.recipient_resources_before,
            "recipient_resources_after": self.recipient_resources_after,
            "group_id": self.group_id,
            "details": self.details,
            "timestamp": self.timestamp,
        }
