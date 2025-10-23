"""Tests for visualization color palette and legend functionality"""

import os
import pytest

# Set headless mode for testing
os.environ['SDL_VIDEODRIVER'] = 'dummy'

import pygame
from src.simulation.main_loop import EmergentLifeSimulation
from src.simulation.visualization import SimulationVisualizer


def test_color_palette_structure():
    """Test that the color palette is properly structured"""
    sim = EmergentLifeSimulation(num_creatures=2, max_steps=10)
    viz = SimulationVisualizer(sim, width=400, height=400)
    
    # Check that all required colors are defined
    required_colors = ['empty', 'food', 'obstacle', 'creature', 
                      'sound_low', 'sound_high', 'text', 
                      'legend_bg', 'legend_border']
    
    for color_name in required_colors:
        assert color_name in viz.colors, f"Color '{color_name}' not found in palette"
        assert isinstance(viz.colors[color_name], tuple), f"Color '{color_name}' should be a tuple"
    
    pygame.quit()


def test_improved_food_color():
    """Test that food color has been changed to be less bright"""
    sim = EmergentLifeSimulation(num_creatures=2, max_steps=10)
    viz = SimulationVisualizer(sim, width=400, height=400)
    
    food_color = viz.colors['food']
    
    # Check that it's the new muted green, not the old bright green
    assert food_color == (80, 140, 60), f"Food color should be (80, 140, 60), got {food_color}"
    
    # Verify it's less saturated than old color (50, 200, 50)
    old_max = 200
    new_max = max(food_color)
    assert new_max < old_max, "New food color should be less bright"
    
    pygame.quit()


def test_legend_toggle():
    """Test that legend toggle state is properly initialized"""
    sim = EmergentLifeSimulation(num_creatures=2, max_steps=10)
    viz = SimulationVisualizer(sim, width=400, height=400)
    
    # Check initial state
    assert hasattr(viz, 'show_legend'), "Visualizer should have show_legend attribute"
    assert viz.show_legend is True, "Legend should be shown by default"
    
    # Test toggle
    viz.show_legend = False
    assert viz.show_legend is False, "Legend should be hideable"
    
    viz.show_legend = True
    assert viz.show_legend is True, "Legend should be showable again"
    
    pygame.quit()


def test_legend_draw_method_exists():
    """Test that the legend drawing method exists"""
    sim = EmergentLifeSimulation(num_creatures=2, max_steps=10)
    viz = SimulationVisualizer(sim, width=400, height=400)
    
    assert hasattr(viz, '_draw_legend'), "Visualizer should have _draw_legend method"
    assert callable(viz._draw_legend), "_draw_legend should be callable"
    
    pygame.quit()


def test_creature_visibility_improvements():
    """Test that creature rendering has visibility improvements"""
    sim = EmergentLifeSimulation(num_creatures=2, max_steps=10)
    viz = SimulationVisualizer(sim, width=400, height=400)
    
    # The implementation uses improved brightness values
    # We can't easily test the actual rendering without running simulation
    # but we can verify the color palette is set up correctly
    
    assert 'creature' in viz.colors, "Creature color should be defined"
    
    # Verify the text color is defined for better readability
    assert 'text' in viz.colors, "Text color should be defined"
    text_color = viz.colors['text']
    # Text should be bright (close to white) for visibility
    assert min(text_color) > 200, "Text color should be bright for visibility"
    
    pygame.quit()
