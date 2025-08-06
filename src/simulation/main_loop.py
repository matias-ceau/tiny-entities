import asyncio
import numpy as np
from typing import List, Dict
from ..world.non_deterministic import NonDeterministicWorldModel
from ..creatures.brain import EnhancedBrain
from ..creatures.action_selection import MoodInfluencedActionSelector
from ..config.api_config import APIConfig


class EmergentLifeSimulation:
    """Main simulation loop for artificial life"""

    def __init__(
        self, num_creatures: int = 5, max_steps: int = 10000, analyze_every: int = 500
    ):
        self.num_creatures = num_creatures
        self.max_steps = max_steps
        self.analyze_every = analyze_every

        # Initialize world
        self.world_model = NonDeterministicWorldModel()

        # Initialize creatures
        self.creatures = self._create_creatures(num_creatures)

        # Action selector
        self.action_selector = MoodInfluencedActionSelector()

        # Data collection
        self.step_count = 0
        self.sound_history = []
        self.emergence_reports = []

        # Cost tracking
        self.daily_cost_eur = 0.0
        self.api_config = APIConfig()

    def _create_creatures(self, num: int) -> List[Dict]:
        """Create initial creatures"""
        creatures = []

        for i in range(num):
            # Random starting position
            x = np.random.randint(10, self.world_model.world.width - 10)
            y = np.random.randint(10, self.world_model.world.height - 10)

            creature = {
                "id": f"creature_{i}",
                "brain": EnhancedBrain(f"creature_{i}"),
                "position": (x, y),
                "alive": True,
                "birth_step": 0,
            }

            creatures.append(creature)

        return creatures

    async def simulation_step(self):
        """Execute one simulation timestep"""

        # Process each creature
        for creature in self.creatures:
            if not creature["alive"]:
                continue

            # Get perception
            world_view = self.world_model.world.get_local_view(
                creature["position"][0], creature["position"][1]
            )
            perception = self._process_perception(world_view)

            # Select action
            action = self.action_selector.select_action(creature["brain"], perception)

            # Execute action in world
            outcome = self.world_model.propose_action(
                creature["id"], action, creature["position"]
            )

            # Update creature position
            creature["position"] = outcome["new_position"]

            # Process cognitive cycle
            brain_update = creature["brain"].process_timestep(
                perception, action, outcome
            )

            # Record sound events
            if action.startswith("make_sound"):
                self.sound_history.append(
                    {
                        "step": self.step_count,
                        "creature_id": creature["id"],
                        "position": creature["position"],
                        "frequency": 0.3 if "low" in action else 0.7,
                        "mood_valence": creature["brain"].mood_system.valence,
                        "mood_arousal": creature["brain"].mood_system.arousal,
                    }
                )

            # Check if creature dies
            if creature["brain"].health <= 0:
                creature["alive"] = False
                print(f"{creature['id']} died at step {self.step_count}")

        # Update world
        self.world_model.world.step()

        self.step_count += 1

    def _process_perception(self, world_view: Dict) -> Dict:
        """Process raw world view into creature perception"""
        return {
            "visual": world_view["visual"],
            "sound": world_view["sound"],
            "food_count": world_view["food_count"],
            "obstacle_count": world_view["obstacle_count"],
            "creature_count": world_view["creature_count"],
        }

    async def analyze_emergence(self):
        """Analyze collective behaviors for emergence"""
        print(f"\n=== Emergence Analysis at step {self.step_count} ===")

        # Simple analysis without API for now
        if len(self.sound_history) > 10:
            recent_sounds = self.sound_history[-50:]
            unique_creatures = set(s["creature_id"] for s in recent_sounds)

            print(
                f"Sound activity: {len(recent_sounds)} sounds from "
                f"{len(unique_creatures)} creatures"
            )

            # Check for patterns
            if len(recent_sounds) > 20:
                # Simple rhythm detection
                time_diffs = []
                for i in range(1, len(recent_sounds)):
                    time_diffs.append(
                        recent_sounds[i]["step"] - recent_sounds[i - 1]["step"]
                    )

                if time_diffs:
                    avg_interval = np.mean(time_diffs)
                    std_interval = np.std(time_diffs)

                    if std_interval < avg_interval * 0.5:
                        print(
                            f"Possible rhythmic pattern detected! "
                            f"Avg interval: {avg_interval:.1f} ± {std_interval:.1f}"
                        )

        # Mood summary
        alive_creatures = [c for c in self.creatures if c["alive"]]
        if alive_creatures:
            avg_valence = np.mean(
                [c["brain"].mood_system.valence for c in alive_creatures]
            )
            avg_arousal = np.mean(
                [c["brain"].mood_system.arousal for c in alive_creatures]
            )

            print(f"Average mood: valence={avg_valence:.2f}, arousal={avg_arousal:.2f}")

        print("=" * 50 + "\n")

    async def run_simulation(self):
        """Run the full simulation"""
        print(f"Starting simulation with {self.num_creatures} creatures")
        print(
            f"World size: {self.world_model.world.width}x"
            f"{self.world_model.world.height}"
        )

        while self.step_count < self.max_steps:
            # Run simulation step
            await self.simulation_step()

            # Periodic analysis
            if self.step_count % self.analyze_every == 0:
                await self.analyze_emergence()

            # Status update
            if self.step_count % 100 == 0:
                alive_count = sum(1 for c in self.creatures if c["alive"])
                print(f"Step {self.step_count}: {alive_count} creatures alive")

            # Check if all creatures died
            if not any(c["alive"] for c in self.creatures):
                print("All creatures have died!")
                break

            # Small delay to prevent blocking
            if self.step_count % 10 == 0:
                await asyncio.sleep(0.001)

        print(f"\nSimulation complete!")
        print(f"Total steps: {self.step_count}")
        print(f"Total cost: €{self.daily_cost_eur:.3f}")


# Entry point
if __name__ == "__main__":
    sim = EmergentLifeSimulation(num_creatures=8, max_steps=5000)
    asyncio.run(sim.run_simulation())
