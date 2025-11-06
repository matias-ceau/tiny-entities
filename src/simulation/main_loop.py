import asyncio
import logging
import time
import numpy as np
from typing import List, Dict, Optional, TYPE_CHECKING

from ..world.non_deterministic import NonDeterministicWorldModel
from ..world.sound_engine import SoundSynthesizer
from ..creatures.brain import EnhancedBrain
from ..creatures.action_selection import MoodInfluencedActionSelector
from ..config.api_config import APIConfig
from ..config.llm_client import get_llm_client
from ..config.logging_config import PerformanceLogger
from ..emergence.music_analyzer import MusicEmergenceAnalyzer

if TYPE_CHECKING:
    from ..config.config_schema import SimulationConfig

logger = logging.getLogger(__name__)


class EmergentLifeSimulation:
    """Main simulation loop for artificial life"""

    def __init__(
        self,
        num_creatures: int = 5,
        max_steps: int = 10000,
        analyze_every: int = 500,
        config: Optional['SimulationConfig'] = None
    ):
        """
        Initialize simulation with optional configuration.

        Args:
            num_creatures: Number of creatures (used if config not provided)
            max_steps: Maximum simulation steps (used if config not provided)
            analyze_every: Analysis frequency (used if config not provided)
            config: Complete SimulationConfig instance
        """
        # Use config if provided, otherwise use parameters
        if config:
            self.num_creatures = config.creatures.initial_count
            self.max_steps = config.max_steps
            self.analyze_every = config.analysis.analyze_every
            self.config = config

            # Initialize world with config
            self.world_model = NonDeterministicWorldModel(
                world_config=config.world,
                action_config=config.actions
            )
        else:
            # Backward compatibility
            self.num_creatures = num_creatures
            self.max_steps = max_steps
            self.analyze_every = analyze_every
            self.config = None

            # Initialize world without config
            self.world_model = NonDeterministicWorldModel()

        logger.info(f"Initializing simulation with {self.num_creatures} creatures")
        logger.info(f"World size: {self.world_model.world.width}x{self.world_model.world.height}")

        # Initialize creatures
        self.creatures = self._create_creatures(self.num_creatures)

        # Action selector
        self.action_selector = MoodInfluencedActionSelector()

        # Optional LLM client for narrative summaries
        self.llm_client = get_llm_client()
        self.music_analyzer = MusicEmergenceAnalyzer()
        self.sound_synth = SoundSynthesizer()

        # Data collection
        self.step_count = 0
        self.sound_history = []
        self.emergence_reports = []
        self.reflection_log = []

        # Cost tracking
        self.daily_cost_eur = 0.0
        self.api_config = APIConfig()

        # Performance tracking
        self.perf_logger = PerformanceLogger(logger)

    def _create_creatures(self, num: int) -> List[Dict]:
        """Create initial creatures"""
        creatures = []

        # Get configs if available
        creature_config = self.config.creatures if self.config else None
        mood_config = self.config.mood if self.config else None

        for i in range(num):
            # Random starting position
            x = np.random.randint(10, self.world_model.world.width - 10)
            y = np.random.randint(10, self.world_model.world.height - 10)

            creature = {
                "id": f"creature_{i}",
                "brain": EnhancedBrain(
                    f"creature_{i}",
                    creature_config=creature_config,
                    mood_config=mood_config
                ),
                "position": (x, y),
                "alive": True,
                "birth_step": 0,
            }

            creatures.append(creature)

        logger.debug(f"Created {num} creatures at random positions")
        return creatures

    async def simulation_step(self):
        """Execute one simulation timestep"""
        step_start = time.time()

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
                synth = self.sound_synth.synthesize(
                    0.3 if "low" in action else 0.7,
                    creature["brain"].mood_system.valence,
                    creature["brain"].mood_system.arousal,
                )
                self.sound_history.append(
                    {
                        "step": self.step_count,
                        "creature_id": creature["id"],
                        "position": creature["position"],
                        "frequency": 0.3 if "low" in action else 0.7,
                        "mood_valence": creature["brain"].mood_system.valence,
                        "mood_arousal": creature["brain"].mood_system.arousal,
                        "waveform": synth.waveform,
                        "sample_rate": synth.sample_rate,
                        "metadata": synth.metadata,
                    }
                )

            if "reflection" in brain_update:
                self.reflection_log.append(
                    {
                        "step": self.step_count,
                        "creature_id": creature["id"],
                        "text": brain_update["reflection"],
                    }
                )

            if "llm_cost_eur" in brain_update:
                self.daily_cost_eur += brain_update["llm_cost_eur"]

            # Check if creature dies
            if creature["brain"].health <= 0:
                creature["alive"] = False
                logger.info(f"{creature['id']} died at step {self.step_count}")

        # Update world
        self.world_model.world.step()

        self.step_count += 1

        # Record performance
        step_duration = time.time() - step_start
        self.perf_logger.record_metric("step_duration", step_duration)

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
        logger.info(f"=== Emergence Analysis at step {self.step_count} ===")

        # Simple analysis with optional LLM enhancements
        if len(self.sound_history) > 10:
            recent_sounds = self.sound_history[-50:]
            unique_creatures = set(s["creature_id"] for s in recent_sounds)

            logger.info(
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
                        logger.info(
                            f"Possible rhythmic pattern detected! "
                            f"Avg interval: {avg_interval:.1f} ± {std_interval:.1f}"
                        )

            analysis = await self.music_analyzer.analyze_collective_music(recent_sounds)
            if analysis:
                logger.info(
                    f"Music score: {analysis['music_score']:.1f}, "
                    f"Coordination: {analysis['coordination_detected']}, "
                    f"Entropy trend: {analysis['entropy_trend']}"
                )
                if analysis.get("full_analysis"):
                    logger.info(f"Full analysis: {analysis.get('full_analysis')}")

        # Mood summary
        alive_creatures = [c for c in self.creatures if c["alive"]]
        if alive_creatures:
            avg_valence = np.mean(
                [c["brain"].mood_system.valence for c in alive_creatures]
            )
            avg_arousal = np.mean(
                [c["brain"].mood_system.arousal for c in alive_creatures]
            )

            logger.info(f"Average mood: valence={avg_valence:.2f}, arousal={avg_arousal:.2f}")

        recent_reflections = self.reflection_log[-3:]
        if recent_reflections:
            logger.info("Recent reflections:")
            for reflection in recent_reflections:
                logger.info(
                    f"  [{reflection['step']}] {reflection['creature_id']}: "
                    f"{reflection['text']}"
                )

        if self.llm_client and (len(self.sound_history) > 10 or recent_reflections):
            sound_metrics = {
                "events": len(self.sound_history),
                "unique_creatures": len({s["creature_id"] for s in self.sound_history}),
            }
            if self.sound_history:
                sound_metrics.update(
                    {
                        "avg_frequency_hint": float(
                            np.mean([s["frequency"] for s in self.sound_history])
                        ),
                    }
                )

            mood_metrics = {
                "average_valence": float(
                    np.mean([c["brain"].mood_system.valence for c in self.creatures])
                ),
                "average_arousal": float(
                    np.mean([c["brain"].mood_system.arousal for c in self.creatures])
                ),
            }

            summary_response = self.llm_client.summarize_emergence(
                sound_metrics,
                mood_metrics,
                [r["text"] for r in recent_reflections],
            )

            if summary_response and summary_response.text:
                logger.info("LLM summary:")
                logger.info(summary_response.text.strip())
                if summary_response.total_cost_eur:
                    self.daily_cost_eur += summary_response.total_cost_eur

        logger.info("=" * 50)

    async def run_simulation(self):
        """Run the full simulation"""
        logger.info(f"Starting simulation with {self.num_creatures} creatures")
        logger.info(
            f"World size: {self.world_model.world.width}x"
            f"{self.world_model.world.height}"
        )

        simulation_start = time.time()

        while self.step_count < self.max_steps:
            # Run simulation step
            await self.simulation_step()

            # Periodic analysis
            if self.step_count % self.analyze_every == 0:
                analysis_start = time.time()
                await self.analyze_emergence()
                self.perf_logger.record_metric("analysis_duration", time.time() - analysis_start)

            # Status update
            if self.step_count % 100 == 0:
                alive_count = sum(1 for c in self.creatures if c["alive"])
                logger.info(f"Step {self.step_count}: {alive_count} creatures alive")

            # Check if all creatures died
            if not any(c["alive"] for c in self.creatures):
                logger.warning("All creatures have died!")
                break

            # Small delay to prevent blocking
            if self.step_count % 10 == 0:
                await asyncio.sleep(0.001)

        simulation_duration = time.time() - simulation_start

        logger.info("=" * 50)
        logger.info("Simulation complete!")
        logger.info(f"Total steps: {self.step_count}")
        logger.info(f"Total time: {simulation_duration:.2f}s")
        logger.info(f"Average step time: {simulation_duration/self.step_count:.4f}s")

        if self.daily_cost_eur > 0:
            logger.info(f"Total LLM cost: €{self.daily_cost_eur:.4f}")

        # Log performance metrics
        logger.info("Performance Metrics:")
        self.perf_logger.log_metrics()


# Entry point
if __name__ == "__main__":
    from ..config.logging_config import setup_logging

    # Setup logging
    setup_logging(level='INFO')

    logger.info("Starting Tiny Entities simulation from main_loop.py")
    sim = EmergentLifeSimulation(num_creatures=8, max_steps=5000)
    asyncio.run(sim.run_simulation())
