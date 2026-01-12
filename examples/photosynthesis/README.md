# Photosynthesis Evaluation Example

Real-world example using Wikipedia content about photosynthesis to demonstrate the 4 evaluation modes.

## Files

- **prompt.txt** - Question about photosynthesis
- **context.txt** - Wikipedia excerpt about photosynthesis (source information)
- **ground_truth.txt** - Expected correct answer

## Source

Context extracted from: https://en.wikipedia.org/wiki/Photosynthesis

## Test Commands

### Mode 1: Basic Relevance Only

```bash
/d/gestoria_agentes/.venv/Scripts/python.exe run_llm.py \
  --llm claude \
  --prompt-file examples/photosynthesis/prompt.txt \
  --eval
```

**What it evaluates:**
- ✅ Is the response relevant to the question?
- ❌ Does NOT check for hallucinations (no context)
- ❌ Does NOT measure accuracy (no ground truth)

**Expected result:** `answer_relevancy` score only

---

### Mode 2: With Context (Hallucination Detection)

```bash
/d/gestoria_agentes/.venv/Scripts/python.exe run_llm.py \
  --llm claude \
  --prompt-file examples/photosynthesis/prompt.txt \
  --context-file examples/photosynthesis/context.txt \
  --eval
```

**What it evaluates:**
- ✅ Is the response relevant?
- ✅ **Does the response stay grounded in the provided context?**
- ✅ **Detects if LLM invents information not in context**
- ❌ Does NOT measure accuracy against reference answer

**Expected result:** `answer_relevancy` + `faithfulness` scores

**Example of what faithfulness catches:**
- Context says: "130 terawatts"
- LLM says: "130 terawatts" ✅ High faithfulness
- LLM says: "200 terawatts" ❌ Low faithfulness (hallucination)

---

### Mode 3: With Ground Truth (Accuracy Measurement)

```bash
/d/gestoria_agentes/.venv/Scripts/python.exe run_llm.py \
  --llm claude \
  --prompt-file examples/photosynthesis/prompt.txt \
  --ground-truth-file examples/photosynthesis/ground_truth.txt \
  --eval
```

**What it evaluates:**
- ✅ Is the response relevant?
- ✅ **How accurate is the response compared to the reference answer?**
- ❌ Does NOT check hallucinations (no context)

**Expected result:** `answer_relevancy` + `answer_correctness` scores

**Example of what correctness measures:**
- Ground truth: "converts light energy into chemical energy"
- LLM says: "converts light into chemical energy" ✅ High correctness
- LLM says: "converts heat into energy" ❌ Low correctness (inaccurate)

---

### Mode 4: Complete Evaluation (All Metrics)

```bash
/d/gestoria_agentes/.venv/Scripts/python.exe run_llm.py \
  --llm claude \
  --prompt-file examples/photosynthesis/prompt.txt \
  --context-file examples/photosynthesis/context.txt \
  --ground-truth-file examples/photosynthesis/ground_truth.txt \
  --eval
```

**What it evaluates:**
- ✅ Is the response relevant? (answer_relevancy)
- ✅ Does it stay grounded in context? (faithfulness)
- ✅ Is it accurate vs reference? (answer_correctness)
- ✅ **Is the context high-quality for this question?** (context_precision)

**Expected result:** All 4 metrics

**What context_precision evaluates:**
- Does the context contain the information needed to answer correctly?
- Is the context relevant to the ground truth?
- Quality of the retrieval system (in RAG scenarios)

---

## Understanding the Differences

### Context vs Ground Truth

| Aspect | Context | Ground Truth |
|--------|---------|--------------|
| **What is it?** | Source material/documentation | Expected correct answer |
| **Purpose** | Information the LLM should use | Reference for accuracy check |
| **Analogy** | Textbook given to student | Teacher's answer key |
| **Used for** | Hallucination detection | Accuracy measurement |
| **Metric** | Faithfulness | Answer Correctness |

### Real-World Scenario

**RAG System for Company Documentation:**

1. **User asks:** "What is our vacation policy?"
2. **System retrieves context:** "Employees receive 15 days annual vacation..."
3. **LLM responds:** "You get 15 days of vacation per year"
4. **Ground truth:** "Employees are entitled to 15 working days of annual vacation"

**Evaluation:**
- **Faithfulness:** Does response use only context info? ✅
- **Correctness:** Does response match official policy? ✅
- **Context Precision:** Did retrieval get the right document? ✅

---

## Expected Results

When running with Claude on this photosynthesis example:

**Mode 1 (relevance only):**
```json
{
  "relevance": 0.85,
  "coherence": null,
  "correctness": null,
  "context_quality": null,
  "overall_score": 0.85,
  "metrics_used": ["answer_relevancy"]
}
```

**Mode 2 (+ context):**
```json
{
  "relevance": 0.87,
  "coherence": 0.92,
  "correctness": null,
  "context_quality": null,
  "overall_score": 0.895,
  "metrics_used": ["answer_relevancy", "faithfulness"]
}
```

**Mode 3 (+ ground truth):**
```json
{
  "relevance": 0.87,
  "coherence": null,
  "correctness": 0.88,
  "context_quality": null,
  "overall_score": 0.875,
  "metrics_used": ["answer_relevancy", "answer_correctness"]
}
```

**Mode 4 (complete):**
```json
{
  "relevance": 0.87,
  "coherence": 0.92,
  "correctness": 0.88,
  "context_quality": 0.79,
  "overall_score": 0.865,
  "metrics_used": ["answer_relevancy", "faithfulness", "answer_correctness", "context_precision"]
}
```

---

## Tips for Testing

1. **Compare providers:** Run the same test with `--llm openai`, `--llm gemini`, `--llm claude`
2. **Check logs:** Results are saved in `logs/` directory as JSON files
3. **Modify context:** Try removing information from context.txt and see faithfulness drop
4. **Test hallucinations:** Ask Claude without context and it might add extra info not in source

## Next Steps

After testing this example:
1. Try the `evaluation_demo` example (simpler, about Python)
2. Create your own examples with topics you know well
3. Compare different LLM providers using the same prompts
4. Use for interview demonstration showing understanding of evaluation strategies
