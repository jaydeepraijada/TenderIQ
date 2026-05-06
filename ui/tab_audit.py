import io

import pandas as pd
import streamlit as st

from core import audit


def render() -> None:
    st.header("Audit Log")

    col1, col2, col3 = st.columns(3)
    with col1:
        bidder_filter = st.selectbox(
            "Filter by bidder",
            options=["All", "bidder_a", "bidder_b", "bidder_c"],
        )
    with col2:
        action_filter = st.selectbox(
            "Filter by action",
            options=["All", "criteria_extracted", "bidder_processed", "criterion_evaluated",
                     "human_review_action", "precomputed_fallback_used", "vision_ocr_invoked"],
        )
    with col3:
        st.markdown("&nbsp;")  # spacer

    filters: dict = {}
    if bidder_filter != "All":
        filters["bidder_id"] = bidder_filter
    if action_filter != "All":
        filters["action"] = action_filter

    rows = audit.query(filters if filters else None)

    if not rows:
        st.info("No audit entries yet. Run an evaluation to generate entries.")
        return

    df = pd.DataFrame(rows)
    display_cols = ["id", "ts", "action", "actor", "bidder_id", "criterion_id", "payload_json"]
    display_cols = [c for c in display_cols if c in df.columns]
    df_display = df[display_cols].copy()
    df_display["ts"] = df_display["ts"].str[:19].str.replace("T", " ")

    st.markdown(f"**{len(rows)} entries** (newest first)")
    st.dataframe(df_display, use_container_width=True, hide_index=True)

    csv_buf = io.StringIO()
    df_display.to_csv(csv_buf, index=False)
    st.download_button(
        label="Export CSV",
        data=csv_buf.getvalue().encode("utf-8"),
        file_name="tenderiq_audit_log.csv",
        mime="text/csv",
    )
