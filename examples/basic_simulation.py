#!/usr/bin/env python3
"""Basic simulation example with optional visualization"""

import asyncio
import argparse
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.simulation.main_loop import EmergentLifeSimulation


async def main():
    parser = argparse.ArgumentParser(description="Run tiny entities simulation")
    parser.add_argument("--creatures", type=int, default=8, help="Number of creatures")
    parser.add_argument("--steps", type=int, default=10000, help="Simulation steps")
    parser.add_argument("--visualize", action="store_true", help="Enable visualization")
    parser.add_argument(
        "--analyze-every", type=int, default=500, help="Steps between analysis"
    )

    args = parser.parse_args()

    # Create simulation
    sim = EmergentLifeSimulation(
        num_creatures=args.creatures,
        max_steps=args.steps,
        analyze_every=args.analyze_every,
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
