"""Tests for visualization color palette and legend functionality"""

import os
import pytest

# Set headless mode for testing
os.environ['SDL_VIDEODRIVER'] = 'dummy'

import pygame
from src.simulation.main_loop import EmergentLifeSimulation
from src.simulation.visualization import SimulationVisualizer


# Constants for testing
REQUIRED_COLORS = ['empty', 'food', 'obstacle', 'creature', 
                   'sound_low', 'sound_high', 'text', 
                   'legend_bg', 'legend_border']

EXPECTED_FOOD_COLOR = (80, 140, 60)  # Muted green for better readability


@pytest.fixture
def visualizer():
    """Fixture to create and cleanup a visualizer for testing"""
    sim = EmergentLifeSimulation(num_creatures=2, max_steps=10)
    viz = SimulationVisualizer(sim, width=400, height=400)
    yield viz
    pygame.quit()


def test_color_palette_structure(visualizer):
    """Test that the color palette is properly structured"""
    # Check that all required colors are defined
    for color_name in REQUIRED_COLORS:
        assert color_name in visualizer.colors, f"Color '{color_name}' not found in palette"
        assert isinstance(visualizer.colors[color_name], tuple), f"Color '{color_name}' should be a tuple"


def test_improved_food_color(visualizer):
    """Test that food color has been changed to be less bright"""
    food_color = visualizer.colors['food']
    
    # Check that it's the new muted green, not the old bright green
    assert food_color == EXPECTED_FOOD_COLOR, f"Food color should be {EXPECTED_FOOD_COLOR}, got {food_color}"
    
    # Verify it's less saturated than old color (50, 200, 50)
    old_max = 200
    new_max = max(food_color)
    assert new_max < old_max, "New food color should be less bright"


def test_legend_toggle(visualizer):
    """Test that legend toggle state is properly initialized"""
    # Check initial state
    assert hasattr(visualizer, 'show_legend'), "Visualizer should have show_legend attribute"
    assert visualizer.show_legend is True, "Legend should be shown by default"
    
    # Test toggle
    visualizer.show_legend = False
    assert visualizer.show_legend is False, "Legend should be hideable"
    
    visualizer.show_legend = True
    assert visualizer.show_legend is True, "Legend should be showable again"


def test_legend_draw_method_exists(visualizer):
    """Test that the legend drawing method exists"""
    assert hasattr(visualizer, '_draw_legend'), "Visualizer should have _draw_legend method"
    assert callable(visualizer._draw_legend), "_draw_legend should be callable"


def test_creature_visibility_improvements(visualizer):
    """Test that creature rendering has visibility improvements"""
    # The implementation uses improved brightness values
    # We can't easily test the actual rendering without running simulation
    # but we can verify the color palette is set up correctly
    
    assert 'creature' in visualizer.colors, "Creature color should be defined"
    
    # Verify the text color is defined for better readability
    assert 'text' in visualizer.colors, "Text color should be defined"
    text_color = visualizer.colors['text']
    # Text should be bright (close to white) for visibility
    assert min(text_color) > 200, "Text color should be bright for visibility"

