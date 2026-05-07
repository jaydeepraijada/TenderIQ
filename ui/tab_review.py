import streamlit as st

from core import audit
from core.config import BIDDER_NAMES
from core.fallback import load_criteria
from core.schemas import Criterion
from ui.components import confidence_bar, verdict_pill


def _crit_map() -> dict[str, Criterion]:
    data = st.session_state.get("criteria")
    return {c["id"]: Criterion(**c) for c in data} if data else {c.id: c for c in load_criteria()}


def render() -> None:
    st.markdown(
        '<h2 style="font-weight:800;font-size:1.5rem;color:var(--text-color);">'
        'Human Review Queue</h2>'
        '<p style="color:var(--text-color);opacity:0.6;font-size:0.875rem;margin-bottom:1rem;">'
        'Verdicts that could not be automatically confirmed require officer sign-off.</p>',
        unsafe_allow_html=True,
    )

    vdata: dict = st.session_state.get("verdicts", {})
    if not vdata:
        st.info("No evaluation results yet. Run the evaluation in the Bidder Evaluation tab first.")
        return

    cm = _crit_map()
    pending = [
        (bid, i, v)
        for bid, verdicts in vdata.items()
        for i, v in enumerate(verdicts)
        if v.get("verdict") == "needs_review" and
        v.get("review_status", "pending") == "pending"
    ]

    if not pending:
        st.success("✅ All flagged verdicts have been actioned. Nothing pending.")
        return

    st.markdown(
        f'<div style="background:rgba(245,158,11,0.1);border:1px solid rgba(245,158,11,0.3);'
        f'border-radius:10px;padding:14px 18px;margin-bottom:1.5rem;'
        f'display:flex;align-items:center;gap:10px;">'
        f'<span style="font-size:1.3rem;">⚠️</span>'
        f'<div>'
        f'<div style="font-weight:700;color:#F59E0B;font-size:0.9rem;">'
        f'{len(pending)} item{"s" if len(pending) != 1 else ""} pending review</div>'
        f'<div style="font-size:0.8rem;color:var(--text-color);opacity:0.6;margin-top:2px;">'
        f'High certainty = model is confident this needs human judgment, '
        f'not that the bidder is ineligible.</div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    for bid, idx, v in pending:
        crit = cm.get(v["criterion_id"])
        crit_title = crit.title if crit else v["criterion_id"]
        company = BIDDER_NAMES.get(bid, bid)

        with st.container(border=True):
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;'
                f'align-items:flex-start;gap:12px;margin-bottom:10px;">'
                f'<div>'
                f'<div style="font-weight:700;font-size:0.95rem;color:var(--text-color);">'
                f'{company}</div>'
                f'<div style="font-size:0.82rem;color:var(--text-color);opacity:0.55;'
                f'margin-top:2px;">{v["criterion_id"]}: {crit_title}</div>'
                f'</div>'
                f'{verdict_pill(v["verdict"])}'
                f'</div>',
                unsafe_allow_html=True,
            )

            col_l, col_r = st.columns([3, 1])
            with col_l:
                if v.get("extracted_value"):
                    st.markdown(
                        f'<div style="font-size:0.84rem;margin-bottom:8px;'
                        f'color:var(--text-color);">'
                        f'<strong>Extracted value:</strong> '
                        f'<code style="background:rgba(128,128,128,0.12);padding:2px 7px;'
                        f'border-radius:4px;">{v["extracted_value"]}</code></div>',
                        unsafe_allow_html=True,
                    )
                if v.get("reason"):
                    st.markdown(
                        f'<div style="background:rgba(245,158,11,0.08);'
                        f'border-left:3px solid #F59E0B;padding:9px 13px;'
                        f'border-radius:0 7px 7px 0;font-size:0.84rem;'
                        f'color:var(--text-color);margin-bottom:8px;">'
                        f'<strong>Reason:</strong> {v["reason"]}</div>',
                        unsafe_allow_html=True,
                    )
                if v.get("source") and v["source"].get("snippet"):
                    st.markdown(
                        f'<div style="background:rgba(128,128,128,0.07);'
                        f'border:1px solid rgba(128,128,128,0.15);padding:9px 13px;'
                        f'border-radius:7px;font-size:0.82rem;color:var(--text-color);'
                        f'font-style:italic;">&ldquo;{v["source"]["snippet"]}&rdquo;</div>',
                        unsafe_allow_html=True,
                    )
            with col_r:
                confidence_bar(v.get("combined_confidence", 0.0), "Certainty")

            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            kp = f"rv_{bid}_{v['criterion_id']}"
            bc1, bc2, bc3 = st.columns(3)

            common = dict(bidder_id=bid, criterion_id=v["criterion_id"],
                          original_verdict=v["verdict"],
                          original_extracted_value=v.get("extracted_value", ""),
                          combined_confidence=v.get("combined_confidence", 0.0))

            with bc1:
                if st.button("✅ Approve", key=f"{kp}_approve",
                             use_container_width=True, type="primary"):
                    st.session_state["verdicts"][bid][idx]["review_status"] = "approved"
                    audit.log("human_review_action", actor="officer",
                              action_taken="approved", **common)
                    st.rerun()
            with bc2:
                edited = st.text_input("Corrected value", key=f"{kp}_edit_val",
                                       placeholder="Optional override…",
                                       label_visibility="collapsed")
                if st.button("✏️ Edit & Approve", key=f"{kp}_edit", use_container_width=True):
                    st.session_state["verdicts"][bid][idx]["review_status"] = "edited"
                    if edited:
                        st.session_state["verdicts"][bid][idx]["extracted_value"] = edited
                    audit.log("human_review_action", actor="officer",
                              action_taken="edited", edited_value=edited, **common)
                    st.rerun()
            with bc3:
                if st.button("❌ Reject", key=f"{kp}_reject", use_container_width=True):
                    st.session_state["verdicts"][bid][idx]["review_status"] = "rejected"
                    audit.log("human_review_action", actor="officer",
                              action_taken="rejected", **common)
                    st.rerun()
