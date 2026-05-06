import shutil

import streamlit as st

from ui.styles import CSS
from ui.tab_overview import render as render_overview
from ui.tab_tender import render as render_tender
from ui.tab_bidders import render as render_bidders
from ui.tab_review import render as render_review
from ui.tab_audit import render as render_audit
from ui.tab_interpretability import render as render_interpretability

st.set_page_config(
    page_title="TenderIQ",
    page_icon="⚖️",
    layout="wide",
)

st.markdown(CSS, unsafe_allow_html=True)


def _probe_llm() -> str:
    """Probe once per session; returns 'green', 'amber', or 'red'."""
    if st.session_state.get("fallback_active"):
        return "amber"
    if "llm_status" in st.session_state:
        return st.session_state["llm_status"]
    from core.llm_client import LLM, LLMUnavailable
    try:
        LLM().chat_json("Respond with valid JSON only.", '{"ping": true}')
        st.session_state["llm_status"] = "green"
        return "green"
    except LLMUnavailable:
        st.session_state["llm_status"] = "red"
        return "red"
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
    for key in list(st.session_state.keys()):
        del st.session_state[key]


# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """<div style="padding:12px 4px 8px;text-align:center;">
        <div style="font-size:2.4rem;line-height:1;">⚖️</div>
        <div style="font-size:1.3rem;font-weight:800;color:#F1F5F9;
                    letter-spacing:-0.01em;margin-top:6px;">TenderIQ</div>
        <div style="font-size:0.72rem;color:#94A3B8;margin-top:3px;
                    text-transform:uppercase;letter-spacing:0.08em;">
            AI Tender Evaluation</div>
        </div>""",
        unsafe_allow_html=True,
    )
    st.divider()

    status = _probe_llm()
    if status == "green":
        st.markdown(
            '<div style="display:flex;align-items:center;gap:8px;padding:6px 0;">'
            '<div style="width:10px;height:10px;border-radius:50%;background:#22C55E;'
            'box-shadow:0 0 6px #22C55E;flex-shrink:0;"></div>'
            '<span style="font-size:0.85rem;font-weight:600;">DeepSeek Connected</span></div>',
            unsafe_allow_html=True,
        )
    elif status == "amber":
        st.markdown(
            '<div style="display:flex;align-items:center;gap:8px;padding:6px 0;">'
            '<div style="width:10px;height:10px;border-radius:50%;background:#F59E0B;'
            'box-shadow:0 0 6px #F59E0B;flex-shrink:0;"></div>'
            '<span style="font-size:0.85rem;font-weight:600;">Pre-computed Mode</span></div>',
            unsafe_allow_html=True,
        )
        st.warning("⚠ Showing pre-computed results.")
    else:
        st.markdown(
            '<div style="display:flex;align-items:center;gap:8px;padding:6px 0;">'
            '<div style="width:10px;height:10px;border-radius:50%;background:#EF4444;'
            'box-shadow:0 0 6px #EF4444;flex-shrink:0;"></div>'
            '<span style="font-size:0.85rem;font-weight:600;">No API Key</span></div>',
            unsafe_allow_html=True,
        )
        st.caption("Using pre-computed fallback data.")

    st.divider()

    if st.button("↺  Reset Session", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
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
    st.caption("CRPF Hackathon · Theme 3\nExplainable AI for Government Procurement")


# ── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🏠  Overview",
    "📄  Tender Analysis",
    "⚖️  Bidder Evaluation",
    "👤  Human Review",
    "📋  Audit Log",
    "🔍  Interpretability",
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
with tab6:
    render_interpretability()
