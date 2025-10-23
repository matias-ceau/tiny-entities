# Tiny Entities

🧬 Artificial life simulation with emergent mood-based cognition and social behaviors.

![Simulation Example](docs/images/simulation_example.png)

**Status**: ✅ **Functional** - Simulations run successfully with graphical visualization

## Features

- 🎭 **Emergent Mood System** - Creatures develop emotional states from reward prediction errors
- 🗺️ **2D Grid World** - Dynamic environment with food, obstacles, and sound propagation  
- 🎨 **Real-time Visualization** - pygame-based rendering with mood-colored creatures
- 🔊 **Sound Communication** - Creatures emit and respond to sounds
- 📊 **Analysis Tools** - Track emergence patterns and collective behaviors
- 🧪 **Headless Mode** - Generate snapshots without display for testing/docs

## Quick Start

### Setup

```bash
# Using pip
pip install -e ".[dev]"
cp .env.example .env

# Or using uv (recommended - faster and more reliable)
uv sync --all-extras  # Use --all-extras to include dev dependencies
cp .env.example .env
```

### API Configuration (Optional)

The simulation can use LLM models for more sophisticated creature behaviors and emergence analysis. The default configuration uses **OpenRouter** with up-to-date models:

- **Action Model**: `meta-llama/llama-3.1-8b-instruct:free` (free tier for creature actions)
- **Analysis Model**: `anthropic/claude-3.5-sonnet` (for emergence analysis)

To enable LLM features, add your OpenRouter API key to `.env`:
```bash
OPENROUTER_API_KEY=your_openrouter_key_here
```

Get your API key at [OpenRouter](https://openrouter.ai/). The free tier models allow you to experiment without cost!

You can customize models in `.env` by setting:
```bash
DEFAULT_FREE_MODEL=meta-llama/llama-3.1-8b-instruct:free
DEFAULT_ANALYSIS_MODEL=anthropic/claude-3.5-sonnet
MAX_DAILY_COST_EUR=2.0
```

### Quick Demo

Run the comprehensive demo to see all features:
```bash
# With uv (recommended)
uv run python demo.py

# Or if you used pip
python demo.py
```

This demonstrates console mode, visualization, and analysis tools in one go.

### Run

Basic simulation (console output):
```bash
# With uv (recommended)
uv run python examples/basic_simulation.py --creatures 8 --steps 5000

# Or if you used pip
python examples/basic_simulation.py --creatures 8 --steps 5000
```

With visualization (requires display):
```bash
# With uv (recommended)
uv run python examples/basic_simulation.py --visualize --creatures 8

# Or if you used pip
python examples/basic_simulation.py --visualize --creatures 8
```

Headless mode (generates PNG snapshots):
```bash
# With uv (recommended)
uv run python examples/headless_visualization.py --creatures 10 --steps 1000

# Or if you used pip
python examples/headless_visualization.py --creatures 10 --steps 1000
```

See [QUICKSTART.md](QUICKSTART.md) for more details and [ROADMAP.md](ROADMAP.md) for development plans.
