import numpy as np
from typing import Dict
from ..config.api_config import APIConfig


class MoodInfluencedActionSelector:
    """Action selection influenced by emergent mood"""

    def __init__(self):
        self.base_actions = [
            "move_north",
            "move_south",
            "move_east",
            "move_west",
            "stay",
            "eat",
            "make_sound_low",
            "make_sound_high",
            "listen",
            "explore",
        ]
        self.api_config = APIConfig()
        self.use_llm = bool(self.api_config.get_action_model())

    def select_action(self, brain, perception: Dict) -> str:
        """Select action based on mood-biased preferences"""

        # Get mood-based biases
        action_biases = brain.get_action_bias()

        # Add situational modifiers
        if perception.get("food_count", 0) > 0 and brain.health < 70:
            # Move toward food when needed
            action_biases["eat"] = 0.8
            action_biases["move_north"] = 0.4  # Simplified - would need direction

        # If very low energy, bias toward staying
        if brain.energy < 20:
            action_biases["stay"] = 0.7

        # If LLM available and have tokens, use it occasionally
        if self.use_llm and brain.action_tokens > 5 and np.random.random() < 0.2:
            return self._llm_action_selection(brain, perception, action_biases)

        # Otherwise use probabilistic selection
        return self._probabilistic_selection(action_biases)

    def _probabilistic_selection(self, action_biases: Dict[str, float]) -> str:
        """Select action probabilistically based on biases"""
        # Convert to action probabilities
        action_probs = {}
        for action in self.base_actions:
            base_prob = 1.0 / len(self.base_actions)
            bias = action_biases.get(action, 0.0)
            action_probs[action] = max(0.01, base_prob + bias)

        # Normalize
        total = sum(action_probs.values())
        action_probs = {a: p / total for a, p in action_probs.items()}

        # Sample action
        actions = list(action_probs.keys())
        probs = list(action_probs.values())

        return np.random.choice(actions, p=probs)

    def _llm_action_selection(
        self, brain, perception: Dict, action_biases: Dict[str, float]
    ) -> str:
        """Use LLM for action selection (blocking for simplicity)"""
        # For now, fall back to probabilistic
        # In production, would make actual API call
        return self._probabilistic_selection(action_biases)
