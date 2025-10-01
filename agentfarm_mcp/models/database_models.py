"""SQLAlchemy models for the simulation database.

This module re-exports models from the new modular structure for backwards compatibility.
"""

# Import base
from .base import Base

# Import agent-related models
from .agent_models import (
    ActionModel,
    AgentModel,
    AgentStateModel,
    HealthIncident,
    LearningExperienceModel,
)

# Import comparison models
from .comparison_models import SimulationComparison, SimulationDifference

# Import interaction models
from .interaction_models import (
    InteractionModel,
    ReproductionEventModel,
    SocialInteractionModel,
)

# Import resource models
from .resource_models import ResourceModel

# Import simulation models
from .simulation_models import (
    ExperimentModel,
    Simulation,
    SimulationConfig,
    SimulationStepModel,
)

# Re-export all models for backwards compatibility
__all__ = [
    "Base",
    "AgentModel",
    "AgentStateModel",
    "ActionModel",
    "LearningExperienceModel",
    "HealthIncident",
    "ResourceModel",
    "InteractionModel",
    "SimulationStepModel",
    "SimulationConfig",
    "ExperimentModel",
    "Simulation",
    "ReproductionEventModel",
    "SocialInteractionModel",
    "SimulationDifference",
    "SimulationComparison",
]
