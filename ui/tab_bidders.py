import streamlit as st

from core import bidder_processor, evaluator
from core.config import BIDDER_NAMES, DATA_DIR
from core.fallback import load_criteria
from core.schemas import Criterion
from ui.components import category_badge, confidence_bar, mandatory_badge, ocr_tier_badge, verdict_pill

_BIDDER_META = {
    "bidder_a": ("Apex Constructions Pvt. Ltd.",   "Clearly Eligible",                "#22C55E"),
    "bidder_b": ("BuildRight Enterprises",          "Ineligible — Low Turnover",        "#EF4444"),
    "bidder_c": ("Shree Constructions & Services",  "Needs Review — Scanned Cert",      "#F59E0B"),
}


def _get_criteria() -> list[Criterion]:
    data = st.session_state.get("criteria")
    return [Criterion(**c) for c in data] if data else load_criteria()


def _overall(verdicts: list[dict], crit_map: dict) -> str:
    mand = [v for v in verdicts if crit_map.get(v["criterion_id"]) and
            crit_map[v["criterion_id"]].mandatory]
    src = mand or verdicts
    if any(v["verdict"] == "not_eligible" for v in src): return "not_eligible"
    if any(v["verdict"] == "needs_review"  for v in src): return "needs_review"
    return "eligible"


