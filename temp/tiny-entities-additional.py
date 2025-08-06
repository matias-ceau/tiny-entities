# Additional Project Files

## src/creatures/action_selection.py
```python
import numpy as np
from typing import Dict, List
import aiohttp
import json
from ..config.api_config import APIConfig

class MoodInfluencedActionSelector:
    """Action selection influenced by emergent mood"""
    
    def __init__(self):
        self.base_actions = [
            'move_north', 'move_south', 'move_east', 'move_west',
            'stay', 'eat', 'make_sound_low', 'make_sound_high',
            'listen', 'explore'
        ]
        self.api_config = APIConfig()
        self.use_llm = bool(self.api_config.get_action_model())
    
    def select_action(self, brain, perception: Dict) -> str:
        """Select action based on mood-biased preferences"""
        
        # Get mood-based biases
        action_biases = brain.get_action_bias()
        
        # Add situational modifiers
        if perception.get('food_count', 0) > 0 and brain.health < 70:
            # Move toward food when needed
            action_biases['eat'] = 0.8
            action_biases['move_north'] = 0.4  # Simplified - would need direction
        
        # If very low energy, bias toward staying
        if brain.energy < 20:
            action_biases['stay'] = 0.7
        
        # If LLM available and have tokens, use it occasionally
        if self.use_llm and brain.action_tokens > 5 and np.random.random() < 0.2:
            return self._llm_action_selection(brain, perception, action_biases)
        
        # Otherwise use probabilistic selection
        return self._probabilistic_selection(action_biases)
    
    def _probabilistic_selection(self, action_biases: Dict[str, float]) -> str:
        """Select action probabilistically based on biases"""
        # Convert to action probabilities
        action_probs = {}
        for action in self.base_actions:
            base_prob = 1.0 / len(self.base_actions)
            bias = action_biases.get(action, 0.0)
            action_probs[action] = max(0.01, base_prob + bias)
        
        # Normalize
        total = sum(action_probs.values())
        action_probs = {a: p/total for a, p in action_probs.items()}
        
        # Sample action
        actions = list(action_probs.keys())
        probs = list(action_probs.values())
        
        return np.random.choice(actions, p=probs)
    
    def _llm_action_selection(self, brain, perception: Dict, 
                            action_biases: Dict[str, float]) -> str:
        """Use LLM for action selection (blocking for simplicity)"""
        # For now, fall back to probabilistic
        # In production, would make actual API call
        return self._probabilistic_selection(action_biases)


## src/world/non_deterministic.py
```python
import numpy as np
from typing import Dict, Tuple
from .physics import SimpleWorld

class NonDeterministicWorldModel:
    """World model that can accept/reject actions and update state"""
    
    def __init__(self, acceptance_rate: float = 0.9):
        self.acceptance_rate = acceptance_rate
        self.world = SimpleWorld()
        
        # Track creature positions
        self.creature_positions = {}
        
    def propose_action(self, creature_id: str, action: str, 
                      current_pos: Tuple[int, int]) -> Dict:
        """Propose action and get world's response"""
        
        # Update creature tracking
        self.creature_positions[creature_id] = current_pos
        
        # World decides whether to accept action
        accepted = np.random.random() < self.acceptance_rate
        
        if not accepted:
            return {
                'accepted': False,
                'new_position': current_pos,
                'effect': 'action_blocked',
                'message': 'World rejected action'
            }
        
        # Execute action if accepted
        result = self._execute_action(creature_id, action, current_pos)
        result['accepted'] = True
        
        return result
    
    def _execute_action(self, creature_id: str, action: str, 
                       pos: Tuple[int, int]) -> Dict:
        """Execute accepted action and update world"""
        x, y = pos
        new_x, new_y = x, y
        effect = 'none'
        extras = {}
        
        # Movement actions
        if action == 'move_north' and y > 0:
            new_y = y - 1
        elif action == 'move_south' and y < self.world.height - 1:
            new_y = y + 1
        elif action == 'move_east' and x < self.world.width - 1:
            new_x = x + 1
        elif action == 'move_west' and x > 0:
            new_x = x - 1
        elif action == 'explore':
            # Random movement
            direction = np.random.choice(['north', 'south', 'east', 'west'])
            if direction == 'north' and y > 0:
                new_y = y - 1
            elif direction == 'south' and y < self.world.height - 1:
                new_y = y + 1
            elif direction == 'east' and x < self.world.width - 1:
                new_x = x + 1
            elif direction == 'west' and x > 0:
                new_x = x - 1
        
        # Check if movement is valid (not into obstacle or another creature)
        if (new_x, new_y) != (x, y):
            if self.world.grid[new_y, new_x] == 2:  # Obstacle
                new_x, new_y = x, y  # Stay in place
                effect = 'blocked_by_obstacle'
            elif self.world.grid[new_y, new_x] == 1:  # Food
                self.world.grid[new_y, new_x] = 0  # Eat food
                effect = 'found_food'
            
            # Check for other creatures
            for other_id, other_pos in self.creature_positions.items():
                if other_id != creature_id and other_pos == (new_x, new_y):
                    new_x, new_y = x, y  # Can't move into another creature
                    effect = 'blocked_by_creature'
                    extras['near_creatures'] = 1
                    break
        
        # Eating action
        if action == 'eat' and self.world.grid[y, x] == 1:
            self.world.grid[y, x] = 0
            effect = 'found_food'
        
        # Sound actions
        if 'sound' in action:
            freq = 0.3 if 'low' in action else 0.7
            self.world.update_sound(x, y, freq, 0.8)
            effect = 'made_sound'
            
            # Check if other creatures nearby to respond
            nearby_creatures = 0
            for other_id, other_pos in self.creature_positions.items():
                if other_id != creature_id:
                    dist = abs(other_pos[0] - x) + abs(other_pos[1] - y)
                    if dist <= 5:
                        nearby_creatures += 1
            
            if nearby_creatures > 0:
                extras['sound_responded_to'] = np.random.random() < 0.3
        
        # Count nearby creatures for social rewards
        nearby_creatures = 0
        for other_id, other_pos in self.creature_positions.items():
            if other_id != creature_id:
                dist = abs(other_pos[0] - new_x) + abs(other_pos[1] - new_y)
                if dist <= 3:
                    nearby_creatures += 1
        
        extras['near_creatures'] = nearby_creatures
        
        # Update creature position tracking
        self.creature_positions[creature_id] = (new_x, new_y)
        
        return {
            'new_position': (new_x, new_y),
            'effect': effect,
            'world_state': self.world.get_local_view(new_x, new_y),
            **extras
        }


