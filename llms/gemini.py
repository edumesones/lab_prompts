"""
Google Gemini LLM provider.
Supports Gemini Pro, Gemini Ultra, and other Gemini models.
"""

from typing import Any
from loguru import logger

from .base import LLMProvider


class GeminiProvider(LLMProvider):
    """Google Gemini LLM provider."""

    def __init__(self, config: dict[str, Any]):
        """
        Initialize Gemini provider.

        Args:
            config: Configuration dict with keys:
                - model_name: Gemini model (default: gemini-1.5-pro)
                - temperature: Sampling temperature (default: 0.1)
                - max_tokens: Maximum tokens (default: 4096)
                - api_key: Google AI API key (required)
        """
        super().__init__(config)
        
        api_key = config.get("api_key")
        if not api_key:
            raise ValueError("Google AI API key is required in config")
        
        try:
            import google.generativeai as genai
            self.genai = genai
            
            genai.configure(api_key=api_key)
            self.model_name = config.get("model_name", "gemini-1.5-pro")
            
            # Initialize model
            self.model = genai.GenerativeModel(self.model_name)
            
            # Generation config
            self.generation_config = genai.types.GenerationConfig(
                temperature=self.temperature,
                max_output_tokens=self.max_tokens,
            )

            # Store last prompt and response for token counting
            self.last_prompt = None
            self.last_response = None

            logger.success(f"✅ Gemini LLM initialized: {self.model_name}")
            
        except ImportError:
            raise ImportError(
                "Google Generative AI library not installed. "
                "Install with: pip install google-generativeai"
            )

    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """Generate response using Gemini."""
        try:
            # Update generation config if overrides provided
            gen_config = self.generation_config
            if temperature is not None or max_tokens is not None:
                gen_config = self.genai.types.GenerationConfig(
                    temperature=temperature or self.temperature,
                    max_output_tokens=max_tokens or self.max_tokens,
                )

            # Combine system prompt with user prompt if provided
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"

            response = self.model.generate_content(
                full_prompt,
                generation_config=gen_config,
            )

            # Store for token counting
            self.last_prompt = full_prompt
            self.last_response = response.text

            return response.text

        except Exception as e:
            logger.error(f"❌ Gemini generation failed: {e}")
            raise

    def get_metadata(self) -> dict[str, Any]:
        """Return provider metadata."""
        return {
            "provider": "gemini",
            "model": self.model_name,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
            "type": "api",
            "vendor": "google",
        }

    def get_usage_info(self) -> dict[str, int]:
        """Extract token usage using Gemini's count_tokens() method."""
        if hasattr(self, 'last_prompt') and hasattr(self, 'last_response'):
            if self.last_prompt and self.last_response:
                try:
                    # Count input tokens
                    input_count = self.model.count_tokens(self.last_prompt)
                    input_tokens = input_count.total_tokens

                    # Count output tokens
                    output_count = self.model.count_tokens(self.last_response)
                    output_tokens = output_count.total_tokens

                    return {
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens,
                        "total_tokens": input_tokens + output_tokens
                    }
                except Exception as e:
                    logger.warning(f"⚠️ Gemini token counting failed: {e}, using estimation")

        # Fallback to estimation
        from .token_counter import estimate_tokens
        input_tokens = estimate_tokens(self.last_prompt or "")
        output_tokens = estimate_tokens(self.last_response or "")

        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens
        }

