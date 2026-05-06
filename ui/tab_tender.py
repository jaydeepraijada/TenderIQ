import tempfile
from pathlib import Path

import streamlit as st

from core import criteria_extractor
from core.config import DATA_DIR

_MOCK_TENDER = DATA_DIR / "tender" / "crpf_construction_tender.pdf"

_CATEGORY_COLORS = {
    "financial": "🔵",
    "technical": "🟢",
    "compliance": "🟠",
}


def render() -> None:
    st.header("Tender Analysis")

    uploaded = st.file_uploader("Upload tender PDF (leave blank to use pre-loaded mock)", type=["pdf"])

    if uploaded:
        tender_bytes = uploaded.read()
        tender_name = uploaded.name
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
            tmp.write(tender_bytes)
            tender_path = Path(tmp.name)
    else:
        tender_path = _MOCK_TENDER
        tender_name = _MOCK_TENDER.name

    st.caption(f"Using: **{tender_name}**")

    if st.button("Extract Criteria (Live LLM)", type="primary"):
        with st.spinner("Calling DeepSeek to extract eligibility criteria…"):
            criteria = criteria_extractor.extract_criteria(tender_path)
        st.session_state["criteria"] = [c.model_dump() for c in criteria]
        st.session_state["tender_path"] = str(tender_path)

    criteria_data = st.session_state.get("criteria")
    if criteria_data:
        st.success(f"Extracted **{len(criteria_data)}** criteria")

        if st.session_state.get("fallback_active"):
            st.warning("⚠ Live API unavailable — showing pre-computed criteria.")

        for c in criteria_data:
            mandatory_badge = "🔴 Mandatory" if c["mandatory"] else "🟡 Optional"
            cat_icon = _CATEGORY_COLORS.get(c["category"], "⚪")
            label = f"{cat_icon} **{c['id']}** — {c['title']}  {mandatory_badge}"
            with st.expander(label, expanded=False):
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown(f"**Description:** {c['description']}")
                    rule = c["rule"]
                    rule_parts = [f"Type: `{rule['type']}`", f"Field: `{rule['field']}`",
                                  f"Operator: `{rule['operator']}`"]
                    if rule.get("value") is not None:
                        rule_parts.append(f"Value: `{rule['value']}`")
                    if rule.get("unit"):
                        rule_parts.append(f"Unit: `{rule['unit']}`")
                    st.markdown(" · ".join(rule_parts))
                with col2:
                    st.markdown(f"**Category:** {c['category'].capitalize()}")
                    st.markdown(f"**Source:** Page {c['source_page']}, Clause {c['source_clause']}")
                    if c.get("query_hints"):
                        hints = ", ".join(f"`{h}`" for h in c["query_hints"])
                        st.markdown(f"**Query hints:** {hints}")
