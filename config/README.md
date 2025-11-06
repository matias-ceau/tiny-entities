# Configuration Files

This directory contains YAML configuration files for Tiny Entities simulations.

## Available Configurations

### `default.yaml`
Standard configuration with balanced parameters. Good starting point for most experiments.
- World: 100x100
- Creatures: 10
- Steps: 10,000

### `small.yaml`
Quick testing configuration with smaller world and fewer steps.
- World: 50x50
- Creatures: 5
- Steps: 2,000
- Purpose: Fast iteration during development

### `large.yaml`
Large-scale simulation for comprehensive experiments.
- World: 200x200
- Creatures: 50
- Steps: 20,000
- Purpose: Long-running experiments with complex emergent behavior

### `experiment_social.yaml`
Optimized for studying social behavior and sound communication.
- Enhanced social rewards
- More creatures (20)
- Slower sound decay
- Purpose: Research on collective behavior

## Usage

### Load a configuration in Python:

```python
from src.config.config_schema import SimulationConfig

# Load from file
config = SimulationConfig.from_yaml(Path("config/default.yaml"))

# Or use defaults
config = SimulationConfig.default()

# Access configuration values
print(config.world.width)
print(config.creatures.initial_count)
```

### Command-line usage:

```bash
# Use a specific configuration
python examples/basic_simulation.py --config config/small.yaml

# Override specific parameters
python examples/basic_simulation.py --config config/default.yaml --creatures 20 --steps 5000
```

## Creating Custom Configurations

1. Copy one of the existing files
2. Modify the parameters you want to change
3. Save with a descriptive name
4. Use with `--config your_config.yaml`

## Configuration Structure

```yaml
world:          # Environment settings
  width: 100
  height: 100
  food_spawn_rate: 0.1
  # ...

creatures:      # Creature behavior
  initial_count: 10
  starting_health: 100.0
  # ...

mood:           # Mood system parameters
  fast_learning_rate: 0.1
  slow_learning_rate: 0.01
  # ...

actions:        # Action selection
  acceptance_rate: 0.9
  llm_action_probability: 0.2

rewards:        # Reward structure
  surprise_multiplier: 0.5
  food_reward: 1.0
  # ...

analysis:       # Analysis settings
  analyze_every: 500
  sound_history_window: 50

# Top-level simulation settings
max_steps: 10000
random_seed: null  # or integer for reproducibility
log_level: INFO
```

## Parameter Guidelines

### World Size
- Small (50x50): Fast, good for testing
- Medium (100x100): Default, balanced
- Large (200x200+): Emergent patterns, slower

### Creature Count
- Few (5-10): Individual behavior tracking
- Medium (10-20): Group dynamics
- Many (30-50+): Collective phenomena

### Learning Rates
- Fast (0.05-0.15): Quick adaptation
- Medium (0.01-0.05): Balanced
- Slow (0.001-0.01): Gradual change

### Random Seeds
- `null`: Different each time
- Integer (e.g., 42): Reproducible results

## Validation

All configurations are validated when loaded. Invalid values will raise descriptive errors:

```python
try:
    config = SimulationConfig.from_yaml(path)
except ValueError as e:
    print(f"Invalid configuration: {e}")
```

## Tips

1. Start with `small.yaml` for quick iteration
2. Use `default.yaml` for standard experiments
3. Create experiment-specific configs for research
4. Set `random_seed` for reproducibility
5. Use `log_level: DEBUG` for troubleshooting
