import streamlit as st

from core import bidder_processor, evaluator
from core.config import BIDDER_NAMES, DATA_DIR
from core.fallback import load_criteria
from core.schemas import Criterion
from ui.components import (
    category_badge, confidence_bar, mandatory_badge,
    ocr_tier_badge, section_header, verdict_pill,
)

_BIDDER_LABELS = {
    "bidder_a": "Apex Constructions Pvt. Ltd.",
    "bidder_b": "BuildRight Enterprises",
    "bidder_c": "Shree Constructions & Services",
}
_BIDDER_SUBLABELS = {
    "bidder_a": "Clearly Eligible",
    "bidder_b": "Ineligible — Turnover Below Threshold",
    "bidder_c": "Needs Review — Scanned Certificate",
}


def _get_criteria() -> list[Criterion]:
    data = st.session_state.get("criteria")
    if data:
        return [Criterion(**c) for c in data]
    return load_criteria()


def _overall_verdict(verdicts: list[dict], crit_map: dict) -> str:
    mandatory = [v for v in verdicts
                 if crit_map.get(v["criterion_id"]) and
                 crit_map[v["criterion_id"]].mandatory]
    if not mandatory:
        mandatory = verdicts
    if any(v["verdict"] == "not_eligible" for v in mandatory):
        return "not_eligible"
    if any(v["verdict"] == "needs_review" for v in mandatory):
        return "needs_review"
    return "eligible"