def render() -> None:
    st.markdown(
        '<h2 style="font-weight:800;font-size:1.5rem;color:var(--text-color);">Bidder Evaluation</h2>'
        '<p style="color:var(--text-color);opacity:0.6;font-size:0.875rem;margin-bottom:1rem;">'
        'Evaluate each bidder against all extracted criteria.</p>',
        unsafe_allow_html=True,
    )

    selected = st.multiselect(
        "Select bidders",
        options=list(BIDDER_NAMES.keys()),
        default=list(BIDDER_NAMES.keys()),
        format_func=lambda x: _BIDDER_META.get(x, (x, "", ""))[0],
    )

    criteria_loaded = bool(st.session_state.get("criteria"))
    if not criteria_loaded:
        st.info(
            "**Criteria not loaded yet.** Go to **Tender Analysis** and click "
            "**Extract Criteria**, or use **Load Pre-computed Demo** on the Overview tab."
        )

    if st.button("▶  Run Evaluation", type="primary", disabled=not criteria_loaded):
        criteria = _get_criteria()
        prog = st.progress(0, text="Starting…")
        total = len(selected) * len(criteria)
        done, vd = 0, {}
        for bid in selected:
            files = sorted(f for f in (DATA_DIR / "bidders" / bid).iterdir()
                           if f.suffix.lower() in {".pdf", ".png", ".jpg"})
            with st.spinner(f"Indexing {_BIDDER_META.get(bid,(bid,'',''))[0]}…"):
                bidder_processor.process_bidder(bid, files)
            vlist = []
            for c in criteria:
                v = evaluator.evaluate(bid, c)
                vlist.append(v.model_dump())
                done += 1
                prog.progress(done / total,
                              text=f"{c.id} · {_BIDDER_META.get(bid,(bid,'',''))[0]}")
            vd[bid] = vlist
        st.session_state["verdicts"] = vd
        prog.empty()
        st.success("Evaluation complete.")
        st.rerun()

    vdata = st.session_state.get("verdicts", {})
    criteria = _get_criteria()
    crit_map = {c.id: c for c in criteria}

    if not vdata:
        st.info("No results yet — click **Run Evaluation** above, or load the demo from Overview.")
        return

    if st.session_state.get("fallback_active"):
        st.warning("⚠ Live API unavailable — showing pre-computed results.")

    for bid in (selected or list(vdata.keys())):
        if bid not in vdata:
            continue
        verdicts = vdata[bid]
        name, tagline, accent = _BIDDER_META.get(bid, (bid, "", "#3B82F6"))
        ov = _overall(verdicts, crit_map)
        passed  = sum(1 for v in verdicts if v["verdict"] == "eligible" and
                      crit_map.get(v["criterion_id"]) and crit_map[v["criterion_id"]].mandatory)
        total_m = sum(1 for v in verdicts if crit_map.get(v["criterion_id"]) and
                      crit_map[v["criterion_id"]].mandatory)

        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        with st.container(border=True):
            # Header
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;'
                f'align-items:center;flex-wrap:wrap;gap:8px;padding:4px 0 12px;">'
                f'<div style="display:flex;align-items:center;gap:10px;">'
                f'<div style="width:40px;height:40px;border-radius:10px;'
                f'background:{accent}22;border:1px solid {accent}44;display:flex;'
                f'align-items:center;justify-content:center;font-size:1.1rem;">🏢</div>'
                f'<div>'
                f'<div style="font-weight:700;font-size:1rem;color:var(--text-color);">{name}</div>'
                f'<div style="font-size:0.78rem;color:var(--text-color);opacity:0.5;margin-top:2px;">'
                f'{tagline}</div></div></div>'
                f'<div style="display:flex;align-items:center;gap:10px;">'
                f'{verdict_pill(ov)}'
                f'<span style="font-size:0.78rem;background:rgba(128,128,128,0.1);'
                f'color:var(--text-color);opacity:0.7;padding:3px 10px;border-radius:20px;'
                f'border:1px solid rgba(128,128,128,0.2);">'
                f'{passed}/{total_m} mandatory passed</span>'
                f'</div></div>',
                unsafe_allow_html=True,
            )

            # Column headers
            st.markdown(
                '<div style="display:grid;grid-template-columns:2.5fr 1.6fr 1.8fr 2.2fr 1.4fr;'
                'gap:8px;padding:6px 2px;border-top:1px solid rgba(128,128,128,0.15);'
                'border-bottom:1px solid rgba(128,128,128,0.15);margin-bottom:4px;">'
                + "".join(
                    f'<div style="font-size:0.68rem;font-weight:700;'
                    f'color:var(--text-color);opacity:0.4;'
                    f'text-transform:uppercase;letter-spacing:0.07em;">{h}</div>'
                    for h in ["Criterion", "Verdict", "Extracted Value", "Source & Tier", "Category"]
                )
                + "</div>",
                unsafe_allow_html=True,
            )

            for v in verdicts:
                crit = crit_map.get(v["criterion_id"])
                title = crit.title if crit else v["criterion_id"]
                mb  = mandatory_badge(crit.mandatory if crit else True)
                cat = category_badge(crit.category if crit else "compliance")
                extracted = v.get("extracted_value") or ""
                src = v.get("source") or {}

                src_html = '<span style="color:var(--text-color);opacity:0.3;">—</span>'
                if src:
                    tier = ocr_tier_badge(src.get("source_type", "text_pdf"))
                    src_html = (
                        f'<span style="font-family:monospace;font-size:0.78rem;'
                        f'background:rgba(128,128,128,0.1);padding:2px 5px;border-radius:4px;'
                        f'border:1px solid rgba(128,128,128,0.2);'
                        f'color:var(--text-color);">{src.get("doc_name","")}</span>'
                        f' <span style="font-size:0.75rem;color:var(--text-color);opacity:0.5;">'
                        f'p{src.get("page","")}</span>'
                        f'<br><div style="margin-top:4px;">{tier}</div>'
                    )

                extracted_cell = (
                    f'<span style="font-size:0.84rem;color:var(--text-color);">{extracted}</span>'
                    if extracted else
                    '<span style="color:var(--text-color);opacity:0.3;">—</span>'
                )

                st.markdown(
                    f'<div style="display:grid;grid-template-columns:2.5fr 1.6fr 1.8fr 2.2fr 1.4fr;'
                    f'gap:8px;padding:10px 2px;align-items:start;">'
                    f'<div>{mb}<div style="font-size:0.85rem;font-weight:600;'
                    f'color:var(--text-color);margin-top:5px;">'
                    f'{v["criterion_id"]}: {title}</div></div>'
                    f'<div style="padding-top:2px;">{verdict_pill(v["verdict"])}</div>'
                    f'<div style="padding-top:4px;">{extracted_cell}</div>'
                    f'<div style="font-size:0.82rem;">{src_html}</div>'
                    f'<div style="padding-top:2px;">{cat}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                confidence_bar(v.get("combined_confidence", 0.0))

                reason  = v.get("reason", "")
                snippet = (v.get("source") or {}).get("snippet", "")
                if reason or snippet:
                    with st.expander("View reasoning & evidence", expanded=False):
                        if reason:
                            st.markdown(
                                f'<div style="background:rgba(37,99,235,0.08);'
                                f'border-left:3px solid #3B82F6;padding:10px 14px;'
                                f'border-radius:0 8px 8px 0;font-size:0.875rem;'
                                f'color:var(--text-color);"><strong>Reason:</strong> {reason}</div>',
                                unsafe_allow_html=True,
                            )
                        if snippet:
                            st.markdown(
                                f'<div style="background:rgba(245,158,11,0.08);'
                                f'border-left:3px solid #F59E0B;padding:10px 14px;'
                                f'border-radius:0 8px 8px 0;margin-top:8px;font-size:0.84rem;'
                                f'color:var(--text-color);font-style:italic;">'
                                f'&ldquo;{snippet}&rdquo;</div>',
                                unsafe_allow_html=True,
                            )

                st.markdown(
                    '<hr style="margin:2px 0;border:none;'
                    'border-top:1px solid rgba(128,128,128,0.1);">',
                    unsafe_allow_html=True,
                )
