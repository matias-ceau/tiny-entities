# Quick Start Guide

## 1. Setup with uv

```bash
# Sync dependencies from lock file (production dependencies only)
uv sync

# OR sync with dev dependencies for development
uv sync --all-extras

# Copy environment file
cp .env.example .env
```

**What happens:** `uv sync` creates a virtual environment (if needed) and installs all dependencies from `uv.lock`. No need to manually activate the environment - use `uv run` to run commands.

## 2. Configure API Keys (Optional)

Edit `.env` and add your API keys for LLM-enhanced features:

**Recommended**: Use **OpenRouter** (single API key for multiple models):
```bash
OPENROUTER_API_KEY=your_key_here
```
Get your key at [OpenRouter](https://openrouter.ai/)

**Default Models** (automatically used via OpenRouter):
- Action model: `meta-llama/llama-3.1-8b-instruct:free` (free tier)
- Analysis model: `anthropic/claude-3.5-sonnet` (latest Claude)

**Alternative providers**:
- `ANTHROPIC_API_KEY` - Direct Anthropic API
- `HUGGINGFACE_API_KEY` - HuggingFace models

The simulation works without API keys using rule-based behaviors. With OpenRouter and free tier models, you can experiment with LLM features at no cost!

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