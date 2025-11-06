import numpy as np
from typing import Dict, List, Tuple, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from ..config.config_schema import WorldConfig


class SimpleWorld:
    """Conway's Game of Life inspired 2D world with resources"""

    def __init__(
        self,
        width: int = 100,
        height: int = 100,
        config: Optional['WorldConfig'] = None
    ):
        """
        Initialize world with optional configuration.

        Args:
            width: World width (used if config not provided)
            height: World height (used if config not provided)
            config: WorldConfig instance with all parameters
        """
        # Use config if provided, otherwise use parameters or defaults
        if config:
            self.width = config.width
            self.height = config.height
            self.food_spawn_rate = config.food_spawn_rate
            self.food_respawn_probability = config.food_respawn_probability
            self.food_respawn_amount = config.food_respawn_amount
            self.obstacle_density = config.obstacle_density
            self.sound_decay_rate = config.sound_decay_rate
        else:
            # Backward compatibility
            self.width = width
            self.height = height
            self.food_spawn_rate = 0.1
            self.food_respawn_probability = 0.01
            self.food_respawn_amount = 0.005
            self.obstacle_density = 0.05
            self.sound_decay_rate = 0.9

        # World state: 0=empty, 1=food, 2=obstacle, 3=creature
        self.grid = np.zeros((self.height, self.width), dtype=int)

        # Sound layer - simple frequency/amplitude at each location
        self.sound_grid = np.zeros((self.height, self.width, 2))  # [frequency, amplitude]

        # Spawn initial resources using configured values
        self._spawn_food(density=self.food_spawn_rate)
        self._spawn_obstacles(density=self.obstacle_density)

    def _spawn_food(self, density: float):
        """Randomly place food in world"""
        food_count = int(self.width * self.height * density)
        for _ in range(food_count):
            x = np.random.randint(0, self.width)
            y = np.random.randint(0, self.height)
            if self.grid[y, x] == 0:  # Empty cell
                self.grid[y, x] = 1  # Food

    def _spawn_obstacles(self, density: float):
        """Place obstacles in clear patterns (not random)"""
        obstacle_count = int(self.width * self.height * density)

        # Create structured patterns instead of random placement
        # This makes obstacles visible and predictable

        # Pattern 1: Vertical walls (30% of obstacles)
        wall_obstacles = int(obstacle_count * 0.3)
        for _ in range(wall_obstacles // 8):  # Create walls of ~8 cells
            x = np.random.randint(10, self.width - 10)
            y_start = np.random.randint(10, self.height - 20)
            for dy in range(8):
                y = y_start + dy
                if 0 <= y < self.height and self.grid[y, x] == 0:
                    self.grid[y, x] = 2

        # Pattern 2: Horizontal walls (30% of obstacles)
        for _ in range(wall_obstacles // 8):
            y = np.random.randint(10, self.height - 10)
            x_start = np.random.randint(10, self.width - 20)
            for dx in range(8):
                x = x_start + dx
                if 0 <= x < self.width and self.grid[y, x] == 0:
                    self.grid[y, x] = 2

        # Pattern 3: Small clusters (20% of obstacles)
        cluster_obstacles = int(obstacle_count * 0.2)
        for _ in range(cluster_obstacles // 4):
            cx = np.random.randint(5, self.width - 5)
            cy = np.random.randint(5, self.height - 5)
            # 2x2 cluster
            for dx in [0, 1]:
                for dy in [0, 1]:
                    x, y = cx + dx, cy + dy
                    if 0 <= x < self.width and 0 <= y < self.height and self.grid[y, x] == 0:
                        self.grid[y, x] = 2

        # Pattern 4: Border obstacles (20% of obstacles)
        border_obstacles = int(obstacle_count * 0.2)
        for _ in range(border_obstacles):
            # Random position on one of the borders
            side = np.random.randint(4)
            if side == 0:  # Top
                x, y = np.random.randint(0, self.width), 0
            elif side == 1:  # Bottom
                x, y = np.random.randint(0, self.width), self.height - 1
            elif side == 2:  # Left
                x, y = 0, np.random.randint(0, self.height)
            else:  # Right
                x, y = self.width - 1, np.random.randint(0, self.height)

            if self.grid[y, x] == 0:
                self.grid[y, x] = 2

    def get_local_view(self, x: int, y: int, radius: int = 5) -> Dict:
        """Get creature's local perception"""
        # Visual perception - grid around creature
        x1, x2 = max(0, x - radius), min(self.width, x + radius + 1)
        y1, y2 = max(0, y - radius), min(self.height, y + radius + 1)

        visual = self.grid[y1:y2, x1:x2].copy()

        # Audio perception - sounds in area
        sound = self.sound_grid[y1:y2, x1:x2].copy()

        return {
            "visual": visual,
            "sound": sound,
            "food_count": np.sum(visual == 1),
            "obstacle_count": np.sum(visual == 2),
            "creature_count": np.sum(visual == 3),
            "center_offset": (radius - (x - x1), radius - (y - y1)),
        }

    def update_sound(self, x: int, y: int, frequency: float, amplitude: float):
        """Creature makes sound at location"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.sound_grid[y, x] = [frequency, amplitude]

            # Simple sound propagation to neighbors
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < self.width and 0 <= ny < self.height:
                        if dx != 0 or dy != 0:  # Not center
                            current_amp = self.sound_grid[ny, nx, 1]
                            propagated_amp = amplitude * 0.5  # 50% strength
                            if propagated_amp > current_amp:
                                self.sound_grid[ny, nx] = [frequency, propagated_amp]

    def step(self):
        """Update world physics each timestep"""
        # Sound decay using configured rate
        self.sound_grid *= self.sound_decay_rate

        # Occasionally spawn new food using configured probability and amount
        if np.random.random() < self.food_respawn_probability:
            self._spawn_food(self.food_respawn_amount)
