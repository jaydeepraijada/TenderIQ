# TenderIQ — Architecture

## Overview

TenderIQ is a single-process Streamlit application that automates eligibility evaluation
of bidders against government tender criteria. All state is local: SQLite for the audit
log, ChromaDB (file-backed) for vector indices, and the filesystem for PDFs and cached
OCR results. The only external dependency is the DeepSeek API.

```
┌──────────────────────────────────────────────────────────────────────┐
│                         Streamlit App (app.py)                        │
│                                                                        │
│  Tab 1: Overview  Tab 2: Tender Analysis  Tab 3: Bidder Evaluation    │
│  Tab 4: Human Review  Tab 5: Audit Log  Tab 6: Interpretability       │
└────────────────────────────┬─────────────────────────────────────────┘
                             │ calls
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
 ┌────────────┐    ┌──────────────────┐   ┌──────────────┐
 │ criteria_  │    │ bidder_processor │   │  evaluator   │
 │ extractor  │    │  ocr_pipeline    │   │  fallback    │
 └────┬───────┘    └────┬─────────────┘   └──────┬───────┘
      │                 │                         │
      ▼                 ▼                         ▼
 ┌──────────┐    ┌─────────────┐         ┌──────────────┐
 │ DeepSeek │    │  ChromaDB   │         │ DeepSeek LLM │
 │   LLM    │    │ (vectors)   │◄────────│  (evaluate)  │
 └──────────┘    └─────────────┘         └──────────────┘
      │                 ▲
      │                 │ index chunks
      │          ┌──────┴──────┐
      │          │ 3-tier OCR  │
      │          │ PyMuPDF     │
      │          │ Tesseract   │
      │          │ Vision LLM  │
      │          └─────────────┘
      │
      ▼
 ┌──────────┐
 │  audit   │ (SQLite, append-only)
 └──────────┘
```

---

## Module Responsibilities

| Module | Responsibility |
|---|---|
| `core/config.py` | Environment loading, constants, paths |
| `core/schemas.py` | Pydantic models: Criterion, Evidence, Verdict, AuditEntry |
| `core/prompts.py` | LLM prompt strings (criteria extraction, evaluation, OCR) |
| `core/llm_client.py` | DeepSeek API wrapper — `chat_json`, `chat_vision`, retry logic, `LLMUnavailable` |
| `core/pdf_utils.py` | PyMuPDF: text extraction, text-PDF detection, page rendering |
| `core/ocr_pipeline.py` | Three-tier OCR orchestrator, MD5-based result cache |
| `core/chunker.py` | Text chunking for tender and bidder documents |
| `core/vectorstore.py` | ChromaDB helpers: get/create collection, upsert, query |
| `core/criteria_extractor.py` | Stage 1: tender PDF → `list[Criterion]` |
| `core/bidder_processor.py` | Stage 2: bidder docs → chunks + evidence retrieval |
| `core/evaluator.py` | Stage 3: per-criterion verdict with combined confidence |
| `core/audit.py` | SQLite audit log: write and query |
| `core/fallback.py` | Load pre-computed JSON when LLM unavailable |

---

## Three-Tier OCR Pipeline

The robustness centrepiece. Handles typed PDFs, scanned PDFs, and photographs of documents.

```
Input file
    │
    ├─ Is image (PNG/JPG)?  ──────────────────────────────────┐
    │                                                         │
    └─ Is PDF?                                                ▼
           │                                         Tier 2: Tesseract
           ├─ is_text_pdf() == True                          │
           │       │                              mean_conf ≥ 0.65?
           │       ▼                                   │
           │  Tier 1: PyMuPDF                    Yes ──┘     No
           │  confidence = 1.0                              │
           │  source_type = "text_pdf"                      ▼
           │                                     Tier 3: DeepSeek Vision LLM
           └─ is_text_pdf() == False             confidence = 0.95
                   │                             source_type = "vision_llm"
                   ▼
           Render pages → Tier 2
```

Each `ExtractedPage` carries: `page`, `text`, `source_type`, `confidence`, `raw_tier_results`.
Results cached under `.ocr_cache/<md5>.json`.

---

## Confidence & Threshold Logic

Combined confidence weights LLM certainty against OCR quality:

| OCR Tier | Formula |
|---|---|
| `text_pdf` | `combined = llm_confidence` |
| `vision_llm` | `combined = 0.7 × llm_confidence + 0.3 × 0.95` |
| `tesseract` | `combined = 0.6 × llm_confidence + 0.4 × tesseract_conf` |

Safety threshold rules (applied in order):

1. LLM returns `needs_review` → keep (regardless of confidence)
2. `combined ≥ 0.80` → keep LLM verdict
3. `0.55 ≤ combined < 0.80` AND verdict is `not_eligible` → downgrade to `needs_review`
4. `combined < 0.55` → force `needs_review`

**The core safety guarantee:** a bidder is never silently disqualified at medium or low confidence.

---

## Fallback Strategy

Every live LLM call is wrapped in `try/except LLMUnavailable`. On failure:

1. `audit.log("precomputed_fallback_used", ...)` is written
2. `st.session_state["fallback_active"] = True` triggers the amber sidebar dot
3. Data is loaded from `data/precomputed/*.json` (committed to the repo)

This means the demo works even if the API is down, rate-limited, or the key is missing.

---

## Audit Log Schema

```sql
CREATE TABLE audit_log (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    ts             TEXT NOT NULL,      -- UTC ISO timestamp
    action         TEXT NOT NULL,      -- see action vocabulary below
    actor          TEXT NOT NULL,      -- "system" or "officer"
    model_version  TEXT,               -- e.g. "deepseek-chat@2026-05-07"
    bidder_id      TEXT,
    criterion_id   TEXT,
    payload_json   TEXT                -- action-specific JSON payload
);
```

Action vocabulary: `criteria_extracted`, `bidder_processed`, `criterion_evaluated`,
`human_review_action`, `precomputed_fallback_used`, `vision_ocr_invoked`.

---

## Data Flow (full pipeline)

```
1. Officer uploads tender PDF
        │
        ▼
2. criteria_extractor.extract_criteria(pdf)
   → LLM reads tender text
   → Returns List[Criterion] with structured rules
   → Stored in st.session_state["criteria"]
        │
        ▼
3. bidder_processor.process_bidder(bidder_id, files)
   → For each file: ocr_pipeline.extract_document()
   → chunker.chunk_bidder()
   → vectorstore.add_chunks("bidder_chunks", ...)
        │
        ▼
4. evaluator.evaluate(bidder_id, criterion)
   → bidder_processor.gather_evidence() — semantic search in ChromaDB
   → LLM evaluates evidence against criterion rule
   → combined_confidence computed
   → threshold safety rules applied
   → Verdict returned + audit logged
        │
        ▼
5. Verdicts stored in st.session_state["verdicts"]
   → Tab 3: evaluation matrix
   → Tab 4: needs_review items surfaced for human action
   → Tab 6: plain-English explanation + Q&A
   → Tab 5: full audit trail
```
