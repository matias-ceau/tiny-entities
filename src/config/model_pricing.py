"""OpenRouter model pricing information for cost simulation"""

# Pricing in USD per million tokens (as of late 2024)
# Source: OpenRouter pricing page
OPENROUTER_PRICING = {
    # Claude models
    "anthropic/claude-3.5-sonnet": {
        "prompt": 3.0,  # $3 per 1M input tokens
        "completion": 15.0,  # $15 per 1M output tokens
    },
    "anthropic/claude-3-sonnet-20240229": {
        "prompt": 3.0,
        "completion": 15.0,
    },
    "anthropic/claude-3-opus": {
        "prompt": 15.0,
        "completion": 75.0,
    },
    "anthropic/claude-3-haiku": {
        "prompt": 0.25,
        "completion": 1.25,
    },
    # Meta Llama models (free tier)
    "meta-llama/llama-3.1-8b-instruct:free": {
        "prompt": 0.0,
        "completion": 0.0,
    },
    "meta-llama/llama-3.1-70b-instruct:free": {
        "prompt": 0.0,
        "completion": 0.0,
    },
    # Meta Llama models (paid)
    "meta-llama/llama-3.1-8b-instruct": {
        "prompt": 0.05,
        "completion": 0.05,
    },
    "meta-llama/llama-3.1-70b-instruct": {
        "prompt": 0.35,
        "completion": 0.40,
    },
    "meta-llama/llama-3.1-405b-instruct": {
        "prompt": 2.70,
        "completion": 2.70,
    },
    # OpenAI models via OpenRouter
    "openai/gpt-4-turbo": {
        "prompt": 10.0,
        "completion": 30.0,
    },
    "openai/gpt-4o": {
        "prompt": 2.5,
        "completion": 10.0,
    },
    "openai/gpt-4o-mini": {
        "prompt": 0.15,
        "completion": 0.60,
    },
    "openai/gpt-3.5-turbo": {
        "prompt": 0.50,
        "completion": 1.50,
    },
}

# USD to EUR exchange rate (approximate)
USD_TO_EUR = 0.92


def get_model_cost(model_name: str, prompt_tokens: int, completion_tokens: int) -> float:
    """
    Calculate cost in EUR for a model inference.
    
    Args:
        model_name: OpenRouter model identifier
        prompt_tokens: Number of input tokens
        completion_tokens: Number of output tokens
        
    Returns:
        Cost in EUR
    """
    if model_name not in OPENROUTER_PRICING:
        # Unknown model, return 0 to avoid breaking simulations
        return 0.0
    
    pricing = OPENROUTER_PRICING[model_name]
    
    # Calculate cost in USD
    prompt_cost = (prompt_tokens / 1_000_000) * pricing["prompt"]
    completion_cost = (completion_tokens / 1_000_000) * pricing["completion"]
    total_usd = prompt_cost + completion_cost
    
    # Convert to EUR
    return total_usd * USD_TO_EUR


def estimate_token_count(text: str) -> int:
    """
    Rough estimate of token count for text.
    Simple heuristic: ~1 token per 4 characters
    
    Args:
        text: Input text
        
    Returns:
        Estimated token count
    """
    return len(text) // 4
