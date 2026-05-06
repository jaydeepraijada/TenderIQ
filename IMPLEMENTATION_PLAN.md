# TenderIQ — Implementation Plan

> **For:** any contributor or fresh AI context picking up this project.
> **You do not need any prior conversation context to use this document.**

---

## 0. How To Use This Plan

This project follows **spec-driven development**:

1. **This document** is the master implementation plan. It defines architecture, modules, schemas, and the build order. It does **not** contain final source code.
2. For **each module or coherent unit of work** listed in this plan, the team will produce a **spec document** (a short markdown file) before writing code. Each spec covers: inputs, outputs, function signatures, error cases, dependencies, and acceptance criteria.
3. Code is written **only against an approved spec**, not directly from this plan.
4. Specs live in `specs/` (e.g. `specs/01_llm_client.md`, `specs/02_ocr_pipeline.md`). One spec per module. Number prefixes follow the build order in section 9.
5. Once a spec is implemented, the spec file is preserved alongside the code as documentation.

**Sequencing rule:** never skip the spec step. If you find yourself wanting to "just code it," stop and write the spec first — it forces precision and exposes hidden assumptions.

---

## 1. Background

### What TenderIQ is
TenderIQ is an AI-powered platform that automates eligibility evaluation of bidders against government tender criteria. It is being built for the **Central Reserve Police Force (CRPF) hackathon, Theme 3 — AI-Based Tender Evaluation and Eligibility Analysis for Government Procurement**.

### Why it exists
Government procurement officers today manually read tender documents (criteria, thresholds, compliance requirements) and bidder submissions (financial statements, certifications, project records — often in mixed formats including scans and photos), and decide whether each bidder meets each criterion. For one tender, a committee may spend days; two evaluators routinely reach different conclusions on the same documents; there is no consistent audit trail.

TenderIQ does this evaluation automatically while preserving human oversight: extract criteria from the tender, parse bidder documents, evaluate criterion-by-criterion with confidence scoring, surface ambiguous cases for human review, and emit a complete audit log.

### Where this project sits in the hackathon
- **Round 1 (Idea Phase)**: written submission — already shortlisted. See `idea.md`.
- **Round 2 (Prototype Phase)**: working prototype — this is what we are building. Submission requirements are in `submission_requirements.md`.

### Source documents in this repository
| File | Purpose |
|---|---|
| `theme.md` | Original problem statement from CRPF (the "why" and the hard constraints) |
| `idea.md` | The shortlisted Round 1 written submission (the "what") |
| `understanding.md` | Synthesized understanding of the problem space |
| `submission_requirements.md` | Form fields required for the Round 2 submission |
| `IMPLEMENTATION_PLAN.md` | **This file** — the build plan |
| `specs/` | Per-module spec documents (created during build, one per module) |

Read those four documents (theme, idea, understanding, submission requirements) before drafting the first spec.

---

## 2. Hard Constraints (from the theme — non-negotiable)

These are evaluator-facing requirements. Every architectural decision must respect them.

1. **Every verdict must be explainable at criterion level** — for each (bidder, criterion) pair the system must show: which criterion was checked, which document and page provided the evidence, what value was extracted, what confidence the system had, and why the verdict was assigned.
2. **Never silently disqualify** — low-confidence or ambiguous cases must be routed to a human review queue with a stated reason, never auto-rejected.
3. **Must handle scanned documents and photographs** — OCR is mandatory. The system cannot assume digital text.
4. **End-to-end auditable** — every action (criterion extraction, evaluation, OCR fallback invocation, human review action) must be logged with timestamp, model version, actor, and payload.

A submission that fails any of these is unlikely to score well. Treat them as acceptance criteria for the system as a whole.

---

## 3. Operating Constraints (this build)

- **Time budget:** ~6 hours total — ~5h build + ~1.5h deck/video/screenshots/submission. Do not exceed scope. Compression strategy is documented in section 11.
- **Platform:** Windows 11 development machine. Streamlit Cloud for hosted demo.
- **Language:** Python 3.10+.
- **Starting point:** the project is empty except for the source documents listed in section 1. Everything below is to be created.
- **API access:** the developer has a **DeepSeek API key**. No other LLM/vision API keys are assumed available.
- **Storage:** file-based only. SQLite for the audit log; ChromaDB persistent client for vectors. No external services beyond the DeepSeek API and Streamlit Cloud.
- **Auth/multi-user:** out of scope. A single hardcoded "officer" identity is used in audit entries.

---

## 4. Confirmed Architectural Decisions

These were the result of explicit trade-off discussions before the plan was written. Do not relitigate without strong reason.

### 4.1 UI / Backend
**Single Streamlit app** (`streamlit==1.39.0`). No separate frontend, no FastAPI service. Streamlit handles UI and orchestration. Deployable free to Streamlit Community Cloud, which satisfies the "Demo Link" submission requirement.

### 4.2 LLM
**DeepSeek API**, model `deepseek-v4-pro`, called via the **OpenAI Python SDK** with `base_url="https://api.deepseek.com/v1"` (DeepSeek is OpenAI-compatible). DeepSeek V4-Pro is multimodal — it accepts image inputs, which we exploit for vision-OCR (section 4.4).

