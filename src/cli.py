"""Command-line interface for Tiny Entities simulation"""

import asyncio
import argparse
import sys
from pathlib import Path

from .simulation.main_loop import EmergentLifeSimulation
from .config.logging_config import setup_logging
from .config.config_schema import SimulationConfig


def main():
    """Main CLI entry point for tiny-entities command"""
    parser = argparse.ArgumentParser(
        description="Tiny Entities - Emergent artificial life simulation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  tiny-entities                              # Run with defaults
  tiny-entities --visualize                  # Run with visualization
  tiny-entities --config config/better_vis.yaml --visualize
  tiny-entities --creatures 15 --steps 20000 --log-level DEBUG

Controls (when visualized):
  SPACE - Pause/Resume
  ESC   - Quit
  M     - Toggle internal thoughts panel
  P     - Toggle communication patterns panel
  H     - Toggle health/energy bars
  L     - Toggle legend
        """
    )

    # Simulation parameters
    parser.add_argument(
        "--creatures",
        type=int,
        default=None,
        help="Number of creatures (default: 10, or from config)"
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=None,
        help="Maximum simulation steps (default: 10000, or from config)"
    )
    parser.add_argument(
        "--analyze-every",
        type=int,
        default=None,
        help="Steps between analysis (default: 500, or from config)"
    )

    # Configuration
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to YAML configuration file"
    )

    # Visualization
    parser.add_argument(
        "--visualize",
        action="store_true",
        help="Enable real-time visualization (requires pygame)"
    )
    parser.add_argument(
        "--no-visualize",
        dest="visualize",
        action="store_false",
        help="Disable visualization (headless mode)"
    )

    # Logging
    parser.add_argument(
        "--log-level",
        type=str,
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level (default: INFO)"
    )
    parser.add_argument(
        "--log-file",
        type=str,
        default=None,
        help="Log to file instead of console"
    )

    args = parser.parse_args()

    # Setup logging
    log_file_path = Path(args.log_file) if args.log_file else None
    setup_logging(level=args.log_level, log_file=log_file_path)

    # Load configuration if provided
    config = None
    if args.config:
        config_path = Path(args.config)
        if not config_path.exists():
            print(f"Error: Configuration file not found: {args.config}", file=sys.stderr)
            sys.exit(1)
        try:
            config = SimulationConfig.from_yaml(config_path)
            print(f"✓ Loaded configuration from {args.config}")
        except Exception as e:
            print(f"Error loading config: {e}", file=sys.stderr)
            sys.exit(1)

    # Determine final parameters (command-line overrides config)
    creatures = args.creatures if args.creatures is not None else (10 if not config else config.creatures.initial_count)
    steps = args.steps if args.steps is not None else (10000 if not config else config.max_steps)
    analyze_every = args.analyze_every if args.analyze_every is not None else (500 if not config else config.analysis.analyze_every)

    # Create simulation
    print(f"🧬 Tiny Entities Simulation")
    print(f"   Creatures: {creatures}")
    print(f"   Max steps: {steps}")
    print(f"   Analysis frequency: every {analyze_every} steps")
    if config:
        print(f"   Config: {args.config}")
    print()

    sim = EmergentLifeSimulation(
        num_creatures=creatures,
        max_steps=steps,
        analyze_every=analyze_every,
        config=config,
    )

    # Run with or without visualization
    if args.visualize:
        try:
            from .simulation.visualization import SimulationVisualizer
            print("🎨 Starting visualization...")
            print("   Controls: SPACE=Pause | M=Thoughts | P=Patterns | H=Health | L=Legend | ESC=Quit")
            print()
            visualizer = SimulationVisualizer(sim)
            asyncio.run(visualizer.run())
        except ImportError as e:
            print("❌ Visualization requires pygame.", file=sys.stderr)
            print("   Install with: pip install pygame", file=sys.stderr)
            print(f"   Error: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("🏃 Running headless simulation...")
        print()
        asyncio.run(sim.run_simulation())


if __name__ == "__main__":
    main()
