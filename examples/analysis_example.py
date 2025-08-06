#!/usr/bin/env python3
"""Example of analyzing emergent behaviors in saved simulation data"""

import json
import numpy as np
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.emergence.music_analyzer import MusicEmergenceAnalyzer

def analyze_sound_patterns(sound_history):
    """Analyze sound patterns for musical emergence"""
    if not sound_history:
        print("No sound data to analyze")
        return
    
    print(f"\nAnalyzing {len(sound_history)} sound events...")
    
    # Time intervals between sounds
    if len(sound_history) > 1:
        intervals = []
        for i in range(1, len(sound_history)):
            interval = sound_history[i]['step'] - sound_history[i-1]['step']
            intervals.append(interval)
        
        avg_interval = np.mean(intervals)
        std_interval = np.std(intervals)
        
        print(f"Average interval between sounds: {avg_interval:.2f} ± {std_interval:.2f} steps")
        
        # Check for rhythm
        if std_interval < avg_interval * 0.3:
            print("Possible rhythmic pattern detected!")
    
    # Frequency analysis
    frequencies = [s['frequency'] for s in sound_history]
    low_freq = sum(1 for f in frequencies if f < 0.5)
    high_freq = sum(1 for f in frequencies if f >= 0.5)
    
    print(f"Frequency distribution: {low_freq} low, {high_freq} high")
    
    # Creature participation
    creatures = set(s['creature_id'] for s in sound_history)
    print(f"Unique creatures making sounds: {len(creatures)}")
    
    # Mood correlation
    if 'mood_valence' in sound_history[0]:
        valences = [s['mood_valence'] for s in sound_history]
        avg_valence = np.mean(valences)
        print(f"Average mood when making sounds: {avg_valence:.2f}")

def analyze_movement_patterns(creature_positions):
    """Analyze spatial patterns and clustering"""
    print("\nAnalyzing movement patterns...")
    
    # This would analyze saved position data
    # For now, just a placeholder
    print("Movement analysis not yet implemented")

async def main():
    """Run analysis on simulation data"""
    
    # In a real implementation, this would load saved data
    # For now, create some example data
    example_sounds = [
        {'step': 100, 'creature_id': 'creature_0', 'frequency': 0.3, 'mood_valence': 0.2},
        {'step': 103, 'creature_id': 'creature_1', 'frequency': 0.7, 'mood_valence': 0.5},
        {'step': 106, 'creature_id': 'creature_0', 'frequency': 0.3, 'mood_valence': 0.3},
        {'step': 109, 'creature_id': 'creature_2', 'frequency': 0.5, 'mood_valence': -0.1},
    ]
    
    print("=== Emergence Analysis Example ===")
    
    # Analyze sound patterns
    analyze_sound_patterns(example_sounds)
    
    # Use music analyzer
    analyzer = MusicEmergenceAnalyzer()
    result = await analyzer.analyze_collective_music(example_sounds)
    
    print("\nMusic Analysis Results:")
    print(f"Music Score: {result['music_score']}/10")
    print(f"Coordination Detected: {result['coordination_detected']}")
    print(f"Entropy Trend: {result['entropy_trend']}")
    print(f"Analysis: {result['full_analysis']}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())