### 4.3 Live-first LLM with cached fallback
The app **always attempts a live LLM call first**. On any `LLMUnavailable` exception (rate limit, network error, malformed JSON after retries, missing key), it **silently falls back** to pre-computed JSON shipped with the repo (`data/precomputed/*.json`). When fallback fires, a banner is shown and an audit entry is written. This means: judges see real AI executing during their evaluation; the demo still works if the API is down or the key is missing.

### 4.4 OCR — three-tier pipeline (the robustness centerpiece)
Bidder documents arrive in mixed formats (typed PDFs, scanned PDFs, photographs of certificates). The OCR pipeline handles each in increasing order of cost:

| Tier | Engine | When it runs | Cost |
|---|---|---|---|
| 1 | PyMuPDF text extraction | Document is a typed PDF (detected via `is_text_pdf` heuristic) | Free, instant |
| 2 | Tesseract (`pytesseract` + system binary) | Document is a scanned PDF or image | Free, fast, accuracy varies |
| 3 | DeepSeek Vision LLM | Tesseract `mean_conf < 0.65` or extracted text suspiciously short | API call, slow, very accurate |

Each extracted page records which tier produced it, and that provenance is shown in the UI ("Read by Tesseract @ 58% → re-read by Vision-LLM @ 95%"). This is more robust than single-engine OCR and is a real production pattern.

### 4.5 Vector store
**ChromaDB** persistent client, embedded in-process, file-backed under `.chroma/`. Default embedding model is `all-MiniLM-L6-v2` from `sentence-transformers` (~80MB, downloaded on first run). Two collections: `tender_chunks`, `bidder_chunks` (filterable by `bidder_id`).

### 4.6 Audit log
**SQLite** single-file DB (`audit.db`) with one append-only table `audit_log`.

### 4.7 Things explicitly cut
- **LayoutLM** — too heavy for the build window. Robustness comes from the 3-tier OCR (vision LLM tier handles documents LayoutLM would otherwise cover).
- **easyocr** — would add ~1GB (PyTorch). Vision-LLM tier replaces it.
- **PostgreSQL** — SQLite is sufficient.
- **React / Next.js / FastAPI split** — Streamlit alone meets all UI needs.
- **Authentication / multi-user** — single hardcoded officer identity.
- **Test infrastructure beyond a smoke test** — explicit time-budget decision.
- **Map-reduce LLM extraction** — mock tender is ~5 pages, fits comfortably in V4's 1M context window in a single call.

---

## 5. Project Structure

```
TenderIQ/
├── app.py                              # Streamlit entry point, tabs router
├── requirements.txt                    # pinned pip deps (section 12)
├── packages.txt                        # apt packages for Streamlit Cloud
├── .env.example                        # DEEPSEEK_API_KEY=
├── .gitignore                          # .env, .chroma/, audit.db, __pycache__, .ocr_cache/
├── README.md                           # run instructions (local + cloud)
├── ARCHITECTURE.md                     # diagram + flow (used as Custom Attachment)
├── IMPLEMENTATION_PLAN.md              # this file
│
├── specs/                              # per-module specs (created during build)
│   ├── 01_config_and_schemas.md
│   ├── 02_llm_client.md
│   ├── 03_pdf_utils.md
│   ├── 04_ocr_pipeline.md
│   ├── 05_chunker.md
│   ├── 06_vectorstore.md
│   ├── 07_criteria_extractor.md
│   ├── 08_bidder_processor.md
│   ├── 09_evaluator.md
│   ├── 10_audit_and_fallback.md
│   ├── 11_mock_data.md
│   ├── 12_precompute.md
│   └── 13_ui_tabs.md
│
├── core/
│   ├── __init__.py
│   ├── config.py                       # env loading, model name, thresholds, paths
│   ├── schemas.py                      # pydantic: Criterion, Evidence, Verdict, AuditEntry
│   ├── prompts.py                      # EXTRACT_CRITERIA_PROMPT, EVALUATE_CRITERION_PROMPT, VISION_OCR_PROMPT
│   ├── llm_client.py                   # DeepSeek wrapper: chat_json, chat_vision, LLMUnavailable
│   ├── pdf_utils.py                    # PyMuPDF: extract_pages, is_text_pdf, render_page_to_image
│   ├── ocr_pipeline.py                 # 3-tier OCR orchestrator
│   ├── chunker.py                      # tender + bidder docs → chunks with metadata
│   ├── vectorstore.py                  # ChromaDB persistent client + helpers
│   ├── criteria_extractor.py           # Stage 1: tender PDF → List[Criterion]
│   ├── bidder_processor.py             # Stage 2: bidder docs → indexed chunks + evidence retrieval
│   ├── evaluator.py                    # Stage 3: per-criterion verdict with combined confidence
│   ├── audit.py                        # SQLite audit log writer/reader
│   └── fallback.py                     # load pre-computed JSON when live LLM fails
│
├── ui/
│   ├── __init__.py
│   ├── tab_overview.py                 # hero, architecture image, KPIs
│   ├── tab_tender.py                   # upload tender → show criteria
│   ├── tab_bidders.py                  # bidder evaluation table with verdicts + sources
│   ├── tab_review.py                   # human review queue (Approve / Edit / Reject)
│   ├── tab_audit.py                    # audit log table + CSV export
│   └── components.py                   # verdict pill, confidence bar, citation chip, OCR-tier badge
│
├── data/
│   ├── tender/
│   │   └── crpf_construction_tender.pdf
│   ├── bidders/
│   │   ├── bidder_a/                   # all eligible — typed PDFs
│   │   ├── bidder_b/                   # ineligible — turnover too low
│   │   └── bidder_c/                   # needs review — scanned turnover cert
│   │       └── turnover_certificate_scan.png
│   └── precomputed/                    # fallback if live API fails
│       ├── criteria.json
│       ├── eval_bidder_a.json
│       ├── eval_bidder_b.json
│       └── eval_bidder_c.json
│
├── scripts/
│   ├── generate_mock_data.py           # reportlab → PDFs + PIL/numpy → noisy scan
│   ├── precompute_results.py           # run pipeline once, save fallback JSON
│   └── smoke_test.py                   # programmatic end-to-end check
│
├── assets/
│   ├── logo.png
│   ├── architecture.png                # for deck + Custom Attachment
│   └── screenshots/                    # 3-5 PNGs for submission
│
└── deck/
    └── TenderIQ_Pitch.pdf              # 8-slide pitch deck
```

