#!/usr/bin/env python3
"""
Analysis tools for post-simulation data visualization using matplotlib.
"""

import sys
import os
import asyncio
import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.simulation.main_loop import EmergentLifeSimulation


async def run_and_analyze():
    """Run simulation and generate analysis plots"""
    parser = argparse.ArgumentParser(
        description="Run simulation and generate analysis plots"
    )
    parser.add_argument("--creatures", type=int, default=8, help="Number of creatures")
    parser.add_argument("--steps", type=int, default=2000, help="Simulation steps")
    parser.add_argument(
        "--output", type=str, default="analysis_output", help="Output directory"
    )

    args = parser.parse_args()

    # Create output directory
    os.makedirs(args.output, exist_ok=True)

    print(f"Running simulation with {args.creatures} creatures for {args.steps} steps...")
    sim = EmergentLifeSimulation(
        num_creatures=args.creatures, max_steps=args.steps, analyze_every=100
    )

    # Data collection
    step_data = []
    mood_data = {f"creature_{i}": {"valence": [], "arousal": []} for i in range(args.creatures)}
    creature_health = {f"creature_{i}": [] for i in range(args.creatures)}
    
    # Run simulation
    while sim.step_count < args.steps:
        await sim.simulation_step()

        # Collect data every 10 steps
        if sim.step_count % 10 == 0:
            step_data.append(sim.step_count)
            
            for creature in sim.creatures:
                cid = creature["id"]
                if creature["alive"]:
                    mood_data[cid]["valence"].append(creature["brain"].mood_system.valence)
                    mood_data[cid]["arousal"].append(creature["brain"].mood_system.arousal)
                    creature_health[cid].append(creature["brain"].health)
                else:
                    # Mark as dead with NaN
                    mood_data[cid]["valence"].append(np.nan)
                    mood_data[cid]["arousal"].append(np.nan)
                    creature_health[cid].append(0)

        # Periodic analysis
        if sim.step_count % sim.analyze_every == 0:
            await sim.analyze_emergence()

    print("\nGenerating analysis plots...")

    # Create comprehensive figure
    fig = plt.figure(figsize=(16, 12))
    gs = GridSpec(3, 3, figure=fig, hspace=0.3, wspace=0.3)

    # 1. Mood valence over time
    ax1 = fig.add_subplot(gs[0, :2])
    for cid in mood_data:
        ax1.plot(step_data, mood_data[cid]["valence"], label=cid, alpha=0.7)
    ax1.set_title("Mood Valence Over Time", fontsize=14, fontweight="bold")
    ax1.set_xlabel("Simulation Step")
    ax1.set_ylabel("Valence (-1 to 1)")
    ax1.axhline(y=0, color="gray", linestyle="--", alpha=0.5)
    ax1.grid(True, alpha=0.3)
    ax1.legend(bbox_to_anchor=(1.05, 1), loc="upper left", fontsize=8)

    # 2. Mood arousal over time
    ax2 = fig.add_subplot(gs[1, :2])
    for cid in mood_data:
        ax2.plot(step_data, mood_data[cid]["arousal"], label=cid, alpha=0.7)
    ax2.set_title("Mood Arousal Over Time", fontsize=14, fontweight="bold")
    ax2.set_xlabel("Simulation Step")
    ax2.set_ylabel("Arousal (0 to 1)")
    ax2.grid(True, alpha=0.3)

    # 3. Health over time
    ax3 = fig.add_subplot(gs[2, :2])
    for cid in creature_health:
        ax3.plot(step_data, creature_health[cid], label=cid, alpha=0.7)
    ax3.set_title("Creature Health Over Time", fontsize=14, fontweight="bold")
    ax3.set_xlabel("Simulation Step")
    ax3.set_ylabel("Health")
    ax3.grid(True, alpha=0.3)

    # 4. Mood state space (valence vs arousal) - final states
    ax4 = fig.add_subplot(gs[0, 2])
    alive_creatures = [c for c in sim.creatures if c["alive"]]
    if alive_creatures:
        final_valences = [c["brain"].mood_system.valence for c in alive_creatures]
        final_arousals = [c["brain"].mood_system.arousal for c in alive_creatures]
        ax4.scatter(final_valences, final_arousals, s=100, alpha=0.6, c="blue")
        for i, c in enumerate(alive_creatures):
            ax4.annotate(
                c["id"].split("_")[1],
                (final_valences[i], final_arousals[i]),
                fontsize=8,
            )
    ax4.set_title("Final Mood States", fontsize=12, fontweight="bold")
    ax4.set_xlabel("Valence")
    ax4.set_ylabel("Arousal")
    ax4.set_xlim(-1.1, 1.1)
    ax4.set_ylim(0, 1.1)
    ax4.axvline(x=0, color="gray", linestyle="--", alpha=0.5)
    ax4.axhline(y=0.5, color="gray", linestyle="--", alpha=0.5)
    ax4.grid(True, alpha=0.3)

    # 5. Sound activity histogram
    ax5 = fig.add_subplot(gs[1, 2])
    if sim.sound_history:
        sound_steps = [s["step"] for s in sim.sound_history]
        ax5.hist(sound_steps, bins=50, alpha=0.7, color="green")
    ax5.set_title("Sound Events Distribution", fontsize=12, fontweight="bold")
    ax5.set_xlabel("Simulation Step")
    ax5.set_ylabel("Count")
    ax5.grid(True, alpha=0.3)

    # 6. Summary statistics
    ax6 = fig.add_subplot(gs[2, 2])
    ax6.axis("off")
    
    alive_count = sum(1 for c in sim.creatures if c["alive"])
    avg_valence = np.nanmean([mood_data[cid]["valence"][-1] for cid in mood_data])
    avg_arousal = np.nanmean([mood_data[cid]["arousal"][-1] for cid in mood_data])
    
    summary_text = f"""
SIMULATION SUMMARY
{'=' * 30}

Total Steps: {sim.step_count}
Creatures: {len(sim.creatures)}
Survived: {alive_count} ({alive_count/len(sim.creatures)*100:.1f}%)

Sound Events: {len(sim.sound_history)}
Avg Sounds/Step: {len(sim.sound_history)/sim.step_count:.2f}

Final Mood:
  Valence: {avg_valence:.3f}
  Arousal: {avg_arousal:.3f}

Cost: €{sim.daily_cost_eur:.3f}
"""
    ax6.text(
        0.1,
        0.9,
        summary_text,
        transform=ax6.transAxes,
        fontsize=10,
        verticalalignment="top",
        fontfamily="monospace",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.5),
    )

    plt.suptitle(
        f"Tiny Entities Simulation Analysis ({args.creatures} creatures, {args.steps} steps)",
        fontsize=16,
        fontweight="bold",
    )

    # Save figure
    output_file = os.path.join(args.output, "simulation_analysis.png")
    plt.savefig(output_file, dpi=150, bbox_inches="tight")
    print(f"\nAnalysis saved to: {output_file}")

    # Also create individual mood trajectory plot
    fig2, ax = plt.subplots(figsize=(12, 8))
    for cid in mood_data:
        valences = np.array(mood_data[cid]["valence"])
        arousals = np.array(mood_data[cid]["arousal"])
        
        # Filter out NaN values
        valid = ~np.isnan(valences) & ~np.isnan(arousals)
        if np.any(valid):
            ax.plot(
                valences[valid],
                arousals[valid],
                alpha=0.5,
                linewidth=2,
                label=cid,
            )
            # Mark start and end
            ax.scatter(valences[valid][0], arousals[valid][0], s=100, marker="o", alpha=0.8)
            ax.scatter(valences[valid][-1], arousals[valid][-1], s=100, marker="x", alpha=0.8)

    ax.set_title("Mood Trajectories (O=start, X=end)", fontsize=14, fontweight="bold")
    ax.set_xlabel("Valence (Negative ← → Positive)", fontsize=12)
    ax.set_ylabel("Arousal (Calm ← → Excited)", fontsize=12)
    ax.set_xlim(-1.1, 1.1)
    ax.set_ylim(0, 1.1)
    ax.axvline(x=0, color="gray", linestyle="--", alpha=0.5)
    ax.axhline(y=0.5, color="gray", linestyle="--", alpha=0.5)
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8)

    # Add quadrant labels
    ax.text(0.7, 0.9, "Happy\nExcited", ha="center", va="center", fontsize=10, alpha=0.5)
    ax.text(-0.7, 0.9, "Sad\nExcited", ha="center", va="center", fontsize=10, alpha=0.5)
    ax.text(0.7, 0.1, "Happy\nCalm", ha="center", va="center", fontsize=10, alpha=0.5)
    ax.text(-0.7, 0.1, "Sad\nCalm", ha="center", va="center", fontsize=10, alpha=0.5)

    trajectory_file = os.path.join(args.output, "mood_trajectories.png")
    plt.savefig(trajectory_file, dpi=150, bbox_inches="tight")
    print(f"Mood trajectories saved to: {trajectory_file}")

    print("\nAnalysis complete!")
    print(f"Output directory: {args.output}")


if __name__ == "__main__":
    asyncio.run(run_and_analyze())
