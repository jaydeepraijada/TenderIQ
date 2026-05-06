# TenderIQ — Project Understanding

---

## Where We Are

The idea phase (Round 1) is **done and shortlisted**. The `idea.md` was the written submission. We are now in the **Prototype Phase (Round 2)**, which requires a working prototype, demo, code repository, pitch deck, and video.

---

## The Problem (from CRPF's perspective)

CRPF issues tenders. Companies bid. Someone has to manually read:
- The tender document (criteria, thresholds, compliance rules)
- Every bidder's stack of supporting documents (PDFs, scans, photos, Word files)

...and verify that each bidder meets each criterion. For one tender, this takes a committee days. Two evaluators may reach different conclusions from the same documents. There's no consistent audit trail.

**The core pain points:**
1. Manual, slow, expensive
2. Inconsistent across evaluators
3. Not auditable / not transparent
4. Documents arrive in messy formats (scanned, photographed, mixed)

---

## What TenderIQ Does

A four-stage AI pipeline:

```
Tender Document ──► [Stage 1] Criteria Extraction
                              │
                              ▼
Bidder Documents ──► [Stage 2] Document Processing (OCR + entity extraction)
                              │
                              ▼
                    [Stage 3] Evaluation Engine (rule-based + confidence)
                              │
                              ▼
                    [Stage 4] Explainability + Audit Layer
                              │
                    ┌─────────┴──────────┐
                    ▼                    ▼
               Auto-decision       Human Review Queue
           (Eligible / Not Eligible)  (Needs Manual Review)
```

### Stage 1 — Tender Understanding
- LLM + rule-based hybrid extracts criteria from tender doc
- Classifies each as mandatory or optional
- Outputs structured, machine-readable criteria list

### Stage 2 — Bidder Document Processing
- Handles: typed PDFs, scanned docs, images, Word files
- OCR for non-digital content
- Layout-aware parsing (tables, forms, certificates)
- Entity extraction: turnover figures, cert names, project counts
- Every extracted value tagged with: source doc, page number, confidence score

### Stage 3 — Evaluation Engine
- Criterion-by-criterion comparison per bidder
- Rule-based validation (threshold checks)
- Confidence-aware: low confidence → "Needs Manual Review", not auto-reject
- Three outcomes: Eligible / Not Eligible / Needs Manual Review

### Stage 4 — Explainability + Audit
- Every decision has: criterion checked, value found, source doc, confidence, reason
- Full audit log: model version, timestamp, reviewer actions
- Human reviewers can approve / edit / reject flagged cases
- Reviewer decisions feed back into system improvement

---

## Non-Negotiables (from theme)

These are hard constraints, not nice-to-haves:

| Constraint | Implication for build |
|---|---|
| Every verdict must be explainable at criterion level | No black-box scoring; each criterion decision must be traceable |
| Never silently disqualify | Low confidence = human review queue, not auto-reject |
| Must handle scanned docs and photographs | OCR is not optional |
| End-to-end auditable | Every system action must be logged with immutable records |

---

## What We Need to Deliver (Prototype Phase)

| Deliverable | What it means |
|---|---|
| Working demo | The pipeline must actually run on mock/sample data |
| Demo link | Hosted or accessible prototype |
| Repo URL | Clean, documented code |
| Source code zip | Packaged for reviewers to run |
| Run instructions | Step-by-step so reviewers can test it |
| Presentation | Pitch deck covering the full solution |
| Video | Demo + pitch walkthrough |
| Snapshots | Screenshots of the UI/output |
| Description | Written summary of the project |

---

## Proposed Tech Stack (from idea)

| Component | Technology | Why |
|---|---|---|
| LLM for criteria extraction | LLM (e.g., Claude, GPT-4, or open-source) | Handles legal language, ambiguity |
| OCR | Tesseract or PaddleOCR | Open-source, handles scanned docs and images |
| Document layout understanding | LayoutLM | Understands tables, forms, structured layouts |
| Backend | Python + FastAPI | Fast to build, good ML ecosystem |
| Database | PostgreSQL + vector DB | Structured storage + semantic search |
| Frontend | React | Dashboard for review, reporting |

---

## Key Design Decisions to Think About

### 1. Hybrid extraction (LLM + rules)
- Pure LLM: flexible but unpredictable on numeric thresholds
- Pure rules: precise but brittle on varied language
- Hybrid: LLM for interpretation, rules for validation — best of both

### 2. Confidence threshold design
- What confidence score triggers "Needs Manual Review"?
- This is a calibration problem — too low a threshold floods reviewers, too high risks bad auto-decisions

### 3. Vector DB role
- Enables semantic search over extracted bidder data
- Useful when a criterion mentions "similar projects" and you need to match against descriptions

### 4. Audit log immutability
- Government procurement context requires tamper-evident logs
- Must capture: what AI decided, why, when, which model version, and what the human reviewer did

---

## Gaps / Things Not Yet Defined

- **Which LLM?** The idea says "LLMs" but doesn't specify. For a prototype, this matters.
- **Which vector DB?** Pinecone, Weaviate, ChromaDB, pgvector — not chosen yet.
- **Criteria schema** — what does the structured criterion object look like exactly?
- **Confidence score methodology** — how is it calculated and what thresholds are used?
- **UI scope** — how much of the review interface needs to be built for the prototype?
- **Mock data** — we need sample tender docs and bidder submissions to demo against.
- **Evaluation report format** — what does the exported report look like?

---

## Summary

The idea is solid and already shortlisted. The core insight is: **don't try to fully automate procurement decisions; build a system that makes human reviewers dramatically faster and more consistent, with a complete audit trail.** The prototype needs to demonstrate this pipeline end-to-end on mock data, with a UI that shows criterion-level explanations.

Next step: define the implementation plan — what to build, in what order, and what scope is realistic for the prototype.