Runtime artifacts (gitignored): `.env`, `.chroma/`, `audit.db`, `.ocr_cache/`, `__pycache__/`.

---

## 6. Module Responsibilities

This is the contract surface for each module. Each one will get its own spec document; the descriptions here are the seed material for those specs.

### `core/config.py`
- Load `DEEPSEEK_API_KEY` from `st.secrets` first, then `.env` via `python-dotenv`.
- Constants:
  - `DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"`
  - `MODEL_NAME = "deepseek-v4-pro"`
  - `MODEL_VERSION = "deepseek-v4-pro@<build-date>"` — used for audit stamping
  - `CONFIDENCE_HIGH = 0.80`
  - `CONFIDENCE_REVIEW = 0.55`
  - `OCR_TESSERACT_MIN_CONF = 0.65`
- Paths: `DATA_DIR`, `CHROMA_DIR = ".chroma"`, `AUDIT_DB = "audit.db"`, `PRECOMPUTED_DIR`, `OCR_CACHE_DIR = ".ocr_cache"`.

### `core/schemas.py`
Pydantic models matching the JSON shapes in section 7. At minimum: `Criterion`, `Rule`, `Evidence`, `Source`, `Verdict`, `AuditEntry`.

### `core/prompts.py`
Three string constants — see section 8.

### `core/llm_client.py`
```
class LLMUnavailable(Exception): ...

class LLM:
    def __init__(self, api_key: str | None = None): ...
    def chat_json(self, system: str, user: str, max_retries: int = 2) -> dict: ...
    def chat_vision(self, system: str, user_text: str, image: bytes | str | Path,
                    max_retries: int = 2) -> str: ...
```
- `chat_json` uses `response_format={"type": "json_object"}`, `temperature=0`, retries on JSON parse errors and 5xx with exponential backoff. Raises `LLMUnavailable` after `max_retries`.
- `chat_vision` encodes the image as `data:image/png;base64,...` and sends a multimodal message in OpenAI-compatible format (`{"type": "image_url", "image_url": {"url": "..."}}`). Returns transcribed text. Raises `LLMUnavailable` on failure.
- Every caller in `core/criteria_extractor.py`, `core/evaluator.py`, `core/ocr_pipeline.py` wraps calls in `try/except LLMUnavailable` and routes to `core/fallback.py` (or to a graceful low-confidence result for the OCR case).

### `core/pdf_utils.py`
- `extract_pages(path: Path) -> list[dict]` — returns `[{"page": int, "text": str}]` via `fitz.open`.
- `is_text_pdf(path: Path) -> bool` — heuristic on average chars per page.
- `render_page_to_image(path: Path, page_no: int, dpi: int = 200) -> PIL.Image` — for OCR.

### `core/ocr_pipeline.py`
The robustness centerpiece. Orchestrates the three tiers described in section 4.4.

```
def extract_document(file_path: Path) -> list[ExtractedPage]: ...
```

`ExtractedPage` shape: `{"page": int, "text": str, "source_type": "text_pdf" | "tesseract" | "vision_llm", "confidence": float, "raw_tier_results": {"tesseract_conf": float | None, "vision_used": bool}}`.

Logic:
1. If file is image (PNG/JPG): treat as 1-page; go straight to tier 2.
2. If file is PDF and `is_text_pdf == True`: tier 1 (text_pdf, conf=1.0).
3. Else: for each page render to image, run tier 2 (Tesseract via `pytesseract.image_to_data`), compute mean confidence excluding `-1`s, divided by 100.
4. If `mean_conf < OCR_TESSERACT_MIN_CONF` or text length absurdly short relative to image size: invoke tier 3 (`llm_client.chat_vision(VISION_OCR_PROMPT, image)`), set `source_type="vision_llm"`, `confidence=0.95`. Log `vision_ocr_invoked` audit entry.
5. If tier 3 raises `LLMUnavailable`: keep tier-2 result with `confidence < 0.65` (will trigger `needs_review` downstream).
6. Cache per-file results in `.ocr_cache/<file_hash>.json` so reruns don't re-OCR.

