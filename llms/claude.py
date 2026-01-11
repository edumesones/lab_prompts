"""
Claude (Anthropic) LLM provider.
Supports Claude Opus, Sonnet, and Haiku models.
"""

from typing import Any
from anthropic import Anthropic
from loguru import logger

from .base import LLMProvider


class ClaudeProvider(LLMProvider):
    """Claude LLM provider."""

    def __init__(self, config: dict[str, Any]):
        """
        Initialize Claude provider.

        Args:
            config: Configuration dict with keys:
                - model_name: Claude model (default: claude-sonnet-4-20250514)
                - temperature: Sampling temperature (default: 0.1)
                - max_tokens: Maximum tokens (default: 4096)
                - api_key: Anthropic API key (required)
        """
        super().__init__(config)
        
        api_key = config.get("api_key")
        if not api_key:
            raise ValueError("Anthropic API key is required in config")
        
        self.client = Anthropic(api_key=api_key)
        self.model_name = config.get("model_name", "claude-sonnet-4-20250514")
        self.last_message = None  # Store last message for token extraction

        logger.success(f"✅ Claude LLM initialized: {self.model_name}")

    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """Generate response using Claude."""
        try:
            message = self.client.messages.create(
                model=self.model_name,
                max_tokens=max_tokens or self.max_tokens,
                temperature=temperature or self.temperature,
                system=system_prompt or "",
                messages=[{"role": "user", "content": prompt}],
            )

            # Store message for token extraction
            self.last_message = message

            response = message.content[0].text
            return response

        except Exception as e:
            logger.error(f"❌ Claude generation failed: {e}")
            raise

    def get_metadata(self) -> dict[str, Any]:
        """Return provider metadata."""
        return {
            "provider": "claude",
            "model": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "type": "api",
            "vendor": "anthropic",
        }

    def get_usage_info(self) -> dict[str, int]:
        """Extract token usage from last Claude message."""
        if hasattr(self, 'last_message') and self.last_message:
            usage = self.last_message.usage
            return {
                "input_tokens": usage.input_tokens,
                "output_tokens": usage.output_tokens,
                "total_tokens": usage.input_tokens + usage.output_tokens
            }

        # Fallback if no message available
        logger.warning("⚠️ No message data available for token counting")
        return {
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0
        }

