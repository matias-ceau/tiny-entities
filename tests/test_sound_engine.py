import os
import sys

import numpy as np

# Ensure src package is importable when running tests directly
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from world.sound_engine import SoundSynthesizer


def test_sound_synthesizer_waveform_bounds():
    synth = SoundSynthesizer(sample_rate=8000, duration=0.1)
    sound = synth.synthesize(0.5, mood_valence=0.2, mood_arousal=0.7)

    assert sound.waveform.ndim == 1
    assert sound.waveform.size == int(0.1 * 8000)
    assert np.all(sound.waveform <= 1.0)
    assert np.all(sound.waveform >= -1.0)
    assert sound.metadata["base_frequency"] > 200
