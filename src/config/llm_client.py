"""Utility helpers for interacting with LLM providers."""

from __future__ import annotations

import os
import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from openai import OpenAI

from .api_config import APIConfig


OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
OPENROUTER_SITE_URL = os.getenv("OPENROUTER_SITE_URL", "https://github.com/tiny-entities")
OPENROUTER_APP_NAME = os.getenv("OPENROUTER_APP_NAME", "Tiny Entities Simulation")


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
        if self._client is not None:
            return

        if not self.config.OPENROUTER_API_KEY:
            return

        self._client = OpenAI(
            base_url=OPENROUTER_BASE_URL,
            api_key=self.config.OPENROUTER_API_KEY,
        )

    @property
    def available(self) -> bool:
        return self._client is not None

    def _chat_completion(
        self,
        model: str,
        system_prompt: str,
        user_prompt: str,
    ) -> Optional[LLMResponse]:
        if not self.available:
            return None

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

        message = response.choices[0].message
        usage = response.usage
        prompt_tokens = usage.prompt_tokens if usage else 0
        completion_tokens = usage.completion_tokens if usage else 0
        total_cost = 0.0
        if usage:
            total_cost = self.config.calculate_call_cost(
                model,
                prompt_tokens,
                completion_tokens,
            )

        return LLMResponse(
            text=message.content or "",
            total_cost_eur=total_cost,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
        )

    def suggest_action(
        self,
        perception_summary: str,
        mood_summary: str,
        available_actions: List[str],
    ) -> Optional[LLMResponse]:
        model = self.config.get_action_model()
        if not model:
            return None

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

    def generate_reflection(
        self,
        creature_id: str,
        context_summary: str,
    ) -> Optional[LLMResponse]:
        model = self.config.get_analysis_model()
        if not model:
            return None

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

    def summarize_emergence(
        self,
        sound_summary: Dict[str, Any],
        mood_summary: Dict[str, Any],
        reflections: List[str],
    ) -> Optional[LLMResponse]:
        model = self.config.get_analysis_model()
        if not model:
            return None

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
