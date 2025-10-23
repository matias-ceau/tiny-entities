"""Procedural sound synthesis utilities for creature vocalisations.""" 

from __future__ import annotations

import numpy as np
from dataclasses import dataclass
from typing import Dict


@dataclass
class SynthesizedSound:
    """Container for generated sound wave data."""

    waveform: np.ndarray
    sample_rate: int
    metadata: Dict[str, float]


class SoundSynthesizer:
    """Simple sine-based sound synthesis for creature vocalisations."""

    def __init__(self, sample_rate: int = 22050, duration: float = 0.35) -> None:
        self.sample_rate = sample_rate
        self.duration = duration

    def synthesize(
        self,
        frequency_hint: float,
        mood_valence: float,
        mood_arousal: float,
    ) -> SynthesizedSound:
        """Generate a waveform influenced by creature mood."""

        base_frequency = 220 + frequency_hint * 660
        t = np.linspace(0, self.duration, int(self.sample_rate * self.duration), endpoint=False)

        # Main tone influenced by arousal (louder) and valence (pitch modulation)
        amplitude = 0.4 + abs(mood_arousal) * 0.6
        vibrato = 1 + mood_valence * 0.05 * np.sin(2 * np.pi * 5 * t)
        carrier = np.sin(2 * np.pi * base_frequency * vibrato * t)

        # Add simple harmonic layer
        harmonic = 0.3 * np.sin(2 * np.pi * base_frequency * 2 * t)
        waveform = amplitude * (carrier + harmonic)

        # Apply envelope so the sound is percussive and short
        envelope = np.linspace(1.0, 0.2, waveform.shape[0])
        waveform = waveform * envelope

        # Clip to safe range
        waveform = np.clip(waveform, -1.0, 1.0)

        metadata = {
            "base_frequency": float(base_frequency),
            "amplitude": float(amplitude),
            "valence": float(mood_valence),
            "arousal": float(mood_arousal),
        }

        return SynthesizedSound(waveform=waveform.astype(np.float32), sample_rate=self.sample_rate, metadata=metadata)
