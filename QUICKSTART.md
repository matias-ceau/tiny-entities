# Quick Start Guide

## 1. Setup with uv

```bash
# Sync dependencies from lock file
uv sync

# Copy environment file
cp .env.example .env
```

**What happens:** `uv sync` creates a virtual environment (if needed) and installs all dependencies from `uv.lock`. No need to manually activate the environment - use `uv run` to run commands.

## 2. Configure API Keys (Optional)

Edit `.env` and add any API keys you have:
- `OPENROUTER_API_KEY` - For LLM-based action selection
- `ANTHROPIC_API_KEY` - For emergence analysis
- `HUGGINGFACE_API_KEY` - For free models

The simulation works without API keys using rule-based behaviors.

## 3. Run the Simulation

### Basic run:
```bash
uv run python -m src.simulation.main_loop
```

### With visualization (requires pygame):
```bash
uv run python examples/basic_simulation.py --visualize
```

### Custom parameters:
```bash
uv run python examples/basic_simulation.py --creatures 10 --steps 5000
```

### Generate analysis plots:
```bash
uv run python examples/analysis_with_plots.py --creatures 8 --steps 2000
```

This creates detailed matplotlib plots showing mood evolution, trajectories, and patterns.

## 4. What to Expect

- Creatures start with random positions and neutral mood
- They explore, eat food, and make sounds
- Mood emerges from reward prediction errors
- Watch for:
  - Coordinated sound patterns (communication)
  - Social clustering (gathering together)
  - Stable "personalities" (consistent mood states)
  - Collective behaviors (synchronized actions)

**Visual Guide**: See [docs/VISUALIZATION.md](docs/VISUALIZATION.md) for detailed explanation of what you're seeing.

## 5. Controls (Visualization Mode)

- **SPACE**: Pause/Resume
- **ESC**: Quit

### Understanding the Display

- **Colored circles** = Creatures (color shows mood)
- **Green squares** = Food
- **Gray squares** = Obstacles  
- **Blue/red halos** = Sound waves
- **Bottom panel** = Statistics

See the [Visualization Guide](docs/VISUALIZATION.md) for complete details.

## 6. Understanding the Output

- **Step counter**: Current simulation step
- **Alive creatures**: How many are still active
- **Sound activity**: Recent sound events
- **Mood summary**: Average emotional state

## Troubleshooting

If you get import errors:
```bash
# Make sure you're in the project root
cd /path/to/tiny-entities

# Resync dependencies
uv sync
```

If pygame doesn't work:
```bash
# Install system dependencies first
# Ubuntu/Debian:
sudo apt-get install python3-dev python3-pygame

# Then add pygame (this updates pyproject.toml and uv.lock)
uv add pygame
```

### Alternative: Using pip instead of uv

If you prefer to use pip:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
python examples/basic_simulation.py --visualize
```