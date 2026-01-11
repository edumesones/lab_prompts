"""
OpenAI LLM provider.
Supports GPT-4, GPT-4 Turbo, and GPT-3.5 models.
"""

from typing import Any
from openai import OpenAI
from loguru import logger

from .base import LLMProvider


class OpenAILLMProvider(LLMProvider):
    """OpenAI LLM provider."""

    def __init__(self, config: dict[str, Any]):
        """
        Initialize OpenAI LLM provider.

        Args:
            config: Configuration dict with keys:
                - model_name: OpenAI model (default: gpt-4-turbo)
                - temperature: Sampling temperature (default: 0.1)
                - max_tokens: Maximum tokens (default: 4096)
                - api_key: OpenAI API key (required)
        """
        super().__init__(config)

        api_key = config.get("api_key")
        if not api_key:
            raise ValueError("OpenAI API key is required in config")

        self.client = OpenAI(api_key=api_key)
        self.model_name = config.get("model_name", "gpt-4-turbo")
        self.last_response = None  # Store last response for token extraction

        logger.success(f"✅ OpenAI LLM initialized: {self.model_name}")

    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """Generate response using OpenAI."""
        try:
            messages = []

            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            messages.append({"role": "user", "content": prompt})

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature or self.temperature,
                max_tokens=max_tokens or self.max_tokens,
            )

            # Store response for token extraction
            self.last_response = response

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"❌ OpenAI generation failed: {e}")
            raise

    def get_metadata(self) -> dict[str, Any]:
        """Return provider metadata."""
        return {
            "provider": "openai",
            "model": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "type": "api",
            "vendor": "openai",
        }

    def get_usage_info(self) -> dict[str, int]:
        """Extract token usage from last OpenAI response."""
        if hasattr(self, 'last_response') and self.last_response:
            usage = self.last_response.usage
            return {
                "input_tokens": usage.prompt_tokens,
                "output_tokens": usage.completion_tokens,
                "total_tokens": usage.total_tokens
            }

        # Fallback if no response available
        logger.warning("⚠️ No response data available for token counting")
        return {
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0
        }

