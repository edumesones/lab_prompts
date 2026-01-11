"""
Token counting utilities for LLM providers.

Provides fallback methods for counting tokens when API doesn't return usage info.
"""

from typing import Any


def estimate_tokens(text: str) -> int:
    """
    Rough estimation of token count.

    Rule of thumb: ~4 characters per token for English text.
    This is a fallback when no better method is available.

    Args:
        text: Text to estimate tokens for

    Returns:
        Estimated token count
    """
    if not text:
        return 0
    return max(1, len(text) // 4)


def count_with_tiktoken(text: str, model: str = "gpt-4") -> int:
    """
    Count tokens using tiktoken library (accurate for OpenAI models).

    Args:
        text: Text to count tokens for
        model: Model name for encoding selection

    Returns:
        Accurate token count

    Raises:
        ImportError: If tiktoken is not installed
    """
    try:
        import tiktoken
    except ImportError:
        raise ImportError(
            "tiktoken is required for accurate token counting. "
            "Install it with: pip install tiktoken"
        )

    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        # Fallback to cl100k_base encoding (used by gpt-4, gpt-3.5-turbo)
        encoding = tiktoken.get_encoding("cl100k_base")

    return len(encoding.encode(text))


def count_messages_tokens(messages: list[dict[str, str]], model: str = "gpt-4") -> dict[str, int]:
    """
    Count tokens for chat messages format (OpenAI style).

    Args:
        messages: List of message dicts with 'role' and 'content'
        model: Model name for accurate counting

    Returns:
        Dict with token breakdown:
        {
            "prompt_tokens": int,
            "estimated": bool
        }
    """
    try:
        import tiktoken

        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")

        # OpenAI chat format tokens calculation
        # Each message follows: <|start|>{role/name}\n{content}<|end|>\n
        tokens_per_message = 3
        tokens_per_name = 1

        num_tokens = 0
        for message in messages:
            num_tokens += tokens_per_message
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":
                    num_tokens += tokens_per_name

        num_tokens += 3  # Every reply is primed with <|start|>assistant<|message|>

        return {
            "prompt_tokens": num_tokens,
            "estimated": False
        }

    except ImportError:
        # Fallback to rough estimation
        total_text = " ".join(msg.get("content", "") for msg in messages)
        return {
            "prompt_tokens": estimate_tokens(total_text),
            "estimated": True
        }


def count_prompt_and_completion(prompt: str, completion: str, model: str = "gpt-4") -> dict[str, Any]:
    """
    Count tokens for both prompt and completion.

    Args:
        prompt: Input prompt text
        completion: Generated completion text
        model: Model name

    Returns:
        Dict with token counts:
        {
            "input_tokens": int,
            "output_tokens": int,
            "total_tokens": int,
            "estimated": bool
        }
    """
    try:
        input_tokens = count_with_tiktoken(prompt, model)
        output_tokens = count_with_tiktoken(completion, model)

        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "estimated": False
        }
    except ImportError:
        input_tokens = estimate_tokens(prompt)
        output_tokens = estimate_tokens(completion)

        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens,
            "estimated": True
        }
