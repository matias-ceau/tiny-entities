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
        
        # Colors
        self.colors = {
            'empty': (20, 20, 20),
            'food': (50, 200, 50),
            'obstacle': (100, 100, 100),
            'creature': (200, 100, 100),
            'sound_low': (100, 100, 255, 50),
            'sound_high': (255, 100, 100, 50)
        }
        
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
            
            if not paused:
                # Run simulation step
                await self.simulation.simulation_step()
                
                # Periodic analysis
                if self.simulation.step_count % self.simulation.analyze_every == 0:
                    await self.simulation.analyze_emergence()
            
            # Draw everything
            self._draw_world()
            self._draw_info()
            
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
                
                # Creature color based on mood
                valence = creature['brain'].mood_system.valence
                arousal = creature['brain'].mood_system.arousal
                
                # Red channel for arousal, blue/green for valence
                r = int(100 + arousal * 155)
                if valence > 0:
                    g = int(100 + valence * 155)
                    b = 100
                else:
                    g = 100
                    b = int(100 - valence * 155)
                
                color = (r, g, b)
                
                # Draw creature as circle
                center = (
                    x * self.cell_width + self.cell_width // 2,
                    y * self.cell_height + self.cell_height // 2
                )
                pygame.draw.circle(self.screen, color, center, self.cell_width // 3)
    
    def _draw_info(self):
        """Draw information panel"""
        info_y = self.height + 10
        
        # Background for info panel
        info_rect = pygame.Rect(0, self.height, self.width, 100)
        pygame.draw.rect(self.screen, (40, 40, 40), info_rect)
        
        # Step counter
        step_text = f"Step: {self.simulation.step_count}/{self.simulation.max_steps}"
        text = self.font.render(step_text, True, (255, 255, 255))
        self.screen.blit(text, (10, info_y))
        
        # Alive creatures
        alive_count = sum(1 for c in self.simulation.creatures if c['alive'])
        alive_text = f"Alive: {alive_count}/{len(self.simulation.creatures)}"
        text = self.font.render(alive_text, True, (255, 255, 255))
        self.screen.blit(text, (200, info_y))
        
        # Sound events
        recent_sounds = len([s for s in self.simulation.sound_history[-100:]])
        sound_text = f"Recent sounds: {recent_sounds}"
        text = self.font.render(sound_text, True, (255, 255, 255))
        self.screen.blit(text, (400, info_y))
        
        # Cost tracking
        cost_text = f"Cost: €{self.simulation.daily_cost_eur:.3f}"
        text = self.font.render(cost_text, True, (255, 255, 255))
        self.screen.blit(text, (600, info_y))
        
        # Instructions
        inst_text = "SPACE: Pause | ESC: Quit"
        text = self.font.render(inst_text, True, (150, 150, 150))
        self.screen.blit(text, (10, info_y + 30))