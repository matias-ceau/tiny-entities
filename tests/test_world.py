import pytest
import numpy as np
from src.world.physics import SimpleWorld
from src.world.non_deterministic import NonDeterministicWorldModel


def test_simple_world_creation():
    """Test world creation and initialization"""
    world = SimpleWorld(width=50, height=50)

    assert world.width == 50
    assert world.height == 50
    assert world.grid.shape == (50, 50)
    assert world.sound_grid.shape == (50, 50, 2)

    # Check that some food and obstacles were spawned
    food_count = np.sum(world.grid == 1)
    obstacle_count = np.sum(world.grid == 2)

    assert food_count > 0
    assert obstacle_count > 0


def test_local_view():
    """Test getting local view around a position"""
    world = SimpleWorld(width=20, height=20)

    # Get view from center
    view = world.get_local_view(10, 10, radius=3)

    assert "visual" in view
    assert "sound" in view
    assert view["visual"].shape == (7, 7)  # 3 radius = 7x7 grid
    assert view["sound"].shape == (7, 7, 2)


def test_sound_propagation():
    """Test sound propagation in world"""
    world = SimpleWorld(width=10, height=10)

    # Make sound at center
    world.update_sound(5, 5, frequency=0.5, amplitude=1.0)

    # Check center has sound
    assert world.sound_grid[5, 5, 1] == 1.0

    # Check neighbors have propagated sound
    assert world.sound_grid[4, 5, 1] == 0.5  # 50% propagation
    assert world.sound_grid[6, 5, 1] == 0.5


def test_non_deterministic_world():
    """Test non-deterministic world model"""
    world_model = NonDeterministicWorldModel(acceptance_rate=0.9)

    # Test action proposal
    result = world_model.propose_action("creature_0", "move_north", (5, 5))

    assert "accepted" in result
    assert "new_position" in result
    assert "effect" in result

    # With 90% acceptance, most actions should be accepted
    accepted_count = 0
    for _ in range(100):
        result = world_model.propose_action("creature_0", "stay", (5, 5))
        if result["accepted"]:
            accepted_count += 1

    # Should be roughly 90 accepted out of 100
    assert 80 < accepted_count < 100
