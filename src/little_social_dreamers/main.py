import asyncio

from .creature import EmotionEngine, MultiModalPerception
from .world import NarrationEngine


async def main():
    # Initialize components
    # config = load_config("config/agent_config.yaml")

    perception = MultiModalPerception(config)
    memory = EpisodicMemory("memory.db")
    emotion = EmotionEngine(config)
    narrator = NarrationEngine(config)

    # Create observation
    obs = Observation(
        visual=load_image("test.jpg"), audio=load_audio("test.wav"), text="Hello world"
    )

    # Process through cognitive cycle
    features = await perception.process(obs)
    emotional_state = await emotion.process(obs)

    # Store in memory
    await memory.store(
        {"observation": obs, "emotion": emotional_state, "features": features}
    )

    # Generate narrative
    narrative = await narrator.generate_narrative(
        {
            "emotion": emotional_state,
            "observations": obs,
            "goals": ["understand environment", "maintain stability"],
        }
    )

    print(f"Internal Narrative: {narrative}")


if __name__ == "__main__":
    asyncio.run(main())
