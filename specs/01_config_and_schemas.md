# Spec 01 — Config, Schemas, and Prompts

**Step:** 3 of 15  
**Time budget:** ~25 min  
**Checkpoint:** `python -c "from core import config, schemas, prompts"` runs without error. All Pydantic models validate sample JSON correctly.

---

## Goal

Finalize `core/config.py`, `core/schemas.py`, and `core/prompts.py` with full working implementations (the skeleton stubs already have the correct content — this step validates and documents them).

---

## `core/config.py`

Loads environment variables. All values are module-level constants.

| Constant | Type | Value / Source |
|---|---|---|
| `DEEPSEEK_API_KEY` | `str | None` | `os.getenv("DEEPSEEK_API_KEY")` |
| `DEEPSEEK_BASE_URL` | `str` | `"https://api.deepseek.com/v1"` |
| `MODEL_NAME` | `str` | `"deepseek-chat"` |
| `MODEL_VERSION` | `str` | `f"{MODEL_NAME}@2026-05-07"` |
| `CONFIDENCE_HIGH` | `float` | `0.80` |
| `CONFIDENCE_REVIEW` | `float` | `0.55` |
| `OCR_TESSERACT_MIN_CONF` | `float` | `0.65` |
| `BASE_DIR` | `Path` | parent of `core/` |
| `DATA_DIR` | `Path` | `BASE_DIR / "data"` |
| `CHROMA_DIR` | `str` | `str(BASE_DIR / ".chroma")` |
| `AUDIT_DB` | `str` | `str(BASE_DIR / "audit.db")` |
| `PRECOMPUTED_DIR` | `Path` | `DATA_DIR / "precomputed"` |
| `OCR_CACHE_DIR` | `Path` | `BASE_DIR / ".ocr_cache"` |

`load_dotenv()` is called at module level so `.env` is sourced before `os.getenv`.

---

## `core/schemas.py`

Pydantic v2 models. All fields have type annotations. Use `from __future__ import annotations`.

### `Rule`
```python
class Rule(BaseModel):
    type: Literal["numeric_threshold", "count_threshold", "certification_present", "document_present"]
    field: str
    operator: Literal[">=", "<=", "==", "exists"]
    value: float | int | None = None
    unit: str | None = None
```

### `Criterion`
```python
class Criterion(BaseModel):
    id: str
    title: str
    category: Literal["financial", "technical", "compliance"]
    mandatory: bool
    description: str
    rule: Rule
    query_hints: list[str]
    source_page: int
    source_clause: str
```

### `Evidence`
```python
class Evidence(BaseModel):
    bidder_id: str
    doc_name: str
    page: int
    text: str
    source_type: Literal["text_pdf", "tesseract", "vision_llm"]
    ocr_confidence: float | None = None
```

### `Source`
```python
class Source(BaseModel):
    doc_name: str
    page: int
    snippet: str
    source_type: Literal["text_pdf", "tesseract", "vision_llm"]
```

### `Verdict`
```python
class Verdict(BaseModel):
    verdict_id: str = Field(default_factory=lambda: f"V-{uuid.uuid4().hex[:8]}")
    bidder_id: str
    criterion_id: str
    verdict: Literal["eligible", "not_eligible", "needs_review"]
    extracted_value: str | None = None
    normalized_value: float | int | None = None
    source: Source | None = None
    llm_confidence: float = 0.0
    ocr_confidence: float | None = None
    combined_confidence: float = 0.0
    reason: str = ""
    model_version: str = ""
    timestamp: str = ""
    review_status: Literal["pending", "approved", "edited", "rejected"] = "pending"
```

### `AuditEntry`
```python
class AuditEntry(BaseModel):
    id: int | None = None
    ts: str
    action: str
    actor: str
    model_version: str | None = None
    bidder_id: str | None = None
    criterion_id: str | None = None
    payload_json: str | None = None
```

---

## `core/prompts.py`

Three string constants already defined in the skeleton — no changes needed.

- `EXTRACT_CRITERIA_PROMPT_SYSTEM`
- `EVALUATE_CRITERION_PROMPT_SYSTEM`
- `VISION_OCR_PROMPT_SYSTEM`
- `VISION_OCR_USER`

---

## Acceptance Criteria

1. `python -c "from core import config, schemas, prompts"` exits 0.
2. `python -c "from core.schemas import Criterion, Verdict, Evidence, AuditEntry; print('OK')"` prints OK.
3. Sample Criterion JSON validates without error:
   ```python
   from core.schemas import Criterion
   c = Criterion(**{"id":"C1","title":"Turnover","category":"financial",
     "mandatory":True,"description":"INR 5Cr","rule":{"type":"numeric_threshold",
     "field":"turnover","operator":">=","value":50000000,"unit":"INR"},
     "query_hints":["turnover"],"source_page":3,"source_clause":"3.2(a)"})
   assert c.mandatory is True
   ```
4. `config.MODEL_VERSION` contains `"deepseek-chat@2026-05-07"`.
