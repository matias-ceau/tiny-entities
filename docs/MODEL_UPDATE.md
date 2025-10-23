# Model Update Summary

## Changes Made

This update modernizes the default models to use OpenRouter with the latest available models.

### Default Models Updated

**Previous defaults:**
- Action Model: `huggingface/meta-llama/Llama-2-7b-chat-hf`
- Analysis Model: `anthropic/claude-3-sonnet-20240229`

**New defaults:**
- Action Model: `meta-llama/llama-3.1-8b-instruct:free` (via OpenRouter)
- Analysis Model: `anthropic/claude-3.5-sonnet` (via OpenRouter)

### Why OpenRouter?

OpenRouter provides:
- **Single API key** for multiple model providers
- **Up-to-date models** from Anthropic, Meta, OpenAI, and others
- **Free tier options** (Llama 3.1 8B) for experimentation
- **Transparent pricing** with competitive rates
- **Automatic fallbacks** and routing

### New Features

1. **Model Pricing Module** (`src/config/model_pricing.py`)
   - Contains pricing for 13 popular OpenRouter models
   - Calculates costs in EUR automatically
   - Supports free tier models (zero cost)
   - Graceful handling of unknown models

2. **Enhanced API Configuration** (`src/config/api_config.py`)
   - New methods: `calculate_call_cost()` and `estimate_tokens()`
   - OpenRouter prioritized for both action and analysis models
   - Backward compatible with direct API keys

3. **Updated Documentation**
   - README.md now includes API configuration section
   - QUICKSTART.md explains OpenRouter setup
   - Clear instructions for getting API keys

### Pricing Information

The new pricing module includes:

| Model | Input ($/1M tokens) | Output ($/1M tokens) |
|-------|---------------------|----------------------|
| meta-llama/llama-3.1-8b-instruct:free | $0.00 | $0.00 |
| anthropic/claude-3.5-sonnet | $3.00 | $15.00 |
| anthropic/claude-3-haiku | $0.25 | $1.25 |
| openai/gpt-4o-mini | $0.15 | $0.60 |

*Plus 9 more models - see `src/config/model_pricing.py` for complete list*

### Benefits

1. **No breaking changes** - existing configurations still work
2. **Free experimentation** - free tier Llama model for testing
3. **Latest Claude** - Claude 3.5 Sonnet is the most capable Claude model
4. **Better cost tracking** - accurate pricing for budget management
5. **Easy setup** - single API key gets you started

### Migration Guide

If you were using the old defaults:

1. Get an OpenRouter API key at https://openrouter.ai/
2. Update your `.env` file:
   ```bash
   OPENROUTER_API_KEY=your_key_here
   ```
3. That's it! The new models will be used automatically.

To keep using old models, set in `.env`:
```bash
DEFAULT_FREE_MODEL=huggingface/meta-llama/Llama-2-7b-chat-hf
DEFAULT_ANALYSIS_MODEL=anthropic/claude-3-sonnet-20240229
```

### Testing

New test file added: `tests/test_config.py`
- Tests pricing calculations
- Validates token estimation
- Checks pricing database structure

Run with:
```bash
python tests/test_config.py
```

### Security

✅ All changes passed CodeQL security analysis
✅ No secrets or sensitive data in code
✅ Environment variables properly handled
