import streamlit as st

from core import audit
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

    st.subheader("How it works")
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
**Stage 1 — Extract Criteria**
DeepSeek LLM reads the tender PDF and extracts each eligibility criterion as structured JSON (category, rule, query hints).

**Stage 2 — OCR & Index Bidder Docs**
Three-tier OCR: PyMuPDF (typed PDF) → Tesseract → DeepSeek Vision LLM (low-confidence scans). All pages indexed into ChromaDB.
""")
    with col_b:
        st.markdown("""
**Stage 3 — Evaluate per Criterion**
Vector search retrieves relevant evidence chunks. DeepSeek evaluates eligible / not_eligible / needs_review with a combined confidence score.

**Stage 4 — Human Review & Audit**
Low-confidence verdicts are routed to the review queue. Every action is logged with timestamp, model version, and payload.
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
            for bidder_id in ["bidder_a", "bidder_b", "bidder_c"]:
                verdicts_dict[bidder_id] = [
                    load_evaluation(bidder_id, c.id).model_dump()
                    for c in criteria
                ]
            st.session_state["verdicts"] = verdicts_dict
            st.success("Pre-computed demo data loaded. Navigate to the other tabs.")
            st.rerun()
    with col2:
        st.info("Or go to **Tender Analysis** tab to run the live LLM pipeline.")
