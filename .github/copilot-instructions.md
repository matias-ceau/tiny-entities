# GitHub Copilot Instructions for Tiny Entities

## Project Overview

Tiny Entities is an artificial life simulation featuring emergent mood-based cognition and social behaviors. Creatures inhabit a 2D grid world where they develop emotional states from reward prediction errors, interact through sound, and can optionally use LLM-assisted cognition for sophisticated decision-making.

**Status**: ✅ Functional - Simulations run successfully with graphical visualization

## Technology Stack

### Core Technologies
- **Language**: Python 3.9+
- **Package Manager**: `uv` (recommended) or `pip`
- **Key Dependencies**:
  - `numpy` - Numerical computations and array operations
  - `pygame` - Real-time visualization and rendering
  - `matplotlib` - Analysis plots and data visualization
  - `scipy` - Scientific computing and signal processing
  - `pandas` - Data analysis and manipulation
  - `rich` - Enhanced terminal output
  - `python-dotenv` - Environment configuration
  - `aiohttp` - Async HTTP client for API calls

### AI/LLM Integration
- **OpenRouter API** (recommended) - Single API key for multiple LLM providers
- **Anthropic** - Direct Claude API access
- **OpenAI** - GPT models support
- **HuggingFace** - Open source model access
- **Default Models**:
  - Action selection: `meta-llama/llama-3.1-8b-instruct:free` (free tier)
  - Emergence analysis: `anthropic/claude-3.5-sonnet`

## Repository Structure

```
tiny-entities/
├── src/                          # Main source code
│   ├── config/                   # Configuration system, API clients, logging
│   ├── creatures/                # Cognitive systems, mood regulation, action policies
│   ├── simulation/               # Main loop, orchestration, LLM-assisted analysis
│   ├── world/                    # Environment models, physics, sound synthesis
│   ├── emergence/                # Pattern detection and analysis tools
│   └── tiny_entities/            # Package namespace
├── config/                       # YAML configuration presets
│   ├── default.yaml              # Standard balanced configuration
│   ├── small.yaml                # Quick testing (50x50, 5 creatures)
│   ├── large.yaml                # Large-scale (200x200, 50 creatures)
│   └── experiment_social.yaml    # Social behavior research optimized
├── examples/                     # Runnable demonstrations
│   ├── basic_simulation.py       # Main entry point with CLI
│   └── headless_visualization.py # PNG snapshot generation
├── tests/                        # Automated unit tests
├── docs/                         # Extended documentation
└── demo.py                       # Comprehensive feature demonstration
```

## Development Setup

### Installation

**Recommended (using uv)**:
```bash
uv sync --all-extras  # Installs all dependencies including dev tools
cp .env.example .env
```

**Alternative (using pip)**:
```bash
pip install -e ".[dev]"
cp .env.example .env
```

### Environment Configuration

Create a `.env` file from `.env.example`:
```bash
# Optional: LLM features (free tier available)
OPENROUTER_API_KEY=your_key_here
DEFAULT_FREE_MODEL=meta-llama/llama-3.1-8b-instruct:free
DEFAULT_ANALYSIS_MODEL=anthropic/claude-3.5-sonnet
MAX_DAILY_COST_EUR=2.0
```

**Note**: The simulation works without API keys using rule-based behaviors.

## Running the Project

### Basic Simulation
```bash
# Console output only
uv run python examples/basic_simulation.py --creatures 8 --steps 5000

# With visualization (requires display)
uv run python examples/basic_simulation.py --visualize --creatures 8

# Using configuration preset
uv run python examples/basic_simulation.py --config config/small.yaml
```

### Testing
```bash
uv sync --all-extras
uv run pytest
```

### Demonstration
```bash
uv run python demo.py  # Showcases all features
```

## Code Style and Conventions

### Python Style
- Follow PEP 8 guidelines
- Use type hints where appropriate
- Keep functions focused and single-purpose
- Document complex algorithms and mood system logic

### Code Organization
- **Separation of Concerns**: Keep world physics, creature cognition, and simulation orchestration separate
- **Configuration**: Use YAML configs in `config/` for experiments, not hardcoded values
- **Logging**: Use the configured logging system (`src/config/logging_config.py`), not print statements
- **Error Handling**: Implement graceful fallbacks, especially for API calls and file I/O

### Naming Conventions
- Classes: `PascalCase` (e.g., `CreatureCognition`, `WorldState`)
- Functions/methods: `snake_case` (e.g., `calculate_mood`, `spawn_food`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `MAX_HEALTH`, `FOOD_SPAWN_RATE`)
- Private methods: `_leading_underscore` (e.g., `_update_internal_state`)

### Testing
- Unit tests in `tests/` directory
- Test file naming: `test_<module>.py`
- Use pytest fixtures for common setup
- Mock external API calls in tests
- Test edge cases for mood calculations and reward prediction

## Key Concepts

### Mood System
- Creatures develop emotional states from **reward prediction errors**
- Fast and slow learning rates control mood adaptation
- Mood influences action selection and social behavior
- Color-coded in visualization (blue=calm, red=excited)

### Sound System
- Creatures vocalize and perceive sounds in the environment
- Sound has radius and decay over time
- Procedural audio synthesis generates mood-infused waveforms
- Foundation for emergent communication patterns

