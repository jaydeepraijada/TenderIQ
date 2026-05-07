import streamlit as st

from core import audit
from core.config import BIDDER_NAMES
from ui.components import stat_card


def render() -> None:
    # Hero — intentional dark gradient, works as a visual anchor in both modes
    st.markdown(
        """<div style="background:linear-gradient(135deg,#0D1B2A 0%,#1E3A5F 60%,#2563EB 100%);
                       border-radius:16px;padding:2.5rem 2.5rem 2rem;margin-bottom:1.5rem;">
          <div style="font-size:0.75rem;font-weight:700;color:#93C5FD;
                      text-transform:uppercase;letter-spacing:0.1em;margin-bottom:8px;">
            CRPF Hackathon · Theme 3</div>
          <h1 style="margin:0;font-size:2.2rem;font-weight:800;color:#FFFFFF;
                     letter-spacing:-0.02em;line-height:1.2;">⚖️ TenderIQ</h1>
          <p style="margin:10px 0 0;font-size:1rem;color:#CBD5E1;max-width:600px;line-height:1.6;">
            Explainable AI for Government Tender Evaluation — automated eligibility
            assessment with criterion-level evidence, three-tier OCR, and a complete
            compliance audit trail.</p>
        </div>""",
        unsafe_allow_html=True,
    )

    # KPIs
    criteria_count = len(st.session_state.get("criteria") or [])
    verdicts       = st.session_state.get("verdicts", {})
    checked        = sum(1 for bv in verdicts.values() for _ in bv)
    audit_count    = len(audit.query())

    c1, c2, c3, c4 = st.columns(4)
    with c1: stat_card(criteria_count,  "Criteria Extracted", "#3B82F6")
    with c2: stat_card(len(verdicts),   "Bidders Evaluated",  "#22C55E")
    with c3: stat_card(checked,         "Criteria Checked",   "#8B5CF6")
    with c4: stat_card(audit_count,     "Audit Entries",      "#F59E0B")

    st.divider()

    # Pipeline stages
    st.markdown(
        '<p style="font-size:1rem;font-weight:700;color:var(--text-color);">'
        'How it works</p>',
        unsafe_allow_html=True,
    )

    stages = [
        ("#3B82F6", "rgba(37,99,235,0.08)",  "1", "Extract Criteria",
         "DeepSeek reads the tender PDF and returns structured JSON for each criterion — "
         "category, mandatory flag, rule, source clause, and query hints."),
        ("#8B5CF6", "rgba(124,58,237,0.08)", "2", "Three-Tier OCR",
         "📄 PyMuPDF for typed PDFs · 🔍 Tesseract for scans · 👁 DeepSeek Vision LLM "
         "when Tesseract confidence < 65%. Every page records its tier and confidence."),
        ("#22C55E", "rgba(34,197,94,0.08)",  "3", "Evaluate per Criterion",
         "Semantic search retrieves the top-k evidence chunks. DeepSeek returns a verdict "
         "with combined confidence. Safety rule: borderline not-eligible is always "
         "downgraded to needs-review."),
        ("#F59E0B", "rgba(245,158,11,0.08)", "4", "Human Review & Audit",
         "Flagged verdicts surface with full evidence and source citations. Every action "
         "is logged to SQLite with timestamp, model version, actor, and payload."),
    ]

    cols = st.columns(4)
    for col, (accent, bg, num, title, body) in zip(cols, stages):
        with col:
            st.markdown(
                f"""<div style="background:{bg};border:1px solid {accent}33;
                                border-radius:12px;padding:18px 16px;height:100%;">
                  <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">
                    <div style="background:{accent};color:#fff;border-radius:50%;
                                width:24px;height:24px;display:flex;align-items:center;
                                justify-content:center;font-size:0.75rem;font-weight:700;
                                flex-shrink:0;">{num}</div>
                    <span style="font-weight:700;font-size:0.9rem;color:var(--text-color);">
                      {title}</span>
                  </div>
                  <p style="margin:0;font-size:0.82rem;color:var(--text-color);
                             opacity:0.75;line-height:1.6;">{body}</p>
                </div>""",
                unsafe_allow_html=True,
            )

    st.divider()

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
