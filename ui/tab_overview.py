import streamlit as st

from core import audit
from core.config import BIDDER_NAMES
from core.fallback import load_criteria
from ui.components import stat_card


def render() -> None:
    # Hero
    st.markdown(
        """<div style="background:linear-gradient(135deg,#0D1B2A 0%,#1E3A5F 60%,#2563EB 100%);
                       border-radius:16px;padding:2.5rem 2.5rem 2rem;margin-bottom:1.5rem;">
          <div style="font-size:0.75rem;font-weight:700;color:#93C5FD;
                      text-transform:uppercase;letter-spacing:0.1em;margin-bottom:8px;">
            CRPF Hackathon · Theme 3</div>
          <h1 style="margin:0;font-size:2.2rem;font-weight:800;color:#FFFFFF;
                     font-family:Inter,sans-serif;letter-spacing:-0.02em;line-height:1.2;">
            ⚖️ TenderIQ</h1>
          <p style="margin:10px 0 0;font-size:1rem;color:#CBD5E1;max-width:600px;
                    line-height:1.6;font-weight:400;">
            Explainable AI for Government Tender Evaluation. Automated eligibility
            assessment with criterion-level evidence, three-tier OCR, and a complete
            compliance audit trail.</p>
        </div>""",
        unsafe_allow_html=True,
    )

    # KPIs
    criteria_count = len(st.session_state.get("criteria", load_criteria()))
    verdicts       = st.session_state.get("verdicts", {})
    checked        = sum(1 for bv in verdicts.values() for _ in bv)
    audit_count    = len(audit.query())

    c1, c2, c3, c4 = st.columns(4)
    with c1: stat_card(criteria_count,    "Criteria Extracted", "#2563EB")
    with c2: stat_card(len(verdicts),     "Bidders Evaluated",  "#059669")
    with c3: stat_card(checked,           "Criteria Checked",   "#7C3AED")
    with c4: stat_card(audit_count,       "Audit Entries",      "#D97706")

    st.divider()

    # Pipeline stages
    st.markdown(
        '<h3 style="margin:0 0 1rem;font-size:1.1rem;font-weight:700;color:#0D1B2A;'
        'font-family:Inter,sans-serif;">How it works</h3>',
        unsafe_allow_html=True,
    )

    stages = [
        ("#2563EB", "#EFF6FF", "#BFDBFE", "1", "Extract Criteria",
         "DeepSeek reads the tender PDF and returns structured JSON for each criterion — "
         "category, mandatory flag, rule (threshold / count / certificate), source clause, "
         "and query hints for downstream retrieval."),
        ("#7C3AED", "#F5F3FF", "#DDD6FE", "2", "Three-Tier OCR",
         "📄 PyMuPDF for typed PDFs · 🔍 Tesseract for scans · 👁 DeepSeek Vision LLM "
         "when Tesseract confidence < 65%. Every page records its tier and confidence score. "
         "Results cached to avoid re-processing."),
        ("#059669", "#F0FDF4", "#BBF7D0", "3", "Evaluate per Criterion",
         "Semantic search retrieves the top-k relevant chunks from ChromaDB. DeepSeek "
         "produces a verdict with combined confidence. Safety rule: borderline "
         "not-eligible is downgraded to needs-review — never silent disqualification."),
        ("#D97706", "#FFFBEB", "#FDE68A", "4", "Human Review & Audit",
         "Flagged verdicts surface in the review queue with full evidence and source "
         "citations. Every action — extraction, OCR, evaluation, officer decision — is "
         "logged to SQLite with timestamp, model version, and payload."),
    ]

    cols = st.columns(4)
    for col, (accent, bg, border, num, title, body) in zip(cols, stages):
        with col:
            st.markdown(
                f"""<div style="background:{bg};border:1px solid {border};border-radius:12px;
                                padding:18px 16px;height:100%;">
                  <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">
                    <div style="background:{accent};color:#fff;border-radius:50%;
                                width:24px;height:24px;display:flex;align-items:center;
                                justify-content:center;font-size:0.75rem;font-weight:700;
                                flex-shrink:0;">{num}</div>
                    <span style="font-weight:700;font-size:0.9rem;color:#0D1B2A;
                                 font-family:Inter,sans-serif;">{title}</span>
                  </div>
                  <p style="margin:0;font-size:0.82rem;color:#374151;line-height:1.6;">{body}</p>
                </div>""",
                unsafe_allow_html=True,
            )

    st.divider()

    # Quick start
    st.markdown(
        '<h3 style="margin:0 0 1rem;font-size:1.1rem;font-weight:700;color:#0D1B2A;'
        'font-family:Inter,sans-serif;">Quick Start</h3>',
        unsafe_allow_html=True,
    )
    col1, col2 = st.columns(2)
    with col1:
        with st.container(border=True):
            st.markdown("**🚀 Pre-computed Demo**")
            st.caption("Instantly load realistic results for all 3 bidders — no API key needed.")
            if st.button("Load Pre-computed Demo", type="primary", use_container_width=True):
                from core.fallback import load_criteria as lc, load_evaluation
                criteria = lc()
                st.session_state["criteria"] = [c.model_dump() for c in criteria]
                vd: dict = {}
                for bid in BIDDER_NAMES:
                    vd[bid] = [load_evaluation(bid, c.id).model_dump() for c in criteria]
                st.session_state["verdicts"] = vd
                st.success("Loaded — navigate to Bidder Evaluation or Interpretability.")
                st.rerun()
    with col2:
        with st.container(border=True):
            st.markdown("**⚡ Live Pipeline**")
            st.caption("Set DEEPSEEK_API_KEY in .env, then use the Tender Analysis tab.")
            st.info("Sidebar shows 🟢 when the API is reachable.")
