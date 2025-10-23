import os
from dotenv import load_dotenv
from .model_pricing import get_model_cost, estimate_token_count

load_dotenv()


class APIConfig:
    """API configuration and model selection"""

    # API Keys
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

    # Model choices - Using OpenRouter for both
    # Free/cheap model for action selection
    FREE_ACTION_MODEL = os.getenv(
        "DEFAULT_FREE_MODEL", "meta-llama/llama-3.1-8b-instruct:free"
    )
    # Updated Claude model for analysis
    ANALYSIS_MODEL = os.getenv(
        "DEFAULT_ANALYSIS_MODEL", "anthropic/claude-3.5-sonnet"
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
        # Prefer OpenRouter (supports both Anthropic and other models)
        if cls.OPENROUTER_API_KEY:
            return cls.ANALYSIS_MODEL
        elif cls.ANTHROPIC_API_KEY:
            return cls.ANALYSIS_MODEL
        return None

    @classmethod
    def calculate_call_cost(
        cls, model_name: str, prompt_tokens: int, completion_tokens: int
    ) -> float:
        """
        Calculate cost in EUR for a model API call.
        
        Args:
            model_name: Model identifier
            prompt_tokens: Number of input tokens
            completion_tokens: Number of output tokens
            
        Returns:
            Cost in EUR
        """
        return get_model_cost(model_name, prompt_tokens, completion_tokens)

    @classmethod
    def estimate_tokens(cls, text: str) -> int:
        """
        Estimate token count for text.
        
        Args:
            text: Input text
            
        Returns:
            Estimated token count
        """
        return estimate_token_count(text)
