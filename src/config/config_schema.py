"""Configuration schema for Tiny Entities simulation."""

from __future__ import annotations

import logging
import yaml
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional, Tuple, Dict, Any

logger = logging.getLogger(__name__)


@dataclass
class WorldConfig:
    """Configuration for the simulation world."""

    width: int = 100
    height: int = 100
    food_spawn_rate: float = 0.1
    food_respawn_probability: float = 0.01
    food_respawn_amount: float = 0.005
    obstacle_density: float = 0.05
    sound_decay_rate: float = 0.9

    def __post_init__(self):
        """Validate configuration values."""
        if self.width < 20 or self.width > 500:
            raise ValueError(f"World width must be between 20 and 500, got {self.width}")
        if self.height < 20 or self.height > 500:
            raise ValueError(f"World height must be between 20 and 500, got {self.height}")
        if not 0.0 <= self.food_spawn_rate <= 1.0:
            raise ValueError(f"Food spawn rate must be between 0 and 1, got {self.food_spawn_rate}")
        if not 0.0 <= self.obstacle_density <= 0.5:
            raise ValueError(f"Obstacle density must be between 0 and 0.5, got {self.obstacle_density}")
        if not 0.0 <= self.sound_decay_rate <= 1.0:
            raise ValueError(f"Sound decay rate must be between 0 and 1, got {self.sound_decay_rate}")

    @property
    def size(self) -> Tuple[int, int]:
        """Get world size as tuple."""
        return (self.width, self.height)


@dataclass
class CreatureConfig:
    """Configuration for creature behavior."""

    initial_count: int = 10
    starting_health: float = 100.0
    starting_energy: float = 100.0
    perception_radius: int = 5
    max_action_tokens: int = 50
    initial_action_tokens: int = 10
    energy_cost_per_step: float = 1.0
    health_decay_when_no_energy: float = 0.1

    def __post_init__(self):
        """Validate configuration values."""
        if self.initial_count < 1:
            raise ValueError(f"Initial count must be at least 1, got {self.initial_count}")
        if self.starting_health <= 0:
            raise ValueError(f"Starting health must be positive, got {self.starting_health}")
        if self.starting_energy <= 0:
            raise ValueError(f"Starting energy must be positive, got {self.starting_energy}")
        if self.perception_radius < 1:
            raise ValueError(f"Perception radius must be at least 1, got {self.perception_radius}")


@dataclass
class MoodConfig:
    """Configuration for the emergent mood system."""

    fast_learning_rate: float = 0.1  # For arousal
    slow_learning_rate: float = 0.01  # For valence
    arousal_decay: float = 0.99
    initial_valence: float = 0.0
    initial_arousal: float = 0.5

    def __post_init__(self):
        """Validate configuration values."""
        if not 0.0 < self.fast_learning_rate <= 1.0:
            raise ValueError(f"Fast learning rate must be between 0 and 1, got {self.fast_learning_rate}")
        if not 0.0 < self.slow_learning_rate <= 1.0:
            raise ValueError(f"Slow learning rate must be between 0 and 1, got {self.slow_learning_rate}")
        if not 0.0 <= self.arousal_decay <= 1.0:
            raise ValueError(f"Arousal decay must be between 0 and 1, got {self.arousal_decay}")
        if not -1.0 <= self.initial_valence <= 1.0:
            raise ValueError(f"Initial valence must be between -1 and 1, got {self.initial_valence}")
        if not 0.0 <= self.initial_arousal <= 1.0:
            raise ValueError(f"Initial arousal must be between 0 and 1, got {self.initial_arousal}")


@dataclass
class ActionConfig:
    """Configuration for action selection."""

    acceptance_rate: float = 0.9
    llm_action_probability: float = 0.2

    def __post_init__(self):
        """Validate configuration values."""
        if not 0.0 <= self.acceptance_rate <= 1.0:
            raise ValueError(f"Acceptance rate must be between 0 and 1, got {self.acceptance_rate}")
        if not 0.0 <= self.llm_action_probability <= 1.0:
            raise ValueError(f"LLM action probability must be between 0 and 1, got {self.llm_action_probability}")


@dataclass
class RewardConfig:
    """Configuration for reward calculations."""

    surprise_multiplier: float = 0.5
    food_reward: float = 1.0
    social_sound_reward: float = 0.3
    collision_penalty: float = -0.2
    proximity_reward: float = 0.1

    def __post_init__(self):
        """Validate configuration values."""
        if self.surprise_multiplier < 0:
            raise ValueError(f"Surprise multiplier must be non-negative, got {self.surprise_multiplier}")


