# Spec 00 — Project Skeleton

**Step:** 1 of 15  
**Time budget:** ~15 min  
**Checkpoint:** `streamlit run app.py` opens in the browser showing 5 named tabs and a sidebar with logo placeholder, project name, and connection status dot. No errors in the terminal.

---

## Goal

Create every file and directory that Step 2 onward will write into. All Python modules are stubs (importable but empty of logic). The running app must render without crashing.

---

## Files to Create

### Root-level files

#### `requirements.txt`
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

#### `packages.txt`
```
tesseract-ocr
poppler-utils
```

#### `.env.example`
```
DEEPSEEK_API_KEY=your_key_here
```

#### `.gitignore`
```
.env
.chroma/
audit.db
__pycache__/
*.pyc
.ocr_cache/
*.egg-info/
dist/
build/
.DS_Store
Thumbs.db
```

#### `app.py` — Streamlit entry point (stub)

Exact stub content:

```python
import streamlit as st

from ui.tab_overview import render as render_overview
from ui.tab_tender import render as render_tender
from ui.tab_bidders import render as render_bidders
from ui.tab_review import render as render_review
from ui.tab_audit import render as render_audit

st.set_page_config(
    page_title="TenderIQ",
    page_icon="⚖️",
    layout="wide",
)

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚖️ TenderIQ")
    st.caption("Explainable AI for Tender Evaluation")
    st.divider()
    # Connection status — placeholder until core/llm_client.py is wired
    st.markdown("🔴 **DeepSeek:** not connected")
    st.divider()
    if st.button("Reset Session", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# ── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "Overview",
    "Tender Analysis",
    "Bidder Evaluation",
    "Human Review",
    "Audit Log",
])

with tab1:
    render_overview()

with tab2:
    render_tender()

with tab3:
    render_bidders()

with tab4:
    render_review()

with tab5:
    render_audit()
```

---

### `core/` package — all stubs

Every file in `core/` must be importable and expose the names that `app.py` or other modules reference at import time. No logic yet — just `pass` stubs and placeholder class/function signatures.

#### `core/__init__.py`
Empty.

#### `core/config.py`
```python
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_KEY: str | None = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
MODEL_NAME = "deepseek-chat"
MODEL_VERSION = f"{MODEL_NAME}@2026-05-07"

CONFIDENCE_HIGH = 0.80
CONFIDENCE_REVIEW = 0.55
OCR_TESSERACT_MIN_CONF = 0.65

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CHROMA_DIR = str(BASE_DIR / ".chroma")
AUDIT_DB = str(BASE_DIR / "audit.db")
PRECOMPUTED_DIR = DATA_DIR / "precomputed"
OCR_CACHE_DIR = BASE_DIR / ".ocr_cache"
```

#### `core/schemas.py`
```python
from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel, Field
import uuid


class Rule(BaseModel):
    type: Literal["numeric_threshold", "count_threshold", "certification_present", "document_present"]
    field: str
    operator: Literal[">=", "<=", "==", "exists"]
    value: float | int | None = None
    unit: str | None = None


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


class Evidence(BaseModel):
    bidder_id: str
    doc_name: str
    page: int
    text: str
    source_type: Literal["text_pdf", "tesseract", "vision_llm"]
    ocr_confidence: float | None = None


class Source(BaseModel):
    doc_name: str
    page: int
    snippet: str
    source_type: Literal["text_pdf", "tesseract", "vision_llm"]


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

#### `core/prompts.py`
```python
EXTRACT_CRITERIA_PROMPT_SYSTEM = """\
You are an expert in Indian government tender analysis (CRPF context). Your job is to extract \
eligibility criteria from a tender document and return them as STRICT JSON. Never invent criteria \
not present in the text. Classify each criterion as mandatory or optional based on cue words: \
"shall", "must", "mandatory", "required", "minimum" → mandatory; "preferred", "desirable", \
"may", "optionally" → optional. For each criterion, generate 3–5 short noun-phrase query_hints \
that an evaluator would search for in bidder documents.\
"""

