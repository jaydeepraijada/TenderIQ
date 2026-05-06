import shutil

import streamlit as st

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
    """Clear session, audit DB, ChromaDB, and OCR cache for a clean demo run."""
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
    st.markdown("## ⚖️ TenderIQ")
    st.caption("Explainable AI for Tender Evaluation")
    st.divider()

    status = _probe_llm()
    if status == "green":
        st.markdown("🟢 **DeepSeek:** connected")
    elif status == "amber":
        st.markdown("🟡 **DeepSeek:** pre-computed mode")
        st.warning("⚠ Pre-computed results active.")
    else:
        st.markdown("🔴 **DeepSeek:** not connected")
        st.caption("Using pre-computed fallback data.")

    st.divider()

    if st.button("Reset Session", use_container_width=True):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

    if st.button("🗑 Reset for Demo", use_container_width=True, type="secondary"):
        st.session_state["confirm_demo_reset"] = True

    if st.session_state.get("confirm_demo_reset"):
        st.warning("Clears audit log, vector index, OCR cache, and session. Sure?")
        col1, col2 = st.columns(2)
        if col1.button("Yes, reset", type="primary", use_container_width=True):
            _reset_demo()
            st.rerun()
        if col2.button("Cancel", use_container_width=True):
            st.session_state.pop("confirm_demo_reset", None)
            st.rerun()

# ── Tabs ─────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "Overview",
    "Tender Analysis",
    "Bidder Evaluation",
    "Human Review",
    "Audit Log",
    "Interpretability",
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
