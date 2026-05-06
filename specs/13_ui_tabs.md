# Spec 13 — UI Tabs

**Step:** 12 of 15  
**Time budget:** ~80 min total

---

## Goal

Implement all five Streamlit tabs and `ui/components.py`. The app must render the full demo flow without an API key (using precomputed data), and with one (calling the live LLM).

---

## `ui/components.py` — Shared widgets

### `verdict_pill(verdict: str) -> str`
Returns a markdown-formatted colored badge string:
- `eligible` → `":green[✅ Eligible]"`
- `not_eligible` → `":red[❌ Not Eligible]"`
- `needs_review` → `":orange[⚠ Needs Review]"`

### `confidence_bar(value: float, label: str = "Confidence") -> None`
Renders `st.progress(value, text=f"{label}: {value:.0%}")`.

### `ocr_tier_badge(source_type: str) -> str`
Returns a short badge string:
- `text_pdf` → "`📄 text_pdf`"
- `tesseract` → "`🔍 tesseract`"
- `vision_llm` → "`👁 vision_llm`"

### `category_badge(category: str) -> str`
Returns `":blue[financial]"`, `":green[technical]"`, or `":orange[compliance]"`.

---

## Tab 1 — Overview (`ui/tab_overview.py`)

Layout:
1. Hero text + tagline.
2. Two-column KPI cards: Criteria Extracted, Bidders Evaluated, Mandatory Criteria Checked, Audit Entries Logged.
3. Architecture summary (text description since no image file yet).
4. "Use Pre-loaded Demo Data" CTA that sets `st.session_state["use_demo"] = True` and shows the criteria count from the fallback file.

KPI values: count from `st.session_state` data and `audit.query()`.

---

## Tab 2 — Tender Analysis (`ui/tab_tender.py`)

Already implemented in Step 6. No changes needed beyond what's there.

---

## Tab 3 — Bidder Evaluation (`ui/tab_bidders.py`)

Layout:
1. `st.header("Bidder Evaluation")`
2. Multi-select for bidders: `["bidder_a", "bidder_b", "bidder_c"]`, default all.
3. Button **"Run Evaluation"** (type=primary).
4. On click:
   a. Ensure criteria are loaded (from session_state or fallback).
   b. For each selected bidder: `process_bidder(...)`, then `evaluate_bidder(...)`.
   c. Store verdicts in `st.session_state["verdicts"]` as `{bidder_id: [Verdict.model_dump(), ...]}`.
5. If verdicts in session:
   - For each bidder: show per-bidder summary header.
   - Show a table of criteria rows using `st.columns`.
   - Each row: criterion title, verdict pill, extracted value, source chip (doc + page), OCR-tier badge, confidence bar.
   - Expandable "Reason" and "Source Snippet" per row.

Per-bidder summary: count eligible/not_eligible/needs_review among mandatory criteria. Overall: Eligible only if all mandatory are eligible; Not Eligible if any are not_eligible; Needs Review otherwise.

---

## Tab 4 — Human Review Queue (`ui/tab_review.py`)

Layout:
1. `st.header("Human Review Queue")`
2. Shows all verdicts where `review_status == "pending"` AND `verdict == "needs_review"`.
3. For each such verdict:
   - Show: bidder_id, criterion title, extracted value, confidence, reason, source snippet.
   - Three buttons: **Approve**, **Edit & Approve**, **Reject**.
   - **Approve**: set `review_status = "approved"`, log `human_review_action` to audit.
   - **Edit & Approve**: show `st.text_input` for edited value, set `review_status = "edited"`, log audit.
   - **Reject**: set `review_status = "rejected"`, log audit.
4. If no pending items: `st.success("No items pending review.")`.

State: verdicts stored in `st.session_state["verdicts"]` as nested dicts. Updates write back to the same structure.

---

## Tab 5 — Audit Log (`ui/tab_audit.py`)

Layout:
1. `st.header("Audit Log")`
2. Filter row: bidder dropdown, action dropdown, date range.
3. Table: `st.dataframe` with columns: ts, action, actor, bidder_id, criterion_id, payload_json.
4. **"Export CSV"** button: `st.download_button` with CSV data from filtered rows.

---

## Sidebar update (`app.py`)

Replace the hardcoded "🔴 **DeepSeek:** not connected" with a live probe:
- Try `LLM().chat_json("ping", '{"ping": true}')` at startup (cached with session_state).
- Green: live and no fallback fired.
- Amber: fallback has fired this session.
- Red: probe failed.

If `st.session_state.get("fallback_active")`: show `st.sidebar.warning("⚠ Pre-computed mode active.")`.

---

## Acceptance Criteria

1. Tab 1 renders without error and shows KPI cards.
2. Tab 3 "Run Evaluation" populates the verdict table for all 3 bidders.
3. Bidder A shows all mandatory criteria eligible. Bidder B shows C1 not_eligible.
4. Tab 4 shows at least one pending review item for Bidder C.
5. Tab 4 Approve button updates `review_status` and adds an audit entry.
6. Tab 5 shows audit entries and CSV download works.
7. Sidebar connection dot is green/amber/red based on API availability.