### `core/chunker.py`
- `chunk_tender(pages: list[dict], tender_id: str) -> list[dict]` — ~500-token chunks per page, regex-detect clause headings (`^\d+(\.\d+)*\s+`).
- `chunk_bidder(pages: list[ExtractedPage], bidder_id: str, doc_name: str) -> list[dict]` — page-level chunks (one per page; or per-doc if very short). Each chunk's metadata includes `bidder_id`, `doc_name`, `page`, `source_type`, `ocr_confidence`.

### `core/vectorstore.py`
- `get_client()` cached with `@st.cache_resource`, returns `chromadb.PersistentClient(path=CHROMA_DIR)`.
- `get_collection(name: str)` — creates if missing.
- `add_chunks(collection, chunks: list[dict], metadatas: list[dict])` — ID = `hash(text)[:16]` to dedupe across reruns.
- `query(collection, text: str, k: int = 4, where: dict | None = None) -> list[dict]` — returns `[{text, metadata, distance}, ...]`.

### `core/criteria_extractor.py`
```
def extract_criteria(tender_pdf_path: Path) -> list[Criterion]: ...
```
1. `pdf_utils.extract_pages(tender_pdf_path)` → join all page text with `\n--- PAGE N ---\n` markers.
2. `llm.chat_json(EXTRACT_CRITERIA_PROMPT_SYSTEM, prompt + tender_text)`.
3. Parse JSON `{"criteria": [...]}`, validate via Pydantic, attach UUIDs if absent.
4. Index criteria text into the `tender_chunks` collection (for future retrieval / explainability features).
5. Return list. On `LLMUnavailable` → `fallback.load_criteria()` + audit `precomputed_fallback_used`.

### `core/bidder_processor.py`
```
def process_bidder(bidder_id: str, files: list[Path]) -> None:
    """Extract, chunk, and index every file for this bidder."""

def gather_evidence(bidder_id: str, criterion: Criterion, k: int = 4) -> list[Evidence]:
    """Retrieve top-k bidder chunks relevant to this criterion."""
```
- Process step: each file → `ocr_pipeline.extract_document` → `chunker.chunk_bidder` → `vectorstore.add_chunks(bidder_chunks, ..., where={"bidder_id": bidder_id})`. Audit: `bidder_processed`.
- Gather step: query string = `criterion.title + " " + " ".join(criterion.query_hints)`; `vectorstore.query(bidder_chunks, q, k=4, where={"bidder_id": bidder_id})`. Map results to `Evidence` objects.

### `core/evaluator.py`
```
def evaluate(bidder_id: str, criterion: Criterion) -> Verdict: ...
def evaluate_bidder(bidder_id: str, criteria: list[Criterion]) -> list[Verdict]: ...
```

Algorithm for `evaluate`:
1. `evidence = bidder_processor.gather_evidence(bidder_id, criterion)`.
2. If `evidence` empty: return `Verdict(verdict="needs_review", reason="No matching evidence found in submitted documents.", llm_confidence=0, combined_confidence=0)` and audit. Done.
3. Call `llm.chat_json(EVALUATE_CRITERION_PROMPT_SYSTEM, render_user(criterion, evidence))`.
4. Parse: `{verdict, extracted_value, normalized_value, chosen_source, llm_confidence, reason}`.
5. Compute `combined_confidence` based on `chosen_source.source_type`:
   - `"text_pdf"`: `combined = llm_confidence`
   - `"vision_llm"`: `combined = 0.7 * llm_confidence + 0.3 * 0.95`
   - `"tesseract"`: `combined = 0.6 * llm_confidence + 0.4 * tesseract_conf`
6. Apply threshold rules (in order):
   - LLM verdict is `needs_review` → keep.
   - `combined >= 0.80` → keep LLM verdict.
   - `0.55 <= combined < 0.80` AND verdict is `not_eligible` → **downgrade to `needs_review`** (never silently disqualify).
   - `combined < 0.55` → force `needs_review`.
7. Build `Verdict` object, audit `criterion_evaluated`, return.
8. On `LLMUnavailable` → `fallback.load_evaluation(bidder_id, criterion.id)` + audit fallback.