@dataclass
class AnalysisConfig:
    """Configuration for emergence analysis."""

    analyze_every: int = 500
    sound_history_window: int = 50
    rhythm_detection_threshold: float = 0.5

    def __post_init__(self):
        """Validate configuration values."""
        if self.analyze_every < 1:
            raise ValueError(f"Analyze every must be at least 1, got {self.analyze_every}")
        if self.sound_history_window < 1:
            raise ValueError(f"Sound history window must be at least 1, got {self.sound_history_window}")


@dataclass
class SimulationConfig:
    """Complete simulation configuration."""

    world: WorldConfig = field(default_factory=WorldConfig)
    creatures: CreatureConfig = field(default_factory=CreatureConfig)
    mood: MoodConfig = field(default_factory=MoodConfig)
    actions: ActionConfig = field(default_factory=ActionConfig)
    rewards: RewardConfig = field(default_factory=RewardConfig)
    analysis: AnalysisConfig = field(default_factory=AnalysisConfig)

    # Simulation control
    max_steps: int = 10000
    random_seed: Optional[int] = None
    log_level: str = "INFO"

    def __post_init__(self):
        """Validate configuration values."""
        if self.max_steps < 1:
            raise ValueError(f"Max steps must be at least 1, got {self.max_steps}")
        valid_log_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if self.log_level.upper() not in valid_log_levels:
            raise ValueError(f"Log level must be one of {valid_log_levels}, got {self.log_level}")

    @classmethod
    def from_yaml(cls, path: Path) -> SimulationConfig:
        """
        Load configuration from a YAML file.

        Args:
            path: Path to YAML configuration file

        Returns:
            SimulationConfig instance

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If configuration is invalid
        """
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")

        try:
            with open(path, 'r') as f:
                data = yaml.safe_load(f)

            if data is None:
                data = {}

            # Extract nested configurations
            world_config = WorldConfig(**data.get('world', {}))
            creatures_config = CreatureConfig(**data.get('creatures', {}))
            mood_config = MoodConfig(**data.get('mood', {}))
            actions_config = ActionConfig(**data.get('actions', {}))
            rewards_config = RewardConfig(**data.get('rewards', {}))
            analysis_config = AnalysisConfig(**data.get('analysis', {}))

            # Extract top-level simulation parameters
            sim_params = {
                'max_steps': data.get('max_steps', 10000),
                'random_seed': data.get('random_seed'),
                'log_level': data.get('log_level', 'INFO'),
            }

            return cls(
                world=world_config,
                creatures=creatures_config,
                mood=mood_config,
                actions=actions_config,
                rewards=rewards_config,
                analysis=analysis_config,
                **sim_params
            )

        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML file: {e}")
            raise ValueError(f"Invalid YAML configuration: {e}")
        except TypeError as e:
            logger.error(f"Error creating configuration: {e}")
            raise ValueError(f"Invalid configuration parameters: {e}")

    @classmethod
    def default(cls) -> SimulationConfig:
        """Create a default configuration."""
        return cls()

    def to_yaml(self, path: Path):
        """
        Save configuration to a YAML file.

        Args:
            path: Path to save YAML configuration
        """
        try:
            # Ensure directory exists
            path.parent.mkdir(parents=True, exist_ok=True)

            data = {
                'world': asdict(self.world),
                'creatures': asdict(self.creatures),
                'mood': asdict(self.mood),
                'actions': asdict(self.actions),
                'rewards': asdict(self.rewards),
                'analysis': asdict(self.analysis),
                'max_steps': self.max_steps,
                'random_seed': self.random_seed,
                'log_level': self.log_level,
            }

            with open(path, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)

            logger.info(f"Configuration saved to {path}")

        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            raise

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            'world': asdict(self.world),
            'creatures': asdict(self.creatures),
            'mood': asdict(self.mood),
            'actions': asdict(self.actions),
            'rewards': asdict(self.rewards),
            'analysis': asdict(self.analysis),
            'max_steps': self.max_steps,
            'random_seed': self.random_seed,
            'log_level': self.log_level,
        }

    def __str__(self) -> str:
        """String representation of configuration."""
        return (
            f"SimulationConfig("
            f"world={self.world.size}, "
            f"creatures={self.creatures.initial_count}, "
            f"max_steps={self.max_steps}, "
            f"seed={self.random_seed})"
        )
