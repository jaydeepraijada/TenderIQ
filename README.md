---
title: TenderIQ
emoji: ⚖️
colorFrom: blue
colorTo: indigo
sdk: streamlit
sdk_version: 1.39.0
app_file: app.py
pinned: true
license: agpl-3.0
short_description: Explainable AI for Government Tender Evaluation (CRPF Hackathon)
---

# TenderIQ — Explainable AI for Tender Evaluation

> Built for the **CRPF Hackathon, Theme 3 — AI-Based Tender Evaluation and Eligibility Analysis for Government Procurement**

TenderIQ automates the eligibility evaluation of bidders against government tender criteria. It extracts structured criteria from any tender PDF, processes bidder documents through a three-tier OCR pipeline, evaluates each (bidder × criterion) pair using a language model with combined confidence scoring, and surfaces ambiguous cases for human review — all with a complete, exportable audit trail.

---

## The Problem

A procurement committee today manually reads hundreds of pages of tender documents and bidder submissions, cross-checks financial statements, certificates, and project records, and decides whether each bidder meets each criterion. For one tender this can take 3–5 days. Two evaluators regularly reach different conclusions on the same documents. There is no consistent audit trail.

TenderIQ reduces this to minutes, with every decision traceable to a specific document, page, and model version.

---

## Key Features

| Feature | Detail |
|---|---|
| **Criterion extraction** | DeepSeek LLM reads the tender PDF and returns each criterion as structured JSON — category, mandatory flag, threshold rule, source clause, and retrieval query hints |
| **Three-tier OCR** | PyMuPDF for typed PDFs → Tesseract for scans → DeepSeek Vision LLM when Tesseract confidence < 65%. Every page records which tier read it |
| **Semantic evidence retrieval** | sentence-transformers all-MiniLM-L6-v2 indexes all bidder document chunks; top-k retrieval feeds the evaluator |
| **Safety threshold rule** | A borderline `not_eligible` verdict at medium confidence (0.55–0.80) is automatically downgraded to `needs_review` — never silent disqualification |
| **Human review queue** | Flagged verdicts surface with full evidence, source snippet, and OCR tier badge. Officers Approve / Edit & Approve / Reject with one click |
| **Interpretability tab** | Plain-English per-criterion breakdown with inline PDF page previews and an LLM-powered Q&A ("Why was this bidder rejected?") |
| **Audit log** | Every action — extraction, OCR invocation, evaluation, human review — logged to SQLite with timestamp, model version, actor, and payload. CSV export |
| **Pre-computed fallback** | If the API is unavailable, pre-computed JSON is served transparently. Sidebar shows an amber dot. Demo always works |

---

## Quick Start

### Without an API key (pre-computed demo)

```bash
git clone <repo-url> && cd TenderIQ
pip install -r requirements.txt
streamlit run app.py
```

Open http://localhost:8501, go to the **Overview** tab, and click **Load Pre-computed Demo**. All tabs populate instantly with realistic results for three mock bidders.

### With a live API key

```bash
cp .env.example .env
# Edit .env and set: DEEPSEEK_API_KEY=your_key_here
streamlit run app.py
```

The sidebar turns 🟢. Then:
1. **Tender Analysis** → select a tender (mock or real CRPF tender) → **Extract Criteria**
2. Remove any criteria you don't want evaluated using the × button
3. **Bidder Evaluation** → **Run Evaluation**
4. Review flagged verdicts in **Human Review**
5. Export the full activity log from **Audit Log**

### Tesseract (for OCR on scanned documents)

```bash
# Linux / Streamlit Cloud — handled automatically via packages.txt
apt install tesseract-ocr poppler-utils

# Windows
# Download installer from https://github.com/UB-Mannheim/tesseract/wiki
# Add to PATH, then restart the app
```

Tesseract is optional. If unavailable, the OCR pipeline falls through to the DeepSeek Vision LLM tier.

---

## Demo Scenarios

Three mock bidders are included, each designed to exercise a different path through the pipeline:

| Bidder | Company | Outcome | Why |
|---|---|---|---|
| **Bidder A** | Apex Constructions Pvt. Ltd. | ✅ Eligible | All 4 mandatory criteria met, typed PDFs, high confidence |
| **Bidder B** | BuildRight Enterprises | ❌ Not Eligible | C1 fails — average turnover INR 1.5 Cr vs 5 Cr threshold |
| **Bidder C** | Shree Constructions & Services | ⚠️ Needs Review | Turnover certificate submitted as a blurry, rotated scan — Tesseract confidence ~55% triggers Vision LLM; combined confidence routes to human review |

Two real CRPF tenders from crpf.gov.in are also included in `data/tender/real_tenders/` for live testing.

---

## Architecture

```
Tender PDF ──► DeepSeek LLM ──► Criteria (JSON)
                                      │
Bidder Docs ──► 3-tier OCR ──► Chunks ──► Vector Index
                │                              │
                │                    semantic search
                │                              │
                └──────────────► DeepSeek LLM (evaluate)
                                      │
                            combined confidence
                                      │
                        ┌─────────────┴─────────────┐
                    eligible /                 needs_review
                  not_eligible              ──► Human Review Queue
                        │                              │
                        └──────────── Audit Log ───────┘
```

