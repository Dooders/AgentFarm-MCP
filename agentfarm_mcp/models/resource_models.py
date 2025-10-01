"""Resource and environment-related database models.

This module contains models for resources and environmental states.
"""

from typing import Any, Dict

from sqlalchemy import Column, Float, ForeignKey, Index, Integer, String

from .base import Base


class ResourceModel(Base):
    """Tracks the state of resources in the environment.

    This model records the amount and location of resources at each simulation step,
    enabling analysis of resource distribution and movement patterns.

    Attributes
    ----------
    id : int
        Unique identifier for the resource state record
    step_number : int
        Simulation step this state represents
    resource_id : int
        Identifier for the specific resource
    amount : float
        Quantity of resource available
    position_x : float
        X-coordinate of resource location
    position_y : float
        Y-coordinate of resource location

    Methods
    -------
    as_dict() -> Dict[str, Any]
        Convert resource state to dictionary format
    """

    __tablename__ = "resource_states"
    __table_args__ = (
        Index("idx_resource_states_step_number", "step_number"),
        Index("idx_resource_states_resource_id", "resource_id"),
    )

    id = Column(Integer, primary_key=True)
    simulation_id = Column(String(64), ForeignKey("simulations.simulation_id"))
    step_number = Column(Integer)
    resource_id = Column(Integer)
    amount = Column(Float)
    position_x = Column(Float)
    position_y = Column(Float)

    def as_dict(self) -> Dict[str, Any]:
        """Convert resource state to dictionary.

        Returns:
            Dictionary representation of resource state
        """
        return {
            "resource_id": self.resource_id,
            "amount": self.amount,
            "position": (self.position_x, self.position_y),
        }
