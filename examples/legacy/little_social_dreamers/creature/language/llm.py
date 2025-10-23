# cognitive_agent/language/llm.py
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from typing import Dict
from ..core.base import CognitiveModule


class NarrationEngine(CognitiveModule):
    def __init__(self, config: Dict):
        self.model_name = "deepseek-ai/deepseek-coder-1.3b-base"  # Using smaller model
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name,
            torch_dtype=torch.float16,
            low_cpu_mem_usage=True,
            device_map="auto",
        )

    async def generate_narrative(self, state: Dict, max_length: int = 100) -> str:
        # Convert state to prompt
        prompt = self._state_to_prompt(state)

        # Generate response
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.model.device)

        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_length=max_length,
                num_return_sequences=1,
                temperature=0.7,
                do_sample=True,
            )

        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)

    def _state_to_prompt(self, state: Dict) -> str:
        # Convert internal state to natural language prompt
        template = """
        Current emotional state: {emotion}
        Recent observations: {observations}
        Current goals: {goals}
        
        Describe the internal experience:
        """.strip()

        return template.format(
            emotion=state["emotion"],
            observations=state["observations"],
            goals=state["goals"],
        )
