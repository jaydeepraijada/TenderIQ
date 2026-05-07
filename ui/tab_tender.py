import tempfile
from pathlib import Path

import streamlit as st

from core import criteria_extractor
from core.config import DATA_DIR

_MOCK_TENDER = DATA_DIR / "tender" / "crpf_construction_tender.pdf"
_REAL_DIR    = DATA_DIR / "tender" / "real_tenders"

_REAL_LABELS = {
    "crpf_bhopal_water_tanks_2025.pdf":
        "CRPF GC Bhopal — Water Storage Tanks (NIT-71, Aug 2025, Est. ₹62.9L)",
    "crpf_jammu_office_repair_2026.pdf":
        "CRPF J&K Zone HQ Jammu — Office Building Repair (Jan 2026, Est. ₹24.3L)",
}

_CAT_ICONS = {"financial": "🔵", "technical": "🟢", "compliance": "🟠"}


def render() -> None:
    st.markdown(
        '<h2 style="font-family:Inter,sans-serif;font-weight:800;font-size:1.5rem;'
        'color:#0D1B2A;margin-bottom:4px;">Tender Analysis</h2>'
        '<p style="color:#64748B;font-size:0.875rem;margin-bottom:1rem;">'
        'Extract eligibility criteria from any tender PDF using DeepSeek.</p>',
        unsafe_allow_html=True,
    )

    # ── Tender source selector ────────────────────────────────────────────────
    real_files = sorted(_REAL_DIR.glob("*.pdf")) if _REAL_DIR.exists() else []

    preset_options = {"Mock tender (CRPF Construction, 5 criteria)": _MOCK_TENDER}
    for f in real_files:
        preset_options[_REAL_LABELS.get(f.name, f.name)] = f

    tab_preset, tab_upload = st.tabs(["📂 Pre-loaded Tenders", "⬆️ Upload Your Own"])

    with tab_preset:
        chosen_label = st.selectbox("Select tender", options=list(preset_options.keys()))
        tender_path  = preset_options[chosen_label]
        tender_name  = tender_path.name

        if real_files and chosen_label != "Mock tender (CRPF Construction, 5 criteria)":
            st.markdown(
                '<div style="background:#F0FDF4;border:1px solid #BBF7D0;border-radius:8px;'
                'padding:10px 14px;font-size:0.83rem;color:#166534;margin-top:6px;">'
                '✅ <strong>Real government tender</strong> — downloaded from crpf.gov.in</div>',
                unsafe_allow_html=True,
            )

    with tab_upload:
        uploaded = st.file_uploader("Upload a tender PDF", type=["pdf"],
                                    label_visibility="collapsed")
        if uploaded:
            tender_bytes = uploaded.read()
            tender_name  = uploaded.name
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                tmp.write(tender_bytes)
                tender_path = Path(tmp.name)

    st.caption(f"Active: **{tender_name}**")

    # ── Extract button ────────────────────────────────────────────────────────
    if st.button("Extract Criteria (Live LLM)", type="primary"):
        with st.spinner("Calling DeepSeek to extract eligibility criteria…"):
            criteria = criteria_extractor.extract_criteria(tender_path)
        st.session_state["criteria"]     = [c.model_dump() for c in criteria]
        st.session_state["tender_path"]  = str(tender_path)
        st.success(f"Extracted {len(criteria)} criteria.")

    # ── Display results ───────────────────────────────────────────────────────
    criteria_data = st.session_state.get("criteria")
    if not criteria_data:
        return

    if st.session_state.get("fallback_active"):
        st.warning("⚠ Live API unavailable — showing pre-computed criteria.")

    st.caption(f"{len(criteria_data)} criteria — click × to remove any you don't want evaluated.")

    for c in criteria_data:
        icon     = _CAT_ICONS.get(c["category"], "⚪")
        mand_lbl = "🔴 Mandatory" if c["mandatory"] else "🟡 Optional"
        rule     = c["rule"]
        rule_str = f'`{rule["type"]}` · `{rule["field"]} {rule["operator"]}'
        if rule.get("value") is not None:
            rule_str += f' {rule["value"]}'
        if rule.get("unit"):
            rule_str += f' {rule["unit"]}'
        rule_str += "`"

        btn_col, exp_col = st.columns([0.04, 0.96])
        with btn_col:
            if st.button("×", key=f"rm_{c['id']}", help=f"Remove {c['id']}"):
                st.session_state["criteria"] = [
                    x for x in criteria_data if x["id"] != c["id"]
                ]
                st.rerun()
        with exp_col:
            with st.expander(
                f'{icon} **{c["id"]}** — {c["title"]}  ·  {mand_lbl}',
                expanded=False,
            ):
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown(f"**Description:** {c['description']}")
                    st.markdown(f"**Rule:** {rule_str}")
                    if c.get("query_hints"):
                        hints = "  ·  ".join(f"`{h}`" for h in c["query_hints"])
                        st.markdown(f"**Query hints:** {hints}")
                with col2:
                    st.markdown(f"**Category:** {c['category'].capitalize()}")
                    st.markdown(f"**Source:** Page {c['source_page']}, Clause `{c['source_clause']}`")
