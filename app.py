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
