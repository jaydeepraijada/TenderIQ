# Spec 09 — Evaluator

**Step:** 9 of 15  
**Time budget:** ~25 min  
**Checkpoint:** `evaluate("bidder_a", c1)` returns eligible with high confidence; `evaluate("bidder_b", c1)` returns not_eligible.

---

## Goal

Implement `core/evaluator.py` — per-criterion verdict generation with combined confidence scoring and threshold-based safety rules.

---

## `evaluate(bidder_id: str, criterion: Criterion) -> Verdict`

### Step 1 — Gather evidence

`evidence = bidder_processor.gather_evidence(bidder_id, criterion)`

If empty: return immediately:
```python
Verdict(
    bidder_id=bidder_id,
    criterion_id=criterion.id,
    verdict="needs_review",
    reason="No matching evidence found in submitted documents.",
    llm_confidence=0.0,
    combined_confidence=0.0,
    model_version=MODEL_VERSION,
    timestamp=now_iso(),
)
```
Log `criterion_evaluated` with verdict=needs_review.

### Step 2 — Build LLM prompt

User message template:
```
CRITERION:
{criterion.model_dump_json(indent=2)}

RETRIEVED EVIDENCE (top-k chunks from bidder {bidder_id}):
{json list of evidence dicts with doc_name, page, ocr_confidence, source_type, text}

Return JSON:
{
  "verdict": "eligible" | "not_eligible" | "needs_review",
  "extracted_value": "<short string as found in evidence>",
  "normalized_value": <number or null>,
  "chosen_source": {"doc_name": "...", "page": <int>, "snippet": "<= 200 chars", "source_type": "..."},
  "llm_confidence": <0.0 to 1.0>,
  "reason": "<one or two sentences>"
}

Rules:
- If evidence directly contains a value satisfying the rule, verdict=eligible with high llm_confidence.
- If evidence directly contradicts the rule, verdict=not_eligible.
- If no relevant evidence retrieved, verdict=needs_review, llm_confidence<=0.4.
- If the source is OCR with low confidence and the value is borderline, lean to needs_review.
```

### Step 3 — Call LLM

`result = llm.chat_json(EVALUATE_CRITERION_PROMPT_SYSTEM, user_prompt)`

On `LLMUnavailable`: return `fallback.load_evaluation(bidder_id, criterion.id)`.

### Step 4 — Parse result

Extract: `verdict`, `extracted_value`, `normalized_value`, `chosen_source`, `llm_confidence`, `reason`.

Build `Source` object from `chosen_source`.

### Step 5 — Combined confidence

Find the evidence chunk matching `chosen_source` to get `ocr_confidence` and `source_type`:

```python
if source_type == "text_pdf":
    combined = llm_confidence
elif source_type == "vision_llm":
    combined = 0.7 * llm_confidence + 0.3 * 0.95
elif source_type == "tesseract":
    tc = ocr_confidence if ocr_confidence and ocr_confidence >= 0 else 0.3
    combined = 0.6 * llm_confidence + 0.4 * tc
else:
    combined = llm_confidence
```

### Step 6 — Apply threshold safety rules (in order)

1. If LLM verdict is `needs_review` → keep.
2. If `combined >= CONFIDENCE_HIGH` → keep LLM verdict.
3. If `CONFIDENCE_REVIEW <= combined < CONFIDENCE_HIGH` AND verdict is `not_eligible` → downgrade to `needs_review` (NEVER silently disqualify at medium confidence).
4. If `combined < CONFIDENCE_REVIEW` → force `needs_review`.

### Step 7 — Build and return Verdict

```python
Verdict(
    bidder_id=bidder_id,
    criterion_id=criterion.id,
    verdict=final_verdict,
    extracted_value=extracted_value,
    normalized_value=normalized_value,
    source=source,
    llm_confidence=llm_confidence,
    ocr_confidence=ocr_confidence_from_best_evidence,
    combined_confidence=combined,
    reason=reason,
    model_version=MODEL_VERSION,
    timestamp=now_iso(),
    review_status="pending",
)
```

Log `criterion_evaluated` to audit.

---

## `evaluate_bidder(bidder_id: str, criteria: list[Criterion]) -> list[Verdict]`

Calls `evaluate(bidder_id, c)` for each criterion in sequence. Returns list.

---

## Acceptance Criteria

1. `evaluate("bidder_a", c1)` → `verdict="eligible"`, `combined_confidence >= 0.8` (or fallback eligible).
2. `evaluate("bidder_b", c1)` → `verdict="not_eligible"` or `"needs_review"` (never silently eligible when turnover is below threshold).
3. `evaluate_bidder("bidder_a", criteria)` returns 5 verdicts.
4. All verdicts are `Verdict` instances with valid `review_status="pending"`.
5. Audit log gains `criterion_evaluated` entries.