EVALUATE_CRITERION_PROMPT_SYSTEM = """\
You are a procurement evaluator. Given ONE criterion and a list of retrieved evidence chunks from \
a bidder's documents, decide eligible / not_eligible / needs_review. Always cite the strongest \
single source. NEVER guess values not present in the evidence. If evidence is missing or \
ambiguous, return needs_review with reason. Output STRICT JSON.\
"""

VISION_OCR_PROMPT_SYSTEM = """\
You are an OCR engine for Indian government procurement documents. Transcribe the image text \
faithfully, preserving numeric values, dates, certificate IDs, and tabular structure (use \
markdown tables). Do NOT summarize, interpret, or omit anything. Output transcribed text only — \
no commentary.\
"""

VISION_OCR_USER = (
    "Transcribe this document page completely. Pay special attention to numeric values like "
    "turnover figures (INR / Crore / Lakh), dates, and registration numbers."
)
```

#### `core/llm_client.py`
```python
from pathlib import Path


class LLMUnavailable(Exception):
    pass


class LLM:
    def __init__(self, api_key: str | None = None):
        pass

    def chat_json(self, system: str, user: str, max_retries: int = 2) -> dict:
        raise NotImplementedError

    def chat_vision(
        self,
        system: str,
        user_text: str,
        image: bytes | str | Path,
        max_retries: int = 2,
    ) -> str:
        raise NotImplementedError
```

#### `core/pdf_utils.py`
```python
from pathlib import Path
import PIL.Image


def extract_pages(path: Path) -> list[dict]:
    raise NotImplementedError


def is_text_pdf(path: Path) -> bool:
    raise NotImplementedError


def render_page_to_image(path: Path, page_no: int, dpi: int = 200) -> PIL.Image.Image:
    raise NotImplementedError
```

#### `core/ocr_pipeline.py`
```python
from pathlib import Path


class ExtractedPage:
    page: int
    text: str
    source_type: str  # "text_pdf" | "tesseract" | "vision_llm"
    confidence: float
    raw_tier_results: dict


def extract_document(file_path: Path) -> list[ExtractedPage]:
    raise NotImplementedError
```

#### `core/chunker.py`
```python
from core.ocr_pipeline import ExtractedPage


def chunk_tender(pages: list[dict], tender_id: str) -> list[dict]:
    raise NotImplementedError


def chunk_bidder(
    pages: list[ExtractedPage], bidder_id: str, doc_name: str
) -> list[dict]:
    raise NotImplementedError
```

#### `core/vectorstore.py`
```python
def get_client():
    raise NotImplementedError


def get_collection(name: str):
    raise NotImplementedError


def add_chunks(collection, chunks: list[dict], metadatas: list[dict]) -> None:
    raise NotImplementedError


def query(
    collection, text: str, k: int = 4, where: dict | None = None
) -> list[dict]:
    raise NotImplementedError
```

#### `core/criteria_extractor.py`
```python
from pathlib import Path
from core.schemas import Criterion


def extract_criteria(tender_pdf_path: Path) -> list[Criterion]:
    raise NotImplementedError
```

#### `core/bidder_processor.py`
```python
from pathlib import Path
from core.schemas import Criterion, Evidence


def process_bidder(bidder_id: str, files: list[Path]) -> None:
    raise NotImplementedError


def gather_evidence(bidder_id: str, criterion: Criterion, k: int = 4) -> list[Evidence]:
    raise NotImplementedError
```

#### `core/evaluator.py`
```python
from core.schemas import Criterion, Verdict


def evaluate(bidder_id: str, criterion: Criterion) -> Verdict:
    raise NotImplementedError


def evaluate_bidder(bidder_id: str, criteria: list[Criterion]) -> list[Verdict]:
    raise NotImplementedError
```

#### `core/audit.py`
```python
def log(action: str, actor: str = "system", **fields) -> int:
    raise NotImplementedError


def query(filters: dict | None = None) -> list[dict]:
    raise NotImplementedError
```

#### `core/fallback.py`
```python
from core.schemas import Criterion, Verdict


def load_criteria() -> list[Criterion]:
    raise NotImplementedError


def load_evaluation(bidder_id: str, criterion_id: str) -> Verdict:
    raise NotImplementedError
