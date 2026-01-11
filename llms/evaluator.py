"""
RAGAS evaluation wrapper for LLM responses.

Evaluates response quality using RAGAS metrics:
- Coherence: Logical consistency and flow
- Relevance: How well the response addresses the prompt
"""

from typing import Any
from loguru import logger


class RAGASEvaluator:
    """RAGAS-based LLM response evaluator."""

    def __init__(self):
        """Initialize RAGAS evaluator with coherence and relevance metrics."""
        try:
            from ragas import evaluate
            from ragas.metrics import answer_relevancy, faithfulness
            from datasets import Dataset

            self.evaluate = evaluate
            self.Dataset = Dataset

            # Use available metrics (coherence might not be directly available)
            # We'll use answer_relevancy and faithfulness as proxies
            self.metrics = [answer_relevancy, faithfulness]

        except ImportError as e:
            logger.error(
                f"❌ RAGAS dependencies not installed: {e}\n"
                "Install with: pip install ragas datasets"
            )
            raise

    def evaluate_response(
        self, prompt: str, response: str, context: str | None = None
    ) -> dict[str, Any]:
        """
        Evaluate response using RAGAS metrics.

        Args:
            prompt: User prompt/question
            response: LLM generated response
            context: Optional context (not used for basic evaluation)

        Returns:
            Dict with evaluation scores:
            {
                "relevance": float,
                "coherence": float,
                "overall_score": float,
                "metrics_used": list[str]
            }
        """
        try:
            # Create dataset for RAGAS
            # RAGAS expects specific format with question, answer, contexts
            data = {
                "question": [prompt],
                "answer": [response],
                "contexts": [[context or ""]],  # RAGAS requires contexts
                "ground_truth": [response],  # Use response as ground truth for faithfulness
            }
            dataset = self.Dataset.from_dict(data)

            # Evaluate
            results = self.evaluate(dataset, metrics=self.metrics)

            # Extract scores
            relevance_score = float(results.get("answer_relevancy", 0.0))
            coherence_score = float(results.get("faithfulness", 0.0))

            overall_score = (relevance_score + coherence_score) / 2

            return {
                "relevance": round(relevance_score, 3),
                "coherence": round(coherence_score, 3),
                "overall_score": round(overall_score, 3),
                "metrics_used": ["answer_relevancy", "faithfulness"],
            }

        except Exception as e:
            logger.error(f"❌ RAGAS evaluation failed: {e}")
            return {
                "relevance": None,
                "coherence": None,
                "overall_score": None,
                "error": str(e),
                "metrics_used": [],
            }


def evaluate_response(prompt: str, response: str) -> dict[str, Any]:
    """
    Convenience function to evaluate a response.

    Args:
        prompt: User prompt
        response: LLM response

    Returns:
        Evaluation results dict
    """
    try:
        evaluator = RAGASEvaluator()
        return evaluator.evaluate_response(prompt, response)
    except Exception as e:
        logger.warning(f"⚠️ Could not initialize evaluator: {e}")
        return {
            "relevance": None,
            "coherence": None,
            "overall_score": None,
            "error": f"Evaluator initialization failed: {str(e)}",
            "metrics_used": [],
        }
