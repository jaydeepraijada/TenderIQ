import io
import json

import pandas as pd
import streamlit as st

from core import audit

_ACTION_LABELS = {
    "criteria_extracted":       "📋 Criteria Extracted",
    "bidder_processed":         "📥 Bidder Document Indexed",
    "criterion_evaluated":      "⚖️ Criterion Evaluated",
    "human_review_action":      "👤 Human Review Action",
    "precomputed_fallback_used":"⚠️ Fallback Used",
    "vision_ocr_invoked":       "👁️ Vision OCR Invoked",
    "smoke_test":               "🧪 Smoke Test",
}

_ACTION_CATEGORIES = {
    "criteria_extracted":        "system",
    "bidder_processed":          "system",
    "criterion_evaluated":       "system",
    "human_review_action":       "human",
    "precomputed_fallback_used": "warning",
    "vision_ocr_invoked":        "system",
}

_VERDICT_ICONS = {
    "eligible":     "✅ Eligible",
    "not_eligible": "❌ Not Eligible",
    "needs_review": "⚠️ Needs Review",
}


def _make_summary(row: dict) -> str:
    action = row.get("action", "")
    bidder = row.get("bidder_id") or ""
    crit = row.get("criterion_id") or ""
    try:
        p = json.loads(row.get("payload_json") or "{}")
    except Exception:
        p = {}

    if action == "criteria_extracted":
        return f"Extracted {p.get('count', '?')} criteria from {p.get('source', 'tender PDF')}"

    if action == "bidder_processed":
        return f"{bidder} — {p.get('doc_name', '?')} indexed ({p.get('chunk_count', '?')} chunks)"

    if action == "criterion_evaluated":
        verdict = _VERDICT_ICONS.get(p.get("verdict", ""), p.get("verdict", "?"))
        conf = p.get("combined_confidence", "?")
        conf_str = f"{float(conf):.0%}" if conf != "?" else "?"
        extracted = p.get("extracted_value", "")
        esc = p.get("escalation_reason", "")
        base = f"{bidder} / {crit} → {verdict} (confidence: {conf_str})"
        if extracted:
            base += f"  |  Extracted: {extracted}"
        if esc:
            base += f"  |  ⚠️ {esc}"
        return base

    if action == "human_review_action":
        taken = p.get("action_taken", "?").capitalize()
        orig = p.get("original_extracted_value", "")
        edited = p.get("edited_value", "")
        base = f"Officer {taken}: {bidder} / {crit}"
        if orig:
            base += f"  |  Original value: {orig}"
        if edited:
            base += f"  →  Edited to: {edited}"
        return base

    if action == "precomputed_fallback_used":
        return f"API unavailable — pre-computed data used  |  {p.get('reason', '')}"

    if action == "vision_ocr_invoked":
        tc = p.get("tesseract_conf", "?")
        tc_str = f"{float(tc):.0%}" if tc != "?" else "?"
        return f"{bidder} page {p.get('page', '?')} — Tesseract confidence {tc_str}, escalated to Vision LLM"

    return action


def _category_color(category: str) -> str:
    return {"system": "🔵", "human": "🟢", "warning": "🟡"}.get(category, "⚪")


def render() -> None:
    st.header("Audit Log")
    st.caption(
        "Every system action and human decision is recorded here. "
        "This log is the compliance trail — it can be exported and submitted as part of the evaluation record."
    )

    # ── Filters ──────────────────────────────────────────────────────────────
    col1, col2, col3 = st.columns(3)
    with col1:
        bidder_filter = st.selectbox(
            "Filter by bidder",
            options=["All", "bidder_a", "bidder_b", "bidder_c"],
        )
    with col2:
        action_filter = st.selectbox(
            "Filter by action",
            options=["All"] + list(_ACTION_LABELS.keys()),
            format_func=lambda x: "All" if x == "All" else _ACTION_LABELS.get(x, x),
        )
    with col3:
        if st.button("🗑 Clear Log", type="secondary", use_container_width=True):
            st.session_state["confirm_clear_audit"] = True

    if st.session_state.get("confirm_clear_audit"):
        st.warning("This will permanently delete all audit entries. Are you sure?")
        c1, c2 = st.columns(2)
        if c1.button("Yes, clear everything", type="primary", use_container_width=True):
            audit.clear()
            st.session_state.pop("confirm_clear_audit", None)
            st.success("Audit log cleared.")
            st.rerun()
        if c2.button("Cancel", use_container_width=True):
            st.session_state.pop("confirm_clear_audit", None)
            st.rerun()

    filters: dict = {}
    if bidder_filter != "All":
        filters["bidder_id"] = bidder_filter
    if action_filter != "All":
        filters["action"] = action_filter

    rows = audit.query(filters if filters else None)

    if not rows:
        st.info("No audit entries yet. Run an evaluation to generate entries.")
        return

    # ── Summary counts ────────────────────────────────────────────────────────
    total = len(rows)
    human_actions = sum(1 for r in rows if r["action"] == "human_review_action")
    fallbacks = sum(1 for r in rows if r["action"] == "precomputed_fallback_used")
    vision_ocr = sum(1 for r in rows if r["action"] == "vision_ocr_invoked")

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total entries", total)
    m2.metric("Human actions", human_actions)
    m3.metric("Fallback events", fallbacks)
    m4.metric("Vision OCR calls", vision_ocr)

    st.divider()

    # ── Human-readable table ──────────────────────────────────────────────────
    df = pd.DataFrame(rows)

    df["Action"] = df["action"].map(lambda x: _ACTION_LABELS.get(x, x))
    df["Category"] = df["action"].map(
        lambda x: _category_color(_ACTION_CATEGORIES.get(x, "system"))
    )
    df["Summary"] = df.apply(_make_summary, axis=1)
    df["Timestamp"] = df["ts"].str[:19].str.replace("T", " ")
    df["Actor"] = df["actor"]
    df["Bidder"] = df["bidder_id"].fillna("—")
    df["Criterion"] = df["criterion_id"].fillna("—")

    display = df[["Category", "Timestamp", "Action", "Bidder", "Criterion", "Summary", "Actor"]].copy()

    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Category":  st.column_config.TextColumn("", width="small"),
            "Timestamp": st.column_config.TextColumn("Timestamp", width="medium"),
            "Action":    st.column_config.TextColumn("Action", width="medium"),
            "Bidder":    st.column_config.TextColumn("Bidder", width="small"),
            "Criterion": st.column_config.TextColumn("Criterion", width="small"),
            "Summary":   st.column_config.TextColumn("Summary", width="large"),
            "Actor":     st.column_config.TextColumn("Actor", width="small"),
        },
    )

    # ── Raw detail expander ───────────────────────────────────────────────────
    with st.expander("Raw payload data (for compliance / full detail)", expanded=False):
        raw_df = df[["Timestamp", "action", "actor", "bidder_id", "criterion_id", "payload_json"]].copy()
        raw_df.columns = ["Timestamp", "action", "actor", "bidder_id", "criterion_id", "payload_json"]
        st.dataframe(raw_df, use_container_width=True, hide_index=True)

    # ── Export ────────────────────────────────────────────────────────────────
    export_df = df[["Timestamp", "Action", "Actor", "Bidder", "Criterion", "Summary"]].copy()
    export_df["raw_payload"] = df["payload_json"]
    csv_buf = io.StringIO()
    export_df.to_csv(csv_buf, index=False)
    st.download_button(
        label="Export CSV",
        data=csv_buf.getvalue().encode("utf-8"),
        file_name="tenderiq_audit_log.csv",
        mime="text/csv",
    )
