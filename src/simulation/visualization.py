import pygame
import numpy as np
from typing import Optional

class SimulationVisualizer:
    """Real-time visualization of the simulation"""
    
    def __init__(self, simulation, width: int = 800, height: int = 800):
        self.simulation = simulation
        self.width = width
        self.height = height
        
        # Calculate cell size
        self.cell_width = width // simulation.world_model.world.width
        self.cell_height = height // simulation.world_model.world.height
        
        # Improved color palette for better readability
        # Using more distinct, less saturated colors to reduce eye strain
        self.colors = {
            'empty': (15, 15, 20),           # Dark blue-black background
            'food': (80, 140, 60),           # Muted green - easier on eyes
            'obstacle': (120, 120, 130),     # Lighter gray for better contrast
            'creature': (200, 100, 100),     # Base creature color
            'sound_low': (80, 120, 200, 60), # Calm blue with transparency
            'sound_high': (200, 80, 80, 60), # Warm red with transparency
            'text': (240, 240, 245),         # Off-white for text
            'legend_bg': (30, 30, 35),       # Dark background for legend
            'legend_border': (80, 80, 90),   # Border color for legend
        }
        
        # Legend toggle state
        self.show_legend = True
        
        # Pygame setup
        pygame.init()
        self.screen = pygame.display.set_mode((width, height + 100))  # Extra space for info
        pygame.display.set_caption("Tiny Entities Simulation")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        
    async def run(self):
        """Run simulation with visualization"""
        running = True
        paused = False
        
        while running and self.simulation.step_count < self.simulation.max_steps:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        paused = not paused
                    elif event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_l or event.key == pygame.K_k:
                        # Toggle legend with 'L' or 'K' key
                        self.show_legend = not self.show_legend
            
            if not paused:
                # Run simulation step
                await self.simulation.simulation_step()
                
                # Periodic analysis
                if self.simulation.step_count % self.simulation.analyze_every == 0:
                    await self.simulation.analyze_emergence()
            
            # Draw everything
            self._draw_world()
            self._draw_info()
            if self.show_legend:
                self._draw_legend()
            
            pygame.display.flip()
            self.clock.tick(30)  # 30 FPS
        
        pygame.quit()
    
    def _draw_world(self):
        """Draw the world grid"""
        self.screen.fill((0, 0, 0))
        
        world = self.simulation.world_model.world
        
        # Draw grid cells
        for y in range(world.height):
            for x in range(world.width):
                cell_value = world.grid[y, x]
                
                # Determine color based on cell content
                if cell_value == 0:
                    color = self.colors['empty']
                elif cell_value == 1:
                    color = self.colors['food']
                elif cell_value == 2:
                    color = self.colors['obstacle']
                
                # Draw cell
                rect = pygame.Rect(
                    x * self.cell_width,
                    y * self.cell_height,
                    self.cell_width,
                    self.cell_height
                )
                pygame.draw.rect(self.screen, color, rect)
        
        # Draw sound waves (overlay)
        sound_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        for y in range(world.height):
            for x in range(world.width):
                amplitude = world.sound_grid[y, x, 1]
                if amplitude > 0.01:
                    frequency = world.sound_grid[y, x, 0]
                    color = self.colors['sound_low'] if frequency < 0.5 else self.colors['sound_high']
                    alpha = int(amplitude * 255)
                    color = (*color[:3], min(alpha, 100))
                    
                    # Draw sound as circle
                    center = (
                        x * self.cell_width + self.cell_width // 2,
                        y * self.cell_height + self.cell_height // 2
                    )
                    radius = int(self.cell_width * amplitude)
                    pygame.draw.circle(sound_surface, color, center, radius)
        
        self.screen.blit(sound_surface, (0, 0))
        
        # Draw creatures
        for creature in self.simulation.creatures:
            if creature['alive']:
                x, y = creature['position']
                
                # Enhanced creature color based on mood for better visibility
                valence = creature['brain'].mood_system.valence
                arousal = creature['brain'].mood_system.arousal
                
                # Base brightness increased for better visibility
                base = 140
                range_val = 115
                
                # Red channel for arousal (always prominent)
                r = int(base + arousal * range_val)
                
                # Green/Blue channels for valence with better contrast
                if valence > 0:
                    # Positive valence: more green
                    g = int(base + valence * range_val)
                    b = int(base - valence * 40)  # Reduce blue for contrast
                else:
                    # Negative valence: more blue
                    g = int(base + valence * 40)  # Reduce green for contrast
                    b = int(base - valence * range_val)
                
                color = (r, g, b)
                
                # Draw creature as circle with a white border for high visibility
                center = (
                    x * self.cell_width + self.cell_width // 2,
                    y * self.cell_height + self.cell_height // 2
                )
                radius = self.cell_width // 3
                # White outline for better visibility
                pygame.draw.circle(self.screen, (255, 255, 255), center, radius + 2)
                pygame.draw.circle(self.screen, color, center, radius)
    
    def _draw_info(self):
        """Draw information panel"""
        info_y = self.height + 10
        
        # Background for info panel
        info_rect = pygame.Rect(0, self.height, self.width, 100)
        pygame.draw.rect(self.screen, (40, 40, 40), info_rect)
        
        # Use improved text color
        text_color = self.colors['text']
        
        # Step counter
        step_text = f"Step: {self.simulation.step_count}/{self.simulation.max_steps}"
        text = self.font.render(step_text, True, text_color)
        self.screen.blit(text, (10, info_y))
        
        # Alive creatures
        alive_count = sum(1 for c in self.simulation.creatures if c['alive'])
        alive_text = f"Alive: {alive_count}/{len(self.simulation.creatures)}"
        text = self.font.render(alive_text, True, text_color)
        self.screen.blit(text, (200, info_y))
        
        # Sound events
        recent_sounds = len([s for s in self.simulation.sound_history[-100:]])
        sound_text = f"Recent sounds: {recent_sounds}"
        text = self.font.render(sound_text, True, text_color)
        self.screen.blit(text, (400, info_y))
        
        # Cost tracking
        cost_text = f"Cost: €{self.simulation.daily_cost_eur:.3f}"
        text = self.font.render(cost_text, True, text_color)
        self.screen.blit(text, (600, info_y))
        
        # Instructions
        inst_text = "SPACE: Pause | ESC: Quit | L/K: Toggle Legend"
        text = self.font.render(inst_text, True, (180, 180, 185))
        self.screen.blit(text, (10, info_y + 30))
    
    def _draw_legend(self):
        """Draw color legend/key explaining the visualization"""
        # Legend dimensions and position (right side of screen)
        legend_width = 200
        legend_height = 280
        legend_x = self.width - legend_width - 10
        legend_y = 10
        
        # Semi-transparent background
        legend_surface = pygame.Surface((legend_width, legend_height), pygame.SRCALPHA)
        legend_surface.fill((*self.colors['legend_bg'], 230))  # Semi-transparent
        
        # Border
        pygame.draw.rect(legend_surface, self.colors['legend_border'], 
                        (0, 0, legend_width, legend_height), 2)
        
        # Title
        small_font = pygame.font.Font(None, 20)
        title = small_font.render("COLOR KEY", True, self.colors['text'])
        legend_surface.blit(title, (10, 10))
        
        # Legend items
        y_offset = 35
        item_height = 25
        
        # Define legend items with colors and descriptions
        legend_items = [
            (self.colors['empty'], "Empty Space"),
            (self.colors['food'], "Food"),
            (self.colors['obstacle'], "Obstacle"),
            ((255, 255, 255), "Creature (outlined)"),
            (self.colors['sound_low'][:3], "Low-freq Sound"),
            (self.colors['sound_high'][:3], "High-freq Sound"),
        ]
        
        for color, description in legend_items:
            # Draw color swatch
            swatch_rect = pygame.Rect(10, y_offset, 20, 15)
            pygame.draw.rect(legend_surface, color, swatch_rect)
            pygame.draw.rect(legend_surface, self.colors['legend_border'], swatch_rect, 1)
            
            # Draw description
            text = small_font.render(description, True, self.colors['text'])
            legend_surface.blit(text, (35, y_offset - 2))
            
            y_offset += item_height
        
        # Add creature mood explanation
        y_offset += 10
        mood_title = small_font.render("CREATURE MOODS:", True, self.colors['text'])
        legend_surface.blit(mood_title, (10, y_offset))
        y_offset += 20
        
        # Mood examples
        mood_examples = [
            ((255, 255, 140), "Happy + Excited"),
            ((255, 140, 140), "Excited Neutral"),
            ((140, 140, 255), "Sad + Calm"),
        ]
        
        for color, description in mood_examples:
            # Draw small circle
            center_x = 20
            center_y = y_offset + 8
            pygame.draw.circle(legend_surface, (255, 255, 255), (center_x, center_y), 9)
            pygame.draw.circle(legend_surface, color, (center_x, center_y), 7)
            
            # Draw description
            text = small_font.render(description, True, self.colors['text'])
            legend_surface.blit(text, (35, y_offset))
            
            y_offset += 20
        
        # Blit legend to main screen
        self.screen.blit(legend_surface, (legend_x, legend_y))