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
  tiny-entities                                    # Run headless
  tiny-entities --visualize                        # pygame window
  tiny-entities --web                              # Browser at http://localhost:8000
  tiny-entities --web --port 9000                  # Different port
  tiny-entities --config config/better_vis.yaml --web
  tiny-entities --creatures 15 --steps 20000

Browser controls:
  Start / Pause / Stop buttons in the web UI
  Side panels: Internal Thoughts, Communication Patterns, Creature Status

pygame controls (--visualize):
  SPACE  Pause/Resume  |  M  Thoughts  |  P  Patterns  |  H  Health  |  ESC  Quit
        """
    )

    parser.add_argument("--creatures",     type=int, default=None)
    parser.add_argument("--steps",         type=int, default=None)
    parser.add_argument("--analyze-every", type=int, default=None)
    parser.add_argument("--config",        type=str, default=None)

    # Run modes (mutually exclusive)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--visualize",    action="store_true", help="pygame window")
    mode.add_argument("--web",          action="store_true", help="browser web app")
    mode.add_argument("--no-visualize", action="store_true", help="headless (default)")

    parser.add_argument("--host",      type=str, default="0.0.0.0", help="Web server host")
    parser.add_argument("--port",      type=int, default=8000,      help="Web server port")
    parser.add_argument("--log-level", type=str, default="INFO",
                        choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    parser.add_argument("--log-file",  type=str, default=None)

    args = parser.parse_args()

    setup_logging(level=args.log_level,
                  log_file=Path(args.log_file) if args.log_file else None)

    # Load config
    config = None
    if args.config:
        p = Path(args.config)
        if not p.exists():
            print(f"Error: config not found: {args.config}", file=sys.stderr)
            sys.exit(1)
        config = SimulationConfig.from_yaml(p)
        print(f"✓ Loaded config from {args.config}")

    creatures     = args.creatures     or (config.creatures.initial_count if config else 10)
    steps         = args.steps         or (config.max_steps                if config else 10000)
    analyze_every = args.analyze_every or (config.analysis.analyze_every   if config else 500)

    # ── WEB mode ──────────────────────────────────────────────────────────
    if args.web:
        try:
            import uvicorn
            from .web.server import app, start_sim
        except ImportError:
            print("❌ Web mode requires: pip install 'tiny-entities[web]'", file=sys.stderr)
            sys.exit(1)

        print(f"🌐 Tiny Entities Web App")
        print(f"   Open http://localhost:{args.port} in your browser")
        print(f"   Works on Android/mobile via your local network IP too!")
        print(f"   Press Ctrl+C to stop\n")

        from . web import server as srv
        srv._auto_start = dict(creatures=creatures, steps=steps,
                               config=args.config)

        @app.on_event("startup")
        async def _auto():
            if getattr(srv, '_auto_start', None):
                await start_sim(**srv._auto_start)

        uvicorn.run(app, host=args.host, port=args.port,
                    log_level=args.log_level.lower())
        return

    # ── PYGAME mode ───────────────────────────────────────────────────────
    print(f"🧬 Tiny Entities  |  creatures={creatures}  steps={steps}")

    sim = EmergentLifeSimulation(
        num_creatures=creatures,
        max_steps=steps,
        analyze_every=analyze_every,
        config=config,
    )

    if args.visualize:
        try:
            from .simulation.visualization import SimulationVisualizer
            print("🎨 Visualization starting…")
            print("   SPACE=Pause  M=Thoughts  P=Patterns  H=Health  ESC=Quit")
            asyncio.run(SimulationVisualizer(sim).run())
        except ImportError as e:
            print(f"❌ pygame required: pip install pygame\n   {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print("🏃 Running headless…")
        asyncio.run(sim.run_simulation())


if __name__ == "__main__":
    main()
