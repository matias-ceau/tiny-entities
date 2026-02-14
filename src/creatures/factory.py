"""Factory for creating creature instances"""

import numpy as np
from typing import List, Dict, Any, Optional, TYPE_CHECKING

from .brain import EnhancedBrain

if TYPE_CHECKING:
    from ..config.config_schema import CreatureConfig, MoodConfig
    from ..config.llm_client import LLMClient
    from ..world.physics import SimpleWorld


def _random_coordinate_with_margin(limit: int, preferred_margin: int = 10) -> int:
    """Return a random coordinate while preferring to avoid world edges."""
    if limit <= 1:
        return 0

    margin = min(preferred_margin, max(0, (limit - 1) // 2))
    low = margin
    high = limit - margin

    if high <= low:
        low = 0
        high = limit

    return np.random.randint(low, high)


def create_creatures(
    num: int,
    world: 'SimpleWorld',
    creature_config: Optional['CreatureConfig'] = None,
    mood_config: Optional['MoodConfig'] = None,
    llm_client: Optional['LLMClient'] = None
) -> List[Dict[str, Any]]:
    """
    Create initial creatures for the simulation.

    Args:
        num: Number of creatures to create
        world: The world they inhabit (for positioning)
        creature_config: Optional creature configuration
        mood_config: Optional mood system configuration
        llm_client: Optional LLM client for reflections

    Returns:
        List of creature dictionaries with brain, position, alive status, etc.
    """
    creatures = []

    for i in range(num):
        # Random starting position (prefer avoiding edges where possible)
        x = _random_coordinate_with_margin(world.width)
        y = _random_coordinate_with_margin(world.height)

        # Create enhanced brain with configurations
        # Note: LLM client is obtained via get_llm_client() internally
        brain = EnhancedBrain(
            creature_id=f"creature_{i}",
            creature_config=creature_config,
            mood_config=mood_config
        )

        creature = {
            "id": f"creature_{i}",
            "brain": brain,
            "position": (x, y),
            "alive": True,
            "birth_step": 0,
        }

        creatures.append(creature)

    return creatures
