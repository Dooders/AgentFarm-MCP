"""Simulation-level database models.

This module contains models for simulations, experiments, and simulation-level metrics.
"""

from datetime import datetime, timezone
from typing import Any, Dict

from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, Index, Integer, PrimaryKeyConstraint, String
from sqlalchemy.orm import relationship

from .base import Base


class SimulationStepModel(Base):
    """Records simulation-wide metrics for each time step.

    This model captures aggregate statistics and metrics about the entire simulation
    state at each step, including population counts, resource metrics, and various
    performance indicators.

    Attributes
    ----------
    step_number : int
        Unique step identifier
    total_agents : int
        Total number of living agents
    system_agents : int
        Number of system-type agents
    independent_agents : int
        Number of independent-type agents
    control_agents : int
        Number of control-type agents
    total_resources : float
        Total resources in environment
    average_agent_resources : float
        Mean resources per agent
    births : int
        Number of new agents created this step
    deaths : int
        Number of agents that died this step
    current_max_generation : int
        Highest generation number present
    resource_efficiency : float
        Measure of resource utilization efficiency
    resource_distribution_entropy : float
        Measure of resource distribution evenness
    average_agent_health : float
        Mean health across all agents
    average_agent_age : int
        Mean age of all agents
    average_reward : float
        Mean reward received by agents
    combat_encounters : int
        Number of combat interactions
    successful_attacks : int
        Number of successful attack actions
    resources_shared : float
        Amount of resources transferred between agents
    resources_shared_this_step : float
        Amount of resources transferred between agents in the current step
    combat_encounters_this_step : int
        Number of combat interactions in the current step
    successful_attacks_this_step : int
        Number of successful attack actions in the current step
    genetic_diversity : float
        Measure of genetic variation in population
    dominant_genome_ratio : float
        Proportion of agents sharing most common genome
    resources_consumed : float
        Total resources consumed by the simulation

    Methods
    -------
    as_dict() -> Dict[str, Any]
        Convert step metrics to dictionary format
    """

    __tablename__ = "simulation_steps"

    __table_args__ = (
        PrimaryKeyConstraint("step_number", "simulation_id"),
        Index("idx_simulation_steps_step_number", "step_number"),
        Index("idx_simulation_steps_simulation_id", "simulation_id"),
    )

    step_number = Column(Integer, primary_key=False)
    simulation_id = Column(String(64), ForeignKey("simulations.simulation_id"))
    total_agents = Column(Integer)
    system_agents = Column(Integer)
    independent_agents = Column(Integer)
    control_agents = Column(Integer)
    total_resources = Column(Float)
    average_agent_resources = Column(Float)
    births = Column(Integer)
    deaths = Column(Integer)
    current_max_generation = Column(Integer)
    resource_efficiency = Column(Float)
    resource_distribution_entropy = Column(Float)
    average_agent_health = Column(Float)
    average_agent_age = Column(Integer)
    average_reward = Column(Float)
    combat_encounters = Column(Integer)
    successful_attacks = Column(Integer)
    resources_shared = Column(Float)
    resources_shared_this_step = Column(Float, default=0.0)
    combat_encounters_this_step = Column(Integer, default=0)
    successful_attacks_this_step = Column(Integer, default=0)
    genetic_diversity = Column(Float)
    dominant_genome_ratio = Column(Float)
    resources_consumed = Column(Float, default=0.0)

    def as_dict(self) -> Dict[str, Any]:
        """Convert simulation step to dictionary.

        Returns:
            Dictionary representation of step metrics
        """
        return {
            "total_agents": self.total_agents,
            "system_agents": self.system_agents,
            "independent_agents": self.independent_agents,
            "control_agents": self.control_agents,
            "total_resources": self.total_resources,
            "average_agent_resources": self.average_agent_resources,
            "births": self.births,
            "deaths": self.deaths,
            "current_max_generation": self.current_max_generation,
            "resource_efficiency": self.resource_efficiency,
            "resource_distribution_entropy": self.resource_distribution_entropy,
            "average_agent_health": self.average_agent_health,
            "average_agent_age": self.average_agent_age,
            "average_reward": self.average_reward,
            "combat_encounters": self.combat_encounters,
            "successful_attacks": self.successful_attacks,
            "resources_shared": self.resources_shared,
            "resources_shared_this_step": self.resources_shared_this_step,
            "combat_encounters_this_step": self.combat_encounters_this_step,
            "successful_attacks_this_step": self.successful_attacks_this_step,
            "genetic_diversity": self.genetic_diversity,
            "dominant_genome_ratio": self.dominant_genome_ratio,
            "resources_consumed": self.resources_consumed,
        }


class SimulationConfig(Base):
    """Simulation configuration records."""

    __tablename__ = "simulation_config"

    simulation_id = Column(String(64), ForeignKey("simulations.simulation_id"))
    config_id = Column(Integer, primary_key=True)
    timestamp = Column(Integer, nullable=False)
    config_data = Column(String(4096), nullable=False)


class ExperimentModel(Base):
    """Represents a research experiment that groups related simulations.

    This model stores metadata about an experiment, including its purpose,
    hypothesis, and parameters varied across simulations.

    Attributes
    ----------
    experiment_id : str
        Unique identifier for the experiment
    name : str
        Human-readable name of the experiment
    description : str
        Detailed description of the experiment's purpose
    hypothesis : str
        The research hypothesis being tested
    creation_date : DateTime
        When the experiment was created
    last_updated : DateTime
        When the experiment was last modified
    status : str
        Current status (e.g., 'planned', 'running', 'completed', 'analyzed')
    tags : list
        List of keywords/tags for categorization
    variables : dict
        Dictionary of variables being manipulated across simulations
    results_summary : dict
        High-level findings from the experiment
    notes : str
        Additional research notes or observations

    Relationships
    ------------
    simulations : List[Simulation]
        All simulations that are part of this experiment
    """

    __tablename__ = "experiments"

    experiment_id = Column(String(64), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(String(4096), nullable=True)
    hypothesis = Column(String(2048), nullable=True)
    creation_date = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_updated = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    status = Column(String(50), default="planned")
    tags = Column(JSON, nullable=True)
    variables = Column(JSON, nullable=True)
    results_summary = Column(JSON, nullable=True)
    notes = Column(String(4096), nullable=True)

    # Relationships
    simulations = relationship("Simulation", back_populates="experiment")

    def __repr__(self) -> str:
        """String representation of experiment.

        Returns:
            String representation
        """
        return f"<Experiment(experiment_id={self.experiment_id}, name={self.name}, status={self.status})>"


class Simulation(Base):
    """Simulation records and metadata."""

    __tablename__ = "simulations"

    simulation_id = Column(String(64), primary_key=True)
    experiment_id = Column(String(64), ForeignKey("experiments.experiment_id"), nullable=True)
    start_time = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    end_time = Column(DateTime, nullable=True)
    status = Column(String(50), default="pending")
    parameters = Column(JSON, nullable=False)
    results_summary = Column(JSON, nullable=True)
    simulation_db_path = Column(String(255), nullable=False)

    # Relationships
    experiment = relationship("ExperimentModel", back_populates="simulations")

    def __repr__(self) -> str:
        """String representation of simulation.

        Returns:
            String representation
        """
        return f"<Simulation(simulation_id={self.simulation_id}, status={self.status})>"
