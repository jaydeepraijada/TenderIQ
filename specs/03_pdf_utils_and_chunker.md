# Spec 03 — PDF Utils and Chunker

**Step:** 5 of 15  
**Time budget:** ~15 min

---

## Goal

Implement `core/pdf_utils.py` (PyMuPDF text extraction and page rendering) and `core/chunker.py` (text → chunks with metadata).

---

## `core/pdf_utils.py`

### `extract_pages(path: Path) -> list[dict]`

- Opens the PDF with `fitz.open(str(path))`.
- For each page `i`: extracts text via `page.get_text("text")`.
- Returns `[{"page": i+1, "text": text}, ...]` (1-indexed pages).

### `is_text_pdf(path: Path) -> bool`

- Opens the PDF.
- Computes average characters per page across all pages.
- Returns `True` if average ≥ 50 characters per page (heuristic for typed PDF vs scanned blank pages).

### `render_page_to_image(path: Path, page_no: int, dpi: int = 200) -> PIL.Image.Image`

- Opens the PDF.
- Gets page at index `page_no - 1` (0-indexed).
- Creates `fitz.Matrix(dpi/72, dpi/72)` and renders via `page.get_pixmap(matrix=mat, colorspace=fitz.csRGB)`.
- Converts pixmap to PIL Image via `Image.frombytes("RGB", [pix.width, pix.height], pix.samples)`.
- Returns the PIL Image.

---

## `core/chunker.py`

### `chunk_tender(pages: list[dict], tender_id: str) -> list[dict]`

Input: list of `{"page": int, "text": str}` dicts.

Strategy:
- Join page text. Split on clause headings detected by regex `r'^\d+(\.\d+)*\s+'` (multiline).
- Each chunk: up to ~500 tokens (~2000 chars). If a section is longer, split on `\n\n` boundaries.
- Each chunk dict: `{"text": str, "tender_id": str, "page": int, "chunk_id": str}`.
- `chunk_id` = `f"{tender_id}_p{page}_c{i}"`.

Simpler implementation (sufficient for 5-page mock tender):
- One chunk per page section: for each page, if text > 2000 chars split into ~2000-char pieces; else one chunk.

### `chunk_bidder(pages: list[ExtractedPage], bidder_id: str, doc_name: str) -> list[dict]`

Input: list of `ExtractedPage` objects.

Strategy: one chunk per page.

Each chunk dict:
```python
{
    "text": page.text,
    "bidder_id": bidder_id,
    "doc_name": doc_name,
    "page": page.page,
    "source_type": page.source_type,
    "ocr_confidence": page.confidence,
    "chunk_id": f"{bidder_id}_{doc_name}_p{page.page}",
}
```

---

## Acceptance Criteria

1. `extract_pages(Path("data/tender/crpf_construction_tender.pdf"))` returns a list of dicts with non-empty text on most pages.
2. `is_text_pdf(Path("data/tender/crpf_construction_tender.pdf"))` returns `True`.
3. `render_page_to_image(Path("data/tender/crpf_construction_tender.pdf"), 1)` returns a PIL Image with width > 0.
4. `chunk_tender(pages, "tender_001")` returns a non-empty list of dicts each having a "text" key.
5. Each bidder chunk has all required metadata keys.
