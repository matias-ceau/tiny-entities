# Tiny Entities

🧬 Artificial life simulation with emergent mood-based cognition and social behaviors.

![Simulation Visualization](docs/images/visualization_with_legend.png)

**Status**: ✅ **Functional** - Simulations run successfully with graphical visualization

## Features

- 🎭 **Emergent Mood System** - Creatures develop emotional states from reward prediction errors
- 🧠 **LLM-assisted Cognition** - Optional OpenRouter integration with free tier models for action selection, self-reflection journals, and emergence analysis
- 💰 **Built-in Cost Tracking** - Automatic pricing calculations and daily spending limits protect your budget
- 🗺️ **2D Grid World** - Dynamic environment with food, obstacles, and sound propagation
- 🎨 **Real-time Visualization** - pygame-based rendering with mood-colored creatures
- 🔊 **Procedural Sound Synthesis** - Every vocalization generates a mood-infused audio waveform for analysis or export
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

The simulation can use LLM models for more sophisticated creature behaviors and emergence analysis. 

#### Why OpenRouter?

We recommend **OpenRouter** as the default API provider because it offers:
- **Single API key** for accessing multiple model providers (Anthropic, Meta, OpenAI, etc.)
- **Free tier models** like Llama 3.1 8B for cost-free experimentation
- **Latest models** including Claude 3.5 Sonnet, the most capable Claude model
- **Transparent pricing** with automatic cost tracking in EUR
- **Automatic fallbacks** and intelligent routing

#### Default Models

- **Action Model**: `meta-llama/llama-3.1-8b-instruct:free` - Free tier model for creature decision-making
- **Analysis Model**: `anthropic/claude-3.5-sonnet` - Premium model for sophisticated emergence analysis

#### Setup

1. Get your free API key at [OpenRouter](https://openrouter.ai/)
2. Add it to your `.env` file:
```bash
OPENROUTER_API_KEY=your_openrouter_key_here
```

The free tier Llama model means you can run simulations with LLM features at **zero cost**!

#### Customization

You can customize models and set spending limits in `.env`:
```bash
DEFAULT_FREE_MODEL=meta-llama/llama-3.1-8b-instruct:free
DEFAULT_ANALYSIS_MODEL=anthropic/claude-3.5-sonnet
MAX_DAILY_COST_EUR=2.0  # Built-in cost protection
```

The system includes automatic cost tracking - see `src/config/model_pricing.py` for pricing data on 13+ popular models.

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
