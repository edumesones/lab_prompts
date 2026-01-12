"""
RAGAS evaluation wrapper for LLM responses.

Evaluates response quality using RAGAS metrics:
- Coherence: Logical consistency and flow
- Relevance: How well the response addresses the prompt

How does it work?
1. How do you calculate faithfulness?
This metric monitors hallucinations. It checks whether what your model says is true based solely on the context you gave it.
Step 1 (Breakdown): Ragas asks the evaluating LLM to break down your model's response into individual sentences or statements.
Step 2 (Verification): Then, for each statement, it asks the LLM, ‘Can this statement be logically deduced from the context provided?’
Calculation: If your response has 10 statements and 8 are supported by the context, your score is 0.8.
2. How does it calculate answer_relevancy?
This metric measures whether the response is relevant to the question, without going off on tangents. It does this with reverse engineering.
Step 1 (Question generation): Ragas takes the answer your model gave and asks the evaluating LLM: ‘Generate 3 possible questions that would have this answer.’
Step 2 (Mathematical comparison): It then uses an Embeddings model to compare the vector similarity between those invented questions and your user's original question.
The logic: If the answer is good, the question that ‘inspires’ it should be almost identical to the original. If the model answered about apples when you asked about pears, the generated question will be about apples and will not match.

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
        Evaluate response using RAGAS metrics (adaptive based on available data).

        Metrics used:
        - answer_relevancy: Always evaluated (measures if response addresses prompt)
        - faithfulness: Only if context provided (checks for hallucinations)

        Args:
            prompt: User prompt/question
            response: LLM generated response
            context: Optional context. If provided, enables faithfulness metric.

        Returns:
            Dict with evaluation scores:
            {
                "relevance": float,
                "coherence": float | None (None if no context),
                "overall_score": float,
                "metrics_used": list[str]
            }

        Note: Without context, only relevance can be measured. Overall score
              will equal relevance score in this case.
        """
        try:
            from ragas.metrics import answer_relevancy, faithfulness

            # Determinar métricas disponibles
            metrics_to_use = [answer_relevancy]  # Siempre disponible
            has_context = context and context.strip()

            # Crear dataset base
            data = {
                "question": [prompt],
                "answer": [response],
            }

            # Agregar context solo si existe
            if has_context:
                data["contexts"] = [[context]]
                metrics_to_use.append(faithfulness)
            else:
                # RAGAS puede requerir contexts aunque sea vacío
                data["contexts"] = [[""]]

            dataset = self.Dataset.from_dict(data)

            # Evaluar con métricas disponibles
            results = self.evaluate(dataset, metrics=metrics_to_use)

            # Convertir a dict (FIX PRINCIPAL del error .get())
            try:
                if hasattr(results, 'to_dict'):
                    results_dict = results.to_dict('records')[0]
                elif hasattr(results, '__getitem__'):
                    # Fallback: acceso por índice
                    results_dict = {
                        "answer_relevancy": float(results["answer_relevancy"][0]) if "answer_relevancy" in results else 0.0,
                        "faithfulness": float(results["faithfulness"][0]) if "faithfulness" in results else 0.0
                    }
                else:
                    raise AttributeError("Cannot convert EvaluationResult to dict")
            except Exception as conv_error:
                logger.warning(f"⚠️ Error converting results: {conv_error}, trying direct access")
                results_dict = {"answer_relevancy": 0.0}

            # Extraer scores disponibles
            relevance_score = float(results_dict.get("answer_relevancy", 0.0))

            # Faithfulness solo si se evaluó
            if has_context and "faithfulness" in results_dict:
                coherence_score = float(results_dict.get("faithfulness", 0.0))
                overall_score = (relevance_score + coherence_score) / 2
                metrics_used = ["answer_relevancy", "faithfulness"]
                logger.info(f"📊 Evaluation complete: relevancy={relevance_score:.3f}, faithfulness={coherence_score:.3f}")
            else:
                coherence_score = None
                overall_score = relevance_score
                metrics_used = ["answer_relevancy"]
                logger.info(f"📊 Evaluation complete (no context): relevancy={relevance_score:.3f}")

            return {
                "relevance": round(relevance_score, 3),
                "coherence": round(coherence_score, 3) if coherence_score is not None else None,
                "overall_score": round(overall_score, 3),
                "metrics_used": metrics_used,
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