### `core/audit.py`
- SQLite single table:
  ```sql
  CREATE TABLE audit_log (
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
- `log(action: str, actor: str = "system", **fields) -> int` — inserts.
- `query(filters: dict | None = None) -> list[dict]` — filterable by `bidder_id`, `action`, date range.
- Action vocabulary: `criteria_extracted`, `bidder_processed`, `criterion_evaluated`, `human_review_action`, `precomputed_fallback_used`, `vision_ocr_invoked`.
- Connection cached with `@st.cache_resource`.

### `core/fallback.py`
- `load_criteria() -> list[Criterion]` — reads `data/precomputed/criteria.json`.
- `load_evaluation(bidder_id: str, criterion_id: str) -> Verdict` — reads `data/precomputed/eval_bidder_<id>.json` and indexes into the `criterion_id` block.
- Each fallback hit logs `precomputed_fallback_used` and sets `st.session_state["fallback_active"] = True` so the UI can render the banner.

---

## 7. Data Schemas

All canonical, all serialized as JSON for storage and inter-module communication.

### `Criterion`
```json
{
  "id": "C1",
  "title": "Minimum Annual Turnover",
  "category": "financial",
  "mandatory": true,
  "description": "Average annual turnover during the last three financial years shall not be less than INR 5 Crore.",
  "rule": {
    "type": "numeric_threshold",
    "field": "annual_turnover_inr",
    "operator": ">=",
    "value": 50000000,
    "unit": "INR"
  },
  "query_hints": ["annual turnover", "total revenue", "ITR", "audited financials"],
  "source_page": 3,
  "source_clause": "3.2(a)"
}
```
Fields:
- `category`: `"financial" | "technical" | "compliance"`.
- `rule.type`: `"numeric_threshold" | "count_threshold" | "certification_present" | "document_present"`.
- `rule.operator`: `">=" | "<=" | "==" | "exists"`.
- `query_hints`: 3–5 short noun phrases used to build retrieval queries.

### `Evidence` (one retrieved chunk during evaluation)
```json
{
  "bidder_id": "bidder_a",
  "doc_name": "audited_financials.pdf",
  "page": 4,
  "text": "...annual turnover for FY 2024-25 was INR 6,20,00,000...",
  "source_type": "text_pdf",
  "ocr_confidence": null
}
```
- `source_type`: `"text_pdf" | "tesseract" | "vision_llm"`.
- `ocr_confidence`: 0.0–1.0 if OCR was used; `null` for `text_pdf`.

### `Verdict`
```json
{
  "verdict_id": "V-uuid",
  "bidder_id": "bidder_a",
  "criterion_id": "C1",
  "verdict": "eligible",
  "extracted_value": "INR 6.2 Cr",
  "normalized_value": 62000000,
  "source": {
    "doc_name": "audited_financials.pdf",
    "page": 4,
    "snippet": "...annual turnover... INR 6,20,00,000...",
    "source_type": "text_pdf"
  },
  "llm_confidence": 0.93,
  "ocr_confidence": null,
  "combined_confidence": 0.93,
  "reason": "Extracted turnover of INR 6.2 Cr exceeds the required threshold of INR 5 Cr.",
  "model_version": "deepseek-v4-pro@2026-05-07",
  "timestamp": "2026-05-07T12:34:56Z",
  "review_status": "pending"
}
```
- `verdict`: `"eligible" | "not_eligible" | "needs_review"`.
- `review_status`: `"pending" | "approved" | "edited" | "rejected"`.

### `AuditEntry`
Maps directly to the SQLite row (see `core/audit.py` description). The `payload_json` field carries the action-specific details (e.g., for `criterion_evaluated`: `{"verdict": "eligible", "combined_confidence": 0.93}`).

---

## 8. LLM Prompts

All three prompts must demand strict JSON output where applicable, run at `temperature=0`, and rely on `response_format={"type": "json_object"}` for the JSON ones.

### `EXTRACT_CRITERIA_PROMPT`
**System:**
> You are an expert in Indian government tender analysis (CRPF context). Your job is to extract eligibility criteria from a tender document and return them as STRICT JSON. Never invent criteria not present in the text. Classify each criterion as mandatory or optional based on cue words: "shall", "must", "mandatory", "required", "minimum" → mandatory; "preferred", "desirable", "may", "optionally" → optional. For each criterion, generate 3–5 short noun-phrase query_hints that an evaluator would search for in bidder documents.

**User template:** the full tender text + a JSON schema example + the instruction:
> Return `{"criteria": [Criterion, ...]}`. Each Criterion must include id (C1, C2, ...), title, category (financial / technical / compliance), mandatory (bool), description (verbatim or close paraphrase), rule (typed per the schema), query_hints, source_page (int), source_clause (string).

### `EVALUATE_CRITERION_PROMPT`
**System:**
> You are a procurement evaluator. Given ONE criterion and a list of retrieved evidence chunks from a bidder's documents, decide eligible / not_eligible / needs_review. Always cite the strongest single source. NEVER guess values not present in the evidence. If evidence is missing or ambiguous, return needs_review with reason. Output STRICT JSON.

**User template** (variables substituted):
```
CRITERION:
{ ...criterion JSON... }

RETRIEVED EVIDENCE (top-k chunks from this bidder, with source + OCR confidence):
[
  { "doc_name": "...", "page": 4, "ocr_confidence": null, "source_type": "text_pdf",
    "text": "..." },
  ...
]

Return JSON:
{
  "verdict": "eligible" | "not_eligible" | "needs_review",
  "extracted_value": "<short string as found>",
  "normalized_value": <number or null>,
  "chosen_source": {"doc_name": "...", "page": <int>, "snippet": "<<= 200 chars>", "source_type": "..."},
  "llm_confidence": <0..1>,
  "reason": "<one or two sentences>"
}

