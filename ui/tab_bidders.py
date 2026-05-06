from pathlib import Path

import streamlit as st

from core import bidder_processor, evaluator
from core.config import DATA_DIR
from core.fallback import load_criteria
from core.schemas import Criterion
from ui.components import category_badge, confidence_bar, ocr_tier_badge, verdict_pill

_BIDDER_LABELS = {
    "bidder_a": "Bidder A — Apex Constructions (Clearly Eligible)",
    "bidder_b": "Bidder B — BuildRight Enterprises (Ineligible: Low Turnover)",
    "bidder_c": "Bidder C — Shree Constructions (Scanned Cert: Needs Review)",
}


def _get_criteria() -> list[Criterion]:
    data = st.session_state.get("criteria")
    if data:
        return [Criterion(**c) for c in data]
    return load_criteria()


def _overall_verdict(verdicts: list[dict]) -> str:
    mandatory = [v for v in verdicts if True]  # all criteria checked
    if any(v["verdict"] == "not_eligible" for v in mandatory):
        return "not_eligible"
    if any(v["verdict"] == "needs_review" for v in mandatory):
        return "needs_review"
    return "eligible"


def render() -> None:
    st.header("Bidder Evaluation")

    selected = st.multiselect(
        "Select bidders to evaluate",
        options=["bidder_a", "bidder_b", "bidder_c"],
        default=["bidder_a", "bidder_b", "bidder_c"],
        format_func=lambda x: _BIDDER_LABELS.get(x, x),
    )

    if st.button("Run Evaluation", type="primary"):
        criteria = _get_criteria()
        verdicts_dict: dict = {}
        progress = st.progress(0, text="Starting evaluation…")
        total = len(selected) * len(criteria)
        done = 0
        for bidder_id in selected:
            files = sorted(
                f for f in (DATA_DIR / "bidders" / bidder_id).iterdir()
                if f.suffix.lower() in {".pdf", ".png", ".jpg"}
            )
            with st.spinner(f"Processing {bidder_id} documents…"):
                bidder_processor.process_bidder(bidder_id, files)
            verdicts_list = []
            for c in criteria:
                v = evaluator.evaluate(bidder_id, c)
                verdicts_list.append(v.model_dump())
                done += 1
                progress.progress(done / total, text=f"Evaluated {c.id} for {bidder_id}")
            verdicts_dict[bidder_id] = verdicts_list
        st.session_state["verdicts"] = verdicts_dict
        progress.empty()
        st.success("Evaluation complete.")
        st.rerun()

    verdicts_data = st.session_state.get("verdicts", {})
    criteria = _get_criteria()
    crit_map = {c.id: c for c in criteria}

    if st.session_state.get("fallback_active"):
        st.warning("⚠ Live API unavailable — showing pre-computed results.")

    for bidder_id in (selected or list(verdicts_data.keys())):
        if bidder_id not in verdicts_data:
            continue
        verdicts = verdicts_data[bidder_id]
        overall = _overall_verdict(verdicts)
        overall_pill = verdict_pill(overall)

        with st.expander(
            f"**{_BIDDER_LABELS.get(bidder_id, bidder_id)}**  —  Overall: {overall_pill}",
            expanded=True,
        ):
            for v in verdicts:
                crit = crit_map.get(v["criterion_id"])
                crit_title = crit.title if crit else v["criterion_id"]
                mandatory_tag = "🔴" if (crit and crit.mandatory) else "🟡"
                cat = category_badge(crit.category if crit else "compliance")

                cols = st.columns([3, 2, 2, 2, 1])
                cols[0].markdown(f"{mandatory_tag} **{v['criterion_id']}** {crit_title}")
                cols[1].markdown(verdict_pill(v["verdict"]))
                cols[2].markdown(f"{v.get('extracted_value') or '—'}")
                if v.get("source"):
                    src = v["source"]
                    tier = ocr_tier_badge(src["source_type"])
                    cols[3].markdown(f"`{src['doc_name']}` p{src['page']}  {tier}")
                else:
                    cols[3].markdown("—")
                cols[4].markdown(cat)

                conf = v.get("combined_confidence", 0.0)
                confidence_bar(conf)

                if v.get("reason") or v.get("source"):
                    with st.expander("Details", expanded=False):
                        if v.get("reason"):
                            st.markdown(f"**Reason:** {v['reason']}")
                        if v.get("source") and v["source"].get("snippet"):
                            st.markdown(f"**Source snippet:** _{v['source']['snippet']}_")
                st.divider()
