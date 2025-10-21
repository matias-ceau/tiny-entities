#!/usr/bin/env python3
"""
Quick demo script to showcase all features of Tiny Entities.
Runs all visualization modes and generates example outputs.
"""

import os
import sys
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("=" * 70)
print("TINY ENTITIES - COMPREHENSIVE DEMO")
print("=" * 70)
print("\nThis demo will showcase all features of the simulation system.\n")

# Set headless mode for visualization tests
os.environ['SDL_VIDEODRIVER'] = 'dummy'

from src.simulation.main_loop import EmergentLifeSimulation
from src.simulation.visualization import SimulationVisualizer
import pygame


async def demo_console_mode():
    """Demonstrate console-only mode"""
    print("\n" + "=" * 70)
    print("1. CONSOLE MODE - Text-based simulation")
    print("=" * 70)
    print("\nRunning 200 steps with 5 creatures...\n")
    
    sim = EmergentLifeSimulation(num_creatures=5, max_steps=200, analyze_every=100)
    
    while sim.step_count < 200:
        await sim.simulation_step()
        if sim.step_count % 50 == 0:
            alive = sum(1 for c in sim.creatures if c['alive'])
            print(f"  Step {sim.step_count}: {alive} creatures alive")
    
    await sim.analyze_emergence()
    
    print("\n✅ Console mode complete!")
    print(f"   - Total steps: {sim.step_count}")
    print(f"   - Sound events: {len(sim.sound_history)}")
    print(f"   - Final alive: {sum(1 for c in sim.creatures if c['alive'])}/{len(sim.creatures)}")


async def demo_headless_visualization():
    """Demonstrate headless visualization with snapshots"""
    print("\n" + "=" * 70)
    print("2. HEADLESS VISUALIZATION - PNG Snapshots")
    print("=" * 70)
    print("\nGenerating visualization snapshots...\n")
    
    output_dir = "/tmp/tiny_entities_demo"
    os.makedirs(output_dir, exist_ok=True)
    
    sim = EmergentLifeSimulation(num_creatures=6, max_steps=200, analyze_every=100)
    viz = SimulationVisualizer(sim, width=800, height=800)
    
    snapshots = []
    for step_target in [50, 100, 150, 200]:
        while sim.step_count < step_target:
            await sim.simulation_step()
        
        viz._draw_world()
        viz._draw_info()
        filename = os.path.join(output_dir, f"demo_step_{sim.step_count:03d}.png")
        pygame.image.save(viz.screen, filename)
        snapshots.append(filename)
        print(f"  ✓ Saved snapshot at step {sim.step_count}")
    
    pygame.quit()
    
    print("\n✅ Headless visualization complete!")
    print(f"   - Snapshots saved to: {output_dir}")
    print(f"   - Generated {len(snapshots)} images")


async def demo_analysis_tools():
    """Demonstrate analysis capabilities"""
    print("\n" + "=" * 70)
    print("3. ANALYSIS TOOLS - Matplotlib Plots")
    print("=" * 70)
    print("\nGenerating analysis plots...\n")
    
    import matplotlib
    matplotlib.use('Agg')  # Use non-interactive backend
    import matplotlib.pyplot as plt
    
    sim = EmergentLifeSimulation(num_creatures=6, max_steps=300, analyze_every=100)
    
    # Collect data
    step_data = []
    mood_valence = {f"creature_{i}": [] for i in range(6)}
    
    while sim.step_count < 300:
        await sim.simulation_step()
        
        if sim.step_count % 10 == 0:
            step_data.append(sim.step_count)
            for creature in sim.creatures:
                if creature['alive']:
                    mood_valence[creature['id']].append(creature['brain'].mood_system.valence)
                else:
                    mood_valence[creature['id']].append(None)
    
    # Create plot
    fig, ax = plt.subplots(figsize=(10, 6))
    for cid, values in mood_valence.items():
        ax.plot(step_data, values, label=cid, alpha=0.7)
    
    ax.set_title("Mood Valence Evolution - Demo", fontsize=14, fontweight='bold')
    ax.set_xlabel("Simulation Step")
    ax.set_ylabel("Valence (-1 to 1)")
    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    ax.grid(True, alpha=0.3)
    ax.legend()
    
    output_file = "/tmp/tiny_entities_demo/analysis_demo.png"
    plt.savefig(output_file, dpi=100, bbox_inches='tight')
    plt.close()
    
    print(f"  ✓ Created mood evolution plot")
    print(f"  ✓ Saved to: {output_file}")
    
    print("\n✅ Analysis tools complete!")


async def main():
    """Run all demos"""
    try:
        await demo_console_mode()
        await demo_headless_visualization()
        await demo_analysis_tools()
        
        print("\n" + "=" * 70)
        print("DEMO COMPLETE!")
        print("=" * 70)
        print("\n✅ All features demonstrated successfully!\n")
        print("Next steps:")
        print("  1. Check /tmp/tiny_entities_demo/ for generated files")
        print("  2. Try: python examples/basic_simulation.py --visualize")
        print("  3. Read: docs/VISUALIZATION.md for detailed guide")
        print("  4. See: ROADMAP.md for development plans")
        print("\n" + "=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error during demo: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
