#!/usr/bin/env python3
"""Basic simulation example with optional visualization"""

import asyncio
import argparse
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.simulation.main_loop import EmergentLifeSimulation
from src.config.logging_config import setup_logging
from src.config.config_schema import SimulationConfig


async def main():
    parser = argparse.ArgumentParser(description="Run tiny entities simulation")
    parser.add_argument("--creatures", type=int, default=None, help="Number of creatures")
    parser.add_argument("--steps", type=int, default=None, help="Simulation steps")
    parser.add_argument("--visualize", action="store_true", help="Enable visualization")
    parser.add_argument(
        "--analyze-every", type=int, default=None, help="Steps between analysis"
    )
    parser.add_argument(
        "--config", type=str, default=None, help="Path to YAML configuration file"
    )
    parser.add_argument(
        "--log-level", type=str, default="INFO", help="Logging level (DEBUG, INFO, WARNING, ERROR)"
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(level=args.log_level)

    # Load configuration if provided
    config = None
    if args.config:
        config_path = Path(args.config)
        if not config_path.exists():
            print(f"Error: Configuration file not found: {args.config}")
            sys.exit(1)
        config = SimulationConfig.from_yaml(config_path)
        print(f"Loaded configuration from {args.config}")

    # Create simulation
    # Command-line args override config if both provided
    creatures = args.creatures if args.creatures is not None else (8 if not config else config.creatures.initial_count)
    steps = args.steps if args.steps is not None else (10000 if not config else config.max_steps)
    analyze_every = args.analyze_every if args.analyze_every is not None else (500 if not config else config.analysis.analyze_every)

    sim = EmergentLifeSimulation(
        num_creatures=creatures,
        max_steps=steps,
        analyze_every=analyze_every,
        config=config,
    )

    if args.visualize:
        try:
            from src.simulation.visualization import SimulationVisualizer

            visualizer = SimulationVisualizer(sim)
            await visualizer.run()
        except ImportError:
            print("Pygame not installed. Running without visualization.")
            print("Install with: pip install pygame")
            await sim.run_simulation()
    else:
        # Run simulation without visualization
        await sim.run_simulation()


if __name__ == "__main__":
    asyncio.run(main())