Rules:
- If evidence directly contains a value satisfying the rule, verdict=eligible with high llm_confidence.
- If evidence directly contradicts the rule, verdict=not_eligible.
- If no relevant evidence retrieved, verdict=needs_review, llm_confidence<=0.4.
- If the source is OCR with low confidence and the value is borderline, lean to needs_review.
```

### `VISION_OCR_PROMPT`
**System:**
> You are an OCR engine for Indian government procurement documents. Transcribe the image text faithfully, preserving numeric values, dates, certificate IDs, and tabular structure (use markdown tables). Do NOT summarize, interpret, or omit anything. Output transcribed text only — no commentary.

**User text:** "Transcribe this document page completely. Pay special attention to numeric values like turnover figures (INR / Crore / Lakh), dates, and registration numbers." (Image attached.)

---

## 9. Build Order

The order is chosen so that the system is **demoable after every major step**. Each numbered item is also the spec sequence — write the spec, get it reviewed, then implement.

### Step 1 — Skeleton (≈ 15 min)
Folder structure, `requirements.txt`, `packages.txt`, `.env.example`, `.gitignore`, stub `app.py` with 5 empty Streamlit tabs and sidebar.
**Spec:** `specs/00_skeleton.md` (light — mostly file list and stub contents).
**Checkpoint:** `streamlit run app.py` shows the empty shell.

### Step 2 — Mock data generation (≈ 25 min)
`scripts/generate_mock_data.py` produces tender PDF, three bidders' PDFs, and the noisy scan PNG (per section 10).
**Spec:** `specs/11_mock_data.md`.
**Checkpoint:** `data/` directory populated; `turnover_certificate_scan.png` is a visibly noisy scan that Tesseract reads with low confidence.

### Step 3 — Config + schemas + prompts (≈ 25 min)
`core/config.py`, `core/schemas.py`, `core/prompts.py`.
**Spec:** `specs/01_config_and_schemas.md`.

### Step 4 — LLM client (≈ 25 min)
`core/llm_client.py` with both `chat_json` and `chat_vision`. Smoke-test with a one-line script that calls each.
**Spec:** `specs/02_llm_client.md`.
**Checkpoint:** ad-hoc REPL call to `chat_json("hi", "respond with {\"ok\": true}")` returns `{"ok": True}`.

### Step 5 — PDF utils + chunker (≈ 15 min)
`core/pdf_utils.py`, `core/chunker.py`.
**Spec:** `specs/03_pdf_utils.md`, `specs/05_chunker.md` (can be combined).

### Step 6 — Criteria extractor + Tab 2 wiring (≈ 30 min)
`core/criteria_extractor.py` + minimal `ui/tab_tender.py`.
**Spec:** `specs/07_criteria_extractor.md`.
**Checkpoint:** Tab 2 in the running app shows 5 criteria extracted from the mock tender.

### Step 7 — OCR pipeline (≈ 30 min)
`core/ocr_pipeline.py`. Verify on `turnover_certificate_scan.png`.
**Spec:** `specs/04_ocr_pipeline.md`.
**Checkpoint:** running `extract_document(turnover_certificate_scan.png)` first attempts Tesseract (low conf), then falls through to vision-LLM, returns `source_type="vision_llm"` with the correct turnover figure.

### Step 8 — Vector store + bidder processor (≈ 25 min)
`core/vectorstore.py`, `core/bidder_processor.py`.
**Spec:** `specs/06_vectorstore.md`, `specs/08_bidder_processor.md`.
**Checkpoint:** `process_bidder("bidder_a", ...)` indexes all five docs; `gather_evidence("bidder_a", turnover_criterion)` returns top-4 chunks, the strongest mentioning "INR 6,20,00,000".

### Step 9 — Evaluator + threshold logic (≈ 25 min)
`core/evaluator.py`.
**Spec:** `specs/09_evaluator.md`.
**Checkpoint:** `evaluate("bidder_a", turnover_criterion)` returns verdict=eligible, combined_confidence ≥ 0.8; `evaluate("bidder_b", turnover_criterion)` returns verdict=not_eligible.

### Step 10 — Audit + fallback (≈ 20 min)
`core/audit.py`, `core/fallback.py`.
**Spec:** `specs/10_audit_and_fallback.md`.

### Step 11 — Pre-compute results (≈ 15 min)
`scripts/precompute_results.py` runs the full pipeline, dumps `criteria.json` + `eval_bidder_*.json`. Commit results.
**Spec:** `specs/12_precompute.md`.
**Checkpoint:** four JSON files exist and validate against the schemas.

### Step 12 — UI tabs (≈ 80 min total)
- Tab 3 — Bidder evaluation (35 min): rows with verdict pills, source chips, OCR-tier badges, confidence bars, expandable Reason and Source Snippet.
- Tab 4 — Review queue (15 min): filtered list of `needs_review` rows with Approve/Edit/Reject.
- Tab 5 — Audit log (15 min): sortable table + CSV export.
- Tab 1 — Overview (15 min): hero, architecture image, KPIs, "Use Pre-loaded Demo" CTA.

`ui/components.py` is built incrementally as Tabs 3 and 4 need it.
**Spec:** `specs/13_ui_tabs.md` (covers all five tabs and `components.py`).

### Step 13 — Smoke test + README (≈ 15 min)
`scripts/smoke_test.py` (programmatic full flow), `README.md`.

### Step 14 — Streamlit Cloud deploy (≈ 25 min)
Push to GitHub, connect Streamlit Cloud, set `DEEPSEEK_API_KEY` in app secrets, verify deployed URL works in incognito with API and again with the key removed (precomputed mode).

### Step 15 — Submission package (≈ 90 min)
Architecture diagram, 8-slide deck, 4 screenshots, 2-min demo video (OBS / Win+G), zip source, fill submission form.

---

## 10. Mock Data Strategy

Single deterministic script `scripts/generate_mock_data.py`, runs in <30 seconds.

### Tender PDF — `data/tender/crpf_construction_tender.pdf`
`reportlab` SimpleDocTemplate, 5–6 pages with these sections: (1) Introduction, (2) Scope of Work, (3) Eligibility Criteria, (4) Submission Procedure, (5) Evaluation Methodology, (6) Annexures. Section 3 contains five criteria phrased in formal tender language (this is the theme's sample scenario verbatim, so judges will recognize it):

| ID | Clause | Text | Mandatory? | Category |
|---|---|---|---|---|
| C1 | 3.2(a) | "...minimum average annual turnover of INR 5 Crore (Rupees Five Crore only) during the last three financial years..." | Yes | financial |
| C2 | 3.2(b) | "...successfully completed at least three (3) similar construction projects in the last five (5) financial years..." | Yes | technical |
| C3 | 3.2(c) | "...shall possess a valid Goods and Services Tax (GST) registration..." | Yes | compliance |
| C4 | 3.2(d) | "...shall hold a valid ISO 9001:2015 Quality Management System certification..." | Yes | compliance |
| C5 | 3.2(e) | "...preferably, the bidder may have prior experience with paramilitary infrastructure..." | **No** | technical |

C5 tests the mandatory-vs-optional classification.

### Bidder A (clearly eligible) — typed PDFs only
`company_profile.pdf`, `audited_financials.pdf` (FY 22-23: ₹5.8 Cr, 23-24: ₹6.2 Cr, 24-25: ₹7.1 Cr), `project_experience.pdf` (5 projects in 5 years), `gst_certificate.pdf` (GSTIN, valid 2027), `iso_9001.pdf` (valid 2027).

### Bidder B (clearly ineligible — turnover too low) — typed PDFs only
Same docs as A but `audited_financials.pdf` shows ₹1.2 / ₹1.5 / ₹1.8 Cr (all below threshold). Other criteria pass.

### Bidder C (needs review — scanned turnover certificate) — typed + one scan
Typed `company_profile.pdf`, `project_experience.pdf` (3 projects — borderline meets count), `gst_certificate.pdf`, `iso_9001.pdf`.

**`turnover_certificate_scan.png`** generation:
1. Render a `reportlab` page with the CA's turnover statement.
2. Convert to `PIL.Image` via `pillow`.
3. Apply: `ImageFilter.GaussianBlur(radius=1.5)`, salt-and-pepper noise via `numpy`, `image.rotate(-2, fillcolor="white")`, JPEG-compress at quality=40, save as PNG.
4. Outcome: Tesseract reads it with mean confidence ~50–65% → triggers Tier-3 vision LLM. Vision LLM transcribes correctly; combined-confidence rule still routes Bidder C to `needs_review` (this is intended — it demonstrates the safety rule).

### Pre-computed fallback files — `data/precomputed/`
After the pipeline modules are working, run `scripts/precompute_results.py` once to produce:
- `criteria.json` — output of `extract_criteria(tender_pdf)`.
- `eval_bidder_a.json`, `eval_bidder_b.json`, `eval_bidder_c.json` — per-bidder verdicts for all criteria.

Commit these four files to the repo. They are the safety net for live demos.

---

## 11. Streamlit UI

5 tabs, left-to-right narrative order:

### Tab 1 — Overview
Hero text ("TenderIQ — explainable AI for tender evaluation"), architecture image (`assets/architecture.png`), 4 KPI cards (criteria extracted, bidders evaluated, hours saved, audit entries). "Use Pre-loaded Demo Data" (default) and "Upload Your Own" CTA.

### Tab 2 — Tender Analysis
File uploader (defaults to mock tender preview). Button **"Extract Criteria (Live LLM)"** runs `criteria_extractor`. Results render as cards with category badge (color-coded), mandatory pill, description, source-page chip. Cached to `st.session_state["criteria"]`.

### Tab 3 — Bidder Evaluation
Bidder multi-select (defaults all 3). Button **"Run Evaluation"** processes each bidder × each criterion. Output: rows with verdict pill (green/red/amber), extracted value, source chip (doc + page + **OCR-tier badge** showing `text_pdf` / `tesseract` / `vision_llm`), confidence bar, expandable Reason and Source Snippet. Per-bidder summary header: "X / 4 mandatory criteria met — Overall: Eligible / Not Eligible / Needs Review".

### Tab 4 — Human Review Queue
Filtered to verdicts where `review_status == "pending"` AND `verdict == "needs_review"`. Each row: criterion, bidder, extracted value (editable), confidence, reason, source snippet, image preview if OCR'd. Buttons: Approve / Edit & Approve / Reject — each writes audit entry and updates `review_status`.

### Tab 5 — Audit Log
Sortable table from `audit.query()`. Filter by bidder, action type. CSV export.

### Sidebar (always visible)
Logo, project name, **DeepSeek connection status dot**:
- Green: live connection, no fallback fired this session.
- Amber: fallback fired at least once this session.
- Red: probe at startup failed.
"Reset Session" button. If `st.session_state["fallback_active"]`, show banner: "⚠ Live API unavailable — showing pre-computed results."

---

## 12. requirements.txt and packages.txt

`requirements.txt` (pinned):
```
streamlit==1.39.0
openai==1.51.0
pymupdf==1.24.10
pytesseract==0.3.13
Pillow==10.4.0
numpy==1.26.4
chromadb==0.5.5
sentence-transformers==3.1.1
pydantic==2.9.2
python-dotenv==1.0.1
reportlab==4.2.5
pandas==2.2.3
```

`packages.txt` (apt packages for Streamlit Cloud):
```
tesseract-ocr
poppler-utils
```

---

## 13. Risks and Mitigations

| Risk | Mitigation |
|---|---|
| **DeepSeek API down or rate-limited mid-demo.** | Live-first with silent fallback to `data/precomputed/*.json`. Sidebar dot turns amber. App keeps working. |
| **Tesseract install on Streamlit Cloud.** | `packages.txt` with `tesseract-ocr`. If it still fails: Tier-3 vision LLM works on raw image input, and `data/precomputed/eval_bidder_c.json` is the final safety net. |
| **DeepSeek vision call (Tier 3) fails.** | Tesseract result accepted with `confidence < 0.65` → flows to `needs_review`. Demo still works. |
| **ChromaDB first-run sentence-transformers download (~80 MB).** | `@st.cache_resource` on the client. README warns "first cloud load may take ~30s". Pre-warm by visiting deployed URL once before submission. |
| **LLM returns malformed JSON.** | `response_format={"type":"json_object"}` + 2 retries with stricter system prompt → fall back to precomputed for that item. |
| **PyMuPDF licensing.** | AGPL but allowed for hackathon use; pin `pymupdf==1.24.10`; mention in README. |
| **API key leak in repo.** | `.env` gitignored; `.env.example` ships with placeholder; Streamlit Cloud secrets used in deploy; pre-commit visual diff check. |
| **Time overrun.** | Compression order: skip Tab 1 KPIs → skip optional 5th criterion → skip CSV export → keep core flow (Tabs 2–4) intact for the video. |

---

## 14. Verification (run before recording the demo video)

Treat this as the acceptance test. The demo video should walk through these steps in order.

1. **Cold start.** Delete `.chroma/`, `audit.db`. Run `streamlit run app.py`. App opens in <10s; Tab 1 renders.
2. **Live extraction.** Tab 2 → "Extract Criteria" → 5 criteria appear within 10–20s. Sidebar dot green.
3. **Live evaluation, Bidder A.** Tab 3 → select Bidder A → "Run Evaluation". All 4 mandatory criteria → `eligible` with combined confidence ≥ 0.80.
4. **Live evaluation, Bidder B.** Turnover criterion → `not_eligible` with reason citing low turnover figure and source page.
5. **Live evaluation, Bidder C — the OCR demo path.** Turnover criterion → triggers Tier 2 (Tesseract low conf) → triggers Tier 3 (DeepSeek Vision). UI shows "Read by Tesseract @ ~58% → Vision-LLM @ 95%". Final verdict: `needs_review`. Audit log gains a `vision_ocr_invoked` entry.
6. **Review action.** Tab 4 → click "Approve" on Bidder C's turnover row → audit log gains `human_review_action` entry within 1 second; `review_status` updates.
7. **Audit export.** Tab 5 → "Export CSV" → CSV downloads with all entries.
8. **No-API run.** Rename `.env` (or unset secret), restart app → all "Run Live" buttons silently fall back to precomputed, banner shown, sidebar dot amber, audit gets `precomputed_fallback_used` entries.
9. **Smoke test.** `python scripts/smoke_test.py` exits 0.
10. **Deployed URL.** Open Streamlit Cloud URL in incognito; repeat steps 1–6.

---

## 15. Submission Deliverables (Round 2 form fields)

Mapping of submission requirements to artifacts:

| Form field | Artifact |
|---|---|
| Title | "TenderIQ — Explainable AI for Tender Evaluation" |
| Description | Adapted from `idea.md` |
| Parent Submission | The shortlisted Round 1 idea |
| Theme | Theme 3 |
| Snapshots | `assets/screenshots/*.png` |
| Video URL | YouTube unlisted link to 2-min demo |
| Presentation | `deck/TenderIQ_Pitch.pdf` |
| Demo Link | Streamlit Cloud URL |
| Repository URL | GitHub URL |
| Source Code | Zip of repo (excluding `.env`, `.chroma/`, `audit.db`) |
| Instructions to Run | `README.md` quickstart |
| Custom Attachment | `ARCHITECTURE.md` exported as PDF (with the architecture diagram embedded) |

---

## 16. Definition of Done

The build is done when **all** of the following are true:

- [ ] All 10 verification steps in section 14 pass.
- [ ] Streamlit Cloud URL is live and reachable.
- [ ] GitHub repo is public, with `.env` not committed.
- [ ] `README.md` quickstart works on a fresh clone with no API key (precomputed mode).
- [ ] Pitch deck, demo video, screenshots, and architecture PDF are produced.
- [ ] Submission form is filled and submitted.
- [ ] Memory note saved with deployment URL and submission timestamp.
