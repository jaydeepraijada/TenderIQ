import streamlit as st

from core import audit
from core.config import BIDDER_NAMES
from core.fallback import load_criteria


def render() -> None:
    st.header("⚖️ TenderIQ — Explainable AI for Tender Evaluation")
    st.markdown(
        "Automated eligibility evaluation of bidders against government tender criteria, "
        "with criterion-level explainability, OCR for scanned documents, and a complete audit trail."
    )
    st.divider()

    # KPI cards
    criteria_count = len(st.session_state.get("criteria", load_criteria()))
    verdicts = st.session_state.get("verdicts", {})
    bidders_evaluated = len(verdicts)
    mandatory_checked = sum(
        1 for bv in verdicts.values() for v in bv
        if v.get("verdict") in ("eligible", "not_eligible", "needs_review")
    )
    audit_entries = len(audit.query())

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Criteria Extracted", criteria_count)
    c2.metric("Bidders Evaluated", bidders_evaluated)
    c3.metric("Criteria Checked", mandatory_checked)
    c4.metric("Audit Entries", audit_entries)

    st.divider()

    # Architecture diagram
    st.subheader("System Architecture")
    st.markdown("""
```
┌─────────────────────────────────────────────────────────────────────┐
│                        TenderIQ Pipeline                            │
└─────────────────────────────────────────────────────────────────────┘

  📄 Tender PDF                      📁 Bidder Documents
       │                              (PDFs, scans, photos)
       │                                      │
       ▼                                      ▼
 ┌───────────┐                    ┌────────────────────────┐
 │  DeepSeek │                    │   3-Tier OCR Pipeline  │
 │    LLM    │                    │  ① PyMuPDF  (typed)   │
 │ (Stage 1) │                    │  ② Tesseract (scans)  │
 └───────────┘                    │  ③ Vision LLM (poor)  │
       │                          └────────────────────────┘
       │                                      │
       ▼                                      ▼
 ┌───────────┐                    ┌────────────────────────┐
 │ Criteria  │                    │   ChromaDB Vector      │
 │  C1 – C5  │                    │   Index (per bidder)   │
 │ (JSON)    │                    └────────────────────────┘
 └───────────┘                                │
       │                                      │  semantic search
       └──────────────────┬───────────────────┘
                          │
                          ▼
               ┌─────────────────────┐
               │   DeepSeek LLM      │
               │   (Stage 3 eval)    │
               │                     │
               │  evidence → verdict │
               │  + confidence score │
               └─────────────────────┘
                          │
            ┌─────────────┴──────────────┐
            │                            │
            ▼                            ▼
   confidence ≥ 0.80            confidence < 0.80
   verdict kept                 downgraded to
                                needs_review
                                      │
                                      ▼
                             ┌─────────────────┐
                             │  Human Review   │
                             │  Queue (Tab 4)  │
                             └─────────────────┘
                                      │
                                      ▼
                             ┌─────────────────┐
                             │   Audit Log     │
                             │  (every action) │
                             └─────────────────┘
```
""")

    st.divider()

    st.subheader("Pipeline Stages")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
**① Extract Criteria**
DeepSeek reads the full tender PDF and extracts each eligibility criterion as structured JSON —
category, mandatory flag, rule (threshold / certification / count), source clause, and query hints
for downstream retrieval.

**② OCR & Index Bidder Documents**
Three-tier pipeline handles any document format:
PyMuPDF for typed PDFs (instant, lossless) →
Tesseract for scans (free, fast) →
DeepSeek Vision LLM when Tesseract confidence < 65%.
All text is chunked and indexed into ChromaDB with full provenance metadata.
""")
    with col_b:
        st.markdown("""
**③ Evaluate per Criterion**
For each (bidder × criterion) pair: semantic search retrieves the most relevant evidence chunks,
DeepSeek decides eligible / not_eligible / needs_review with a combined confidence score
that weights LLM certainty against OCR quality.
The safety rule: never silently disqualify — borderline cases always go to human review.

**④ Human Review & Audit**
Flagged verdicts surface in the Review Queue with full evidence and source citations.
Every action — extraction, indexing, evaluation, review — is logged to SQLite with
timestamp, model version, actor, and payload.
""")

    st.divider()

    st.subheader("Quick Start")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Load Pre-computed Demo", type="primary", use_container_width=True):
            from core.fallback import load_criteria as lc, load_evaluation
            criteria = lc()
            st.session_state["criteria"] = [c.model_dump() for c in criteria]
            verdicts_dict: dict = {}
            for bidder_id in BIDDER_NAMES:
                verdicts_dict[bidder_id] = [
                    load_evaluation(bidder_id, c.id).model_dump()
                    for c in criteria
                ]
            st.session_state["verdicts"] = verdicts_dict
            st.success("Pre-computed demo loaded. Navigate to the other tabs.")
            st.rerun()
    with col2:
        st.info("Or go to **Tender Analysis** to run the live LLM pipeline.")
