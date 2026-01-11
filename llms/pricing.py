"""
Model pricing data and cost calculation utilities.

Pricing sources (as of January 2025):
- OpenAI: https://openai.com/pricing
- Anthropic: https://www.anthropic.com/pricing
- Google Gemini: https://ai.google.dev/pricing
- HuggingFace: Usage-based or free tier
"""

from typing import Any

# Pricing in USD per 1 million tokens
# Last updated: 2025-01-10
MODEL_PRICING = {
    # OpenAI Models
    "gpt-4-turbo": {
        "input": 10.00,
        "output": 30.00
    },
    "gpt-4": {
        "input": 30.00,
        "output": 60.00
    },
    "gpt-3.5-turbo": {
        "input": 0.50,
        "output": 1.50
    },
    "gpt-4o": {
        "input": 5.00,
        "output": 15.00
    },
    "gpt-4o-mini": {
        "input": 0.15,
        "output": 0.60
    },

    # Anthropic Claude Models
    "claude-sonnet-4-20250514": {
        "input": 3.00,
        "output": 15.00
    },
    "claude-opus-3-20240229": {
        "input": 15.00,
        "output": 75.00
    },
    "claude-sonnet-3-5-20240229": {
        "input": 3.00,
        "output": 15.00
    },
    "claude-haiku-3-20240307": {
        "input": 0.25,
        "output": 1.25
    },

    # Google Gemini Models
    "gemini-1.5-pro": {
        "input": 1.25,
        "output": 5.00
    },
    "gemini-1.5-flash": {
        "input": 0.075,
        "output": 0.30
    },
    "gemini-pro": {
        "input": 0.50,
        "output": 1.50
    },

    # HuggingFace (free tier or usage-based)
    "deepseek-ai/DeepSeek-R1:novita": {
        "input": 0.0,
        "output": 0.0
    },

    # Default fallback for unknown models
    "default": {
        "input": 0.0,
        "output": 0.0
    }
}


class CostCalculator:
    """Calculate costs for LLM API calls."""

    @staticmethod
    def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> dict[str, Any]:
        """
        Calculate cost based on token usage and model pricing.

        Args:
            model: Model name
            input_tokens: Number of input/prompt tokens
            output_tokens: Number of output/completion tokens

        Returns:
            Dict with cost breakdown:
            {
                "input_cost": float,
                "output_cost": float,
                "total_cost": float,
                "currency": "USD",
                "pricing_available": bool
            }
        """
        # Get pricing for model, fallback to default if not found
        pricing_available = model in MODEL_PRICING
        pricing = MODEL_PRICING.get(model, MODEL_PRICING["default"])

        # Calculate costs (pricing is per 1M tokens)
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        total_cost = input_cost + output_cost

        return {
            "input_cost": round(input_cost, 6),
            "output_cost": round(output_cost, 6),
            "total_cost": round(total_cost, 6),
            "currency": "USD",
            "pricing_available": pricing_available
        }

    @staticmethod
    def get_model_pricing(model: str) -> dict[str, float] | None:
        """
        Get pricing info for a specific model.

        Args:
            model: Model name

        Returns:
            Dict with input/output pricing or None if not found
        """
        return MODEL_PRICING.get(model)

    @staticmethod
    def format_cost(cost: float) -> str:
        """
        Format cost for display.

        Args:
            cost: Cost in USD

        Returns:
            Formatted string (e.g., "$0.0006")
        """
        return f"${cost:.6f}".rstrip('0').rstrip('.')
