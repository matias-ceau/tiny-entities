"""Test model pricing and configuration"""
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config.model_pricing import (
    get_model_cost,
    estimate_token_count,
    OPENROUTER_PRICING
)


def test_model_pricing():
    """Test that pricing calculations work"""
    # Test Claude 3.5 Sonnet
    cost = get_model_cost("anthropic/claude-3.5-sonnet", 1000, 500)
    assert cost > 0, "Claude should have non-zero cost"
    assert cost < 1.0, "Cost should be reasonable for small token counts"
    
    # Test free model
    free_cost = get_model_cost("meta-llama/llama-3.1-8b-instruct:free", 10000, 5000)
    assert free_cost == 0.0, "Free model should have zero cost"
    
    # Test unknown model
    unknown_cost = get_model_cost("unknown/model", 1000, 500)
    assert unknown_cost == 0.0, "Unknown model should return zero cost"


def test_token_estimation():
    """Test token count estimation"""
    # Simple text
    text = "Hello world"
    tokens = estimate_token_count(text)
    assert tokens > 0, "Should estimate positive tokens"
    assert tokens < len(text), "Tokens should be less than character count"
    
    # Empty text
    assert estimate_token_count("") == 0


def test_pricing_database():
    """Test that pricing database has expected models"""
    # Check for new default models
    assert "anthropic/claude-3.5-sonnet" in OPENROUTER_PRICING
    assert "meta-llama/llama-3.1-8b-instruct:free" in OPENROUTER_PRICING
    
    # Check old models are still supported
    assert "anthropic/claude-3-sonnet-20240229" in OPENROUTER_PRICING
    
    # Verify structure
    for model, pricing in OPENROUTER_PRICING.items():
        assert "prompt" in pricing, f"{model} missing prompt pricing"
        assert "completion" in pricing, f"{model} missing completion pricing"
        assert pricing["prompt"] >= 0, f"{model} has negative prompt pricing"
        assert pricing["completion"] >= 0, f"{model} has negative completion pricing"


if __name__ == "__main__":
    test_model_pricing()
    print("✓ Model pricing tests passed")
    
    test_token_estimation()
    print("✓ Token estimation tests passed")
    
    test_pricing_database()
    print("✓ Pricing database tests passed")
    
    print("\n✓ All tests passed!")
