import pygame
import numpy as np
from typing import Optional, List, Dict, Any

class SimulationVisualizer:
    """Real-time visualization with internal monologue and communication patterns"""

    def __init__(self, simulation, width: int = 800, height: int = 800):
        self.simulation = simulation
        self.width = width
        self.height = height

        # Calculate cell size
        self.cell_width = width // simulation.world_model.world.width
        self.cell_height = height // simulation.world_model.world.height

        # IMPROVED color palette with much better visibility
        self.colors = {
            'empty': (15, 15, 20),           # Dark blue-black background
            'food': (120, 220, 80),          # BRIGHT green - very visible!
            'food_outline': (180, 255, 140),  # Brighter outline
            'obstacle': (180, 80, 60),       # Reddish-brown - clear and distinct
            'obstacle_border': (220, 120, 90), # Lighter border
            'creature': (200, 100, 100),     # Base creature color
            'sound_low': (80, 150, 255, 100), # Bright blue with transparency
            'sound_high': (255, 100, 100, 100), # Bright red with transparency
            'text': (240, 240, 245),         # Off-white for text
            'legend_bg': (30, 30, 35),       # Dark background for legend
            'legend_border': (80, 80, 90),   # Border color for legend
            'monologue_bg': (20, 20, 30),    # Background for internal monologue panel
            'monologue_text': (180, 200, 255), # Light blue text for thoughts
            'pattern_text': (255, 200, 100), # Orange for detected patterns
            'health_bar_bg': (60, 60, 70),   # Health bar background
            'health_bar': (100, 255, 100),   # Green health
            'energy_bar': (255, 200, 100),   # Orange energy
        }

        # UI toggle states
        self.show_legend = True
        self.show_monologue = True  # Show internal thoughts
        self.show_patterns = True   # Show detected communication patterns
        self.show_health_bars = True # Show creature health/energy

        # Pygame setup - LARGER window for side panels
        self.panel_width = 380
        total_width = width + self.panel_width
        pygame.init()
        self.screen = pygame.display.set_mode((total_width, height + 100))
        pygame.display.set_caption("Tiny Entities - Internal Lives Visualized")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        self.tiny_font = pygame.font.Font(None, 14)

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
                    elif event.key == pygame.K_l:
                        self.show_legend = not self.show_legend
                    elif event.key == pygame.K_m:
                        self.show_monologue = not self.show_monologue
                    elif event.key == pygame.K_p:
                        self.show_patterns = not self.show_patterns
                    elif event.key == pygame.K_h:
                        self.show_health_bars = not self.show_health_bars

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
            if self.show_monologue:
                self._draw_monologue_panel()
            if self.show_patterns:
                self._draw_pattern_panel()

            pygame.display.flip()
            self.clock.tick(30)  # 30 FPS

        pygame.quit()

    def _draw_world(self):
        """Draw the world grid with improved visibility"""
        self.screen.fill((0, 0, 0))

        world = self.simulation.world_model.world

        # Draw grid cells
        for y in range(world.height):
            for x in range(world.width):
                cell_value = world.grid[y, x]

                rect = pygame.Rect(
                    x * self.cell_width,
                    y * self.cell_height,
                    self.cell_width,
                    self.cell_height
                )

                # Draw based on cell content with IMPROVED VISIBILITY
                if cell_value == 0:
                    # Empty - just background
                    pygame.draw.rect(self.screen, self.colors['empty'], rect)

                elif cell_value == 1:
                    # FOOD - bright with outline for visibility
                    pygame.draw.rect(self.screen, self.colors['food'], rect)
                    # Add bright outline
                    pygame.draw.rect(self.screen, self.colors['food_outline'], rect, 1)

                elif cell_value == 2:
                    # OBSTACLE - distinct color with border
                    pygame.draw.rect(self.screen, self.colors['obstacle'], rect)
                    pygame.draw.rect(self.screen, self.colors['obstacle_border'], rect, 2)

        # Draw sound waves (overlay) with better visibility
        sound_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        for y in range(world.height):
            for x in range(world.width):
                amplitude = world.sound_grid[y, x, 1]
                if amplitude > 0.01:
                    frequency = world.sound_grid[y, x, 0]
                    base_color = self.colors['sound_low'] if frequency < 0.5 else self.colors['sound_high']
                    alpha = min(int(amplitude * 200), 150)  # Increased visibility
                    color = (*base_color[:3], alpha)

                    # Draw sound as filled rect with glow
                    sound_rect = pygame.Rect(
                        x * self.cell_width,
                        y * self.cell_height,
                        self.cell_width,
                        self.cell_height
                    )
                    pygame.draw.rect(sound_surface, color, sound_rect)

        self.screen.blit(sound_surface, (0, 0))

        # Draw creatures with health bars
        for creature in self.simulation.creatures:
            if creature['alive']:
                x, y = creature['position']

                # Creature color based on mood with better contrast
                valence = creature['brain'].mood_system.valence
                arousal = creature['brain'].mood_system.arousal

                # MORE VIBRANT colors for visibility
                base = 150
                range_val = 105

                r = int(base + arousal * range_val)
                if valence > 0:
                    g = int(base + valence * range_val)
                    b = int(base - valence * 50)
                else:
                    g = int(base + valence * 50)
                    b = int(base - valence * range_val)

                color = (min(255, r), min(255, g), min(255, b))

                # Draw creature as circle with white border
                center = (
                    x * self.cell_width + self.cell_width // 2,
                    y * self.cell_height + self.cell_height // 2
                )
                radius = max(self.cell_width // 3, 3)
                pygame.draw.circle(self.screen, (255, 255, 255), center, radius + 2)
                pygame.draw.circle(self.screen, color, center, radius)

                # Health/Energy bars if enabled
                if self.show_health_bars:
                    self._draw_creature_stats(creature, center[0], center[1] - radius - 5)

    def _draw_creature_stats(self, creature: Dict, x: int, y: int):
        """Draw small health and energy bars above creature"""
        bar_width = max(self.cell_width - 2, 8)
        bar_height = 3

        health = creature['brain'].health / 100.0  # Normalize to 0-1
        energy = creature['brain'].energy / 100.0

        # Health bar
        health_rect = pygame.Rect(x - bar_width // 2, y - 8, bar_width, bar_height)
        pygame.draw.rect(self.screen, self.colors['health_bar_bg'], health_rect)
        filled_health = pygame.Rect(x - bar_width // 2, y - 8, int(bar_width * health), bar_height)
        pygame.draw.rect(self.screen, self.colors['health_bar'], filled_health)

        # Energy bar
        energy_rect = pygame.Rect(x - bar_width // 2, y - 4, bar_width, bar_height)
        pygame.draw.rect(self.screen, self.colors['health_bar_bg'], energy_rect)
        filled_energy = pygame.Rect(x - bar_width // 2, y - 4, int(bar_width * energy), bar_height)
        pygame.draw.rect(self.screen, self.colors['energy_bar'], filled_energy)

    def _draw_info(self):
        """Draw information panel"""
        info_y = self.height + 10

        # Background for info panel
        info_rect = pygame.Rect(0, self.height, self.width + self.panel_width, 100)
        pygame.draw.rect(self.screen, (40, 40, 40), info_rect)

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
        sound_text = f"Sounds: {recent_sounds}"
        text = self.font.render(sound_text, True, text_color)
        self.screen.blit(text, (380, info_y))

        # Reflections
        recent_reflections = len([r for r in self.simulation.reflection_log[-10:]])
        reflection_text = f"Thoughts: {recent_reflections}"
        text = self.font.render(reflection_text, True, text_color)
        self.screen.blit(text, (520, info_y))

        # Cost tracking
        cost_text = f"Cost: €{self.simulation.daily_cost_eur:.3f}"
        text = self.font.render(cost_text, True, text_color)
        self.screen.blit(text, (680, info_y))

        # Instructions
        inst_text = "SPACE:Pause | ESC:Quit | L:Legend | M:Thoughts | P:Patterns | H:Health"
        text = self.tiny_font.render(inst_text, True, (180, 180, 185))
        self.screen.blit(text, (10, info_y + 35))

        # Status indicators
        status_y = info_y + 55
        status_items = []
        if self.show_legend:
            status_items.append("Legend:ON")
        if self.show_monologue:
            status_items.append("Thoughts:ON")
        if self.show_patterns:
            status_items.append("Patterns:ON")
        if self.show_health_bars:
            status_items.append("Health:ON")

        status_text = " | ".join(status_items)
        text = self.tiny_font.render(status_text, True, (100, 255, 100))
        self.screen.blit(text, (10, status_y))

    def _draw_monologue_panel(self):
        """Draw internal monologue panel showing creature thoughts"""
        panel_x = self.width + 5
        panel_y = 10
        panel_width = self.panel_width - 10
        panel_height = (self.height // 2) - 15

        # Panel background
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surface.fill((*self.colors['monologue_bg'], 240))
        pygame.draw.rect(panel_surface, self.colors['legend_border'],
                        (0, 0, panel_width, panel_height), 2)

        # Title
        title = self.small_font.render("💭 INTERNAL THOUGHTS", True, self.colors['text'])
        panel_surface.blit(title, (10, 10))

        # Get recent reflections
        recent_reflections = self.simulation.reflection_log[-8:]  # Last 8 thoughts

        y_offset = 40
        line_height = 16

        if not recent_reflections:
            no_thoughts = self.tiny_font.render(
                "No internal thoughts yet...",
                True,
                (120, 120, 140)
            )
            panel_surface.blit(no_thoughts, (10, y_offset))
        else:
            for reflection in reversed(recent_reflections):  # Most recent first
                # Creature ID and step
                header = f"[{reflection['creature_id']}] @ step {reflection['step']}"
                header_text = self.tiny_font.render(header, True, (150, 150, 170))
                panel_surface.blit(header_text, (10, y_offset))
                y_offset += line_height

                # Thought text - wrap if too long
                thought = reflection['text']
                max_chars = 50
                if len(thought) > max_chars:
                    # Wrap text
                    words = thought.split()
                    lines = []
                    current_line = ""
                    for word in words:
                        if len(current_line) + len(word) + 1 <= max_chars:
                            current_line += word + " "
                        else:
                            if current_line:
                                lines.append(current_line.strip())
                            current_line = word + " "
                    if current_line:
                        lines.append(current_line.strip())

                    # Draw wrapped lines (max 2 lines per thought)
                    for i, line in enumerate(lines[:2]):
                        thought_text = self.tiny_font.render(
                            line, True, self.colors['monologue_text']
                        )
                        panel_surface.blit(thought_text, (15, y_offset))
                        y_offset += line_height

                    if len(lines) > 2:
                        more = self.tiny_font.render("...", True, (100, 100, 120))
                        panel_surface.blit(more, (15, y_offset - line_height))
                else:
                    thought_text = self.tiny_font.render(
                        thought, True, self.colors['monologue_text']
                    )
                    panel_surface.blit(thought_text, (15, y_offset))
                    y_offset += line_height

                y_offset += 8  # Spacing between thoughts

                # Stop if panel is full
                if y_offset > panel_height - 30:
                    break

        self.screen.blit(panel_surface, (panel_x, panel_y))

    def _draw_pattern_panel(self):
        """Draw detected communication patterns and social dynamics"""
        panel_x = self.width + 5
        panel_y = (self.height // 2) + 5
        panel_width = self.panel_width - 10
        panel_height = (self.height // 2) - 15

        # Panel background
        panel_surface = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        panel_surface.fill((*self.colors['monologue_bg'], 240))
        pygame.draw.rect(panel_surface, self.colors['legend_border'],
                        (0, 0, panel_width, panel_height), 2)

        # Title
        title = self.small_font.render("🎵 COMMUNICATION PATTERNS", True, self.colors['text'])
        panel_surface.blit(title, (10, 10))

        y_offset = 40
        line_height = 16

        # Analyze recent sounds for patterns
        recent_sounds = self.simulation.sound_history[-50:]

        if len(recent_sounds) < 3:
            no_data = self.tiny_font.render(
                "Not enough sound data...",
                True,
                (120, 120, 140)
            )
            panel_surface.blit(no_data, (10, y_offset))
        else:
            # Sound activity
            unique_creatures = set(s['creature_id'] for s in recent_sounds)
            activity_text = f"Active communicators: {len(unique_creatures)}"
            text = self.tiny_font.render(activity_text, True, self.colors['pattern_text'])
            panel_surface.blit(text, (10, y_offset))
            y_offset += line_height + 5

            # Frequency distribution
            low_freq = sum(1 for s in recent_sounds if s['frequency'] < 0.5)
            high_freq = len(recent_sounds) - low_freq
            freq_text = f"Low freq: {low_freq} | High freq: {high_freq}"
            text = self.tiny_font.render(freq_text, True, (180, 200, 255))
            panel_surface.blit(text, (10, y_offset))
            y_offset += line_height + 10

            # Check for rhythmic patterns
            if len(recent_sounds) > 10:
                time_diffs = []
                for i in range(1, min(len(recent_sounds), 20)):
                    time_diffs.append(recent_sounds[i]['step'] - recent_sounds[i-1]['step'])

                if time_diffs:
                    avg_interval = np.mean(time_diffs)
                    std_interval = np.std(time_diffs)

                    rhythm_text = f"Avg interval: {avg_interval:.1f} ± {std_interval:.1f}"
                    text = self.tiny_font.render(rhythm_text, True, (150, 220, 150))
                    panel_surface.blit(text, (10, y_offset))
                    y_offset += line_height

                    # Detect rhythm
                    if std_interval < avg_interval * 0.5 and avg_interval > 0:
                        pattern = self.tiny_font.render(
                            "⚠ RHYTHMIC PATTERN DETECTED!",
                            True,
                            (255, 200, 100)
                        )
                        panel_surface.blit(pattern, (10, y_offset))
                        y_offset += line_height + 5

            y_offset += 10

            # Mood dynamics
            alive_creatures = [c for c in self.simulation.creatures if c['alive']]
            if alive_creatures:
                avg_valence = np.mean([c['brain'].mood_system.valence for c in alive_creatures])
                avg_arousal = np.mean([c['brain'].mood_system.arousal for c in alive_creatures])

                mood_title = self.tiny_font.render("Group Mood:", True, self.colors['text'])
                panel_surface.blit(mood_title, (10, y_offset))
                y_offset += line_height

                valence_text = f"  Valence: {avg_valence:+.2f} "
                valence_text += "😊" if avg_valence > 0.2 else "😐" if avg_valence > -0.2 else "😔"
                text = self.tiny_font.render(valence_text, True, (180, 255, 180))
                panel_surface.blit(text, (10, y_offset))
                y_offset += line_height

                arousal_text = f"  Arousal: {avg_arousal:.2f} "
                arousal_text += "🔥" if avg_arousal > 0.7 else "⚡" if arousal > 0.4 else "💤"
                text = self.tiny_font.render(arousal_text, True, (255, 180, 180))
                panel_surface.blit(text, (10, y_offset))
                y_offset += line_height + 10

                # Individual mood variation
                valences = [c['brain'].mood_system.valence for c in alive_creatures]
                arousals = [c['brain'].mood_system.arousal for c in alive_creatures]

                var_text = f"Mood diversity: {np.std(valences):.2f} val, {np.std(arousals):.2f} arousal"
                text = self.tiny_font.render(var_text, True, (200, 200, 220))
                panel_surface.blit(text, (10, y_offset))
                y_offset += line_height

                if np.std(valences) < 0.1 and np.std(arousals) < 0.1:
                    warning = self.tiny_font.render(
                        "⚠ Low mood variation!",
                        True,
                        (255, 150, 150)
                    )
                    panel_surface.blit(warning, (10, y_offset))

        self.screen.blit(panel_surface, (panel_x, panel_y))

    def _draw_legend(self):
        """Draw color legend/key - now more compact"""
        legend_width = 180
        legend_height = 240
        legend_x = 10
        legend_y = 10

        # Semi-transparent background
        legend_surface = pygame.Surface((legend_width, legend_height), pygame.SRCALPHA)
        legend_surface.fill((*self.colors['legend_bg'], 230))
        pygame.draw.rect(legend_surface, self.colors['legend_border'],
                        (0, 0, legend_width, legend_height), 2)

        # Title
        title = self.small_font.render("COLOR KEY", True, self.colors['text'])
        legend_surface.blit(title, (10, 10))

        # Legend items
        y_offset = 35
        item_height = 22

        legend_items = [
            (self.colors['empty'], "Empty Space"),
            (self.colors['food'], "Food (bright!)"),
            (self.colors['obstacle'], "Obstacle (red)"),
            ((255, 255, 255), "Creature"),
            (self.colors['sound_low'][:3], "Low Sound"),
            (self.colors['sound_high'][:3], "High Sound"),
        ]

        for color, description in legend_items:
            # Color swatch
            swatch_rect = pygame.Rect(10, y_offset, 18, 14)
            pygame.draw.rect(legend_surface, color, swatch_rect)
            pygame.draw.rect(legend_surface, self.colors['legend_border'], swatch_rect, 1)

            # Description
            text = self.tiny_font.render(description, True, self.colors['text'])
            legend_surface.blit(text, (32, y_offset))

            y_offset += item_height

        # Mood examples
        y_offset += 5
        mood_title = self.tiny_font.render("MOOD COLORS:", True, self.colors['text'])
        legend_surface.blit(mood_title, (10, y_offset))
        y_offset += 18

        mood_examples = [
            ((255, 255, 150), "Happy"),
            ((255, 150, 150), "Excited"),
            ((150, 150, 255), "Sad"),
        ]

        for color, description in mood_examples:
            pygame.draw.circle(legend_surface, (255, 255, 255), (18, y_offset + 7), 8)
            pygame.draw.circle(legend_surface, color, (18, y_offset + 7), 6)
            text = self.tiny_font.render(description, True, self.colors['text'])
            legend_surface.blit(text, (32, y_offset))
            y_offset += 18

        self.screen.blit(legend_surface, (legend_x, legend_y))
