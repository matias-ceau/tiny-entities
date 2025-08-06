import numpy as np
from typing import Dict, List, Tuple, Optional


class SimpleWorld:
    """Conway's Game of Life inspired 2D world with resources"""

    def __init__(self, width: int = 100, height: int = 100):
        self.width = width
        self.height = height

        # World state: 0=empty, 1=food, 2=obstacle, 3=creature
        self.grid = np.zeros((height, width), dtype=int)

        # Sound layer - simple frequency/amplitude at each location
        self.sound_grid = np.zeros((height, width, 2))  # [frequency, amplitude]

        # Spawn some food randomly
        self._spawn_food(density=0.1)
        self._spawn_obstacles(density=0.05)

    def _spawn_food(self, density: float):
        """Randomly place food in world"""
        food_count = int(self.width * self.height * density)
        for _ in range(food_count):
            x = np.random.randint(0, self.width)
            y = np.random.randint(0, self.height)
            if self.grid[y, x] == 0:  # Empty cell
                self.grid[y, x] = 1  # Food

    def _spawn_obstacles(self, density: float):
        """Place obstacles that block movement"""
        obstacle_count = int(self.width * self.height * density)
        for _ in range(obstacle_count):
            x = np.random.randint(0, self.width)
            y = np.random.randint(0, self.height)
            if self.grid[y, x] == 0:  # Empty cell
                self.grid[y, x] = 2  # Obstacle

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
        # Sound decay
        self.sound_grid *= 0.9

        # Occasionally spawn new food
        if np.random.random() < 0.01:
            self._spawn_food(0.005)
