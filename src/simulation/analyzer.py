"""Emergence analysis for detecting patterns in simulation data."""

import logging
from typing import List, Dict, Any, Optional

import numpy as np

from ..config.llm_client import LLMClient
from ..emergence.music_analyzer import MusicEmergenceAnalyzer

logger = logging.getLogger(__name__)


class EmergenceAnalyzer:
    """
    Analyzes patterns in simulation data.

    Responsibilities:
    - Detect rhythmic patterns in sound
    - Analyze collective music emergence
    - Track mood dynamics
    - Generate LLM summaries if available
    """

    def __init__(
        self,
        music_analyzer: Optional[MusicEmergenceAnalyzer] = None,
        llm_client: Optional[LLMClient] = None
    ):
        """
        Initialize emergence analyzer.

        Args:
            music_analyzer: Music emergence analyzer instance
            llm_client: Optional LLM client for summaries
        """
        self.music_analyzer = music_analyzer or MusicEmergenceAnalyzer()
        self.llm_client = llm_client

        logger.debug("EmergenceAnalyzer initialized")

    async def analyze(
        self,
        step: int,
        sound_history: List[Dict[str, Any]],
        creatures: List[Dict[str, Any]],
        reflections: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Perform comprehensive emergence analysis.

        Args:
            step: Current simulation step
            sound_history: Recent sound events
            creatures: List of all creatures
            reflections: Recent reflections

        Returns:
            Analysis results dictionary
        """
        analysis = {"step": step}

        # Sound pattern analysis
        if sound_history:
            analysis["sound_patterns"] = self._analyze_sound_patterns(sound_history)
            analysis["music_emergence"] = await self._analyze_music(sound_history)

        # Mood analysis
        alive_creatures = [c for c in creatures if c["alive"]]
        if alive_creatures:
            analysis["mood_dynamics"] = self._analyze_mood(alive_creatures)

        # Reflection analysis
        if reflections:
            analysis["recent_reflections"] = [
                {
                    "step": r["step"],
                    "creature_id": r["creature_id"],
                    "text": r["text"]
                }
                for r in reflections
            ]

        # LLM summary
        if self.llm_client and (sound_history or reflections):
            analysis["llm_summary"] = await self._generate_llm_summary(
                sound_history, alive_creatures, reflections
            )

        return analysis

    def _analyze_sound_patterns(
        self, sound_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Detect patterns in sound events.

        Args:
            sound_history: List of sound events

        Returns:
            Pattern analysis results
        """
        unique_creatures = set(s["creature_id"] for s in sound_history)

        patterns = {
            "total_sounds": len(sound_history),
            "unique_creatures": len(unique_creatures),
        }

        # Rhythm detection
        if len(sound_history) > 20:
            time_diffs = []
            for i in range(1, len(sound_history)):
                time_diffs.append(
                    sound_history[i]["step"] - sound_history[i - 1]["step"]
                )

            if time_diffs:
                avg_interval = float(np.mean(time_diffs))
                std_interval = float(np.std(time_diffs))

                patterns["avg_interval"] = avg_interval
                patterns["std_interval"] = std_interval

                # Check for rhythmic pattern
                if std_interval < avg_interval * 0.5:
                    patterns["rhythmic_pattern_detected"] = True
                    logger.info(
                        f"Rhythmic pattern detected! "
                        f"Interval: {avg_interval:.1f} ± {std_interval:.1f}"
                    )
                else:
                    patterns["rhythmic_pattern_detected"] = False

        return patterns

    async def _analyze_music(
        self, sound_history: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Analyze collective music emergence.

        Args:
            sound_history: List of sound events

        Returns:
            Music analysis results or None
        """
        try:
            analysis = await self.music_analyzer.analyze_collective_music(
                sound_history
            )

            if analysis:
                logger.info(
                    f"Music score: {analysis.get('music_score', 0):.1f}, "
                    f"Coordination: {analysis.get('coordination_detected', False)}, "
                    f"Entropy: {analysis.get('entropy_trend', 'unknown')}"
                )

            return analysis

        except Exception as e:
            logger.error(f"Error in music analysis: {e}")
            return None

    def _analyze_mood(
        self, alive_creatures: List[Dict[str, Any]]
    ) -> Dict[str, float]:
        """
        Analyze collective mood dynamics.

        Args:
            alive_creatures: List of alive creatures

        Returns:
            Mood statistics
        """
        valences = [c["brain"].mood_system.valence for c in alive_creatures]
        arousals = [c["brain"].mood_system.arousal for c in alive_creatures]

        mood_stats = {
            "avg_valence": float(np.mean(valences)),
            "avg_arousal": float(np.mean(arousals)),
            "std_valence": float(np.std(valences)),
            "std_arousal": float(np.std(arousals)),
            "num_creatures": len(alive_creatures),
        }

        logger.info(
            f"Mood: valence={mood_stats['avg_valence']:.2f}, "
            f"arousal={mood_stats['avg_arousal']:.2f}"
        )

        return mood_stats

    async def _generate_llm_summary(
        self,
        sound_history: List[Dict[str, Any]],
        alive_creatures: List[Dict[str, Any]],
        reflections: List[Dict[str, Any]]
    ) -> Optional[str]:
        """
        Generate LLM summary of emergence.

        Args:
            sound_history: Sound events
            alive_creatures: Alive creatures
            reflections: Recent reflections

        Returns:
            LLM summary text or None
        """
        if not self.llm_client:
            return None

        try:
            # Prepare metrics
            sound_metrics = {
                "events": len(sound_history),
                "unique_creatures": len({s["creature_id"] for s in sound_history}),
            }

            if sound_history:
                sound_metrics["avg_frequency_hint"] = float(
                    np.mean([s["frequency"] for s in sound_history])
                )

            mood_metrics = {
                "average_valence": float(
                    np.mean([c["brain"].mood_system.valence for c in alive_creatures])
                ),
                "average_arousal": float(
                    np.mean([c["brain"].mood_system.arousal for c in alive_creatures])
                ),
            }

            # Get LLM summary
            response = self.llm_client.summarize_emergence(
                sound_metrics,
                mood_metrics,
                [r["text"] for r in reflections],
            )

            if response and response.text:
                logger.info(f"LLM summary generated: {len(response.text)} chars")
                return response.text.strip()

            return None

        except Exception as e:
            logger.error(f"Error generating LLM summary: {e}")
            return None
