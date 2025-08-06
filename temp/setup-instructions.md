# Setup Instructions for Tiny Entities

## 1. GitHub Repository Setup

### Create Repository Structure
```bash
# Clone your repository
git clone https://github.com/yourusername/tiny-entities.git
cd tiny-entities

# Create directory structure
mkdir -p src/{world,creatures,emergence,simulation}
mkdir -p config examples tests
mkdir -p .github/workflows

# Create __init__.py files
touch src/__init__.py
touch src/world/__init__.py
touch src/creatures/__init__.py
touch src/emergence/__init__.py
touch src/simulation/__init__.py
touch config/__init__.py
touch tests/__init__.py

# Copy all the generated files to their respective locations
```

### Initial Commit
```bash
# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Emergent artificial life simulation with mood-based cognition"

# Push to GitHub
git push origin main
```

## 2. Claude Code Configuration

### Install Claude Code CLI
```bash
# If you haven't already installed Claude Code
npm install -g @anthropic/claude-code
```

### Configure Your Project
1. Copy the `claude_code_config.json` to your project root
2. Create a `.env` file from `.env.example`:
```bash
cp .env.example .env
```

3. Add your API keys to `.env`:
```env
OPENROUTER_API_KEY=your_actual_openrouter_key
ANTHROPIC_API_KEY=your_actual_anthropic_key
HUGGINGFACE_API_KEY=your_actual_huggingface_key
```

### Initialize Claude Code
```bash
# In your project directory
claude-code init

# Link to the configuration
claude-code config set project-config ./claude_code_config.json
```

## 3. Python Environment Setup

### Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Install Development Dependencies
```bash
# For development
pip install pytest-watch black flake8
```

## 4. Running the Simulation

### Basic Run
```bash
# Run basic simulation
python -m src.simulation.main_loop

# Or use the example script
python examples/basic_simulation.py
```

### With Visualization
```bash
# Run with pygame visualization
python examples/basic_simulation.py --visualize --creatures 10
```

### Run Tests
```bash
# Run all tests
pytest

# Watch mode for development
pytest-watch
```

## 5. API Configuration

### OpenRouter Setup
1. Get API key from https://openrouter.ai/
2. Add to `.env`: `OPENROUTER_API_KEY=sk-or-...`
3. OpenRouter provides access to many models with single API

### HuggingFace Setup (Free)
1. Create account at https://huggingface.co/
2. Get API token from settings
3. Add to `.env`: `HUGGINGFACE_API_KEY=hf_...`

### Cost Management
- Set daily limit in `.env`: `MAX_DAILY_COST_EUR=2.0`
- Monitor costs in simulation output
- Use free models (HuggingFace) for creature actions
- Reserve expensive models (Claude) for weekly analysis

## 6. Claude Code Workflow

### Start Development
```bash
# Start Claude Code in watch mode
claude-code dev

# This will:
# - Watch for file changes
# - Auto-restart simulation
# - Show logs in real-time
```

### Claude Code Commands
```bash
# Run simulation
claude-code run

# Run with visualization
claude-code run visualize

# Run tests
claude-code test

# Analyze emergence
claude-code run analyze
```

## 7. Project Structure Summary

```
tiny-entities/
├── src/                    # Main source code
│   ├── world/             # World physics and rules
│   ├── creatures/         # Creature brains and behavior
│   ├── emergence/         # Analysis tools
│   └── simulation/        # Main loop and visualization
├── config/                # Configuration modules
├── examples/              # Example scripts
├── tests/                 # Unit tests
├── .env                   # Your API keys (not in git!)
├── requirements.txt       # Python dependencies
├── claude_code_config.json # Claude Code config
└── README.md             # Documentation
```

## 8. Development Tips

### Debugging Creatures
```python
# Add debug prints in brain.py
print(f"{self.creature_id}: mood={self.mood_system.valence:.2f}, "
      f"tokens={self.action_tokens}, thought='{thoughts}'")
```

### Adjusting Parameters
Edit `config/simulation_config.py`:
```python
WORLD_SIZE = (100, 100)
INITIAL_CREATURES = 8
FOOD_DENSITY = 0.1
SOUND_DECAY_RATE = 0.9
```

### Monitoring Emergence
- Watch for coordination in sound patterns
- Check if creatures develop "personalities" (stable moods)
- Look for spatial clustering behaviors
- Monitor entropy trends in collective behavior

## 9. Troubleshooting

### Common Issues

**ImportError**: Make sure you're in the project root and have activated venv
```bash
cd tiny-entities
source venv/bin/activate
```

**API Key Errors**: Check `.env` file has correct keys
```bash
cat .env  # Should show your keys
```

**Pygame Issues**: Install system dependencies
```bash
# Ubuntu/Debian
sudo apt-get install python3-pygame

# macOS
brew install pygame
```

**Memory Issues**: Reduce world size or creature count
```python
# In main_loop.py
sim = EmergentLifeSimulation(num_creatures=5)  # Fewer creatures
```

## 10. Next Steps

1. **Run Initial Simulation**: Start with default parameters
2. **Observe Behaviors**: Watch for emergent patterns
3. **Tune Parameters**: Adjust rewards, world size, etc.
4. **Add Features**: Implement new actions or perceptions
5. **Analyze Results**: Use Claude to analyze emergence weekly

### Research Questions to Explore
- Do creatures develop stable "personalities"?
- Can musical patterns emerge from simple rules?
- Do social clusters form naturally?
- How does mood affect collective behavior?
- Can proto-communication emerge?

Good luck with your artificial life experiments! 🧬🎵