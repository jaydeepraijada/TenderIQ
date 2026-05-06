# Spec 10 — Audit and Fallback

**Step:** 10 of 15  
**Time budget:** ~20 min

---

## Goal

Document and finalize `core/audit.py` and `core/fallback.py`. Both were implemented early (Step 6) to unblock the criteria extractor. This spec records their contracts.

---

## `core/audit.py`

### SQLite schema

```sql
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT NOT NULL,
    action TEXT NOT NULL,
    actor TEXT NOT NULL,
    model_version TEXT,
    bidder_id TEXT,
    criterion_id TEXT,
    payload_json TEXT
);
```

Single file: `AUDIT_DB = str(BASE_DIR / "audit.db")`.

### `log(action: str, actor: str = "system", **fields) -> int`

- Writes one row. Returns the inserted `rowid`.
- `ts`: UTC ISO timestamp.
- `model_version`: from `fields` if present, else `config.MODEL_VERSION`.
- `bidder_id`, `criterion_id`: extracted from `fields` if present.
- Remaining `fields` → `payload_json = json.dumps(fields)`.

### `query(filters: dict | None = None) -> list[dict]`

- Returns rows from `audit_log` ordered by `id DESC`.
- Supports filters: `bidder_id`, `action`, `date_from` (ts >=), `date_to` (ts <=).

### Action vocabulary

| Action | When logged |
|---|---|
| `criteria_extracted` | After successful LLM criteria extraction |
| `bidder_processed` | After each document is indexed |
| `criterion_evaluated` | After each (bidder, criterion) verdict |
| `human_review_action` | When evaluator approves/edits/rejects a verdict |
| `precomputed_fallback_used` | When LLM is unavailable and fallback fires |
| `vision_ocr_invoked` | When Tier 3 vision LLM is called |

---

## `core/fallback.py`

### `load_criteria() -> list[Criterion]`

- Reads `data/precomputed/criteria.json` if it exists, parses `{"criteria": [...]}`.
- Falls back to `_HARDCODED_CRITERIA` (5 hardcoded criteria matching the mock tender exactly) if file is missing.

### `load_evaluation(bidder_id: str, criterion_id: str) -> Verdict`

- Reads `data/precomputed/eval_{bidder_id}.json` if it exists.
- Finds the dict where `criterion_id` matches.
- Falls back to a `needs_review` Verdict with reason "Pre-computed evaluation not available."

### `_HARDCODED_CRITERIA`

Five criteria matching the mock tender (C1–C5), with correct rules and query_hints. These are the ultimate safety net if `precompute_results.py` has not been run.

---

## Acceptance Criteria

1. `audit.log("test")` inserts a row; `audit.query()` returns it.
2. `audit.query({"action": "criteria_extracted"})` filters correctly.
3. `fallback.load_criteria()` returns 5 criteria even with no precomputed file.
4. `fallback.load_evaluation("bidder_a", "C1")` returns a `Verdict` with `verdict_id` set.
