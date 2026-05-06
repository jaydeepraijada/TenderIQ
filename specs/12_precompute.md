# Spec 12 — Pre-compute Results

**Step:** 11 of 15  
**Time budget:** ~15 min  
**Checkpoint:** Four JSON files exist in `data/precomputed/` and validate against the schemas.

---

## Goal

`scripts/precompute_results.py` runs the full pipeline once (requires a valid API key), saves the results as JSON fallback files, and commits them to the repo. When the API is unavailable during a demo, `fallback.py` reads these files instead.

---

## Script: `scripts/precompute_results.py`

```python
"""Step 11 — runs the full pipeline and writes data/precomputed/*.json."""
```

### Steps

1. Ensure `data/precomputed/` exists.
2. Extract criteria from mock tender → save `data/precomputed/criteria.json`:
   ```json
   {"criteria": [<Criterion.model_dump()>, ...]}
   ```
3. For each bidder (`bidder_a`, `bidder_b`, `bidder_c`):
   a. Process all bidder docs (`process_bidder`).
   b. Evaluate all criteria (`evaluate_bidder`).
   c. Save `data/precomputed/eval_{bidder_id}.json`:
      ```json
      [<Verdict.model_dump()>, ...]
      ```
4. Print summary and exit 0.

### Error handling

If the LLM fails for any criterion: catch `LLMUnavailable`, log a warning, skip that criterion (don't crash). At least the criteria file and partial evals are better than nothing.

If no API key: print instructions and exit 1.

---

## Fallback file format

### `criteria.json`
```json
{
  "criteria": [
    {"id": "C1", "title": "...", ...},
    ...
  ]
}
```

### `eval_bidder_a.json`
```json
[
  {"verdict_id": "V-abc123", "bidder_id": "bidder_a", "criterion_id": "C1", "verdict": "eligible", ...},
  ...
]
```

---

## Acceptance Criteria

1. Running `python scripts/precompute_results.py` exits 0 when API key is set.
2. `data/precomputed/criteria.json` exists and contains `{"criteria": [...]}` with 5 items.
3. Each `eval_bidder_*.json` contains a list of 5 `Verdict` dicts.
4. `from core.fallback import load_criteria` returns 5 `Criterion` objects from the file.
5. `from core.fallback import load_evaluation` returns the correct `Verdict` for bidder_a, C1.
