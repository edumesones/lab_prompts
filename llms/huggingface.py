"""
HuggingFace LLM provider.
Uses HuggingFace Router with OpenAI-compatible API.
"""

from typing import Any
import os
from openai import OpenAI
from loguru import logger

from .base import LLMProvider


class HuggingFaceProvider(LLMProvider):
    """HuggingFace LLM provider using Router API."""

    def __init__(self, config: dict[str, Any]):
        """
        Initialize HuggingFace provider.

        Args:
            config: Configuration dict with keys:
                - model_name: HuggingFace model name (e.g., "deepseek-ai/DeepSeek-R1:novita")
                - temperature: Sampling temperature (default: 0.2)
                - max_tokens: Maximum tokens (default: 1024)
                - api_key: HuggingFace token (required, or set HF_TOKEN env var)
                - base_url: API endpoint (default: https://router.huggingface.co/v1)
        """
        super().__init__(config)
        
        # Get API key from config or environment
        api_key = config.get("api_key") or os.environ.get("HF_TOKEN")
        if not api_key:
            raise ValueError(
                "HuggingFace API key is required. "
                "Set 'api_key' in config or HF_TOKEN environment variable. "
                "Get your token at https://huggingface.co/settings/tokens"
            )
        
        # Get base URL (allow custom endpoints)
        base_url = config.get("base_url", "https://router.huggingface.co/v1")
        
        # Initialize OpenAI client with HuggingFace endpoint
        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key,
        )
        
        self.model_name = config.get("model_name")
        if not self.model_name:
            raise ValueError("model_name is required in config")

        self.last_response = None  # Store last response for token extraction
        self.last_prompt = None  # Store prompt for fallback estimation

        logger.success(f"✅ HuggingFace LLM initialized: {self.model_name}")

    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """Generate response using HuggingFace."""
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

            # Store for token extraction
            self.last_response = response
            self.last_prompt = prompt

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"❌ HuggingFace generation failed: {e}")
            raise

    def get_metadata(self) -> dict[str, Any]:
        """Return provider metadata."""
        return {
            "provider": "huggingface",
            "model": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "type": "api",
            "vendor": "huggingface",
        }

    def get_usage_info(self) -> dict[str, int]:
        """Extract token usage from last HuggingFace response."""
        # Try to extract from response (OpenAI-compatible format)
        if hasattr(self, 'last_response') and self.last_response:
            try:
                if hasattr(self.last_response, 'usage') and self.last_response.usage:
                    usage = self.last_response.usage
                    return {
                        "input_tokens": usage.prompt_tokens,
                        "output_tokens": usage.completion_tokens,
                        "total_tokens": usage.total_tokens
                    }
            except Exception:
                pass  # Fallback to estimation

        # Fallback to estimation if API doesn't provide usage
        logger.warning("⚠️ HuggingFace usage data not available, using estimation")
        from .token_counter import estimate_tokens

        input_tokens = estimate_tokens(self.last_prompt or "")
        output_text = ""
        if hasattr(self, 'last_response') and self.last_response:
            try:
                output_text = self.last_response.choices[0].message.content or ""
            except Exception:
                pass

        output_tokens = estimate_tokens(output_text)

        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens
        }

