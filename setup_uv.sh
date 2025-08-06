#!/bin/bash

echo "Setting up Tiny Entities with uv..."

# Create virtual environment with uv
echo "Creating virtual environment..."
uv venv

# Activate it
echo "Activating environment..."
source .venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
uv pip install -e ".[dev]"

# Copy environment file
if [ ! -f .env ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "Please edit .env with your API keys"
fi

echo ""
echo "Setup complete! To run the simulation:"
echo "  source .venv/bin/activate"
echo "  python -m src.simulation.main_loop"
echo ""
echo "Or use the example script:"
echo "  python examples/basic_simulation.py"