```

---

### `ui/` package — all stubs

Each tab module exports a single `render()` function that renders a placeholder heading. No logic.

#### `ui/__init__.py`
Empty.

#### `ui/tab_overview.py`
```python
import streamlit as st

def render() -> None:
    st.header("Overview")
    st.info("Coming soon — architecture diagram, KPIs, and demo CTA.")
```

#### `ui/tab_tender.py`
```python
import streamlit as st

def render() -> None:
    st.header("Tender Analysis")
    st.info("Coming soon — upload tender and extract eligibility criteria.")
```

#### `ui/tab_bidders.py`
```python
import streamlit as st

def render() -> None:
    st.header("Bidder Evaluation")
    st.info("Coming soon — per-bidder, per-criterion verdict table.")
```

#### `ui/tab_review.py`
```python
import streamlit as st

def render() -> None:
    st.header("Human Review Queue")
    st.info("Coming soon — approve / edit / reject flagged verdicts.")
```

#### `ui/tab_audit.py`
```python
import streamlit as st

def render() -> None:
    st.header("Audit Log")
    st.info("Coming soon — sortable audit log with CSV export.")
```

#### `ui/components.py`
```python
# Shared UI widgets — implemented incrementally as Tab 3 and Tab 4 need them.
```

---

### `data/` directory structure (empty folders only)

```
data/
  tender/
  bidders/
    bidder_a/
    bidder_b/
    bidder_c/
  precomputed/
```

No files yet — Step 2 (mock data generation) populates these.

---

### `scripts/` directory (empty stubs)

#### `scripts/generate_mock_data.py`
```python
"""Step 2 — generates mock tender and bidder PDFs + noisy scan PNG."""
```

#### `scripts/precompute_results.py`
```python
"""Step 11 — runs the full pipeline and writes data/precomputed/*.json."""
```

#### `scripts/smoke_test.py`
```python
"""Step 13 — programmatic end-to-end check; exits 0 on success."""
```

---

### `assets/` directory (empty, for later)

```
assets/
  screenshots/
```

---

### `deck/` directory (empty, for later)

```
deck/
```

---

## Directory Tree After This Step

```
TenderIQ/
├── app.py
├── requirements.txt
├── packages.txt
├── .env.example
├── .gitignore
├── specs/
│   └── 00_skeleton.md          ← this file
├── core/
│   ├── __init__.py
│   ├── config.py
│   ├── schemas.py
│   ├── prompts.py
│   ├── llm_client.py
│   ├── pdf_utils.py
│   ├── ocr_pipeline.py
│   ├── chunker.py
│   ├── vectorstore.py
│   ├── criteria_extractor.py
│   ├── bidder_processor.py
│   ├── evaluator.py
│   ├── audit.py
│   └── fallback.py
├── ui/
│   ├── __init__.py
│   ├── tab_overview.py
│   ├── tab_tender.py
│   ├── tab_bidders.py
│   ├── tab_review.py
│   ├── tab_audit.py
│   └── components.py
├── data/
│   ├── tender/
│   ├── bidders/
│   │   ├── bidder_a/
│   │   ├── bidder_b/
│   │   └── bidder_c/
│   └── precomputed/
├── scripts/
│   ├── generate_mock_data.py
│   ├── precompute_results.py
│   └── smoke_test.py
├── assets/
│   └── screenshots/
└── deck/
```

Runtime artifacts (gitignored, not created here): `.env`, `.chroma/`, `audit.db`, `.ocr_cache/`.

---

## Acceptance Criteria

1. `python -c "import app"` executes without `ImportError` (all stubs importable).
2. `streamlit run app.py` opens in the browser without a Python traceback.
3. Five tabs are visible: Overview, Tender Analysis, Bidder Evaluation, Human Review, Audit Log.
4. Sidebar shows "⚖️ TenderIQ", a caption, a red connection dot placeholder, and a "Reset Session" button.
5. Each tab body shows an `st.info(...)` placeholder — no blank white screens.
6. `python -c "from core import config, schemas, prompts"` runs without error.

---

## What This Step Does NOT Do

- No logic implemented in any `core/` module.
- No Streamlit secrets or `.env` required to pass the checkpoint.
- No data files generated (Step 2 does that).
- No pip install triggered (assumed the environment is set up separately).
