# Tiny Entities

🧬 Artificial life simulation with emergent mood-based cognition and social behaviors.

![Simulation Example](docs/images/simulation_example.png)

**Status**: ✅ **Functional** - Simulations run successfully with graphical visualization

## Features

- 🎭 **Emergent Mood System** - Creatures develop emotional states from reward prediction errors
- 🧠 **LLM-assisted cognition** - Optional OpenRouter models steer action selection, generate self-reflection journals, and narrate emergence reports
- 🗺️ **2D Grid World** - Dynamic environment with food, obstacles, and sound propagation
- 🎨 **Real-time Visualization** - pygame-based rendering with mood-colored creatures
- 🔊 **Procedural Sound Synthesis** - Every vocalization now generates a mood-infused audio waveform for analysis or export
- 📊 **Analysis Tools** - Track emergence patterns and collective behaviors, including AI-written summaries when LLMs are enabled
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

This demonstrates console mode, visualization, and analysis tools in one go. When LLM credentials are present the demo will also showcase reflective journaling and AI-generated emergence summaries.

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

## Running Tests

Ensure the development dependencies (including scientific libraries such as `numpy`) are installed before executing the test
suite:

```bash
uv sync --all-extras
uv run pytest
```

`uv sync` provisions the shared virtual environment, so `uv run` will automatically reuse the resolved packages when executing
`pytest`.

## Repository Layout

- `src/` – Primary simulation engine and modules
  - `tiny_entities/` – Package namespace
  - `simulation/` – Main loop, LLM-assisted analysis hooks, orchestration utilities
  - `creatures/` – Cognitive systems, mood regulation, and action policies
  - `world/` – Environment models, physics, and procedural audio synthesizer
- `examples/` – Runnable demonstrations and legacy prototypes (see `examples/legacy/little_social_dreamers`)
- `docs/` – Extended documentation and design notes
- `tests/` – Automated unit tests (including coverage for the new sound synthesizer)

See [QUICKSTART.md](QUICKSTART.md) for more details and [ROADMAP.md](ROADMAP.md) for development plans.
