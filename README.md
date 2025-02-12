# Project Structure
cognitive_agent/
├── pyproject.toml           # Project dependencies and metadata
├── config/
│   ├── models.yaml         # Model configurations and paths
│   └── agent_config.yaml   # Agent parameters and thresholds
│
├── cognitive_agent/
│   ├── core/
│   │   ├── base.py        # Abstract base classes and interfaces
│   │   └── types.py       # Custom types and dataclasses
│   │
│   ├── perception/
│   │   ├── __init__.py
│   │   ├── visual.py      # MobileNetV2 for visual processing
│   │   ├── auditory.py    # Basic rhythm/MFCC processing
│   │   └── multimodal.py  # Fusion of different modalities
│   │
│   ├── memory/
│   │   ├── __init__.py
│   │   ├── episodic.py    # Time-series event storage (SQLite)
│   │   ├── semantic.py    # FAISS-based vector storage
│   │   ├── working.py     # Short-term memory buffer
│   │   └── schema.py      # Memory structure definitions
│   │
│   ├── emotion/
│   │   ├── __init__.py
│   │   ├── affect.py      # Core emotion engine
│   │   ├── appraisal.py   # Event evaluation
│   │   └── regulation.py  # Emotion regulation systems
│   │
│   ├── cognition/
│   │   ├── __init__.py
│   │   ├── attention.py   # Attention mechanisms
│   │   ├── reasoning.py   # Inference engine
│   │   └── goals.py       # Goal management
│   │
│   ├── language/
│   │   ├── __init__.py
│   │   ├── llm.py        # DeepSeek R1 integration
│   │   ├── narrator.py   # Internal state verbalization
│   │   └── dialogue.py   # Inter-agent communication
│   │
│   ├── action/
│   │   ├── __init__.py
│   │   ├── planning.py   # Action planning
│   │   └── execution.py  # Action execution
│   │
│   └── world/
│       ├── __init__.py
│       ├── state.py      # World state management
│       └── physics.py    # Simple physics/rules
│
├── tests/
│   ├── test_perception.py
│   ├── test_memory.py
│   └── test_integration.py
│
└── examples/
    ├── single_agent.py
    └── basic_interaction.py