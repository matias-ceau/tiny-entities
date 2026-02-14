import numpy as np
from src.creatures.mood_system import EmergentMoodSystem
from src.creatures.brain import EnhancedBrain
from src.creatures.action_selection import MoodInfluencedActionSelector
from src.creatures.factory import create_creatures


class DummyWorld:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

def test_mood_system():
    """Test emergent mood system"""
    mood = EmergentMoodSystem()
    
    # Initial state
    assert mood.valence == 0.0
    assert mood.arousal == 0.5
    
    # Process positive surprise
    situation = {'food_nearby': True, 'creatures_nearby': 2}
    result = mood.process_experience(situation, actual_reward=1.0)
    
    # Should increase valence (positive surprise)
    assert result['valence'] > 0
    assert result['arousal'] > 0.5
    assert 'prediction_error' in result

def test_brain_creation():
    """Test brain initialization"""
    brain = EnhancedBrain("test_creature")
    
    assert brain.creature_id == "test_creature"
    assert brain.health == 100.0
    assert brain.energy == 100.0
    assert brain.action_tokens == 10
    assert isinstance(brain.mood_system, EmergentMoodSystem)

def test_brain_perception_surprise():
    """Test surprise calculation"""
    brain = EnhancedBrain("test_creature")
    
    # First perception
    perception1 = {
        'food_count': 5,
        'creature_count': 2,
        'sound': np.zeros((5, 5, 2))
    }
    
    # Process timestep
    outcome = {'effect': 'none'}
    result = brain.process_timestep(perception1, 'stay', outcome)
    
    assert 'surprise' in result
    assert 'reward' in result
    assert 'tokens_gained' in result
    
    # Different perception should cause surprise
    perception2 = {
        'food_count': 0,
        'creature_count': 5,
        'sound': np.ones((5, 5, 2)) * 0.5
    }
    
    result2 = brain.process_timestep(perception2, 'move_north', outcome)
    assert result2['surprise'] > 0

def test_action_selection():
    """Test mood-influenced action selection"""
    selector = MoodInfluencedActionSelector()
    brain = EnhancedBrain("test_creature")
    
    # Set positive mood
    brain.mood_system.valence = 0.8
    brain.mood_system.arousal = 0.7
    
    perception = {
        'food_count': 0,
        'creature_count': 1,
        'sound': np.zeros((5, 5, 2))
    }
    
    # Should select an action
    action = selector.select_action(brain, perception)
    assert action in selector.base_actions
    
    # Test with low energy
    brain.energy = 10
    action2 = selector.select_action(brain, perception)
    # Low energy should bias toward staying
    assert action2 in selector.base_actions

def test_action_biases():
    """Test that mood creates action biases"""
    brain = EnhancedBrain("test_creature")
    
    # High arousal should bias exploration
    brain.mood_system.arousal = 0.8
    biases = brain.get_action_bias()
    assert 'explore' in biases
    assert biases['explore'] > 0
    
    # Positive mood should bias social behaviors
    brain.mood_system.valence = 0.5
    brain.mood_system.arousal = 0.5
    biases = brain.get_action_bias()
    assert 'make_sound_low' in biases


def test_create_creatures_small_world_supported():
    """Creature creation should work for worlds at or below the default margin size."""
    world = DummyWorld(width=20, height=20)

    creatures = create_creatures(5, world)

    assert len(creatures) == 5
    for creature in creatures:
        x, y = creature["position"]
        assert 0 <= x < world.width
        assert 0 <= y < world.height


def test_create_creatures_tiny_world_supported():
    """Creature creation should also work for very tiny worlds."""
    world = DummyWorld(width=1, height=1)

    creatures = create_creatures(1, world)

    assert creatures[0]["position"] == (0, 0)
