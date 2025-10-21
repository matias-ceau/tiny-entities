#!/usr/bin/env python3
"""
Headless visualization demo that generates PNG snapshots of the simulation.
Useful for testing visualization without requiring a display or for creating documentation.
"""

import os
import sys
import asyncio
import argparse

# Set pygame to headless mode before importing it
os.environ['SDL_VIDEODRIVER'] = 'dummy'

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.simulation.main_loop import EmergentLifeSimulation
from src.simulation.visualization import SimulationVisualizer
import pygame


async def main():
    """Run simulation and save visualization snapshots"""
    parser = argparse.ArgumentParser(
        description="Generate visualization snapshots of simulation"
    )
    parser.add_argument("--creatures", type=int, default=8, help="Number of creatures")
    parser.add_argument("--steps", type=int, default=500, help="Total simulation steps")
    parser.add_argument(
        "--snapshot-every", type=int, default=50, help="Steps between snapshots"
    )
    parser.add_argument(
        "--output-dir", type=str, default="./simulation_output", help="Output directory"
    )

    args = parser.parse_args()

    # Create output directory
    os.makedirs(args.output_dir, exist_ok=True)

    print(f"Creating simulation with {args.creatures} creatures...")
    sim = EmergentLifeSimulation(
        num_creatures=args.creatures,
        max_steps=args.steps,
        analyze_every=args.snapshot_every,
    )

    print("Creating visualizer...")
    visualizer = SimulationVisualizer(sim, width=800, height=800)

    # Run simulation and save snapshots
    screenshots = []
    snapshot_count = 0

    while sim.step_count < args.steps:
        # Run one step
        await sim.simulation_step()

        # Save snapshot at intervals
        if sim.step_count % args.snapshot_every == 0:
            # Draw the current state
            visualizer._draw_world()
            visualizer._draw_info()

            # Save screenshot
            filename = os.path.join(
                args.output_dir, f"snapshot_{sim.step_count:05d}.png"
            )
            pygame.image.save(visualizer.screen, filename)
            screenshots.append(filename)
            snapshot_count += 1
            print(f"Snapshot {snapshot_count}: step {sim.step_count} -> {filename}")

            # Run emergence analysis
            await sim.analyze_emergence()

    # Final snapshot
    visualizer._draw_world()
    visualizer._draw_info()
    filename = os.path.join(args.output_dir, f"snapshot_{sim.step_count:05d}_final.png")
    pygame.image.save(visualizer.screen, filename)
    screenshots.append(filename)
    print(f"Final snapshot: {filename}")

    # Print summary
    print("\n" + "=" * 60)
    print("SIMULATION COMPLETE")
    print("=" * 60)
    print(f"Total steps: {sim.step_count}")
    alive_count = sum(1 for c in sim.creatures if c["alive"])
    print(f"Creatures alive: {alive_count}/{len(sim.creatures)}")
    print(f"Sound events: {len(sim.sound_history)}")

    if alive_count > 0:
        alive_creatures = [c for c in sim.creatures if c["alive"]]
        avg_valence = (
            sum(c["brain"].mood_system.valence for c in alive_creatures) / alive_count
        )
        avg_arousal = (
            sum(c["brain"].mood_system.arousal for c in alive_creatures) / alive_count
        )
        print(f"Final avg mood: valence={avg_valence:.2f}, arousal={avg_arousal:.2f}")

    print(f"\nSnapshots saved to: {args.output_dir}")
    print(f"Total snapshots: {len(screenshots)}")
    print("=" * 60)

    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())
