from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List, Optional, Any
import numpy as np


@dataclass
class Observation:
    """Multimodal observation from the environment"""

    visual: Optional[np.ndarray] = None
    audio: Optional[np.ndarray] = None
    text: Optional[str] = None
    timestamp: float = 0.0


@dataclass
class EmotionalState:
    """PAD (Pleasure-Arousal-Dominance) emotional model"""

    pleasure: float = 0.0  # -1 to 1
    arousal: float = 0.0  # -1 to 1
    dominance: float = 0.0  # -1 to 1

    def update(self, delta: "EmotionalState", rate: float = 0.1):
        """Smooth emotional state updates"""
        self.pleasure += rate * (delta.pleasure - self.pleasure)
        self.arousal += rate * (delta.arousal - self.arousal)
        self.dominance += rate * (delta.dominance - self.dominance)


class CognitiveModule(ABC):
    """Base class for all cognitive modules"""

    @abstractmethod
    async def process(self, input_data: Any) -> Any:
        """Process input data and return results"""
        pass

    @abstractmethod
    async def update(self, feedback: Any) -> None:
        """Update internal state based on feedback"""
        pass
