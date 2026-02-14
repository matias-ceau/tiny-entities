#!/usr/bin/env python3
"""Minimal test to find where simulation hangs"""

import asyncio
import logging
import sys

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger()

async def test_minimal():
    """Test with absolute minimum"""
    logger.info("1. Importing...")
    from src.creatures.brain import EnhancedBrain
    from src.world.physics import SimpleWorld
    from src.world.non_deterministic import NonDeterministicWorldModel
    from src.creatures.action_selection import MoodInfluencedActionSelector

    logger.info("2. Creating world...")
    world = SimpleWorld(width=10, height=10)

    logger.info("3. Creating world model...")
    world_model = NonDeterministicWorldModel()

    logger.info("4. Creating brain...")
    brain = EnhancedBrain("test_creature")

    logger.info("5. Creating creature...")
    creature = {
        "id": "test",
        "brain": brain,
        "position": (5, 5),
        "alive": True,
    }

    logger.info("6. Creating action selector...")
    selector = MoodInfluencedActionSelector()

    logger.info("7. Getting perception...")
    view = world_model.world.get_local_view(5, 5)
    perception = {
        "visual": view["visual"],
        "sound": view["sound"],
        "food_count": view["food_count"],
    }

    logger.info("8. Selecting action...")
    action = selector.select_action(brain, perception)
    logger.info(f"   Action selected: {action}")

    logger.info("9. Proposing action...")
    outcome = world_model.propose_action("test", action, (5, 5))
    logger.info(f"   Outcome: {outcome}")

    logger.info("10. Processing timestep in brain...")
    result = brain.process_timestep(perception, action, outcome)
    logger.info(f"    Result keys: {list(result.keys())}")

    logger.info("✅ ALL TESTS PASSED!")

if __name__ == "__main__":
    asyncio.run(test_minimal())
