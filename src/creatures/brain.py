import json
import logging
import numpy as np
from typing import Dict, List, Any, Optional, TYPE_CHECKING

from ..config.llm_client import get_llm_client
from .mood_system import EmergentMoodSystem

if TYPE_CHECKING:
    from ..config.config_schema import CreatureConfig, MoodConfig

logger = logging.getLogger(__name__)


class EnhancedBrain:
    """Brain with emergent mood based on reward learning"""

    def __init__(
        self,
        creature_id: str,
        creature_config: Optional['CreatureConfig'] = None,
        mood_config: Optional['MoodConfig'] = None
    ):
        """
        Initialize brain with optional configuration.

        Args:
            creature_id: Unique identifier for this creature
            creature_config: Configuration for creature parameters
            mood_config: Configuration for mood system parameters
        """
        self.creature_id = creature_id

        # Use config if provided, otherwise use defaults
        if creature_config:
            starting_health = creature_config.starting_health
            starting_energy = creature_config.starting_energy
            self.action_tokens = creature_config.initial_action_tokens
            self.max_tokens = creature_config.max_action_tokens
            self.max_memory = 20  # Not yet configurable
            self.energy_cost_per_step = creature_config.energy_cost_per_step
            self.health_decay_rate = creature_config.health_decay_when_no_energy
        else:
            # Default values for backward compatibility
            starting_health = 100.0
            starting_energy = 100.0
            self.action_tokens = 10
            self.max_tokens = 50
            self.max_memory = 20
            self.energy_cost_per_step = 1.0
            self.health_decay_rate = 0.1

        # Basic survival
        self.health = starting_health
        self.energy = starting_energy

        # Emergent mood system with config
        self.mood_system = EmergentMoodSystem(config=mood_config)

        # Memory for surprise calculation
        self.perception_memory = []

        # Learned action preferences based on outcomes
        self.action_values = {}  # action -> expected value

        # Basic vocabulary for internal monologue
        self.vocabulary = [
            "food",
            "creature",
            "sound",
            "move",
            "stay",
            "good",
            "bad",
            "near",
            "far",
            "loud",
            "quiet",
            "hungry",
            "tired",
            "happy",
            "sad",
        ]

        # Optional LLM client for reflective narration
        self.llm_client = get_llm_client()
        self.last_reflection_cost = 0.0

    def process_timestep(
        self, perception: Dict, action_taken: str, outcome: Dict
    ) -> Dict:
        """Complete cognitive cycle with emergent mood with input validation."""
        try:
            # Validate inputs
            if not isinstance(perception, dict):
                logger.error(f"Invalid perception type: {type(perception)}")
                perception = {}

            if not isinstance(action_taken, str):
                logger.warning(f"Invalid action_taken type: {type(action_taken)}")
                action_taken = str(action_taken) if action_taken else "unknown"

            if not isinstance(outcome, dict):
                logger.error(f"Invalid outcome type: {type(outcome)}")
                outcome = {}

            cost_before = self.last_reflection_cost

            # 1. Calculate surprise from perception
            surprise = self._calculate_perceptual_surprise(perception)

            # 2. Calculate total reward (surprise + survival outcomes)
            reward = self._calculate_total_reward(surprise, outcome)

            # 3. Create situation representation
            sound_field = perception.get("sound")
            try:
                sound_level = float(
                    np.mean(np.asarray(sound_field)[:, :, 1]) if sound_field is not None else 0.0
                )
            except (IndexError, ValueError, TypeError) as e:
                logger.warning(f"Error calculating sound level: {e}")
                sound_level = 0.0

            situation = {
                "food_nearby": perception.get("food_count", 0) > 0,
                "creatures_nearby": perception.get("creature_count", 0),
                "sound_level": sound_level,
            }

            # 4. Update mood based on reward prediction error
            mood_update = self.mood_system.process_experience(situation, reward)

            # 5. Update action values based on outcome
            self._update_action_values(action_taken, reward)

            # 6. Gain tokens from surprise
            tokens_gained = int(surprise * 10)
            self.action_tokens = min(self.max_tokens, self.action_tokens + tokens_gained)

            # 7. Update health/energy based on outcome
            if outcome.get("effect") == "found_food":
                self.health = min(100, self.health + 20)
                self.energy = min(100, self.energy + 30)

            self.energy -= self.energy_cost_per_step  # Energy cost per timestep
            self.health -= self.health_decay_rate if self.energy <= 0 else 0

            summary = {
                "mood": mood_update,
                "surprise": surprise,
                "reward": reward,
                "tokens_gained": tokens_gained,
            }

            if self.llm_client and np.random.random() < 0.1:
                reflection = self._generate_llm_reflection(perception, outcome)
                if reflection:
                    summary["reflection"] = reflection

            cost_delta = max(0.0, self.last_reflection_cost - cost_before)
            if cost_delta > 0:
                summary["llm_cost_eur"] = cost_delta

            return summary

        except Exception as e:
            logger.error(f"Error in process_timestep for {self.creature_id}: {e}", exc_info=True)
            # Return minimal valid summary on error
            return {
                "mood": {"valence": 0.0, "arousal": 0.5},
                "surprise": 0.0,
                "reward": 0.0,
                "tokens_gained": 0,
            }

    def _calculate_perceptual_surprise(self, perception: Dict) -> float:
        """Calculate surprise based on how different perception is from memory with validation."""
        try:
            # Validate perception structure
            if not isinstance(perception, dict):
                logger.warning(f"Invalid perception type: {type(perception)}, expected dict")
                return 0.0

            # Validate required keys
            required_keys = ['food_count', 'creature_count', 'sound']
            missing_keys = [k for k in required_keys if k not in perception]
            if missing_keys:
                logger.warning(f"Perception missing keys: {missing_keys}")
                # Use defaults for missing keys
                perception = {
                    'food_count': perception.get('food_count', 0),
                    'creature_count': perception.get('creature_count', 0),
                    'sound': perception.get('sound', None)
                }

            if not self.perception_memory:
                self.perception_memory.append(perception)
                return 0.5  # Moderate surprise for first perception

            # Simple surprise: changes in key features
            last_perception = self.perception_memory[-1]

            # Validate numeric values
            try:
                food_change = abs(
                    float(perception.get("food_count", 0)) - float(last_perception.get("food_count", 0))
                )
            except (TypeError, ValueError) as e:
                logger.warning(f"Invalid food_count value: {e}")
                food_change = 0.0

            try:
                creature_change = abs(
                    float(perception.get("creature_count", 0))
                    - float(last_perception.get("creature_count", 0))
                )
            except (TypeError, ValueError) as e:
                logger.warning(f"Invalid creature_count value: {e}")
                creature_change = 0.0

            # Sound surprise with validation
            current_field = perception.get("sound")
            last_field = last_perception.get("sound")

            try:
                # Validate sound field is ndarray
                if current_field is not None:
                    if not isinstance(current_field, np.ndarray):
                        logger.warning("Current sound field is not ndarray, converting")
                        current_field = np.asarray(current_field)
                    # Validate shape
                    if current_field.ndim < 3 or current_field.shape[2] < 2:
                        logger.warning(f"Invalid sound field shape: {current_field.shape}")
                        current_field = None

                if last_field is not None:
                    if not isinstance(last_field, np.ndarray):
                        logger.warning("Last sound field is not ndarray, converting")
                        last_field = np.asarray(last_field)
                    if last_field.ndim < 3 or last_field.shape[2] < 2:
                        logger.warning(f"Invalid last sound field shape: {last_field.shape}")
                        last_field = None

                current_sound = float(
                    np.mean(current_field[:, :, 1]) if current_field is not None else 0.0
                )
                last_sound = float(
                    np.mean(last_field[:, :, 1]) if last_field is not None else 0.0
                )
                sound_change = abs(current_sound - last_sound)
            except (IndexError, ValueError, TypeError) as e:
                logger.warning(f"Error processing sound field: {e}")
                sound_change = 0.0

            # Combine surprises
            surprise = (
                food_change * 0.3 + creature_change * 0.3 + sound_change * 0.4
            ) / 3.0

            # Update memory
            self.perception_memory.append(perception)
            if len(self.perception_memory) > self.max_memory:
                self.perception_memory.pop(0)

            return min(1.0, float(surprise))

        except Exception as e:
            logger.error(f"Unexpected error calculating surprise: {e}", exc_info=True)
            return 0.0

    def _calculate_total_reward(self, surprise: float, outcome: Dict) -> float:
        """Combine surprise reward with survival rewards"""
        reward = surprise * 0.5  # Base reward from surprise

        # Survival rewards
        if outcome.get("effect") == "found_food":
            reward += 1.0
        elif (
            outcome.get("effect") == "made_sound"
            and outcome.get("creatures_responded", 0) > 0
        ):
            reward += 0.3 * outcome["creatures_responded"]
        elif outcome.get("effect") == "collision":
            reward -= 0.2

        # Social reward for being near others
        if outcome.get("near_creatures", 0) > 0:
            reward += 0.1 * min(3, outcome["near_creatures"])

        return reward

    def _update_action_values(self, action: str, reward: float):
        """Update expected value of actions"""
        if action not in self.action_values:
            self.action_values[action] = 0.0

        # Simple exponential moving average
        alpha = 0.1
        self.action_values[action] = (1 - alpha) * self.action_values[
            action
        ] + alpha * reward

    def get_action_bias(self) -> Dict[str, float]:
        """Get mood-influenced action preferences"""
        biases = {}

        # Mood influences
        valence = self.mood_system.valence
        arousal = self.mood_system.arousal

        # High arousal → more exploration
        if arousal > 0.7:
            biases["explore"] = 0.3
            biases["make_sound_high"] = 0.2

        # Low arousal → conservation
        if arousal < 0.3:
            biases["stay"] = 0.3
            biases["listen"] = 0.2

        # Positive mood → social behaviors
        if valence > 0.3:
            biases["make_sound_low"] = 0.2
            biases["move_north"] = 0.1  # Arbitrary direction preference

        # Negative mood → avoidance
        if valence < -0.3:
            biases["move_south"] = 0.2
            biases["stay"] = 0.1

        # Add learned action values
        for action, value in self.action_values.items():
            if action in biases:
                biases[action] += value * 0.2
            else:
                biases[action] = value * 0.2

        return biases

    def generate_internal_monologue(self) -> str:
        """Generate internal thoughts using heuristics or an optional LLM."""

        if self.llm_client:
            latest_perception = self.perception_memory[-1] if self.perception_memory else {}
            context = {
                "valence": round(self.mood_system.valence, 2),
                "arousal": round(self.mood_system.arousal, 2),
                "health": round(self.health, 1),
                "energy": round(self.energy, 1),
                "perception": {
                    "food": latest_perception.get("food_count", 0),
                    "creatures": latest_perception.get("creature_count", 0),
                },
            }
            response = self.llm_client.generate_reflection(
                self.creature_id,
                json.dumps(context),
            )
            if response and response.text:
                self.last_reflection_cost = response.total_cost_eur
                return response.text.strip()

        words = []

        # Mood words
        if self.mood_system.valence > 0.5:
            words.append("happy")
        elif self.mood_system.valence < -0.5:
            words.append("sad")

        # Need words
        if self.health < 30:
            words.append("hungry")
        if self.energy < 30:
            words.append("tired")

        # Perception words
        if len(self.perception_memory) > 0:
            last_p = self.perception_memory[-1]
            if last_p.get("food_count", 0) > 0:
                words.append("food near")
            if last_p.get("creature_count", 0) > 0:
                words.append("creature near")

            last_field = last_p.get("sound")
            sound_level = float(
                np.mean(np.asarray(last_field)[:, :, 1]) if last_field is not None else 0.0
            )
            if sound_level > 0.5:
                words.append("loud")

        return " ".join(words) if words else "..."

    def _generate_llm_reflection(self, perception: Dict, outcome: Dict) -> str:
        """Generate a short reflection from the LLM client."""

        if not self.llm_client:
            return ""

        # Convert numpy arrays to lists for JSON serialization
        def convert_for_json(obj):
            """Recursively convert numpy arrays to lists."""
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {k: convert_for_json(v) for k, v in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [convert_for_json(item) for item in obj]
            return obj

        serializable_data = {
            "perception": convert_for_json(perception),
            "outcome": convert_for_json(outcome),
            "mood": {
                "valence": self.mood_system.valence,
                "arousal": self.mood_system.arousal,
            },
        }

        context_summary = json.dumps(serializable_data)

        response = self.llm_client.generate_reflection(
            self.creature_id,
            context_summary,
        )

        if response and response.text:
            self.last_reflection_cost = response.total_cost_eur
            return response.text.strip()

        return ""
