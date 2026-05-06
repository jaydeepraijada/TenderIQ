# Spec 07 — Criteria Extractor

**Step:** 6 of 15  
**Time budget:** ~30 min  
**Checkpoint:** Tab 2 in the running app shows 5 criteria extracted from the mock tender.

---

## Goal

Implement `core/criteria_extractor.py` and wire up `ui/tab_tender.py` to call it. On `LLMUnavailable`, fall back to `fallback.load_criteria()`. Cache result in `st.session_state["criteria"]`.

---

## `core/criteria_extractor.py`

### `extract_criteria(tender_pdf_path: Path) -> list[Criterion]`

1. Call `pdf_utils.extract_pages(tender_pdf_path)` → list of `{"page": int, "text": str}`.
2. Join pages: `tender_text = "\n\n--- PAGE {n} ---\n\n".join(p["text"] for p in pages)`.
3. Build user prompt:
   ```
   {tender_text}
   
   ---
   Return JSON in this exact format:
   {"criteria": [
     {"id": "C1", "title": "...", "category": "financial|technical|compliance",
      "mandatory": true|false, "description": "...",
      "rule": {"type": "numeric_threshold|count_threshold|certification_present|document_present",
               "field": "...", "operator": ">=|<=|==|exists", "value": null_or_number, "unit": null_or_string},
      "query_hints": ["...", "..."],
      "source_page": <int>, "source_clause": "..."},
     ...
   ]}
   ```
4. Call `llm.chat_json(EXTRACT_CRITERIA_PROMPT_SYSTEM, user_prompt)`.
5. Parse `result["criteria"]` → validate each item as `Criterion(**item)`.
6. Log `criteria_extracted` to audit with `payload_json=json.dumps({"count": len(criteria)})`.
7. Return `list[Criterion]`.

On `LLMUnavailable`:
- Log `precomputed_fallback_used` to audit.
- Set `st.session_state["fallback_active"] = True`.
- Return `fallback.load_criteria()`.

LLM singleton: use `@st.cache_resource` on a getter `_get_llm()` so the client is created once per Streamlit session.

---

## `ui/tab_tender.py`

Renders the Tender Analysis tab. Replaces the stub.

Layout:
1. `st.header("Tender Analysis")`
2. File uploader: `uploaded = st.file_uploader("Upload tender PDF", type=["pdf"])`. If nothing uploaded, use the preloaded mock: `data/tender/crpf_construction_tender.pdf`.
3. Show the filename being used.
4. Button **"Extract Criteria (Live LLM)"**:
   - Save uploaded bytes to a temp file (or use the mock path directly).
   - Call `criteria_extractor.extract_criteria(path)`.
   - Store in `st.session_state["criteria"]`.
5. If `st.session_state.get("criteria")`:
   - Show `st.success(f"Extracted {len(criteria)} criteria")`.
   - For each criterion, render a card using `st.expander`:
     - Title + mandatory/optional badge (🔴 Mandatory / 🟡 Optional).
     - Category badge (color-coded: financial=blue, technical=green, compliance=orange).
     - Description text.
     - Source: page + clause.
     - Rule details (type, operator, value, unit).

---

## Acceptance Criteria

1. `extract_criteria(Path("data/tender/crpf_construction_tender.pdf"))` returns a list of 5 `Criterion` objects (when LLM is available) or the precomputed fallback (when not).
2. Tab 2 renders without error in both modes.
3. Each extracted criterion shows title, mandatory status, category, and source clause.
4. `st.session_state["criteria"]` is populated after the button is clicked.
