import streamlit as st

from core import audit
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
    st.divider()

    for bidder_id, idx, v in pending_items:
        crit = crit_map.get(v["criterion_id"])
        crit_title = crit.title if crit else v["criterion_id"]

        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{bidder_id}** — {v['criterion_id']}: {crit_title}")
                st.markdown(f"Verdict: {verdict_pill(v['verdict'])}")
                if v.get("extracted_value"):
                    st.markdown(f"Extracted value: `{v['extracted_value']}`")
                if v.get("reason"):
                    st.markdown(f"Reason: _{v['reason']}_")
                if v.get("source") and v["source"].get("snippet"):
                    st.markdown(f"Source snippet: _{v['source']['snippet']}_")
            with col2:
                conf = v.get("combined_confidence", 0.0)
                confidence_bar(conf, "Confidence")

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
                        edited_value=edit_val,
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
                    )
                    st.rerun()
