"""High-level simulation orchestrator - coordinates all components."""

import logging
from typing import List, Dict, Any, Optional, TYPE_CHECKING

from .engine import SimulationEngine
from .data_collector import DataCollector
from .analyzer import EmergenceAnalyzer
from ..creatures.factory import create_creatures
from ..creatures.action_selection import MoodInfluencedActionSelector
from ..world.non_deterministic import NonDeterministicWorldModel
from ..world.physics import SimpleWorld

if TYPE_CHECKING:
    from ..config.config_schema import SimulationConfig
    from ..config.llm_client import LLMClient

logger = logging.getLogger(__name__)


class SimulationOrchestrator:
    """
    High-level coordinator for the entire simulation.

    Responsibilities:
    - Initialize all simulation components
    - Coordinate simulation loop
    - Trigger periodic analysis
    - Provide public API for running simulations
    """

    def __init__(
        self,
        config: Optional['SimulationConfig'] = None,
        llm_client: Optional['LLMClient'] = None
    ):
        """
        Initialize simulation orchestrator.

        Args:
            config: Complete simulation configuration
            llm_client: Optional LLM client for advanced features
        """
        self.config = config
        self.llm_client = llm_client

        # Core components (initialized in setup())
        self.world_model: Optional[NonDeterministicWorldModel] = None
        self.engine: Optional[SimulationEngine] = None
        self.collector: Optional[DataCollector] = None
        self.analyzer: Optional[EmergenceAnalyzer] = None
        self.action_selector: Optional[MoodInfluencedActionSelector] = None

        # Configuration parameters
        if config:
            self.num_creatures = config.creatures.initial_count
            self.max_steps = config.creatures.max_steps
            self.analyze_every = config.analysis.analyze_every
        else:
            self.num_creatures = 5
            self.max_steps = 10000
            self.analyze_every = 500

        logger.debug("SimulationOrchestrator initialized")

    def setup(self) -> None:
        """
        Set up all simulation components.

        Creates world, creatures, and initializes all subsystems.
        """
        logger.info("Setting up simulation components...")

        # Create world model
        if self.config:
            self.world_model = NonDeterministicWorldModel(
                world_config=self.config.world,
                action_config=self.config.actions
            )
        else:
            world = SimpleWorld()
            self.world_model = NonDeterministicWorldModel(world=world)

        # Create action selector
        self.action_selector = MoodInfluencedActionSelector()

        # Create simulation engine
        self.engine = SimulationEngine(
            world_model=self.world_model,
            action_selector=self.action_selector
        )

        # Create creatures
        if self.config:
            creatures = create_creatures(
                self.num_creatures,
                self.world_model.world,
                creature_config=self.config.creatures,
                mood_config=self.config.mood,
                llm_client=self.llm_client
            )
        else:
            creatures = create_creatures(
                self.num_creatures,
                self.world_model.world,
                llm_client=self.llm_client
            )

        self.engine.add_creatures(creatures)

        # Create data collector
        self.collector = DataCollector()

        # Create emergence analyzer
        from ..emergence.music_analyzer import MusicEmergenceAnalyzer
        music_analyzer = MusicEmergenceAnalyzer()
        self.analyzer = EmergenceAnalyzer(
            music_analyzer=music_analyzer,
            llm_client=self.llm_client
        )

        logger.info(
            f"Simulation setup complete: "
            f"{self.num_creatures} creatures, "
            f"{self.world_model.world.width}x{self.world_model.world.height} world"
        )

    async def run(
        self,
        callback: Optional[Any] = None,
        analyze_callback: Optional[Any] = None
    ) -> Dict[str, Any]:
        """
        Run the complete simulation.

        Args:
            callback: Optional callback function called each step
            analyze_callback: Optional callback for analysis results

        Returns:
            Simulation summary dictionary
        """
        if not self.engine:
            raise RuntimeError("Simulation not set up. Call setup() first.")

        logger.info(f"Starting simulation for {self.max_steps} steps...")

        for step in range(self.max_steps):
            # Execute one timestep
            events = await self.engine.step()

            # Record events
            self.collector.process_events(events)

            # User callback
            if callback:
                should_continue = callback(step, self.engine.creatures)
                if not should_continue:
                    logger.info(f"Simulation stopped by callback at step {step}")
                    break

            # Periodic analysis
            if step > 0 and step % self.analyze_every == 0:
                await self._perform_analysis(step, analyze_callback)

            # Check termination
            if self.engine.all_dead():
                logger.warning(f"All creatures died at step {step}")
                break

        # Final analysis
        await self._perform_analysis(self.engine.step_count, analyze_callback)

        # Generate summary
        summary = self._generate_summary()

        logger.info(
            f"Simulation complete: {self.engine.step_count} steps, "
            f"{self.engine.get_alive_count()} creatures alive"
        )

        return summary

    async def _perform_analysis(
        self,
        step: int,
        callback: Optional[Any] = None
    ) -> None:
        """
        Perform emergence analysis.

        Args:
            step: Current simulation step
            callback: Optional callback for analysis results
        """
        try:
            # Get recent data
            sound_history = self.collector.get_recent_sounds(n=50)
            reflections = self.collector.get_recent_reflections(n=3)

            # Analyze
            analysis = await self.analyzer.analyze(
                step=step,
                sound_history=sound_history,
                creatures=self.engine.creatures,
                reflections=reflections
            )

            # User callback
            if callback:
                callback(step, analysis)

            logger.debug(f"Analysis complete for step {step}")

        except Exception as e:
            logger.error(f"Error during analysis at step {step}: {e}", exc_info=True)

    def _generate_summary(self) -> Dict[str, Any]:
        """
        Generate final simulation summary.

        Returns:
            Summary dictionary with statistics and metrics
        """
        data_summary = self.collector.get_summary()

        alive_count = self.engine.get_alive_count()
        total_creatures = len(self.engine.creatures)

        summary = {
            "total_steps": self.engine.step_count,
            "creatures_alive": alive_count,
            "creatures_total": total_creatures,
            "survival_rate": alive_count / total_creatures if total_creatures > 0 else 0.0,
            **data_summary
        }

        return summary

    def get_creatures(self) -> List[Dict[str, Any]]:
        """Get all creatures."""
        if not self.engine:
            return []
        return self.engine.creatures

    def get_world_state(self) -> Optional[Dict[str, Any]]:
        """Get current world state."""
        if not self.world_model:
            return None

        world = self.world_model.world
        return {
            "width": world.width,
            "height": world.height,
            "food_grid": world.food_grid,
            "obstacle_grid": world.obstacle_grid,
            "sound_field": world.sound_field,
        }

    def reset(self) -> None:
        """Reset simulation state."""
        if self.collector:
            self.collector.clear()

        if self.engine:
            self.engine.step_count = 0

        logger.debug("Simulation reset")
