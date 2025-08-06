# Quick Start Guide

## 1. Setup with uv

```bash
# Create and activate virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install the package
uv pip install -e ".[dev]"

# Copy environment file
cp .env.example .env
```

## 2. Configure API Keys (Optional)

Edit `.env` and add any API keys you have:
- `OPENROUTER_API_KEY` - For LLM-based action selection
- `ANTHROPIC_API_KEY` - For emergence analysis
- `HUGGINGFACE_API_KEY` - For free models

The simulation works without API keys using rule-based behaviors.

## 3. Run the Simulation

### Basic run:
```bash
python -m src.simulation.main_loop
```

### With visualization (requires pygame):
```bash
python examples/basic_simulation.py --visualize
```

### Custom parameters:
```bash
python examples/basic_simulation.py --creatures 10 --steps 5000
```

## 4. What to Expect

- Creatures start with random positions
- They explore, eat food, make sounds
- Mood emerges from reward prediction errors
- Watch for:
  - Coordinated sound patterns
  - Social clustering
  - Stable "personalities" (mood states)
  - Collective behaviors

## 5. Controls (Visualization Mode)

- **SPACE**: Pause/Resume
- **ESC**: Quit

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

# Activate the environment
source .venv/bin/activate

# Reinstall
uv pip install -e ".[dev]"
```

If pygame doesn't work:
```bash
# Install system dependencies first
# Ubuntu/Debian:
sudo apt-get install python3-dev python3-pygame

# Then reinstall
uv pip install pygame
```