## src/emergence/music_analyzer.py
```python
import numpy as np
from typing import List, Dict
import json
from ..config.api_config import APIConfig

class MusicEmergenceAnalyzer:
    """Use sophisticated AI to judge emergent music quality"""
    
    def __init__(self):
        self.api_config = APIConfig()
        self.model = self.api_config.get_analysis_model()
        
    async def analyze_collective_music(self, sound_history: List[Dict]) -> Dict:
        """Analyze if creatures are making music together"""
        
        if not self.model:
            # Fallback to simple analysis
            return self._simple_analysis(sound_history)
        
        # Convert sound data to analysis prompt
        sound_summary = self._summarize_sounds(sound_history)
        
        prompt = f"""
Analyze this sequence of sounds made by artificial creatures:

{sound_summary}

Evaluate:
1. Is there evidence of musical structure? (rhythm, harmony, patterns)
2. Are creatures coordinating their sounds?
3. Is entropy/randomness decreasing over time?
4. Rate musical quality (0-10)
5. Detect any emergent musical behaviors

Provide a JSON response with these fields:
- music_score (0-10)
- coordination_detected (true/false)
- rhythmic_patterns (description)
- harmonic_relationships (description)
- entropy_trend (increasing/stable/decreasing)
- emergent_behaviors (list of observed behaviors)

JSON Response:"""
        
        # In production, would make actual API call
        # For now, return mock analysis
        return {
            'music_score': np.random.randint(3, 8),
            'coordination_detected': len(sound_history) > 20 and np.random.random() > 0.5,
            'entropy_trend': self._calculate_entropy_trend(sound_history),
            'full_analysis': 'Mock analysis - API not connected'
        }
    
    def _summarize_sounds(self, sound_history: List[Dict]) -> str:
        """Convert sound data to text summary"""
        summary = []
        
        # Group by time windows
        time_window = 10
        current_window = []
        current_step = None
        
        for event in sound_history:
            if current_step is None:
                current_step = event['step']
            
            if event['step'] - current_step < time_window:
                current_window.append(event)
            else:
                # Summarize window
                if current_window:
                    summary.append(self._summarize_window(current_window, current_step))
                current_window = [event]
                current_step = event['step']
        
        # Don't forget last window
        if current_window:
            summary.append(self._summarize_window(current_window, current_step))
        
        return '\n'.join(summary[-10:])  # Last 10 windows
    
    def _summarize_window(self, events: List[Dict], start_step: int) -> str:
        """Summarize events in a time window"""
        creatures = set(e['creature_id'] for e in events)
        frequencies = [e['frequency'] for e in events]
        avg_freq = np.mean(frequencies) if frequencies else 0
        
        # Check for patterns
        low_sounds = sum(1 for e in events if e['frequency'] < 0.5)
        high_sounds = sum(1 for e in events if e['frequency'] >= 0.5)
        
        # Get average mood
        avg_valence = np.mean([e.get('mood_valence', 0) for e in events])
        avg_arousal = np.mean([e.get('mood_arousal', 0.5) for e in events])
        
        return (f"Step {start_step}-{start_step+10}: "
                f"{len(creatures)} creatures made {len(events)} sounds "
                f"(low:{low_sounds}, high:{high_sounds}, avg_freq:{avg_freq:.2f}, "
                f"mood: valence={avg_valence:.2f}, arousal={avg_arousal:.2f})")
    
    def _calculate_entropy_trend(self, sound_history: List[Dict]) -> str:
        """Calculate if entropy is increasing or decreasing"""
        if len(sound_history) < 20:
            return "insufficient_data"
        
        # Calculate entropy for first and last quarter
        quarter_size = len(sound_history) // 4
        
        first_quarter = sound_history[:quarter_size]
        last_quarter = sound_history[-quarter_size:]
        
        first_entropy = self._calculate_entropy(first_quarter)
        last_entropy = self._calculate_entropy(last_quarter)
        
        if last_entropy < first_entropy * 0.8:
            return "decreasing"
        elif last_entropy > first_entropy * 1.2:
            return "increasing"
        else:
            return "stable"
    
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
    
    def _simple_analysis(self, sound_history: List[Dict]) -> Dict:
        """Simple analysis without API"""
        return {
            'music_score': len(sound_history) / 10,  # Simple metric
            'coordination_detected': self._detect_simple_coordination(sound_history),
            'entropy_trend': self._calculate_entropy_trend(sound_history),
            'full_analysis': 'Simple analysis (no API configured)'
        }
    
    def _detect_simple_coordination(self, sound_history: List[Dict]) -> bool:
        """Simple coordination detection"""
        if len(sound_history) < 10:
            return False
        
        # Check if creatures respond to each other
        response_count = 0
        for i in range(1, len(sound_history)):
            curr = sound_history[i]
            prev = sound_history[i-1]
            
            # Different creatures, close in time
            if (curr['creature_id'] != prev['creature_id'] and 
                curr['step'] - prev['step'] <= 3):
                # Similar frequency = possible response
                if abs(curr['frequency'] - prev['frequency']) < 0.2:
                    response_count += 1
        
        return response_count > len(sound_history) * 0.2


## src/simulation/visualization.py
```python
import pygame
import numpy as np
from typing import Optional
import asyncio

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
        
        while running and self.simulation.step_count < self.simulation.max_steps:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # Pause/unpause
                        await self._pause_menu()
            
            # Run simulation step
            await self.simulation.simulation_step()
            
            # Update visualization
            self._draw_world()
            self._draw_info()
            
            pygame.display.flip()
            self.clock.tick(30)  # 30 FPS
            
            # Periodic analysis
            if self.simulation.step_count % self.simulation.analyze_every == 0:
                await self.simulation.analyze_emergence()
        
        pygame.quit()
    
    def _draw_world(self):
        """Draw the world grid"""
        self.screen.fill((0, 0, 0))
        
        world = self.simulation.world_model.world
        
        # Draw grid cells
        for y in range(world.height):
            for x in range(world.width):
                cell_type = world.grid[y, x]
                
                # Base color
                if cell_type == 0:
                    color = self.colors['empty']
                elif cell_type == 1:
                    color = self.colors['food']
                elif cell_type == 2:
                    color = self.colors['obstacle']
                else:
                    color = self.colors['empty']
                
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
                if amplitude > 0.1:
                    frequency = world.sound_grid[y, x, 0]
                    if frequency < 0.5:
                        color = (*self.colors['sound_low'][:3], int(amplitude * 100))
                    else:
                        color = (*self.colors['sound_high'][:3], int(amplitude * 100))
                    
                    # Draw sound as circle
                    center = (
                        x * self.cell_width + self.cell_width // 2,
                        y * self.cell_height + self.cell_height // 2
                    )
                    radius = int(amplitude * self.cell_width * 2)
                    pygame.draw.circle(sound_surface, color, center, radius)
        
        self.screen.blit(sound_surface, (0, 0))
        
        # Draw creatures
        for creature in self.simulation.creatures:
            if creature['alive']:
                x, y = creature['position']
                
                # Color based on mood
                mood = creature['brain'].mood_system
                base_color = np.array(self.colors['creature'])
                
                # Valence affects red/green
                if mood.valence > 0:
                    base_color[1] = min(255, base_color[1] + int(mood.valence * 100))
                else:
                    base_color[0] = min(255, base_color[0] + int(-mood.valence * 100))
                
                # Arousal affects brightness
                brightness = 0.5 + mood.arousal * 0.5
                color = tuple(int(c * brightness) for c in base_color)
                
                # Draw creature
                center = (
                    x * self.cell_width + self.cell_width // 2,
                    y * self.cell_height + self.cell_height // 2
                )
                pygame.draw.circle(self.screen, color, center, self.cell_width // 2)
                
                # Draw ID
                text = self.font.render(creature['id'][-1], True, (255, 255, 255))
                text_rect = text.get_rect(center=center)
                self.screen.blit(text, text_rect)
    
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
    
    async def _pause_menu(self):
        """Simple pause menu"""
        paused = True
        while paused:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        paused = False
            
            # Draw pause overlay
            overlay = pygame.Surface((self.width, self.height + 100))
            overlay.set_alpha(128)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))
            
            # Pause text
            pause_text = self.font.render("PAUSED - Press SPACE to continue", 
                                        True, (255, 255, 255))
            text_rect = pause_text.get_rect(center=(self.width//2, self.height//2))
            self.screen.blit(pause_text, text_rect)
            
            pygame.display.flip()
            await asyncio.sleep(0.1)  # Prevent blocking
```
