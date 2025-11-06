"""Data collection and event recording for simulation."""

import logging
from typing import List, Dict, Any

from ..world.sound_engine import SoundSynthesizer

logger = logging.getLogger(__name__)


class DataCollector:
    """
    Records simulation events and metrics.

    Responsibilities:
    - Record sound events with synthesized waveforms
    - Record creature reflections
    - Track LLM costs
    - Provide summary statistics
    """

    def __init__(self):
        """Initialize data collector."""
        self.sound_history: List[Dict[str, Any]] = []
        self.reflection_log: List[Dict[str, Any]] = []
        self.action_log: List[Dict[str, Any]] = []
        self.death_events: List[Dict[str, Any]] = []
        self.performance_metrics: List[Dict[str, float]] = []

        self.total_llm_cost_eur = 0.0
        self.sound_synth = SoundSynthesizer()

        logger.debug("DataCollector initialized")

    def process_events(self, events: List[Dict[str, Any]]) -> None:
        """
        Process events from a simulation step.

        Args:
            events: List of event dictionaries from SimulationEngine
        """
        for event in events:
            event_type = event.get("type")

            if event_type == "action":
                self._record_action(event)
            elif event_type == "death":
                self._record_death(event)
            elif event_type == "performance":
                self._record_performance(event)

    def _record_action(self, event: Dict[str, Any]) -> None:
        """Record an action event."""
        # Record basic action
        self.action_log.append({
            "step": event["step"],
            "creature_id": event["creature_id"],
            "action": event["action"],
            "position": event["new_position"],
        })

        # Check for sound events
        if event["action"].startswith("make_sound"):
            self._record_sound(event)

        # Check for reflections
        brain_update = event.get("brain_update", {})
        if "reflection" in brain_update:
            self._record_reflection(event, brain_update["reflection"])

        # Track LLM costs
        if "llm_cost_eur" in brain_update:
            self.total_llm_cost_eur += brain_update["llm_cost_eur"]

    def _record_sound(self, event: Dict[str, Any]) -> None:
        """Record a sound event with synthesized waveform."""
        action = event["action"]
        mood = event["mood"]

        # Synthesize sound
        frequency = 0.3 if "low" in action else 0.7
        synth = self.sound_synth.synthesize(
            frequency,
            mood["valence"],
            mood["arousal"],
        )

        # Record sound event
        self.sound_history.append({
            "step": event["step"],
            "creature_id": event["creature_id"],
            "position": event["new_position"],
            "frequency": frequency,
            "mood_valence": mood["valence"],
            "mood_arousal": mood["arousal"],
            "waveform": synth.waveform,
            "sample_rate": synth.sample_rate,
            "metadata": synth.metadata,
        })

        logger.debug(
            f"Sound recorded: {event['creature_id']} at step {event['step']}"
        )

    def _record_reflection(self, event: Dict[str, Any], reflection: str) -> None:
        """Record a creature reflection."""
        self.reflection_log.append({
            "step": event["step"],
            "creature_id": event["creature_id"],
            "text": reflection,
        })

        logger.debug(
            f"Reflection recorded: {event['creature_id']} at step {event['step']}"
        )

    def _record_death(self, event: Dict[str, Any]) -> None:
        """Record a death event."""
        self.death_events.append({
            "step": event["step"],
            "creature_id": event["creature_id"],
            "position": event["position"],
        })

        logger.info(
            f"Death recorded: {event['creature_id']} at step {event['step']}"
        )

    def _record_performance(self, event: Dict[str, Any]) -> None:
        """Record performance metrics."""
        self.performance_metrics.append({
            "step": event["step"],
            "step_duration": event["step_duration"],
        })

    def get_summary(self) -> Dict[str, Any]:
        """
        Get summary statistics.

        Returns:
            Dictionary of summary statistics
        """
        return {
            "total_sounds": len(self.sound_history),
            "total_reflections": len(self.reflection_log),
            "total_actions": len(self.action_log),
            "total_deaths": len(self.death_events),
            "total_llm_cost_eur": self.total_llm_cost_eur,
        }

    def get_recent_sounds(self, n: int = 50) -> List[Dict[str, Any]]:
        """Get recent sound events."""
        return self.sound_history[-n:] if self.sound_history else []

    def get_recent_reflections(self, n: int = 3) -> List[Dict[str, Any]]:
        """Get recent reflections."""
        return self.reflection_log[-n:] if self.reflection_log else []

    def clear(self) -> None:
        """Clear all collected data."""
        self.sound_history.clear()
        self.reflection_log.clear()
        self.action_log.clear()
        self.death_events.clear()
        self.performance_metrics.clear()
        self.total_llm_cost_eur = 0.0
        logger.debug("DataCollector cleared")
