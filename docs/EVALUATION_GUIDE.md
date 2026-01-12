# Complete RAGAS Evaluation Guide

## Overview

This system implements an **adaptive evaluation strategy** using RAGAS metrics. Metrics automatically activate based on available data, making evaluation practical for various scenarios from basic relevance checks to complete RAG system assessment.

## Quick Start

### Basic Usage (Relevance Only)

```bash
/d/gestoria_agentes/.venv/Scripts/python.exe run_llm.py \
  --llm claude \
  --prompt "What is Python?" \
  --eval
```

**Result:** Only `answer_relevancy` metric

### With Context (Hallucination Detection)

```bash
/d/gestoria_agentes/.venv/Scripts/python.exe run_llm.py \
  --llm claude \
  --prompt "What is Python?" \
  --context "Python is a high-level programming language..." \
  --eval
```

**Result:** `answer_relevancy` + `faithfulness` metrics

### With Ground Truth (Accuracy Measurement)

```bash
/d/gestoria_agentes/.venv/Scripts/python.exe run_llm.py \
  --llm claude \
  --prompt "What is Python?" \
  --ground-truth "Python is a high-level interpreted language..." \
  --eval
```

**Result:** `answer_relevancy` + `answer_correctness` metrics

### Complete Evaluation (All Metrics)

```bash
/d/gestoria_agentes/.venv/Scripts/python.exe run_llm.py \
  --llm claude \
  --prompt "What is Python?" \
  --context "Python is a high-level programming language..." \
  --ground-truth "Python is a high-level interpreted language..." \
  --eval
```

**Result:** All 4 metrics (relevancy, faithfulness, correctness, context_precision)

## Available Flags

### Evaluation Flags

- `--eval` - Enable RAGAS evaluation
- `--context <text>` - Provide context for faithfulness evaluation
- `--context-file <path>` - Read context from file
- `--ground-truth <text>` - Provide reference answer for correctness evaluation
- `--ground-truth-file <path>` - Read ground truth from file

### Other Flags

- `--llm <name>` - LLM provider (openai, claude, gemini, huggingface)
- `--prompt <text>` - Direct prompt text
- `--prompt-file <path>` - Read prompt from file
- `--system <text>` - System prompt (optional)
- `--no-log` - Disable automatic JSON logging

## Metrics Explained

### 1. Answer Relevancy (Always Available)

**What:** Measures if the response addresses the question

**Requirements:** Prompt + Response only

**How it works:**
1. Generates 3 questions that would fit the response
2. Compares these questions to the original using embeddings
3. Higher similarity = more relevant response

**Score interpretation:**
- 0.9-1.0: Highly relevant, directly answers question
- 0.7-0.9: Relevant with minor tangents
- 0.5-0.7: Partially relevant
- <0.5: Off-topic or irrelevant

---

### 2. Faithfulness (Context Required)

**What:** Detects hallucinations - checks if response is grounded in context

**Requirements:** Prompt + Response + Context

**How it works:**
1. Breaks response into individual claims
2. For each claim, verifies if it can be inferred from context
3. Score = supported claims / total claims

**Score interpretation:**
- 0.9-1.0: Excellent - all claims supported by context
- 0.7-0.9: Good - most claims supported
- 0.5-0.7: Fair - many unsupported claims
- <0.5: Poor - significant hallucination

---

### 3. Answer Correctness (Ground Truth Required)

**What:** Measures accuracy against a reference answer

**Requirements:** Prompt + Response + Ground Truth

**How it works:**
1. Compares semantic similarity between response and ground truth
2. Checks factual alignment
3. Considers completeness

**Score interpretation:**
- 0.9-1.0: Highly accurate
- 0.7-0.9: Mostly correct with minor errors
- 0.5-0.7: Partially correct
- <0.5: Significantly incorrect

---

### 4. Context Precision (Context + Ground Truth Required)

**What:** Evaluates quality of retrieved context (for RAG systems)

**Requirements:** Prompt + Response + Context + Ground Truth

**How it works:**
1. Checks if context contains information relevant to ground truth
2. Measures how much unnecessary information is in context
3. Higher precision = better retrieval quality

**Score interpretation:**
- 0.9-1.0: Excellent retrieval - highly relevant context
- 0.7-0.9: Good retrieval - mostly relevant
- 0.5-0.7: Fair - mixed relevance
- <0.5: Poor - irrelevant or noisy context

---

## Evaluation Modes Matrix

