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
            from langchain_openai import ChatOpenAI, OpenAIEmbeddings
            import os

            self.evaluate = evaluate
            self.Dataset = Dataset

            # Configure LLM and embeddings explicitly for RAGAS
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                logger.warning("⚠️ OPENAI_API_KEY not set - RAGAS evaluation may fail")
                self.llm = None
                self.embeddings = None
            else:
                # Use modern OpenAI API with explicit configuration
                self.llm = ChatOpenAI(
                    model="gpt-3.5-turbo",
                    api_key=api_key,
                    temperature=0
                )
                self.embeddings = OpenAIEmbeddings(
                    model="text-embedding-3-small",
                    api_key=api_key
                )

            # Use available metrics (coherence might not be directly available)
            # We'll use answer_relevancy and faithfulness as proxies
            self.metrics = [answer_relevancy, faithfulness]

        except ImportError as e:
            logger.error(
                f"❌ RAGAS dependencies not installed: {e}\n"
                "Install with: pip install ragas datasets langchain-openai"
            )
            raise

    def evaluate_response(
        self,
        prompt: str,
        response: str,
        context: str | None = None,
        ground_truth: str | None = None
    ) -> dict[str, Any]:
        """
        Evaluate response using RAGAS metrics (adaptive based on available data).

        Metrics used (adaptive):
        - answer_relevancy: Always evaluated (measures if response addresses prompt)
        - faithfulness: Only if context provided (checks for hallucinations)
        - answer_correctness: Only if ground_truth provided (measures accuracy)
        - context_precision: Only if both context + ground_truth provided (RAG quality)

        Args:
            prompt: User prompt/question
            response: LLM generated response
            context: Optional context. If provided, enables faithfulness metric.
            ground_truth: Optional reference answer. If provided, enables answer_correctness.

        Returns:
            Dict with evaluation scores:
            {
                "relevance": float,
                "coherence": float | None (faithfulness score),
                "correctness": float | None (answer_correctness score),
                "context_quality": float | None (context_precision score),
                "overall_score": float,
                "metrics_used": list[str]
            }

        Note: Metrics adapt based on available data. See METRIC_SELECTION.md for details.
        """
        try:
            from ragas.metrics import (
                answer_relevancy,
                faithfulness,
                answer_correctness,
                context_precision
            )

            # Determine available metrics based on provided data
            metrics_to_use = [answer_relevancy]  # Always available
            has_context = context and context.strip()
            has_ground_truth = ground_truth and ground_truth.strip()

            # Build dataset base
            data = {
                "question": [prompt],
                "answer": [response],
            }

            # Add context if exists (enables faithfulness and context_precision)
            if has_context:
                data["contexts"] = [[context]]
                metrics_to_use.append(faithfulness)
            else:
                # RAGAS requires contexts even if empty
                data["contexts"] = [[""]]

            # Add ground_truth if exists (enables answer_correctness)
            if has_ground_truth:
                data["ground_truth"] = [ground_truth]
                metrics_to_use.append(answer_correctness)

                # Add context_precision only if BOTH context and ground_truth exist
                if has_context:
                    metrics_to_use.append(context_precision)

            dataset = self.Dataset.from_dict(data)

            # Evaluar con métricas disponibles y LLM/embeddings explícitos
            if self.llm and self.embeddings:
                results = self.evaluate(
                    dataset,
                    metrics=metrics_to_use,
                    llm=self.llm,
                    embeddings=self.embeddings
                )
            else:
                # Fallback sin configuración explícita (puede fallar)
                logger.warning("⚠️ Evaluating without explicit LLM/embeddings configuration")
                results = self.evaluate(dataset, metrics=metrics_to_use)

            # Convertir a dict (FIX PRINCIPAL del error .get())
            try:
                # RAGAS 0.4.x uses to_pandas() instead of to_dict()
                if hasattr(results, 'to_pandas'):
                    df = results.to_pandas()
                    if len(df) > 0:
                        results_dict = df.iloc[0].to_dict()
                    else:
                        raise ValueError("Empty results from RAGAS evaluation")
                elif hasattr(results, 'scores'):
                    # Direct access to scores attribute
                    results_dict = results.scores.iloc[0].to_dict() if hasattr(results.scores, 'iloc') else dict(results.scores)
                elif hasattr(results, '__getitem__'):
                    # Fallback: acceso por índice
                    results_dict = {}
                    if "answer_relevancy" in results:
                        val = results["answer_relevancy"]
                        results_dict["answer_relevancy"] = float(val[0]) if hasattr(val, '__getitem__') else float(val)
                    if "faithfulness" in results:
                        val = results["faithfulness"]
                        results_dict["faithfulness"] = float(val[0]) if hasattr(val, '__getitem__') else float(val)
                else:
                    raise AttributeError("Cannot convert EvaluationResult to dict")
            except Exception as conv_error:
                logger.warning(f"⚠️ Error converting results: {conv_error}")
                logger.warning(f"Results type: {type(results)}")
                if hasattr(results, 'scores'):
                    logger.warning(f"Scores available: {results.scores}")
                # Last resort: return default values
                results_dict = {"answer_relevancy": 0.0}

            # Extract available scores
            relevance_score = float(results_dict.get("answer_relevancy", 0.0))

            # Verify evaluation worked
            if relevance_score == 0.0 and "answer_relevancy" not in results_dict:
                logger.warning("⚠️ RAGAS evaluation produced no valid scores - check OpenAI API key and connectivity")
                return {
                    "relevance": None,
                    "coherence": None,
                    "correctness": None,
                    "context_quality": None,
                    "overall_score": None,
                    "error": "RAGAS evaluation failed - no valid scores produced. Check OpenAI API key and logs.",
                    "metrics_used": [],
                }

            # Extract scores for metrics that were evaluated
            coherence_score = None
            correctness_score = None
            context_quality_score = None
            scores_for_average = [relevance_score]
            metrics_used = ["answer_relevancy"]

            # Faithfulness (coherence) - only if context provided
            if has_context and "faithfulness" in results_dict:
                coherence_score = float(results_dict.get("faithfulness", 0.0))
                scores_for_average.append(coherence_score)
                metrics_used.append("faithfulness")

            # Answer correctness - only if ground_truth provided
            if has_ground_truth and "answer_correctness" in results_dict:
                correctness_score = float(results_dict.get("answer_correctness", 0.0))
                scores_for_average.append(correctness_score)
                metrics_used.append("answer_correctness")

            # Context precision - only if both context and ground_truth provided
            if has_context and has_ground_truth and "context_precision" in results_dict:
                context_quality_score = float(results_dict.get("context_precision", 0.0))
                scores_for_average.append(context_quality_score)
                metrics_used.append("context_precision")

            # Calculate overall score as average of available metrics
            overall_score = sum(scores_for_average) / len(scores_for_average)

            # Log results
            log_parts = [f"relevancy={relevance_score:.3f}"]
            if coherence_score is not None:
                log_parts.append(f"faithfulness={coherence_score:.3f}")
            if correctness_score is not None:
                log_parts.append(f"correctness={correctness_score:.3f}")
            if context_quality_score is not None:
                log_parts.append(f"context_precision={context_quality_score:.3f}")

            logger.info(f"📊 Evaluation complete: {', '.join(log_parts)}")

            return {
                "relevance": round(relevance_score, 3),
                "coherence": round(coherence_score, 3) if coherence_score is not None else None,
                "correctness": round(correctness_score, 3) if correctness_score is not None else None,
                "context_quality": round(context_quality_score, 3) if context_quality_score is not None else None,
                "overall_score": round(overall_score, 3),
                "metrics_used": metrics_used,
            }

        except Exception as e:
            logger.error(f"❌ RAGAS evaluation failed: {e}")
            return {
                "relevance": None,
                "coherence": None,
                "correctness": None,
                "context_quality": None,
                "overall_score": None,
                "error": str(e),
                "metrics_used": [],
            }


def evaluate_response(
    prompt: str,
    response: str,
    context: str | None = None,
    ground_truth: str | None = None
) -> dict[str, Any]:
    """
    Convenience function to evaluate a response.

    Args:
        prompt: User prompt
        response: LLM response
        context: Optional context for faithfulness evaluation
        ground_truth: Optional ground truth answer for correctness evaluation

    Returns:
        Evaluation results dict
    """
    try:
        evaluator = RAGASEvaluator()
        return evaluator.evaluate_response(prompt, response, context, ground_truth)
    except Exception as e:
        logger.warning(f"⚠️ Could not initialize evaluator: {e}")
        return {
            "relevance": None,
            "coherence": None,
            "correctness": None,
            "context_quality": None,
            "overall_score": None,
            "error": f"Evaluator initialization failed: {str(e)}",
            "metrics_used": [],
        }
