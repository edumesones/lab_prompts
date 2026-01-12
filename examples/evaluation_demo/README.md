# RAGAS Evaluation Demo Examples

This directory contains example files demonstrating the adaptive RAGAS evaluation system.

## Files

- **prompt.txt** - The question to ask the LLM
- **context.txt** - Reference context (for faithfulness evaluation)
- **ground_truth.txt** - Expected correct answer (for correctness evaluation)

## Evaluation Modes

Our system uses **adaptive evaluation** - metrics activate based on what data you provide.

### Mode 1: Basic Relevance Only

**Command:**
```bash
/d/gestoria_agentes/.venv/Scripts/python.exe run_llm.py \
  --llm claude \
  --prompt-file examples/evaluation_demo/prompt.txt \
  --eval
```

**Metrics:**
- ✅ answer_relevancy

**Use case:** Quick relevance check without reference data

---

### Mode 2: With Context (Hallucination Detection)

**Command:**
```bash
/d/gestoria_agentes/.venv/Scripts/python.exe run_llm.py \
  --llm claude \
  --prompt-file examples/evaluation_demo/prompt.txt \
  --context-file examples/evaluation_demo/context.txt \
  --eval
```

**Metrics:**
- ✅ answer_relevancy
- ✅ faithfulness (checks if response stays grounded in context)

**Use case:** RAG applications, document Q&A systems

---

### Mode 3: With Ground Truth (Accuracy Measurement)

**Command:**
```bash
/d/gestoria_agentes/.venv/Scripts/python.exe run_llm.py \
  --llm claude \
  --prompt-file examples/evaluation_demo/prompt.txt \
  --ground-truth-file examples/evaluation_demo/ground_truth.txt \
  --eval
```

**Metrics:**
- ✅ answer_relevancy
- ✅ answer_correctness (compares response vs. reference answer)

**Use case:** Benchmarking LLM accuracy, quality assurance

---

### Mode 4: Complete RAG Evaluation (All Metrics)

**Command:**
```bash
/d/gestoria_agentes/.venv/Scripts/python.exe run_llm.py \
  --llm claude \
  --prompt-file examples/evaluation_demo/prompt.txt \
  --context-file examples/evaluation_demo/context.txt \
  --ground-truth-file examples/evaluation_demo/ground_truth.txt \
  --eval
```

**Metrics:**
- ✅ answer_relevancy
- ✅ faithfulness (hallucination detection)
- ✅ answer_correctness (accuracy measurement)
- ✅ context_precision (retrieval quality)

**Use case:** Complete RAG system evaluation and optimization

---

## Understanding the Output

The evaluation results will be saved in the JSON log file (in `logs/` directory) with this structure:

```json
{
  "evaluation": {
    "relevance": 0.85,        // How well response addresses the question
    "coherence": 0.92,        // Faithfulness to context (if provided)
    "correctness": 0.88,      // Accuracy vs ground truth (if provided)
    "context_quality": 0.79,  // Quality of context retrieval (if both provided)
    "overall_score": 0.86,    // Average of all evaluated metrics
    "metrics_used": [
      "answer_relevancy",
      "faithfulness",
      "answer_correctness",
      "context_precision"
    ]
  }
}
```

## Inline Flag Usage

You can also use inline text instead of files:

```bash
# With inline context
/d/gestoria_agentes/.venv/Scripts/python.exe run_llm.py \
  --llm claude \
  --prompt "What is Python?" \
  --context "Python is a high-level programming language created in 1991." \
  --eval

# With inline ground truth
/d/gestoria_agentes/.venv/Scripts/python.exe run_llm.py \
  --llm claude \
  --prompt "What is Python?" \
  --ground-truth "Python is a high-level interpreted language known for readability." \
  --eval
```

## Comparing LLM Providers

Test the same prompt across different LLMs:

```bash
# Test with Claude
/d/gestoria_agentes/.venv/Scripts/python.exe run_llm.py \
  --llm claude \
  --prompt-file examples/evaluation_demo/prompt.txt \
  --context-file examples/evaluation_demo/context.txt \
  --ground-truth-file examples/evaluation_demo/ground_truth.txt \
  --eval

# Test with OpenAI
/d/gestoria_agentes/.venv/Scripts/python.exe run_llm.py \
  --llm openai \
  --prompt-file examples/evaluation_demo/prompt.txt \
  --context-file examples/evaluation_demo/context.txt \
  --ground-truth-file examples/evaluation_demo/ground_truth.txt \
  --eval

# Test with Gemini
/d/gestoria_agentes/.venv/Scripts/python.exe run_llm.py \
  --llm gemini \
  --prompt-file examples/evaluation_demo/prompt.txt \
  --context-file examples/evaluation_demo/context.txt \
  --ground-truth-file examples/evaluation_demo/ground_truth.txt \
  --eval
```

Then compare the evaluation scores in the log files!

## For Interview Demonstration

To showcase your understanding of LLM evaluation:

1. **Start simple** - Show basic relevance evaluation
2. **Add context** - Demonstrate hallucination detection
3. **Add ground truth** - Show accuracy measurement
4. **Complete evaluation** - Display full RAG assessment
5. **Compare providers** - Benchmark different LLMs

This progressive demonstration shows:
- ✅ Understanding of evaluation metrics
- ✅ Knowledge of metric selection trade-offs
- ✅ Practical implementation skills
- ✅ System design thinking (adaptive architecture)

See `docs/METRIC_SELECTION.md` for detailed rationale behind metric choices.