def render() -> None:
    st.header("Bidder Evaluation")
    st.caption("Run the full evaluation pipeline or load pre-computed results from the Overview tab.")

    selected = st.multiselect(
        "Select bidders to evaluate",
        options=list(BIDDER_NAMES.keys()),
        default=list(BIDDER_NAMES.keys()),
        format_func=lambda x: f"{_BIDDER_LABELS.get(x, x)} — {_BIDDER_SUBLABELS.get(x, '')}",
    )

    if st.button("▶  Run Evaluation", type="primary"):
        criteria = _get_criteria()
        verdicts_dict: dict = {}
        progress = st.progress(0, text="Starting…")
        total = len(selected) * len(criteria)
        done = 0
        for bidder_id in selected:
            files = sorted(
                f for f in (DATA_DIR / "bidders" / bidder_id).iterdir()
                if f.suffix.lower() in {".pdf", ".png", ".jpg"}
            )
            with st.spinner(f"Processing {_BIDDER_LABELS.get(bidder_id, bidder_id)}…"):
                bidder_processor.process_bidder(bidder_id, files)
            verdicts_list = []
            for c in criteria:
                v = evaluator.evaluate(bidder_id, c)
                verdicts_list.append(v.model_dump())
                done += 1
                progress.progress(done / total,
                                  text=f"Evaluated {c.id} · {_BIDDER_LABELS.get(bidder_id, bidder_id)}")
            verdicts_dict[bidder_id] = verdicts_list
        st.session_state["verdicts"] = verdicts_dict
        progress.empty()
        st.success("Evaluation complete. Results saved.")
        st.rerun()

    verdicts_data = st.session_state.get("verdicts", {})
    criteria = _get_criteria()
    crit_map = {c.id: c for c in criteria}

    if not verdicts_data:
        st.info("No results yet. Click **Run Evaluation** above, or load the demo from the Overview tab.")
        return

    if st.session_state.get("fallback_active"):
        st.warning("⚠ Live API unavailable — showing pre-computed results.")

    for bidder_id in (selected or list(verdicts_data.keys())):
        if bidder_id not in verdicts_data:
            continue
        verdicts = verdicts_data[bidder_id]
        overall = _overall_verdict(verdicts, crit_map)
        op = verdict_pill(overall)
        friendly = _BIDDER_LABELS.get(bidder_id, bidder_id)
        sublabel = _BIDDER_SUBLABELS.get(bidder_id, "")
        passed = sum(1 for v in verdicts
                     if v["verdict"] == "eligible" and
                     crit_map.get(v["criterion_id"]) and
                     crit_map[v["criterion_id"]].mandatory)
        total_mand = sum(1 for v in verdicts
                         if crit_map.get(v["criterion_id"]) and
                         crit_map[v["criterion_id"]].mandatory)

        with st.container(border=True):
            # Bidder header
            st.markdown(
                f"""<div style="display:flex;justify-content:space-between;
                            align-items:center;flex-wrap:wrap;gap:8px;
                            padding:4px 0 12px;">
                <div>
                    <div style="font-size:1.05rem;font-weight:700;color:#0D1B2A;">{friendly}</div>
                    <div style="font-size:0.8rem;color:#64748B;margin-top:2px;">{sublabel}</div>
                </div>
                <div style="display:flex;align-items:center;gap:12px;">
                    {op}
                    <span style="font-size:0.78rem;color:#94A3B8;background:#F1F5F9;
                                 padding:3px 10px;border-radius:20px;">
                        {passed}/{total_mand} mandatory passed
                    </span>
                </div>
                </div>""",
                unsafe_allow_html=True,
            )

            # Column headers
            hcols = st.columns([3, 2, 2, 3, 2])
            for col, lbl in zip(hcols, ["Criterion", "Verdict", "Extracted Value",
                                         "Source & OCR Tier", "Category"]):
                col.markdown(
                    f'<div style="font-size:0.72rem;font-weight:700;color:#94A3B8;'
                    f'text-transform:uppercase;letter-spacing:0.06em;padding-bottom:4px;">'
                    f'{lbl}</div>',
                    unsafe_allow_html=True,
                )
            st.markdown('<hr style="margin:0 0 8px;border-color:#F1F5F9;">', unsafe_allow_html=True)

            for v in verdicts:
                crit = crit_map.get(v["criterion_id"])
                crit_title = crit.title if crit else v["criterion_id"]
                mb = mandatory_badge(crit.mandatory if crit else True)
                cat = category_badge(crit.category if crit else "compliance")

                cols = st.columns([3, 2, 2, 3, 2])
                cols[0].markdown(
                    f'{mb} <span style="font-weight:600;font-size:0.88rem;">'
                    f'{v["criterion_id"]}</span>'
                    f'<div style="font-size:0.8rem;color:#374151;margin-top:2px;">{crit_title}</div>',
                    unsafe_allow_html=True,
                )
                cols[1].markdown(verdict_pill(v["verdict"]), unsafe_allow_html=True)
                extracted = v.get("extracted_value") or ""
                extracted_html = (
                    f'<span style="font-size:0.85rem;color:#374151;">{extracted}</span>'
                    if extracted else
                    '<span style="color:#9CA3AF;">—</span>'
                )
                cols[2].markdown(extracted_html, unsafe_allow_html=True)
                if v.get("source"):
                    src = v["source"]
                    tier = ocr_tier_badge(src["source_type"])
                    cols[3].markdown(
                        f'<span style="font-size:0.82rem;font-family:monospace;'
                        f'background:#F8FAFC;padding:2px 6px;border-radius:4px;'
                        f'border:1px solid #E2E8F0;">{src["doc_name"]}</span>'
                        f' p{src["page"]}<br>{tier}',
                        unsafe_allow_html=True,
                    )
                else:
                    cols[3].markdown('<span style="color:#9CA3AF;">—</span>', unsafe_allow_html=True)
                cols[4].markdown(cat, unsafe_allow_html=True)

                confidence_bar(v.get("combined_confidence", 0.0))

                if v.get("reason") or (v.get("source") and v["source"].get("snippet")):
                    with st.expander("View details", expanded=False):
                        if v.get("reason"):
                            st.markdown(
                                f'<div style="background:#F8FAFC;border-left:3px solid #3B82F6;'
                                f'padding:10px 14px;border-radius:0 6px 6px 0;'
                                f'font-size:0.88rem;color:#374151;">'
                                f'<strong>Reason:</strong> {v["reason"]}</div>',
                                unsafe_allow_html=True,
                            )
                        if v.get("source") and v["source"].get("snippet"):
                            st.markdown(
                                f'<div style="background:#FFFBEB;border-left:3px solid #F59E0B;'
                                f'padding:10px 14px;border-radius:0 6px 6px 0;margin-top:8px;'
                                f'font-size:0.85rem;color:#374151;font-style:italic;">'
                                f'"{v["source"]["snippet"]}"</div>',
                                unsafe_allow_html=True,
                            )
                st.markdown('<hr style="margin:6px 0;border-color:#F1F5F9;">', unsafe_allow_html=True)
