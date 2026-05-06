import shutil
import streamlit as st

from ui.styles import CSS
from ui.tab_overview import render as render_overview
from ui.tab_tender import render as render_tender
from ui.tab_bidders import render as render_bidders
from ui.tab_review import render as render_review
from ui.tab_audit import render as render_audit
from ui.tab_interpretability import render as render_interpretability

st.set_page_config(page_title="TenderIQ", page_icon="⚖️", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)


def _probe_llm() -> str:
    if st.session_state.get("fallback_active"):
        return "amber"
    if "llm_status" in st.session_state:
        return st.session_state["llm_status"]
    from core.llm_client import LLM, LLMUnavailable
    try:
        LLM().chat_json("Respond with valid JSON only.", '{"ping": true}')
        st.session_state["llm_status"] = "green"
        return "green"
    except Exception:
        st.session_state["llm_status"] = "red"
        return "red"


def _reset_demo() -> None:
    from core import audit
    from core.config import CHROMA_DIR, OCR_CACHE_DIR
    audit.clear()
    shutil.rmtree(CHROMA_DIR, ignore_errors=True)
    shutil.rmtree(str(OCR_CACHE_DIR), ignore_errors=True)
    st.cache_resource.clear()
    for k in list(st.session_state.keys()):
        del st.session_state[k]


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    # Branding
    st.markdown(
        """<div style="padding:16px 8px 12px;text-align:center;">
          <div style="font-size:2.6rem;">⚖️</div>
          <div style="font-size:1.4rem;font-weight:800;color:#F8FAFC;
                      letter-spacing:-0.02em;margin-top:4px;
                      font-family:Inter,sans-serif;">TenderIQ</div>
          <div style="font-size:0.7rem;color:#64748B;margin-top:4px;
                      text-transform:uppercase;letter-spacing:0.1em;">
            AI Tender Evaluation</div>
        </div>""",
        unsafe_allow_html=True,
    )
    st.divider()

    # Connection status
    status = _probe_llm()
    dot_color  = {"green": "#22C55E", "amber": "#F59E0B", "red": "#EF4444"}[status]
    dot_shadow = {"green": "#22C55E", "amber": "#F59E0B", "red": "#EF4444"}[status]
    status_label = {"green": "DeepSeek Connected", "amber": "Pre-computed Mode",
                    "red": "No API Key"}[status]
    st.markdown(
        f"""<div style="display:flex;align-items:center;gap:9px;
                        padding:8px 4px;margin-bottom:4px;">
          <div style="width:9px;height:9px;border-radius:50%;flex-shrink:0;
                      background:{dot_color};
                      box-shadow:0 0 0 3px {dot_color}33,0 0 8px {dot_shadow}88;">
          </div>
          <span style="font-size:0.82rem;font-weight:600;color:#E2E8F0;">
            {status_label}</span>
        </div>""",
        unsafe_allow_html=True,
    )
    if status == "amber":
        st.warning("Using pre-computed results.")
    elif status == "red":
        st.caption("Set DEEPSEEK_API_KEY in .env to enable live mode.")

    st.divider()
    if st.button("↺  Reset Session", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

    if st.button("🗑  Reset for Demo", use_container_width=True, type="secondary"):
        st.session_state["confirm_demo_reset"] = True

    if st.session_state.get("confirm_demo_reset"):
        st.warning("Clears audit log, vector index, OCR cache, and session.")
        c1, c2 = st.columns(2)
        if c1.button("Yes, reset", type="primary", use_container_width=True):
            _reset_demo()
            st.rerun()
        if c2.button("Cancel", use_container_width=True):
            st.session_state.pop("confirm_demo_reset", None)
            st.rerun()

    st.divider()
    st.markdown(
        """<div style="font-size:0.7rem;color:#334155;text-align:center;
                       line-height:1.6;padding:0 4px;">
          CRPF Hackathon · Theme 3<br>
          Explainable AI for Government Procurement
        </div>""",
        unsafe_allow_html=True,
    )

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🏠 Overview",
    "📄 Tender Analysis",
    "⚖️ Bidder Evaluation",
    "👤 Human Review",
    "📋 Audit Log",
    "🔍 Interpretability",
])

with tab1: render_overview()
with tab2: render_tender()
with tab3: render_bidders()
with tab4: render_review()
with tab5: render_audit()
with tab6: render_interpretability()
