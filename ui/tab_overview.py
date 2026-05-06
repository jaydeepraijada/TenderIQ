import streamlit as st

from core import audit
from core.config import BIDDER_NAMES
from core.fallback import load_criteria


def render() -> None:
    # Hero banner
    st.markdown(
        """<div class="tiq-hero">
        <h1>⚖️ TenderIQ</h1>
        <p>Explainable AI for Government Tender Evaluation &nbsp;·&nbsp;
           CRPF Hackathon Theme 3</p>
        <p style="font-size:0.88rem;margin-top:8px;color:#94A3B8;">
        Automated eligibility evaluation with criterion-level explainability,
        three-tier OCR for scanned documents, and a complete audit trail.</p>
        </div>""",
        unsafe_allow_html=True,
    )

    # KPI strip
    criteria_count = len(st.session_state.get("criteria", load_criteria()))
    verdicts = st.session_state.get("verdicts", {})
    bidders_evaluated = len(verdicts)
    mandatory_checked = sum(
        1 for bv in verdicts.values() for v in bv
        if v.get("verdict") in ("eligible", "not_eligible", "needs_review")
    )
    audit_entries = len(audit.query())

    c1, c2, c3, c4 = st.columns(4)
    for col, val, lbl in [
        (c1, criteria_count,    "Criteria Extracted"),
        (c2, bidders_evaluated, "Bidders Evaluated"),
        (c3, mandatory_checked, "Criteria Checked"),
        (c4, audit_entries,     "Audit Entries"),
    ]:
        col.markdown(
            f'<div class="tiq-kpi">'
            f'<div class="tiq-kpi-val">{val}</div>'
            f'<div class="tiq-kpi-lbl">{lbl}</div>'
            f'</div>',
            unsafe_allow_html=True,
        )

    st.divider()

    # Architecture
    st.markdown('<div class="tiq-section-header"><div style="font-size:1.1rem;font-weight:700;color:#0D1B2A;">Pipeline Architecture</div></div>', unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
<div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:12px;padding:20px;">
<div style="font-weight:700;color:#1E3A5F;margin-bottom:12px;">📥 Ingestion</div>

<div style="display:flex;align-items:flex-start;gap:10px;margin-bottom:10px;">
<div style="background:#DBEAFE;color:#1E40AF;border-radius:6px;padding:3px 8px;font-size:0.75rem;font-weight:700;flex-shrink:0;">1</div>
<div><strong>Extract Criteria</strong><br><span style="font-size:0.82rem;color:#64748B;">DeepSeek LLM reads the full tender PDF and returns structured JSON — category, mandatory flag, rule, source clause, query hints.</span></div>
</div>

<div style="display:flex;align-items:flex-start;gap:10px;">
<div style="background:#DBEAFE;color:#1E40AF;border-radius:6px;padding:3px 8px;font-size:0.75rem;font-weight:700;flex-shrink:0;">2</div>
<div><strong>Three-Tier OCR</strong><br><span style="font-size:0.82rem;color:#64748B;">
📄 PyMuPDF → 🔍 Tesseract → 👁 Vision LLM.<br>
Each page records its tier and confidence score.
Chunks indexed into ChromaDB with full provenance.</span></div>
</div>
</div>
""", unsafe_allow_html=True)

    with col_b:
        st.markdown("""
<div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:12px;padding:20px;">
<div style="font-weight:700;color:#1E3A5F;margin-bottom:12px;">⚖️ Evaluation & Oversight</div>

<div style="display:flex;align-items:flex-start;gap:10px;margin-bottom:10px;">
<div style="background:#DCFCE7;color:#166534;border-radius:6px;padding:3px 8px;font-size:0.75rem;font-weight:700;flex-shrink:0;">3</div>
<div><strong>Evaluate per Criterion</strong><br><span style="font-size:0.82rem;color:#64748B;">Semantic search retrieves top-k evidence chunks. DeepSeek returns verdict + confidence. Safety rule: borderline "not eligible" is downgraded to "needs review" — never silent disqualification.</span></div>
</div>

<div style="display:flex;align-items:flex-start;gap:10px;">
<div style="background:#FEF3C7;color:#92400E;border-radius:6px;padding:3px 8px;font-size:0.75rem;font-weight:700;flex-shrink:0;">4</div>
<div><strong>Human Review & Audit</strong><br><span style="font-size:0.82rem;color:#64748B;">Flagged verdicts surface with full evidence. Every action — extraction, OCR, evaluation, review — is logged to SQLite with timestamp, model version, and payload.</span></div>
</div>
</div>
""", unsafe_allow_html=True)

    st.divider()

    # Quick start
    st.markdown('<div class="tiq-section-header"><div style="font-size:1.1rem;font-weight:700;color:#0D1B2A;">Quick Start</div></div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("**🚀 Pre-computed Demo**")
            st.caption("Instantly load realistic results for all 3 bidders — no API key needed.")
            if st.button("Load Pre-computed Demo", type="primary", use_container_width=True):
                from core.fallback import load_criteria as lc, load_evaluation
                criteria = lc()
                st.session_state["criteria"] = [c.model_dump() for c in criteria]
                verdicts_dict: dict = {}
                for bidder_id in BIDDER_NAMES:
                    verdicts_dict[bidder_id] = [
                        load_evaluation(bidder_id, c.id).model_dump() for c in criteria
                    ]
                st.session_state["verdicts"] = verdicts_dict
                st.success("Loaded. Navigate to Bidder Evaluation or Interpretability.")
                st.rerun()
    with col2:
        with st.container(border=True):
            st.markdown("**⚡ Live Pipeline**")
            st.caption("Upload a tender PDF, run extraction and evaluation against the DeepSeek API.")
            st.info("Set `DEEPSEEK_API_KEY` in `.env`, then use the Tender Analysis tab.")
