import logging
import numpy as np
from typing import Dict, Tuple, Optional, TYPE_CHECKING
from .physics import SimpleWorld

if TYPE_CHECKING:
    from ..config.config_schema import WorldConfig, ActionConfig

logger = logging.getLogger(__name__)

# Valid action names
VALID_ACTIONS = {
    "move_north", "move_south", "move_east", "move_west",
    "explore", "stay", "eat", "listen",
    "make_sound_low", "make_sound_high"
}


class NonDeterministicWorldModel:
    """World model that can accept/reject actions and update state"""

    def __init__(
        self,
        acceptance_rate: float = 0.9,
        world_config: Optional['WorldConfig'] = None,
        action_config: Optional['ActionConfig'] = None
    ):
        """
        Initialize world model with optional configuration.

        Args:
            acceptance_rate: Legacy parameter (use action_config instead)
            world_config: Configuration for world parameters
            action_config: Configuration for action acceptance
        """
        # Use action_config if provided, otherwise use acceptance_rate parameter
        if action_config:
            self.acceptance_rate = action_config.acceptance_rate
        else:
            self.acceptance_rate = acceptance_rate

        # Create world with config
        self.world = SimpleWorld(config=world_config)

        # Track creature positions
        self.creature_positions = {}

    def propose_action(
        self, creature_id: str, action: str, current_pos: Tuple[int, int]
    ) -> Dict:
        """Propose action and get world's response with validation."""
        try:
            # Validate creature_id
            if not creature_id or not isinstance(creature_id, str):
                logger.warning(f"Invalid creature_id: {creature_id}")
                return {
                    "accepted": False,
                    "new_position": current_pos,
                    "effect": "invalid_id",
                    "message": "Invalid creature ID"
                }

            # Validate action name
            if not isinstance(action, str):
                logger.warning(f"Invalid action type for {creature_id}: {type(action)}")
                action = str(action) if action else "stay"

            if action not in VALID_ACTIONS:
                logger.debug(f"Unknown action '{action}' for {creature_id}, treating as 'stay'")
                action = "stay"

            # Validate position
            if not self._is_valid_position(current_pos):
                logger.error(f"Invalid position for {creature_id}: {current_pos}")
                # Try to clamp to valid bounds
                current_pos = self._clamp_position(current_pos)
                logger.info(f"Clamped position to {current_pos}")

            # Update creature tracking
            self.creature_positions[creature_id] = current_pos

            # World decides whether to accept action
            accepted = np.random.random() < self.acceptance_rate

            if not accepted:
                return {
                    "accepted": False,
                    "new_position": current_pos,
                    "effect": "action_blocked",
                    "message": "World rejected action",
                }

            # Execute action if accepted
            result = self._execute_action(creature_id, action, current_pos)
            result["accepted"] = True

            return result

        except Exception as e:
            logger.error(f"Error in propose_action for {creature_id}: {e}", exc_info=True)
            # Return safe fallback
            return {
                "accepted": False,
                "new_position": current_pos,
                "effect": "error",
                "message": f"Action processing error: {e}",
                "near_creatures": 0
            }

    def _is_valid_position(self, pos: Tuple[int, int]) -> bool:
        """Check if position is within world bounds."""
        try:
            x, y = pos
            return (
                isinstance(x, (int, np.integer)) and
                isinstance(y, (int, np.integer)) and
                0 <= x < self.world.width and
                0 <= y < self.world.height
            )
        except (TypeError, ValueError):
            return False

    def _clamp_position(self, pos: Tuple[int, int]) -> Tuple[int, int]:
        """Clamp position to valid world bounds."""
        try:
            x, y = pos
            x = max(0, min(int(x), self.world.width - 1))
            y = max(0, min(int(y), self.world.height - 1))
            return (x, y)
        except (TypeError, ValueError) as e:
            logger.error(f"Cannot clamp invalid position {pos}: {e}")
            # Return safe default (center of world)
            return (self.world.width // 2, self.world.height // 2)

    def _execute_action(
        self, creature_id: str, action: str, pos: Tuple[int, int]
    ) -> Dict:
        """Execute accepted action and update world with validation."""
        try:
            x, y = pos
            new_x, new_y = x, y
            effect = "none"
            extras = {}

            # Movement actions with bounds checking
            if action == "move_north" and y > 0:
                new_y = y - 1
            elif action == "move_south" and y < self.world.height - 1:
                new_y = y + 1
            elif action == "move_east" and x < self.world.width - 1:
                new_x = x + 1
            elif action == "move_west" and x > 0:
                new_x = x - 1
            elif action == "explore":
                # Random movement with bounds checking
                direction = np.random.choice(["north", "south", "east", "west"])
                if direction == "north" and y > 0:
                    new_y = y - 1
                elif direction == "south" and y < self.world.height - 1:
                    new_y = y + 1
                elif direction == "east" and x < self.world.width - 1:
                    new_x = x + 1
                elif direction == "west" and x > 0:
                    new_x = x - 1

            # Validate new position is in bounds
            if not self._is_valid_position((new_x, new_y)):
                logger.warning(f"Calculated invalid new position ({new_x}, {new_y}), staying at ({x}, {y})")
                new_x, new_y = x, y

            # Check if movement is valid (not into obstacle or another creature)
            if (new_x, new_y) != (x, y):
                # Safe grid access with bounds check
                if 0 <= new_y < self.world.height and 0 <= new_x < self.world.width:
                    if self.world.grid[new_y, new_x] == 2:  # Obstacle
                        new_x, new_y = x, y  # Can't move
                        effect = "collision"
                    elif self.world.grid[new_y, new_x] == 1:  # Food
                        effect = "found_food"

                # Check for other creatures
                for other_id, other_pos in self.creature_positions.items():
                    if other_id != creature_id and other_pos == (new_x, new_y):
                        new_x, new_y = x, y  # Can't move into another creature
                        effect = "collision"
                        break

            # Eating action with bounds check
            if action == "eat":
                if 0 <= y < self.world.height and 0 <= x < self.world.width:
                    if self.world.grid[y, x] == 1:
                        self.world.grid[y, x] = 0
                        effect = "found_food"
                else:
                    logger.warning(f"Eat action at invalid position ({x}, {y})")

            # Sound actions
            if "sound" in action:
                if 0 <= x < self.world.width and 0 <= y < self.world.height:
                    freq = 0.3 if "low" in action else 0.7
                    self.world.update_sound(x, y, freq, 0.8)
                    effect = "made_sound"

                    # Check if other creatures nearby to respond
                    nearby_creatures = 0
                    for other_id, other_pos in self.creature_positions.items():
                        if other_id != creature_id:
                            try:
                                dist = abs(other_pos[0] - x) + abs(other_pos[1] - y)
                                if dist <= 3:  # Within hearing range
                                    nearby_creatures += 1
                            except (TypeError, IndexError):
                                logger.warning(f"Invalid position for {other_id}: {other_pos}")
                                continue

                    if nearby_creatures > 0:
                        extras["creatures_responded"] = nearby_creatures
                else:
                    logger.warning(f"Sound action at invalid position ({x}, {y})")

            # Count nearby creatures for social rewards
            nearby_creatures = 0
            for other_id, other_pos in self.creature_positions.items():
                if other_id != creature_id:
                    try:
                        dist = abs(other_pos[0] - x) + abs(other_pos[1] - y)
                        if dist <= 2:
                            nearby_creatures += 1
                    except (TypeError, IndexError):
                        logger.warning(f"Invalid position for {other_id}: {other_pos}")
                        continue

            extras["near_creatures"] = nearby_creatures

            # Update creature position tracking
            self.creature_positions[creature_id] = (new_x, new_y)

            return {
                "new_position": (new_x, new_y),
                "effect": effect,
                "world_state": self.world.get_local_view(new_x, new_y),
                **extras,
            }

        except Exception as e:
            logger.error(f"Error executing action '{action}' for {creature_id}: {e}", exc_info=True)
            # Return safe fallback
            return {
                "new_position": pos,
                "effect": "error",
                "world_state": None,
                "near_creatures": 0
            }
