"""Utility helpers for interacting with LLM providers."""

from __future__ import annotations

import os
import json
import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from openai import OpenAI, APIError as OpenAIAPIError, APITimeoutError, APIConnectionError

from .api_config import APIConfig

logger = logging.getLogger(__name__)


OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
OPENROUTER_SITE_URL = os.getenv("OPENROUTER_SITE_URL", "https://github.com/tiny-entities")
OPENROUTER_APP_NAME = os.getenv("OPENROUTER_APP_NAME", "Tiny Entities Simulation")


class LLMAPIError(Exception):
    """Custom exception for LLM API errors."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


@dataclass
class LLMResponse:
    """Container for LLM responses."""

    text: str
    total_cost_eur: float = 0.0
    prompt_tokens: int = 0
    completion_tokens: int = 0


class LLMClient:
    """Thin wrapper around the OpenRouter compatible API."""

    def __init__(self) -> None:
        self.config = APIConfig()
        self._client: Optional[OpenAI] = None
        self._ensure_client()

    def _ensure_client(self) -> None:
        """Initialize the OpenAI client with error handling."""
        if self._client is not None:
            return

        if not self.config.OPENROUTER_API_KEY:
            logger.info("No OpenRouter API key found, LLM features disabled")
            return

        try:
            self._client = OpenAI(
                base_url=OPENROUTER_BASE_URL,
                api_key=self.config.OPENROUTER_API_KEY,
            )
            logger.info("LLM client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize LLM client: {e}")
            self._client = None

    @property
    def available(self) -> bool:
        return self._client is not None

    def _chat_completion(
        self,
        model: str,
        system_prompt: str,
        user_prompt: str,
    ) -> Optional[LLMResponse]:
        """Execute a chat completion with comprehensive error handling."""
        if not self.available:
            logger.debug("LLM client not available (no API key)")
            return None

        try:
            response = self._client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                extra_headers={
                    "HTTP-Referer": OPENROUTER_SITE_URL,
                    "X-Title": OPENROUTER_APP_NAME,
                },
            )

            # Validate response structure
            if not response.choices or len(response.choices) == 0:
                logger.error("API returned response with no choices")
                return None

            message = response.choices[0].message
            if not message or not hasattr(message, 'content'):
                logger.error("API returned invalid message structure")
                return None

            usage = response.usage
            prompt_tokens = usage.prompt_tokens if usage else 0
            completion_tokens = usage.completion_tokens if usage else 0
            total_cost = 0.0
            if usage:
                try:
                    total_cost = self.config.calculate_call_cost(
                        model,
                        prompt_tokens,
                        completion_tokens,
                    )
                except Exception as e:
                    logger.warning(f"Error calculating cost: {e}, using 0.0")
                    total_cost = 0.0

            return LLMResponse(
                text=message.content or "",
                total_cost_eur=total_cost,
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
            )

        except APITimeoutError as e:
            logger.error(f"API timeout: {e}")
            return None
        except APIConnectionError as e:
            logger.error(f"API connection error: {e}")
            return None
        except OpenAIAPIError as e:
            logger.error(f"API error: {e}")
            return None
        except ValueError as e:
            logger.error(f"Invalid response data: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error in LLM completion: {e}", exc_info=True)
            return None

    def suggest_action(
        self,
        perception_summary: str,
        mood_summary: str,
        available_actions: List[str],
    ) -> Optional[LLMResponse]:
        """Suggest an action based on perception and mood with validation."""
        if not available_actions:
            logger.warning("suggest_action called with empty available_actions")
            return None

        model = self.config.get_action_model()
        if not model:
            logger.debug("No action model configured")
            return None

        try:
            system_prompt = (
                "You are the collective subconscious of a tiny creature navigating a "
                "2D world. Respond with the single best next action from the provided "
                "list. Only respond with the action identifier."
            )
            user_prompt = (
                f"Perception summary: {perception_summary}\n"
                f"Mood summary: {mood_summary}\n"
                f"Possible actions: {', '.join(available_actions)}"
            )

            return self._chat_completion(model, system_prompt, user_prompt)
        except Exception as e:
            logger.error(f"Error in suggest_action: {e}")
            return None

    def generate_reflection(
        self,
        creature_id: str,
        context_summary: str,
    ) -> Optional[LLMResponse]:
        """Generate a creature reflection with validation."""
        if not creature_id:
            logger.warning("generate_reflection called with empty creature_id")
            return None

        model = self.config.get_analysis_model()
        if not model:
            logger.debug("No analysis model configured")
            return None

        try:
            system_prompt = (
                "You are an introspective tiny creature. Provide a brief first-person "
                "reflection (<= 3 sentences) about the recent experience. Focus on "
                "feelings, intentions, and perceived social patterns."
            )
            user_prompt = (
                f"Creature: {creature_id}\n"
                f"Situation: {context_summary}"
            )

            return self._chat_completion(model, system_prompt, user_prompt)
        except Exception as e:
            logger.error(f"Error in generate_reflection: {e}")
            return None

    def summarize_emergence(
        self,
        sound_summary: Dict[str, Any],
        mood_summary: Dict[str, Any],
        reflections: List[str],
    ) -> Optional[LLMResponse]:
        """Generate emergence summary with validation."""
        model = self.config.get_analysis_model()
        if not model:
            logger.debug("No analysis model configured")
            return None

        try:
            # Validate and sanitize inputs
            sound_summary = sound_summary or {}
            mood_summary = mood_summary or {}
            reflections = reflections or []

            system_prompt = (
                "You are a research assistant observing emergent behaviours in a "
                "tiny creature society. Provide a concise analytic summary (<= 4 "
                "sentences) describing musical coordination, collective mood, and "
                "notable self-reflections."
            )

            user_prompt = (
                f"Sound summary: {json.dumps(sound_summary)}\n"
                f"Mood summary: {json.dumps(mood_summary)}\n"
                f"Recent reflections: {json.dumps(reflections)}"
            )

            return self._chat_completion(model, system_prompt, user_prompt)
        except (TypeError, ValueError) as e:
            logger.error(f"Error serializing emergence data: {e}")
            return None
        except Exception as e:
            logger.error(f"Error in summarize_emergence: {e}")
            return None


_llm_client: Optional[LLMClient] = None


def get_llm_client() -> Optional[LLMClient]:
    global _llm_client
    if _llm_client is None:
        client = LLMClient()
        if client.available:
            _llm_client = client
        else:
            _llm_client = None
    return _llm_client
