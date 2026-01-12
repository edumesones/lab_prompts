# RAGAS Metric Selection Strategy

## Overview

This document explains the rationale behind selecting specific RAGAS metrics for LLM response evaluation in our system.

## Selection Criteria

When choosing metrics, we prioritized:

1. **Practical Applicability** - Metrics that work in real-world scenarios
2. **Progressive Enhancement** - Ability to add more metrics as data availability increases
3. **Clear Use Cases** - Each metric serves a distinct evaluation purpose
4. **Minimal Overhead** - Avoiding metrics that require excessive setup or ground truth data
5. **Demonstration Value** - Showcasing understanding of evaluation strategies for interviews

## Selected Metrics

### 1. Answer Relevancy ✅ **[CORE - Always Active]**

**What it measures**: Whether the response actually addresses the question asked

**Requirements**:
- ✅ Prompt
- ✅ Response
- ❌ Context (not required)
- ❌ Ground truth (not required)

**Why selected**:
- **Zero dependencies** - Works without any additional data
- **Fundamental metric** - If a response isn't relevant, nothing else matters
- **Low cost** - Only requires LLM + embeddings for question generation
- **Universal applicability** - Every response should be evaluated for relevance

**Use case**: Baseline evaluation for all responses, even without reference data

---

### 2. Faithfulness ✅ **[Context-Enabled]**

**What it measures**: Whether the response stays grounded in provided context (hallucination detection)

**Requirements**:
- ✅ Prompt
- ✅ Response
- ✅ Context (required)
- ❌ Ground truth (not required)

**Why selected**:
- **Critical for RAG systems** - Essential when working with document retrieval
- **Hallucination detection** - Identifies when LLM invents information not in context
- **Single dependency** - Only requires context, not hard-to-obtain ground truth
- **Practical value** - Real-world applications often have context but not ground truth

**Use case**: RAG applications, document Q&A, context-based assistants

**Why NOT context_relevancy**: This metric doesn't exist in RAGAS 0.4.x, faithfulness is more fundamental

---

### 3. Answer Correctness ✅ **[Quality-Enabled]**

**What it measures**: How accurate the response is compared to a reference answer

**Requirements**:
- ✅ Prompt
- ✅ Response
- ❌ Context (not required)
- ✅ Ground truth (required)

**Why selected**:
- **Accuracy measurement** - Directly measures correctness, not just relevance
- **Benchmark capability** - Allows comparison across different LLM providers
- **Single dependency** - Only requires ground truth, not context
- **Interview value** - Shows understanding of evaluation vs. validation

**Use case**: Testing against known-good answers, benchmark comparisons, quality assurance

**Why NOT answer_similarity**: answer_correctness provides both semantic similarity AND factual accuracy

---

### 4. Context Precision ✅ **[RAG-Enabled]**

**What it measures**: Quality of context retrieval - is the retrieved context actually useful?

**Requirements**:
- ✅ Prompt
- ✅ Response
- ✅ Context (required)
- ✅ Ground truth (required)

**Why selected**:
- **RAG optimization** - Helps tune retrieval systems
- **Diagnostic value** - Identifies if poor responses are due to bad retrieval
- **System improvement** - Actionable insights for RAG pipeline optimization
- **Complete picture** - Combined with context_recall, shows full retrieval quality

**Use case**: RAG system optimization, retrieval pipeline tuning

**Why NOT context_relevancy**: Not available in RAGAS 0.4.x, and context_precision is more actionable

---

## Metrics NOT Selected

### ❌ Context Recall

**Why rejected**:
- Requires both context AND ground truth (same as context_precision)
- Measures "how much of ground truth is in context" - less actionable than precision
- If we have ground truth, context_precision provides more value
- **Trade-off decision**: With limited resources, precision > recall for this use case

### ❌ Other advanced metrics

**Why rejected**:
- Not available in RAGAS 0.4.x
- Require multi-turn conversations or specialized setups
- Add complexity without proportional value for demonstration purposes

---

## Evaluation Strategy Matrix

Our system uses an **adaptive evaluation strategy** based on available data:

| Data Available | Metrics Used | Use Case |
|----------------|--------------|----------|
| **Prompt + Response only** | answer_relevancy | Quick relevance check |
| **+ Context** | answer_relevancy, faithfulness | RAG applications |
| **+ Ground Truth** | answer_relevancy, answer_correctness | Accuracy benchmarking |
| **+ Context + Ground Truth** | All 4 metrics | Complete RAG evaluation |

## Implementation Benefits

### For Development
- **Progressive enhancement** - Start simple, add complexity as needed
- **Clear failure modes** - Each metric has distinct failure signatures
- **Actionable insights** - Each metric points to specific improvements

### For Interviews
- **Strategic thinking** - Shows understanding of trade-offs and priorities
- **Practical knowledge** - Metrics chosen for real-world applicability
- **System design** - Demonstrates adaptive architecture based on data availability

### For Production
- **Cost-effective** - Only compute metrics when data is available
- **Scalable** - Can evaluate responses with or without reference data
- **Maintainable** - Clear documentation of what each metric requires

---

## Metric Selection Decision Tree

```
Do you have a prompt and response?
├─ YES → Use answer_relevancy (always)
│   │
│   ├─ Do you have context?
│   │  ├─ YES → Add faithfulness
│   │  │   │
│   │  │   ├─ Do you have ground truth?
│   │  │   │  ├─ YES → Add answer_correctness + context_precision (complete RAG eval)
│   │  │   │  └─ NO → Stop (RAG without ground truth)
│   │  │
│   │  └─ NO → Do you have ground truth?
│   │     ├─ YES → Add answer_correctness (accuracy eval)
│   │     └─ NO → Stop (basic relevance only)
│   │
│   └─ NO → Cannot evaluate
```

---

## Conclusion

This metric selection balances **practicality**, **demonstration value**, and **real-world applicability**.

The 4-metric system provides:
- ✅ Baseline evaluation (answer_relevancy)
- ✅ Hallucination detection (faithfulness)
- ✅ Accuracy measurement (answer_correctness)
- ✅ RAG optimization (context_precision)

Each metric serves a distinct purpose and activates only when its required data is available, making the system both powerful and resource-efficient.
