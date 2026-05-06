# TenderIQ — Explainable AI for Tender Evaluation

AI-powered eligibility evaluation of bidders against government tender criteria, built for the **CRPF Hackathon, Theme 3**.

## What it does

1. **Extract criteria** — DeepSeek LLM reads the tender PDF and extracts each eligibility criterion as structured JSON (category, rule, query hints, source clause).
2. **OCR & index bidder documents** — Three-tier OCR pipeline: PyMuPDF (typed PDF) → Tesseract → DeepSeek Vision LLM (for low-confidence scans). All pages indexed into ChromaDB.
3. **Evaluate per criterion** — Vector search retrieves relevant evidence; DeepSeek decides eligible / not_eligible / needs_review with combined confidence scoring.
4. **Human review & audit** — Low-confidence verdicts are routed to a review queue. Every action is logged with timestamp, model version, actor, and payload.

## Quick Start (local)

```bash
# 1. Clone the repo
git clone <repo-url> && cd TenderIQ

# 2. Install dependencies
pip install -r requirements.txt
# On Linux/Mac also: apt install tesseract-ocr poppler-utils

# 3. Set your API key (optional — works without key using pre-computed data)
cp .env.example .env
# Edit .env: DEEPSEEK_API_KEY=your_key_here

# 4. Generate mock data (already committed — only needed if you delete data/)
python scripts/generate_mock_data.py

# 5. Run the app
streamlit run app.py
```

Open http://localhost:8501 in your browser.

## Running without an API key (pre-computed mode)

The app works without a DeepSeek API key. Pre-computed results in `data/precomputed/` are used as fallback automatically. The sidebar shows an amber dot and a banner when in this mode.

The demo flow:
1. Go to **Overview** tab → click **Load Pre-computed Demo** to instantly populate all tabs with realistic results.
2. Navigate to **Bidder Evaluation** to see the verdict table with confidence bars and OCR-tier badges.
3. **Human Review** tab shows Bidder C's turnover criterion flagged for review (low-confidence scan).
4. **Audit Log** tab shows the full activity log with CSV export.

## Running with a live API key

Set `DEEPSEEK_API_KEY` in `.env` (or Streamlit Cloud secrets). The sidebar shows a green dot. Then:
1. **Tender Analysis** → click **Extract Criteria (Live LLM)** — extracts 5 criteria from the mock tender.
2. **Bidder Evaluation** → click **Run Evaluation** — processes all 3 bidders.

## Running the smoke test

```bash
python scripts/smoke_test.py
```

Exits 0 on success (43 checks, ~10 seconds).

## Pre-computing results

If you have an API key and want to regenerate the fallback JSON:
```bash
python scripts/precompute_results.py
```

## Project structure

```
TenderIQ/
├── app.py                    # Streamlit entry point
├── core/
│   ├── config.py             # Constants and paths
│   ├── schemas.py            # Pydantic models
│   ├── prompts.py            # LLM prompt strings
│   ├── llm_client.py         # DeepSeek wrapper
│   ├── pdf_utils.py          # PyMuPDF extraction
│   ├── ocr_pipeline.py       # 3-tier OCR
│   ├── chunker.py            # Text chunking
│   ├── vectorstore.py        # ChromaDB helpers
│   ├── criteria_extractor.py # Stage 1: tender → criteria
│   ├── bidder_processor.py   # Stage 2: bidder docs → chunks
│   ├── evaluator.py          # Stage 3: verdict generation
│   ├── audit.py              # SQLite audit log
│   └── fallback.py           # Pre-computed fallback
├── ui/                       # Streamlit tab modules
├── data/
│   ├── tender/               # Mock tender PDF
│   ├── bidders/              # Mock bidder documents
│   └── precomputed/          # Fallback JSON files
├── scripts/                  # generate_mock_data, precompute, smoke_test
└── specs/                    # Per-module specs (spec-driven development)
```

## Notes

- **PyMuPDF (AGPL)** — allowed for hackathon use; see LICENSE for details.
- **Tesseract** — must be installed separately on Windows. Available via `packages.txt` on Streamlit Cloud.
- **First cloud load** — ChromaDB downloads the all-MiniLM-L6-v2 model (~80 MB) on first run. Pre-warm by visiting the deployed URL once before the demo.
