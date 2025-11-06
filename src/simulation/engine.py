"""Core simulation engine - handles timestep processing."""

import logging
import time
from typing import List, Dict, Any, Optional

import numpy as np

from ..creatures.action_selection import MoodInfluencedActionSelector
from ..world.non_deterministic import NonDeterministicWorldModel

logger = logging.getLogger(__name__)


class SimulationEngine:
    """
    Core simulation loop - processes one timestep.

    Responsibilities:
    - Execute one simulation step
    - Process each creature's perception-action cycle
    - Update world physics
    - Track step count
    """

    def __init__(
        self,
        world_model: NonDeterministicWorldModel,
        action_selector: MoodInfluencedActionSelector
    ):
        """
        Initialize simulation engine.

        Args:
            world_model: The world model for physics and actions
            action_selector: Action selection strategy
        """
        self.world_model = world_model
        self.action_selector = action_selector
        self.creatures: List[Dict[str, Any]] = []
        self.step_count = 0

    def add_creatures(self, creatures: List[Dict[str, Any]]) -> None:
        """
        Add creatures to the simulation.

        Args:
            creatures: List of creature dictionaries
        """
        self.creatures = creatures
        logger.debug(f"Added {len(creatures)} creatures to simulation engine")

    async def step(self) -> List[Dict[str, Any]]:
        """
        Execute one simulation step.

        Returns:
            List of events that occurred this step
        """
        events = []
        step_start = time.time()

        # Process each creature
        for creature in self.creatures:
            if not creature["alive"]:
                continue

            try:
                # Get perception
                world_view = self.world_model.world.get_local_view(
                    creature["position"][0], creature["position"][1]
                )
                perception = self._process_perception(world_view)

                # Select action
                action = self.action_selector.select_action(
                    creature["brain"], perception
                )

                # Execute action in world
                outcome = self.world_model.propose_action(
                    creature["id"], action, creature["position"]
                )

                # Update creature position
                old_position = creature["position"]
                creature["position"] = outcome["new_position"]

                # Process cognitive cycle
                brain_update = creature["brain"].process_timestep(
                    perception, action, outcome
                )

                # Create event
                event = {
                    "type": "action",
                    "step": self.step_count,
                    "creature_id": creature["id"],
                    "action": action,
                    "old_position": old_position,
                    "new_position": creature["position"],
                    "outcome": outcome,
                    "brain_update": brain_update,
                    "mood": {
                        "valence": creature["brain"].mood_system.valence,
                        "arousal": creature["brain"].mood_system.arousal,
                    },
                }
                events.append(event)

                # Check for death
                if creature["brain"].health <= 0:
                    creature["alive"] = False
                    death_event = {
                        "type": "death",
                        "step": self.step_count,
                        "creature_id": creature["id"],
                        "position": creature["position"],
                    }
                    events.append(death_event)
                    logger.info(f"{creature['id']} died at step {self.step_count}")

            except Exception as e:
                logger.error(
                    f"Error processing creature {creature['id']}: {e}",
                    exc_info=True
                )
                # Continue with other creatures

        # Update world physics
        self.world_model.world.step()

        self.step_count += 1

        # Add performance event
        step_duration = time.time() - step_start
        events.append({
            "type": "performance",
            "step": self.step_count,
            "step_duration": step_duration,
        })

        return events

    def _process_perception(self, world_view: Dict) -> Dict:
        """
        Process raw world view into creature perception.

        Args:
            world_view: Raw view from world model

        Returns:
            Processed perception dictionary
        """
        return {
            "visual": world_view["visual"],
            "sound": world_view["sound"],
            "food_count": world_view["food_count"],
            "obstacle_count": world_view["obstacle_count"],
            "creature_count": world_view["creature_count"],
        }

    def get_alive_count(self) -> int:
        """Get number of alive creatures."""
        return sum(1 for c in self.creatures if c["alive"])

    def all_dead(self) -> bool:
        """Check if all creatures are dead."""
        return not any(c["alive"] for c in self.creatures)