Full module documentation: [`ARCHITECTURE.md`](ARCHITECTURE.md)

---

## Project Structure

```
TenderIQ/
├── app.py                        # Streamlit entry point, 6 tabs, sidebar
├── core/
│   ├── config.py                 # Constants, paths, thresholds
│   ├── schemas.py                # Pydantic: Criterion, Evidence, Verdict, AuditEntry
│   ├── prompts.py                # LLM prompt strings
│   ├── llm_client.py             # DeepSeek wrapper — chat_json, chat_vision, LLMUnavailable
│   ├── pdf_utils.py              # PyMuPDF: extract_pages, render_page_to_image
│   ├── ocr_pipeline.py           # 3-tier OCR orchestrator with MD5 cache
│   ├── chunker.py                # Tender and bidder document chunking
│   ├── vectorstore.py            # In-memory vector store (sentence-transformers + BM25 fallback)
│   ├── criteria_extractor.py     # Stage 1: tender PDF → List[Criterion]
│   ├── bidder_processor.py       # Stage 2: bidder docs → indexed chunks
│   ├── evaluator.py              # Stage 3: per-criterion verdict + confidence
│   ├── audit.py                  # SQLite audit log
│   └── fallback.py               # Pre-computed JSON fallback
├── ui/
│   ├── tab_overview.py           # Hero, KPIs, pipeline diagram, demo CTA
│   ├── tab_tender.py             # Upload tender, extract + discard criteria
│   ├── tab_bidders.py            # Evaluation table with bidder toggles
│   ├── tab_review.py             # Human review queue — Approve / Edit / Reject
│   ├── tab_audit.py              # Audit log table + CSV export
│   ├── tab_interpretability.py   # Plain-English breakdown + LLM Q&A
│   ├── components.py             # Shared HTML badge/pill/bar components
│   └── styles.py                 # Global CSS injection
├── data/
│   ├── tender/                   # Mock tender PDF + real CRPF tenders
│   ├── bidders/                  # Mock bidder documents (A, B, C)
│   └── precomputed/              # Fallback JSON (criteria + verdicts)
├── scripts/
│   ├── generate_mock_data.py     # Generates all mock PDFs and noisy scan
│   ├── precompute_results.py     # Runs full pipeline, saves fallback JSON
│   ├── generate_deck.py          # Generates pitch deck PDF
│   └── smoke_test.py             # 43-check end-to-end test, exits 0
├── specs/                        # Per-module spec documents
├── deck/                         # Pitch deck PDF
└── ARCHITECTURE.md               # Full architecture reference
```

---

## Running the Smoke Test

```bash
python scripts/smoke_test.py
```

43 checks covering imports, config, schemas, PDF utils, OCR pipeline, fallback, audit, evaluator threshold logic, and precomputed files. Exits 0 on success (~10 seconds, no API key needed).

---

## Tech Stack

| Component | Technology |
|---|---|
| UI & orchestration | Streamlit 1.39 |
| LLM (criteria extraction + evaluation) | DeepSeek API via OpenAI SDK |
| OCR Tier 1 | PyMuPDF 1.24 |
| OCR Tier 2 | Tesseract (pytesseract) |
| OCR Tier 3 | DeepSeek Vision LLM |
| Semantic retrieval | sentence-transformers 2.7 (all-MiniLM-L6-v2) |
| Data validation | Pydantic v2 |
| Audit log | SQLite |
| Mock data generation | ReportLab + Pillow + NumPy |

---

## Future Work

The current build is scoped to the hackathon prototype. Directions for production:

- **Multi-tender workspace** — evaluate the same pool of bidders against multiple tenders simultaneously, with a unified eligibility matrix
- **GeM portal integration** — pull live tenders directly from the Government e-Marketplace API instead of uploading PDFs
- **Automated bidder ranking** — weighted scoring across criteria to produce an ordered shortlist, not just pass/fail
- **LayoutLM for complex tables** — better structured extraction from financial statements with multi-column layouts and merged cells
- **Multi-evaluator workflow** — role-based access (Evaluator / Reviewer / Approver) with parallel review and conflict resolution
- **Review queue notifications** — email or SMS alerts when verdicts are flagged, so officers don't need to poll the app
- **Bulk bidder upload** — ZIP/folder upload for large tenders with many bidders, with background processing and progress tracking
- **Audit export for compliance** — structured PDF report per tender, formatted for submission to procurement oversight bodies

---

## Notes

- **PyMuPDF (AGPL)** — used under AGPL; acceptable for hackathon use.
- **No auth / multi-user** — single hardcoded `officer` identity in audit entries. Out of scope for this prototype.
- **First run** — sentence-transformers downloads all-MiniLM-L6-v2 (~90 MB) on first evaluation. Subsequent runs use the cache.
