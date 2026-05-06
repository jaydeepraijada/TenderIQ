import streamlit as st

from core import bidder_processor, evaluator
from core.config import BIDDER_NAMES, DATA_DIR
from core.fallback import load_criteria
from core.schemas import Criterion
from ui.components import category_badge, confidence_bar, ocr_tier_badge, verdict_pill

_BIDDER_LABELS = {
    "bidder_a": "Bidder A — Apex Constructions Pvt. Ltd. (Clearly Eligible)",
    "bidder_b": "Bidder B — BuildRight Enterprises (Ineligible: Low Turnover)",
    "bidder_c": "Bidder C — Shree Constructions & Services (Scanned Cert: Needs Review)",
}


def _get_criteria() -> list[Criterion]:
    data = st.session_state.get("criteria")
    if data:
        return [Criterion(**c) for c in data]
    return load_criteria()


def _overall_verdict(verdicts: list[dict], crit_map: dict) -> str:
    """Only mandatory criteria determine overall eligibility."""
    mandatory = [v for v in verdicts if crit_map.get(v["criterion_id"], None) and
                 crit_map[v["criterion_id"]].mandatory]
    if not mandatory:
        mandatory = verdicts  # fallback if crit_map is missing
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
            with st.spinner(f"Processing {BIDDER_NAMES.get(bidder_id, bidder_id)} documents…"):
                bidder_processor.process_bidder(bidder_id, files)
            verdicts_list = []
            for c in criteria:
                v = evaluator.evaluate(bidder_id, c)
                verdicts_list.append(v.model_dump())
                done += 1
                progress.progress(done / total,
                                  text=f"Evaluated {c.id} for {BIDDER_NAMES.get(bidder_id, bidder_id)}")
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
        overall = _overall_verdict(verdicts, crit_map)
        overall_pill = verdict_pill(overall)
        friendly = BIDDER_NAMES.get(bidder_id, bidder_id)
        mandatory_count = sum(1 for v in verdicts
                              if crit_map.get(v["criterion_id"]) and
                              crit_map[v["criterion_id"]].mandatory)
        passed = sum(1 for v in verdicts
                     if v["verdict"] == "eligible" and
                     crit_map.get(v["criterion_id"]) and
                     crit_map[v["criterion_id"]].mandatory)

        with st.container(border=True):
            st.markdown(
                f"#### {friendly}  —  Overall: {overall_pill}"
                f"  <span style='font-size:0.85em; color:grey;'>"
                f"({passed}/{mandatory_count} mandatory criteria met)</span>",
                unsafe_allow_html=True,
            )

            # Column headers
            hcols = st.columns([3, 2, 2, 2, 1])
            hcols[0].caption("Criterion")
            hcols[1].caption("Verdict")
            hcols[2].caption("Extracted Value")
            hcols[3].caption("Source / OCR Tier")
            hcols[4].caption("Category")
            st.divider()

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

                if v.get("reason") or (v.get("source") and v["source"].get("snippet")):
                    with st.expander("Details", expanded=False):
                        if v.get("reason"):
                            st.markdown(f"**Reason:** {v['reason']}")
                        if v.get("source") and v["source"].get("snippet"):
                            st.markdown(f"**Source snippet:** _{v['source']['snippet']}_")
                st.divider()
