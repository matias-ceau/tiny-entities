"""Entry point for running the simulation as a module"""

import asyncio
from .simulation.main_loop import EmergentLifeSimulation

def main():
    """Run the simulation with default parameters"""
    sim = EmergentLifeSimulation(num_creatures=8, max_steps=5000)
    asyncio.run(sim.run_simulation())

if __name__ == "__main__":
    main()