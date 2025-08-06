import numpy as np
from typing import Dict, Tuple
from .physics import SimpleWorld


class NonDeterministicWorldModel:
    """World model that can accept/reject actions and update state"""

    def __init__(self, acceptance_rate: float = 0.9):
        self.acceptance_rate = acceptance_rate
        self.world = SimpleWorld()

        # Track creature positions
        self.creature_positions = {}

    def propose_action(
        self, creature_id: str, action: str, current_pos: Tuple[int, int]
    ) -> Dict:
        """Propose action and get world's response"""

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

    def _execute_action(
        self, creature_id: str, action: str, pos: Tuple[int, int]
    ) -> Dict:
        """Execute accepted action and update world"""
        x, y = pos
        new_x, new_y = x, y
        effect = "none"
        extras = {}

        # Movement actions
        if action == "move_north" and y > 0:
            new_y = y - 1
        elif action == "move_south" and y < self.world.height - 1:
            new_y = y + 1
        elif action == "move_east" and x < self.world.width - 1:
            new_x = x + 1
        elif action == "move_west" and x > 0:
            new_x = x - 1
        elif action == "explore":
            # Random movement
            direction = np.random.choice(["north", "south", "east", "west"])
            if direction == "north" and y > 0:
                new_y = y - 1
            elif direction == "south" and y < self.world.height - 1:
                new_y = y + 1
            elif direction == "east" and x < self.world.width - 1:
                new_x = x + 1
            elif direction == "west" and x > 0:
                new_x = x - 1

        # Check if movement is valid (not into obstacle or another creature)
        if (new_x, new_y) != (x, y):
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

        # Eating action
        if action == "eat" and self.world.grid[y, x] == 1:
            self.world.grid[y, x] = 0
            effect = "found_food"

        # Sound actions
        if "sound" in action:
            freq = 0.3 if "low" in action else 0.7
            self.world.update_sound(x, y, freq, 0.8)
            effect = "made_sound"

            # Check if other creatures nearby to respond
            nearby_creatures = 0
            for other_id, other_pos in self.creature_positions.items():
                if other_id != creature_id:
                    dist = abs(other_pos[0] - x) + abs(other_pos[1] - y)
                    if dist <= 3:  # Within hearing range
                        nearby_creatures += 1

            if nearby_creatures > 0:
                extras["creatures_responded"] = nearby_creatures

        # Count nearby creatures for social rewards
        nearby_creatures = 0
        for other_id, other_pos in self.creature_positions.items():
            if other_id != creature_id:
                dist = abs(other_pos[0] - x) + abs(other_pos[1] - y)
                if dist <= 2:
                    nearby_creatures += 1

        extras["near_creatures"] = nearby_creatures

        # Update creature position tracking
        self.creature_positions[creature_id] = (new_x, new_y)

        return {
            "new_position": (new_x, new_y),
            "effect": effect,
            "world_state": self.world.get_local_view(new_x, new_y),
            **extras,
        }
