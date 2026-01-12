"""
Abstract base class for LLM providers.
All LLM providers must implement this interface.
"""

from abc import ABC, abstractmethod
from typing import Any
import time


class LLMProvider(ABC):
    """Abstract base for all LLM providers."""

    def __init__(self, config: dict[str, Any]):
        """
        Initialize LLM provider.

        Args:
            config: Configuration dictionary with provider-specific settings
        """
        self.config = config
        self.model_name = config.get("model_name")
        self.temperature = config.get("temperature", 0.1)
        self.max_tokens = config.get("max_tokens", 4096)

        # Logging configuration
        self.enable_logging = config.get("enable_logging", True)
        self.enable_evaluation = config.get("enable_evaluation", False)
        self.eval_context = config.get("eval_context")
        self.eval_ground_truth = config.get("eval_ground_truth")
        self.logger = None

        if self.enable_logging:
            from .logger import ExecutionLogger
            self.logger = ExecutionLogger()

    @abstractmethod
    def generate(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """
        Generate response from prompt.

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Override temperature (uses default if None)
            max_tokens: Override max tokens (uses default if None)

        Returns:
            Generated text response
        """
        pass

    @abstractmethod
    def get_metadata(self) -> dict[str, Any]:
        """
        Return provider metadata for tracking and comparison.

        Returns:
            Dict with provider info (provider name, model, parameters, etc.)
        """
        pass

    @abstractmethod
    def get_usage_info(self) -> dict[str, int]:
        """
        Extract token usage information from last generation.

        Must be implemented by each provider to extract usage from their API response.

        Returns:
            Dict with token counts:
            {
                "input_tokens": int,
                "output_tokens": int,
                "total_tokens": int
            }
        """
        pass

    def generate_with_logging(
        self,
        prompt: str,
        system_prompt: str | None = None,
        temperature: float | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """
        Generate response with automatic logging.

        This method wraps the generate() method to add automatic logging of:
        - Prompt and response
        - Token usage and costs
        - Latency
        - Optional evaluation metrics

        Args:
            prompt: User prompt
            system_prompt: Optional system prompt
            temperature: Override temperature (uses default if None)
            max_tokens: Override max tokens (uses default if None)

        Returns:
            Generated text response
        """
        # Measure latency
        start_time = time.perf_counter()

        # Generate response
        response = self.generate(prompt, system_prompt, temperature, max_tokens)

        # Calculate latency in milliseconds
        end_time = time.perf_counter()
        latency_ms = (end_time - start_time) * 1000

        # Log execution if enabled
        if self.enable_logging and self.logger:
            try:
                from .pricing import CostCalculator

                # Get token usage from provider
                usage = self.get_usage_info()

                # Get metadata
                metadata = self.get_metadata()

                # Calculate cost
                cost_calc = CostCalculator()
                cost = cost_calc.calculate_cost(
                    self.model_name,
                    usage["input_tokens"],
                    usage["output_tokens"]
                )

                # Log execution
                log_file = self.logger.log_execution(
                    prompt={"user": prompt, "system": system_prompt},
                    response=response,
                    metadata=metadata,
                    tokens=usage,
                    cost=cost,
                    latency=latency_ms
                )

                # Add evaluation if enabled
                if self.enable_evaluation and log_file:
                    try:
                        from .evaluator import evaluate_response
                        eval_results = evaluate_response(
                            prompt,
                            response,
                            context=self.eval_context,
                            ground_truth=self.eval_ground_truth
                        )
                        self.logger.add_evaluation_metrics(log_file, eval_results)
                    except Exception as e:
                        from loguru import logger as log
                        log.warning(f"⚠️ Evaluation failed: {e}")

            except Exception as e:
                from loguru import logger as log
                log.warning(f"⚠️ Logging failed: {e}")

        return response

