import streamlit as st

from core import audit
from core.config import BIDDER_NAMES
from core.fallback import load_criteria
from core.schemas import Criterion
from ui.components import confidence_bar, verdict_pill


def _get_criteria_map() -> dict[str, Criterion]:
    data = st.session_state.get("criteria")
    if data:
        return {c["id"]: Criterion(**c) for c in data}
    return {c.id: c for c in load_criteria()}


def render() -> None:
    st.header("Human Review Queue")

    verdicts_data: dict = st.session_state.get("verdicts", {})
    if not verdicts_data:
        st.info("No evaluation results yet. Run the evaluation in the Bidder Evaluation tab first.")
        return

    crit_map = _get_criteria_map()
    pending_items = []
    for bidder_id, verdicts in verdicts_data.items():
        for i, v in enumerate(verdicts):
            if v.get("verdict") == "needs_review" and v.get("review_status", "pending") == "pending":
                pending_items.append((bidder_id, i, v))

    if not pending_items:
        st.success("No items pending review. All flagged verdicts have been actioned.")
        return

    st.markdown(f"**{len(pending_items)} item(s) pending review**")
    st.caption(
        "These verdicts require human confirmation before being finalised. "
        "The certainty bar shows how confident the model is in its decision to flag the item — "
        "not how likely the bidder meets the criterion."
    )
    st.divider()

    for bidder_id, idx, v in pending_items:
        crit = crit_map.get(v["criterion_id"])
        crit_title = crit.title if crit else v["criterion_id"]

        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            friendly = BIDDER_NAMES.get(bidder_id, bidder_id)
            with col1:
                st.markdown(
                    f'<div style="font-weight:700;font-size:1rem;color:#0D1B2A;">'
                    f'{friendly}</div>'
                    f'<div style="font-size:0.85rem;color:#64748B;margin-top:2px;">'
                    f'{v["criterion_id"]}: {crit_title}</div>',
                    unsafe_allow_html=True,
                )
                st.markdown(verdict_pill(v["verdict"]), unsafe_allow_html=True)
                if v.get("extracted_value"):
                    st.markdown(
                        f'<div style="margin-top:6px;font-size:0.85rem;">'
                        f'<strong>Extracted value:</strong> '
                        f'<code>{v["extracted_value"]}</code></div>',
                        unsafe_allow_html=True,
                    )
                if v.get("reason"):
                    st.markdown(
                        f'<div style="background:#FFFBEB;border-left:3px solid #F59E0B;'
                        f'padding:8px 12px;border-radius:0 6px 6px 0;margin-top:8px;'
                        f'font-size:0.85rem;color:#374151;">'
                        f'<strong>Reason:</strong> {v["reason"]}</div>',
                        unsafe_allow_html=True,
                    )
                if v.get("source") and v["source"].get("snippet"):
                    st.markdown(
                        f'<div style="background:#F8FAFC;border:1px solid #E2E8F0;'
                        f'padding:8px 12px;border-radius:6px;margin-top:6px;'
                        f'font-size:0.82rem;color:#374151;font-style:italic;">'
                        f'"{v["source"]["snippet"]}"</div>',
                        unsafe_allow_html=True,
                    )
            with col2:
                conf = v.get("combined_confidence", 0.0)
                confidence_bar(conf, "Certainty in assessment")

            btn_col1, btn_col2, btn_col3 = st.columns(3)
            key_prefix = f"review_{bidder_id}_{v['criterion_id']}"

            with btn_col1:
                if st.button("✅ Approve", key=f"{key_prefix}_approve", use_container_width=True):
                    st.session_state["verdicts"][bidder_id][idx]["review_status"] = "approved"
                    audit.log(
                        "human_review_action",
                        actor="officer",
                        bidder_id=bidder_id,
                        criterion_id=v["criterion_id"],
                        action_taken="approved",
                        original_verdict=v["verdict"],
                        original_extracted_value=v.get("extracted_value", ""),
                        combined_confidence=v.get("combined_confidence", 0.0),
                    )
                    st.rerun()

            with btn_col2:
                edit_val = st.text_input("Edited value", key=f"{key_prefix}_edit_val",
                                          placeholder="Enter corrected value…")
                if st.button("✏ Edit & Approve", key=f"{key_prefix}_edit", use_container_width=True):
                    st.session_state["verdicts"][bidder_id][idx]["review_status"] = "edited"
                    if edit_val:
                        st.session_state["verdicts"][bidder_id][idx]["extracted_value"] = edit_val
                    audit.log(
                        "human_review_action",
                        actor="officer",
                        bidder_id=bidder_id,
                        criterion_id=v["criterion_id"],
                        action_taken="edited",
                        original_verdict=v["verdict"],
                        original_extracted_value=v.get("extracted_value", ""),
                        edited_value=edit_val,
                        combined_confidence=v.get("combined_confidence", 0.0),
                    )
                    st.rerun()

            with btn_col3:
                if st.button("❌ Reject", key=f"{key_prefix}_reject", use_container_width=True):
                    st.session_state["verdicts"][bidder_id][idx]["review_status"] = "rejected"
                    audit.log(
                        "human_review_action",
                        actor="officer",
                        bidder_id=bidder_id,
                        criterion_id=v["criterion_id"],
                        action_taken="rejected",
                        original_verdict=v["verdict"],
                        original_extracted_value=v.get("extracted_value", ""),
                        combined_confidence=v.get("combined_confidence", 0.0),
                    )
                    st.rerun()
