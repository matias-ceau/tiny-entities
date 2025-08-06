import numpy as np
from typing import Dict, List


class EmergentMoodSystem:
    """Mood emerges from reward prediction errors and accumulated experience"""

    def __init__(self):
        # Core state
        self.valence = 0.0  # -1 to 1, emerges from reward history
        self.arousal = 0.5  # 0 to 1, intensity/activation level

        # Reward prediction system
        self.expected_reward = 0.0
        self.reward_history = []  # Recent rewards
        self.reward_baseline = 0.0  # Long-term average

        # Association memory - what situations led to what outcomes
        self.situation_outcomes = {}  # Hash of situation -> list of outcomes

        # Learning rates
        self.fast_learning = 0.1  # For arousal (immediate response)
        self.slow_learning = 0.01  # For valence (stable mood)

    def process_experience(self, situation: Dict, actual_reward: float):
        """Update mood based on prediction error"""

        # Calculate prediction error (surprise)
        prediction_error = actual_reward - self.expected_reward

        # Update arousal based on absolute prediction error
        # Big surprises (good or bad) increase arousal
        arousal_change = abs(prediction_error) * self.fast_learning
        self.arousal = min(1.0, self.arousal + arousal_change)

        # Update valence based on signed prediction error
        # Better than expected → positive mood
        # Worse than expected → negative mood
        valence_change = prediction_error * self.slow_learning
        self.valence = np.clip(self.valence + valence_change, -1.0, 1.0)

        # Update reward prediction for next time
        situation_key = self._hash_situation(situation)
        if situation_key not in self.situation_outcomes:
            self.situation_outcomes[situation_key] = []

        self.situation_outcomes[situation_key].append(actual_reward)

        # Update expected reward based on similar past situations
        self.expected_reward = self._predict_reward(situation)

        # Arousal naturally decays over time
        self.arousal *= 0.99

        return {
            "valence": self.valence,
            "arousal": self.arousal,
            "prediction_error": prediction_error,
        }

    def _hash_situation(self, situation: Dict) -> str:
        """Create a simple hash of the situation for memory"""
        # Simple categorical representation
        key_parts = []

        # Visual features
        if "food_nearby" in situation:
            key_parts.append(f"food_{situation['food_nearby']}")
        if "creatures_nearby" in situation:
            key_parts.append(f"creatures_{situation['creatures_nearby']}")
        if "sound_level" in situation:
            sound_level = "high" if situation["sound_level"] > 0.5 else "low"
            key_parts.append(f"sound_{sound_level}")

        return "_".join(key_parts)

    def _predict_reward(self, situation: Dict) -> float:
        """Predict reward based on past experiences"""
        situation_key = self._hash_situation(situation)

        if situation_key in self.situation_outcomes:
            recent_outcomes = self.situation_outcomes[situation_key][-10:]
            return np.mean(recent_outcomes)
        else:
            return self.reward_baseline
