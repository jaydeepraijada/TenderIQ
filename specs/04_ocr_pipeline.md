# Spec 04 — OCR Pipeline

**Step:** 7 of 15  
**Time budget:** ~30 min  
**Checkpoint:** `extract_document(Path("data/bidders/bidder_c/turnover_certificate_scan.png"))` returns a list with `source_type` reflecting the OCR tier used.

---

## Goal

Implement `core/ocr_pipeline.py` — the three-tier OCR orchestrator. For each document/image, determines the best extraction method: PyMuPDF text (Tier 1), Tesseract (Tier 2), or DeepSeek Vision LLM (Tier 3). Caches results per file to avoid re-OCR on re-runs.

---

## `ExtractedPage` dataclass

```python
@dataclasses.dataclass
class ExtractedPage:
    page: int
    text: str
    source_type: str  # "text_pdf" | "tesseract" | "vision_llm"
    confidence: float
    raw_tier_results: dict
```

---

## `extract_document(file_path: Path) -> list[ExtractedPage]`

### Cache check

- Compute `file_hash = hashlib.md5(file_path.read_bytes()).hexdigest()`.
- Cache path: `OCR_CACHE_DIR / f"{file_hash}.json"`.
- If cache exists: deserialize and return `list[ExtractedPage]`.

### Routing

**Case A — Image file (PNG/JPG/JPEG/BMP/TIFF):**
- Treat as single page (page=1).
- Go directly to Tier 2 (Tesseract).
- If Tier 2 confidence < `OCR_TESSERACT_MIN_CONF`: try Tier 3.

**Case B — PDF file:**
- Call `pdf_utils.is_text_pdf(file_path)`.
- If `True`: Tier 1 — call `pdf_utils.extract_pages(file_path)`, set `source_type="text_pdf"`, `confidence=1.0`.
- If `False`: for each page, render to image via `pdf_utils.render_page_to_image`, then Tier 2.

### Tier 2 — Tesseract

```python
import pytesseract
data = pytesseract.image_to_data(pil_image, output_type=pytesseract.Output.DATAFRAME)
# Filter rows with conf != -1
valid = data[data["conf"] != -1]
mean_conf = float(valid["conf"].mean()) / 100 if len(valid) > 0 else 0.0
text = " ".join(str(w) for w in valid["text"] if str(w).strip())
```

If `mean_conf < OCR_TESSERACT_MIN_CONF` OR `len(text.strip()) < 20`: attempt Tier 3.

### Tier 3 — DeepSeek Vision LLM

- Convert PIL Image to PNG bytes via `io.BytesIO`.
- Call `LLM().chat_vision(VISION_OCR_PROMPT_SYSTEM, VISION_OCR_USER, image_bytes)`.
- On success: `source_type="vision_llm"`, `confidence=0.95`.
- Log `vision_ocr_invoked` audit entry.
- On `LLMUnavailable`: keep Tier 2 result with its `confidence` (will trigger `needs_review` downstream).

### Cache write

After processing all pages, serialize to JSON and save to cache file.

---

## Serialization format for cache

```json
[
  {
    "page": 1,
    "text": "...",
    "source_type": "text_pdf",
    "confidence": 1.0,
    "raw_tier_results": {"tesseract_conf": null, "vision_used": false}
  }
]
```

---

## Acceptance Criteria

1. `extract_document(Path("data/bidders/bidder_a/audited_financials.pdf"))` returns pages with `source_type="text_pdf"`.
2. `extract_document(Path("data/bidders/bidder_c/turnover_certificate_scan.png"))` — if Tesseract is available and confidence < 0.65, attempts vision LLM (or returns tesseract result with low confidence when LLM unavailable).
3. Second call to `extract_document` on same file returns cached result (no re-processing).
4. Each returned `ExtractedPage` has non-empty `text`.
