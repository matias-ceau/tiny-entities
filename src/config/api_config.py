import os
from dotenv import load_dotenv

load_dotenv()


class APIConfig:
    """API configuration and model selection"""

    # API Keys
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

    # Model choices
    FREE_ACTION_MODEL = os.getenv(
        "DEFAULT_FREE_MODEL", "huggingface/meta-llama/Llama-2-7b-chat-hf"
    )
    ANALYSIS_MODEL = os.getenv(
        "DEFAULT_ANALYSIS_MODEL", "anthropic/claude-3-sonnet-20240229"
    )

    # Cost limits
    MAX_DAILY_COST_EUR = float(os.getenv("MAX_DAILY_COST_EUR", "2.0") or "2.0")

    @classmethod
    def get_action_model(cls):
        """Get model for creature action selection"""
        if cls.OPENROUTER_API_KEY:
            return cls.FREE_ACTION_MODEL
        elif cls.HUGGINGFACE_API_KEY:
            return "huggingface"
        return None

    @classmethod
    def get_analysis_model(cls):
        """Get model for emergence analysis"""
        if cls.ANTHROPIC_API_KEY:
            return cls.ANALYSIS_MODEL
        return None