### Action Selection
- Rule-based (default): Deterministic based on state and mood
- LLM-assisted (optional): Context-aware decisions from language models
- Configurable acceptance rate balances exploration/exploitation

### Configuration System
- YAML-based configuration validation (`src/config/config_schema.py`)
- Four presets: default, small, large, experiment_social
- Override via CLI arguments or custom YAML files
- See `config/README.md` for parameter guidelines

## Important Files to Know

### Entry Points
- `examples/basic_simulation.py` - Main CLI for running simulations
- `examples/headless_visualization.py` - Generates PNG snapshots without display
- `demo.py` - Feature demonstration script

### Core Systems
- `src/simulation/main_loop.py` - Simulation orchestration
- `src/creatures/cognition.py` - Creature decision-making
- `src/creatures/mood.py` - Mood system implementation
- `src/world/state.py` - Environment physics and state
- `src/world/sound_engine.py` - Procedural audio synthesis

### Configuration
- `src/config/config_schema.py` - Configuration validation and loading
- `src/config/logging_config.py` - Logging setup
- `src/config/model_pricing.py` - LLM cost tracking
- `config/*.yaml` - Simulation presets

### Testing
- `tests/test_creatures.py` - Creature behavior tests
- `tests/test_world.py` - World physics tests
- `tests/test_config.py` - Configuration system tests

## Common Tasks

### Adding a New Feature
1. Determine which module it belongs to (creatures, world, simulation)
2. Add configuration parameters to `config_schema.py` if needed
3. Implement the feature with proper error handling
4. Add unit tests in `tests/`
5. Update relevant YAML configs if it affects presets
6. Document in appropriate `docs/` file

### Modifying Mood System
- Core logic in `src/creatures/mood.py`
- Reward calculations in `src/creatures/rewards.py`
- Test thoroughly - mood affects entire simulation behavior
- Update configuration schema if adding parameters

### Adding LLM Integration
- Use API clients in `src/config/` (openrouter_client.py, etc.)
- Implement cost tracking (see `model_pricing.py`)
- Add graceful fallbacks for API failures
- Test with and without API keys
- Update `.env.example` with new environment variables

### Updating Documentation
- User-facing: Update `README.md` and `QUICKSTART.md`
- Technical details: Use `docs/` directory
- Configuration changes: Update `config/README.md`
- Keep code comments minimal and focused on "why", not "what"

## Build and Deployment

### Dependencies
- Use `uv add <package>` to add new dependencies (updates `pyproject.toml` and `uv.lock`)
- Or manually edit `pyproject.toml` and run `uv sync`
- Separate dev dependencies in `[project.optional-dependencies.dev]`

### Git Workflow
- `.gitignore` excludes: `__pycache__/`, `.venv/`, `.env`, `logs/`, `outputs/`, build artifacts
- **Keep committed**: `uv.lock` (for reproducible builds)
- Create descriptive commit messages
- Branch for new features, PR for review

### Performance Considerations
- Large worlds (200x200+) and many creatures (50+) can be slow
- Sound synthesis is computationally expensive
- LLM API calls add latency - use sparingly in main loop
- Use `small.yaml` config for rapid iteration

## Troubleshooting

### Common Issues
1. **Import errors**: Run `uv sync --all-extras` from project root
2. **Pygame issues**: Install system dependencies (`python3-dev python3-pygame` on Ubuntu)
3. **API timeouts**: Check network, increase timeout in API client
4. **Slow simulation**: Reduce world size, creature count, or disable LLM features
5. **Memory issues**: Large worlds accumulate history - implement periodic cleanup

### Debug Mode
- Set `log_level: DEBUG` in YAML config
- Check `logs/` directory for detailed output
- Use `--visualize` to observe behavior in real-time

## Best Practices

1. **Configuration over Code**: Use YAML configs for experiments, not code changes
2. **Test Early**: Run tests before committing changes
3. **Graceful Degradation**: Always provide fallbacks for optional features (LLMs, visualization)
4. **Profile Before Optimizing**: Use `cProfile` to identify bottlenecks
5. **Document Complex Logic**: Especially mood calculations and emergent behavior patterns
6. **Version Dependencies**: Keep `uv.lock` updated and committed
7. **Cost Awareness**: Always implement cost tracking for LLM features

## API Integration Guidelines

### OpenRouter (Recommended)
- Single API key for multiple providers
- Free tier models available (Llama 3.1 8B)
- Automatic cost tracking in EUR
- Set `MAX_DAILY_COST_EUR` to protect budget

### API Call Patterns
- Always use async/await for API calls
- Implement exponential backoff for retries
- Log all API requests/responses for debugging
- Track costs per request
- Handle rate limits gracefully

### Error Handling
- Catch network errors and provide rule-based fallback
- Log API failures without crashing simulation
- Display user-friendly error messages
- Respect API rate limits and quotas

## Questions or Issues?

- Check existing documentation in `docs/`
- Review configuration examples in `config/`
- Look at `examples/` for usage patterns
- Refer to inline comments in source code for implementation details

## Recent Changes

**Phase 1 Improvements (November 2025)**:
- ✅ Comprehensive error handling for API calls
- ✅ YAML-based configuration system with validation
- ✅ Professional logging with performance metrics
- ✅ Four configuration presets (default, small, large, social)

See `docs/PHASE1_PROGRESS.md` for details.