| Mode | Flags Required | Metrics | Use Case |
|------|---------------|---------|----------|
| **Basic** | `--eval` | answer_relevancy | Quick relevance check |
| **RAG Without GT** | `--eval --context` | answer_relevancy, faithfulness | Document Q&A, RAG apps |
| **Accuracy Test** | `--eval --ground-truth` | answer_relevancy, answer_correctness | Benchmarking, QA |
| **Complete RAG** | `--eval --context --ground-truth` | All 4 metrics | RAG optimization |

## Output Format

Evaluation results are saved in the JSON log file with this structure:

```json
{
  "prompt": "What is Python?",
  "response": "Python is a high-level...",
  "model": "claude-sonnet-4-20250514",
  "evaluation": {
    "relevance": 0.85,
    "coherence": 0.92,
    "correctness": 0.88,
    "context_quality": 0.79,
    "overall_score": 0.86,
    "metrics_used": [
      "answer_relevancy",
      "faithfulness",
      "answer_correctness",
      "context_precision"
    ]
  }
}
```

## Example Files

Demo examples are available in `examples/evaluation_demo/`:

- `prompt.txt` - Sample question
- `context.txt` - Reference context
- `ground_truth.txt` - Expected answer
- `README.md` - Detailed usage examples

## Best Practices

### For Development

1. **Start with basic evaluation** - Test relevance first
2. **Add context for RAG** - Enable hallucination detection
3. **Use ground truth sparingly** - Only when you have reference answers
4. **Compare LLM providers** - Benchmark using same prompts/context

### For Production

1. **Use appropriate metrics** - Don't require ground truth if unavailable
2. **Monitor trends** - Track scores over time
3. **Set thresholds** - Define minimum acceptable scores
4. **Log everything** - Keep evaluation history for analysis

### For Interviews

1. **Demonstrate progression** - Show all 4 evaluation modes
2. **Explain trade-offs** - Discuss why each metric was selected
3. **Show metric selection rationale** - Reference `docs/METRIC_SELECTION.md`
4. **Compare providers** - Benchmark Claude vs OpenAI vs Gemini

## Technical Details

### Requirements

- OpenAI API key (RAGAS uses OpenAI for LLM and embeddings internally)
- Python 3.11+
- Dependencies: ragas, datasets, langchain-openai

### Performance

- Basic evaluation (relevancy only): ~8-10 seconds
- With context (+ faithfulness): ~12-15 seconds
- Complete evaluation (all metrics): ~20-25 seconds

### Cost Considerations

Each evaluation makes calls to:
- OpenAI LLM (GPT-3.5-turbo) for metric computation
- OpenAI Embeddings (text-embedding-3-small) for similarity

Estimated cost per evaluation: $0.001-0.003 USD

## Troubleshooting

### "OpenAI API key not set"

**Solution:** Ensure `.env` file has `OPENAI_API_KEY=your-key-here` (no space after =)

### "RAGAS evaluation failed"

**Common causes:**
1. Missing OpenAI API key
2. Network connectivity issues
3. Invalid context or ground truth format

**Solution:** Check logs for specific error, verify API key, ensure text fields are non-empty

### "Evaluation produces 0.0 scores"

**Cause:** Evaluation ran but failed to compute metrics

**Solution:** Check if OpenAI API key is valid and has credits

## Advanced Usage

### Custom Evaluation in Python

```python
from llms.evaluator import RAGASEvaluator

evaluator = RAGASEvaluator()

# Basic evaluation
result = evaluator.evaluate_response(
    prompt="What is Python?",
    response="Python is a programming language."
)

# With context
result = evaluator.evaluate_response(
    prompt="What is Python?",
    response="Python is a programming language.",
    context="Python is a high-level language created in 1991."
)

# Complete evaluation
result = evaluator.evaluate_response(
    prompt="What is Python?",
    response="Python is a programming language.",
    context="Python is a high-level language created in 1991.",
    ground_truth="Python is a high-level interpreted language."
)

print(result)
# {
#   "relevance": 0.85,
#   "coherence": 0.92,
#   "correctness": 0.88,
#   "context_quality": 0.79,
#   "overall_score": 0.86,
#   "metrics_used": [...]
# }
```

## References

- **Metric Selection Rationale:** `docs/METRIC_SELECTION.md`
- **Demo Examples:** `examples/evaluation_demo/README.md`
- **RAGAS Documentation:** https://docs.ragas.io/
- **OpenAI Pricing:** https://openai.com/pricing

## Summary

This evaluation system provides:

✅ **Adaptive metrics** - Only compute what's possible with available data
✅ **Progressive enhancement** - Start simple, add complexity as needed
✅ **Clear interpretation** - Well-documented score meanings
✅ **Production-ready** - Robust error handling and logging
✅ **Interview-friendly** - Demonstrates evaluation strategy understanding

See `docs/METRIC_SELECTION.md` for detailed rationale behind architectural decisions.
