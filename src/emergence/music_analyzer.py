import numpy as np
from typing import List, Dict
from ..config.api_config import APIConfig

class MusicEmergenceAnalyzer:
    """Use sophisticated AI to judge emergent music quality"""
    
    def __init__(self):
        self.api_config = APIConfig()
        self.model = self.api_config.get_analysis_model()
        
    async def analyze_collective_music(self, sound_history: List[Dict]) -> Dict:
        """Analyze if creatures are making music together"""
        
        if not self.model:
            return self._simple_analysis(sound_history)
        
        # In production, would make actual API call
        # For now, return simple analysis
        return self._simple_analysis(sound_history)
    
    def _simple_analysis(self, sound_history: List[Dict]) -> Dict:
        """Simple analysis without API"""
        if len(sound_history) < 10:
            return {
                'music_score': 0,
                'coordination_detected': False,
                'entropy_trend': 'insufficient_data',
                'full_analysis': 'Not enough sound data'
            }
        
        # Calculate basic metrics
        music_score = min(10, len(sound_history) / 10)
        coordination = self._detect_simple_coordination(sound_history)
        entropy_trend = self._calculate_entropy_trend(sound_history)
        
        return {
            'music_score': music_score,
            'coordination_detected': coordination,
            'entropy_trend': entropy_trend,
            'full_analysis': 'Simple analysis (no API configured)'
        }
    
    def _detect_simple_coordination(self, sound_history: List[Dict]) -> bool:
        """Simple coordination detection"""
        if len(sound_history) < 10:
            return False
        
        # Check if creatures respond to each other
        response_count = 0
        for i in range(1, len(sound_history)):
            if sound_history[i]['step'] - sound_history[i-1]['step'] <= 3:
                if sound_history[i]['creature_id'] != sound_history[i-1]['creature_id']:
                    response_count += 1
        
        return response_count > len(sound_history) * 0.2
    
    def _calculate_entropy_trend(self, sound_history: List[Dict]) -> str:
        """Calculate if entropy is increasing or decreasing"""
        if len(sound_history) < 20:
            return 'insufficient_data'
        
        # Calculate entropy for first and last quarter
        quarter_size = len(sound_history) // 4
        
        first_quarter = sound_history[:quarter_size]
        last_quarter = sound_history[-quarter_size:]
        
        first_entropy = self._calculate_entropy(first_quarter)
        last_entropy = self._calculate_entropy(last_quarter)
        
        if last_entropy < first_entropy * 0.8:
            return 'decreasing'
        elif last_entropy > first_entropy * 1.2:
            return 'increasing'
        else:
            return 'stable'
    
    def _calculate_entropy(self, events: List[Dict]) -> float:
        """Calculate entropy of sound events"""
        if not events:
            return 0.0
        
        # Calculate frequency distribution
        frequencies = [e['frequency'] for e in events]
        
        # Bin frequencies
        bins = np.linspace(0, 1, 10)
        hist, _ = np.histogram(frequencies, bins=bins)
        
        # Calculate entropy
        probs = hist / len(frequencies)
        probs = probs[probs > 0]  # Remove zeros
        
        if len(probs) == 0:
            return 0.0
        
        entropy = -np.sum(probs * np.log2(probs))
        return entropy