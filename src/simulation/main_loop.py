"""Legacy main simulation loop - now uses refactored components.

This module provides backward compatibility while using the new
orchestrator-based architecture internally.
"""

import asyncio
import logging
import time
from typing import List, Dict, Optional, TYPE_CHECKING

from .orchestrator import SimulationOrchestrator
from ..config.llm_client import get_llm_client
from ..config.logging_config import PerformanceLogger

if TYPE_CHECKING:
    from ..config.config_schema import SimulationConfig

logger = logging.getLogger(__name__)


class EmergentLifeSimulation:
    """
    Main simulation loop for artificial life.

    NOTE: This class now wraps SimulationOrchestrator for backward compatibility.
    New code should use SimulationOrchestrator directly for better control.
    """

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
        self.num_creatures = num_creatures
        self.max_steps = max_steps
        self.analyze_every = analyze_every
        self.config = config

        # Get LLM client
        self.llm_client = get_llm_client()

        # Create orchestrator with config
        if config:
            # Override config with any provided parameters
            if num_creatures != 5:
                config.creatures.initial_count = num_creatures
            if max_steps != 10000:
                config.max_steps = max_steps
            if analyze_every != 500:
                config.analysis.analyze_every = analyze_every

        self.orchestrator = SimulationOrchestrator(
            config=config,
            llm_client=self.llm_client
        )

        # Setup simulation
        self.orchestrator.setup()

        # Performance tracking
        self.perf_logger = PerformanceLogger(logger)

        # Track cost for backward compatibility
        self.daily_cost_eur = 0.0

        logger.info(f"Initialized simulation with {self.orchestrator.num_creatures} creatures")
        logger.info(
            f"World size: {self.orchestrator.world_model.world.width}x"
            f"{self.orchestrator.world_model.world.height}"
        )

    @property
    def creatures(self) -> List[Dict]:
        """Get creatures list for backward compatibility."""
        return self.orchestrator.get_creatures()

    @property
    def step_count(self) -> int:
        """Get current step count."""
        return self.orchestrator.engine.step_count if self.orchestrator.engine else 0

    @property
    def world_model(self):
        """Get world model for backward compatibility."""
        return self.orchestrator.world_model

    @property
    def sound_history(self) -> List[Dict]:
        """Get sound history for backward compatibility."""
        if self.orchestrator.collector:
            return self.orchestrator.collector.sound_history
        return []

    @property
    def reflection_log(self) -> List[Dict]:
        """Get reflection log for backward compatibility."""
        if self.orchestrator.collector:
            return self.orchestrator.collector.reflection_log
        return []

    async def simulation_step(self):
        """
        Execute one simulation timestep.

        NOTE: This is now handled by SimulationEngine internally.
        This method is kept for backward compatibility only.
        """
        logger.warning(
            "simulation_step() is deprecated. "
            "Use SimulationOrchestrator.run() instead."
        )
        if self.orchestrator.engine:
            events = await self.orchestrator.engine.step()
            if self.orchestrator.collector:
                self.orchestrator.collector.process_events(events)

    async def analyze_emergence(self):
        """
        Analyze collective behaviors for emergence.

        NOTE: This is now handled by EmergenceAnalyzer internally.
        This method logs results for backward compatibility.
        """
        if not self.orchestrator.collector or not self.orchestrator.analyzer:
            return

        logger.info(f"=== Emergence Analysis at step {self.step_count} ===")

        # Get recent data
        sound_history = self.orchestrator.collector.get_recent_sounds(n=50)
        reflections = self.orchestrator.collector.get_recent_reflections(n=3)

        # Analyze
        analysis = await self.orchestrator.analyzer.analyze(
            step=self.step_count,
            sound_history=sound_history,
            creatures=self.creatures,
            reflections=reflections
        )

        # Log results (for backward compatibility)
        if "sound_patterns" in analysis:
            patterns = analysis["sound_patterns"]
            logger.info(
                f"Sound activity: {patterns.get('total_sounds', 0)} sounds from "
                f"{patterns.get('unique_creatures', 0)} creatures"
            )
            if patterns.get("rhythmic_pattern_detected"):
                logger.info(
                    f"Rhythmic pattern detected! "
                    f"Interval: {patterns.get('avg_interval', 0):.1f} ± "
                    f"{patterns.get('std_interval', 0):.1f}"
                )

        if "music_emergence" in analysis and analysis["music_emergence"]:
            music = analysis["music_emergence"]
            logger.info(
                f"Music score: {music.get('music_score', 0):.1f}, "
                f"Coordination: {music.get('coordination_detected', False)}, "
                f"Entropy trend: {music.get('entropy_trend', 'unknown')}"
            )

        if "mood_dynamics" in analysis:
            mood = analysis["mood_dynamics"]
            logger.info(
                f"Average mood: valence={mood['avg_valence']:.2f}, "
                f"arousal={mood['avg_arousal']:.2f}"
            )

        if "recent_reflections" in analysis:
            logger.info("Recent reflections:")
            for r in analysis["recent_reflections"]:
                logger.info(f"  [{r['step']}] {r['creature_id']}: {r['text']}")

        if "llm_summary" in analysis and analysis["llm_summary"]:
            logger.info("LLM summary:")
            logger.info(analysis["llm_summary"])

        logger.info("=" * 50)

    async def run_simulation(self):
        """Run the full simulation."""
        logger.info(f"Starting simulation with {self.orchestrator.num_creatures} creatures")
        logger.info(
            f"World size: {self.orchestrator.world_model.world.width}x"
            f"{self.orchestrator.world_model.world.height}"
        )

        simulation_start = time.time()

        # Status callback
        def step_callback(step: int, creatures: List[Dict]) -> bool:
            """Called each step for status updates."""
            if step % 100 == 0:
                alive_count = sum(1 for c in creatures if c["alive"])
                logger.info(f"Step {step}: {alive_count} creatures alive")
            return True  # Continue simulation

        # Analysis callback
        def analysis_callback(step: int, analysis: Dict) -> None:
            """Called after each analysis."""
            # Track costs if present
            if self.orchestrator.collector:
                self.daily_cost_eur = self.orchestrator.collector.total_llm_cost_eur

        # Run simulation through orchestrator
        summary = await self.orchestrator.run(
            callback=step_callback,
            analyze_callback=analysis_callback
        )

        simulation_duration = time.time() - simulation_start

        # Final summary
        logger.info("=" * 50)
        logger.info("Simulation complete!")
        logger.info(f"Total steps: {summary['total_steps']}")
        logger.info(f"Total time: {simulation_duration:.2f}s")
        if summary['total_steps'] > 0:
            logger.info(
                f"Average step time: {simulation_duration/summary['total_steps']:.4f}s"
            )
        logger.info(f"Creatures alive: {summary['creatures_alive']}/{summary['creatures_total']}")
        logger.info(f"Survival rate: {summary['survival_rate']:.1%}")

        if summary.get('total_llm_cost_eur', 0) > 0:
            logger.info(f"Total LLM cost: €{summary['total_llm_cost_eur']:.4f}")

        # Performance metrics
        if self.orchestrator.collector and self.orchestrator.collector.performance_metrics:
            avg_step_duration = sum(
                m['step_duration']
                for m in self.orchestrator.collector.performance_metrics
            ) / len(self.orchestrator.collector.performance_metrics)
            logger.info(f"Average step duration: {avg_step_duration:.4f}s")

        logger.info("=" * 50)


# Entry point
if __name__ == "__main__":
    from ..config.logging_config import setup_logging

    # Setup logging
    setup_logging(level='INFO')

    logger.info("Starting Tiny Entities simulation from main_loop.py")
    sim = EmergentLifeSimulation(num_creatures=8, max_steps=5000)
    asyncio.run(sim.run_simulation())
