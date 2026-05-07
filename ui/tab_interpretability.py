import streamlit as st

from core.config import BIDDER_NAMES, DATA_DIR
from core.fallback import load_criteria
from core.llm_client import LLM, LLMUnavailable
from core.pdf_utils import render_page_to_image
from core.schemas import Criterion
from ui.components import confidence_bar, verdict_pill

_VERDICT_CFG = {
    "eligible":     ("rgba(34,197,94,0.12)",  "#22C55E", "✅ PASSED"),
    "not_eligible": ("rgba(239,68,68,0.12)",   "#EF4444", "❌ FAILED"),
    "needs_review": ("rgba(245,158,11,0.12)",  "#F59E0B", "⚠️ NEEDS REVIEW"),
}

_RULE_PLAIN = {
    "numeric_threshold":    lambda r: f"must be {r['operator']} {r['value']:,} {r.get('unit') or ''}".strip(),
    "count_threshold":      lambda r: f"must have completed at least {int(r['value'])}",
    "certification_present": lambda _: "valid certificate must be present",
    "document_present":     lambda _: "supporting document must be present",
}


def _get_criteria() -> list[Criterion]:
    data = st.session_state.get("criteria")
    return [Criterion(**c) for c in data] if data else load_criteria()


def _explain(v: dict, crit: Criterion | None) -> str:
    verdict   = v.get("verdict", "")
    extracted = v.get("extracted_value", "") or ""
    reason    = v.get("reason", "") or ""
    if not crit:
        return reason
    rule = crit.rule
    rule_desc = _RULE_PLAIN.get(rule.type, lambda _: "")(rule.model_dump())
    if verdict == "eligible":
        return (f"Found **{extracted}**. " if extracted else "") + reason
    elif verdict == "not_eligible":
        return ((f"Found **{extracted}** — does not meet requirement ({rule_desc}). "
                 if extracted else f"Requirement: {rule_desc}. ") + reason)
    else:
        return (f"Extracted value: **{extracted}**. " if extracted else "") + reason


def _qa_context(bid: str, verdicts: list[dict], criteria: list[Criterion]) -> str:
    cm = {c.id: c for c in criteria}
    lines = [f"BIDDER: {BIDDER_NAMES.get(bid, bid)}", ""]
    for v in verdicts:
        c = cm.get(v["criterion_id"])
        rule = _RULE_PLAIN.get(c.rule.type, lambda _: "")(c.rule.model_dump()) if c else ""
        lines += [
            f"{v['criterion_id']} — {c.title if c else '?'} "
            f"[{'Mandatory' if c and c.mandatory else 'Optional'}]: {v['verdict'].upper()}",
            f"  Requirement: {rule}",
            f"  Extracted: {v.get('extracted_value') or 'not found'}",
            f"  Confidence: {v.get('combined_confidence', 0):.0%}",
            f"  Reason: {v.get('reason', '')}",
        ]
        if v.get("source"):
            s = v["source"]
            lines.append(f"  Evidence: {s.get('doc_name')} page {s.get('page')} "
                         f"[{s.get('source_type')}]")
            if s.get("snippet"):
                lines.append(f'  Snippet: "{s["snippet"][:200]}"')
        lines.append("")
    return "\n".join(lines)


def _answer(question: str, context: str) -> str:
    system = (
        "You are a procurement compliance assistant. Answer questions about an AI-generated "
        "tender evaluation in plain professional English. Always cite specific document names "
        "and page numbers. Be concise (2-4 sentences). Never invent information not in the context. "
        'Return JSON: {"answer": "<your answer>"}'
    )
    try:
        result = LLM().chat_json(system, f"{context}\n\nQUESTION: {question}")
        return result.get("answer", "")
    except LLMUnavailable:
        return _rule_answer(question, context)


def _rule_answer(q: str, context: str) -> str:
    q = q.lower()
    lines = context.splitlines()
    if any(w in q for w in ["reject", "fail", "not eligible", "disqualif"]):
        fails = [l.strip() for l in lines if "NOT_ELIGIBLE" in l or "NEEDS_REVIEW" in l]
        return ("Failing criteria: " + "; ".join(fails[:3]) + ".") if fails else "No failing criteria found."
    if any(w in q for w in ["pass", "eligible", "meet"]):
        passes = [l.strip() for l in lines if "ELIGIBLE" in l and "NOT_ELIGIBLE" not in l]
        return ("Passing criteria: " + "; ".join(passes[:3]) + ".") if passes else "No passing criteria."
    if any(w in q for w in ["turnover", "financial", "c1", "revenue"]):
        rel = [l.strip() for l in lines if "C1" in l or "turnover" in l.lower() or "Extracted" in l]
        return " ".join(rel[:4]) if rel else "Turnover information not found."
    return "Live LLM is unavailable. The evaluation summary above contains the full details."


def render() -> None:
    st.markdown(
        '<h2 style="font-weight:800;font-size:1.5rem;color:var(--text-color);">Interpretability</h2>'
        '<p style="color:var(--text-color);opacity:0.6;font-size:0.875rem;margin-bottom:1rem;">'
        'Plain-English explanations with source citations. Ask any question about the evaluation.</p>',
        unsafe_allow_html=True,
    )

    vdata = st.session_state.get("verdicts", {})
    if not vdata:
        st.info("No results yet. Load the pre-computed demo from Overview, or run evaluation.")
        return

    criteria = _get_criteria()
    crit_map = {c.id: c for c in criteria}

    bid = st.selectbox("Select bidder", options=list(vdata.keys()),
                       format_func=lambda x: BIDDER_NAMES.get(x, x))
    verdicts = vdata.get(bid, [])
    if not verdicts:
        st.warning("No verdicts for this bidder.")
        return

    company = BIDDER_NAMES.get(bid, bid)
    mand = [v for v in verdicts if crit_map.get(v["criterion_id"]) and
            crit_map[v["criterion_id"]].mandatory]
    failed = [v for v in mand if v["verdict"] == "not_eligible"]
    review = [v for v in mand if v["verdict"] == "needs_review"]
    passed = [v for v in mand if v["verdict"] == "eligible"]

    if failed:
        ov, fg, icon = "not_eligible", "#EF4444", "❌"
        summary = f"Failed {len(failed)} mandatory criterion/criteria. Must meet all to qualify."
    elif review:
        ov, fg, icon = "needs_review", "#F59E0B", "⚠️"
        summary = (f"Passed {len(passed)} mandatory criteria, but {len(review)} "
                   f"require officer sign-off.")
    else:
        ov, fg, icon = "eligible", "#22C55E", "✅"
        summary = f"All {len(passed)} mandatory criteria satisfied."

    bg, _, label = _VERDICT_CFG.get(ov, ("rgba(128,128,128,0.1)", "#888", ov))
    st.markdown(
        f'<div style="background:{bg};border:1px solid {fg}33;border-radius:12px;'
        f'padding:18px 20px;margin-bottom:1.5rem;display:flex;align-items:center;gap:14px;">'
        f'<div style="font-size:2rem;line-height:1;">{icon}</div>'
        f'<div>'
        f'<div style="font-weight:800;font-size:1.05rem;color:{fg};">'
        f'{company} — {label}</div>'
        f'<div style="font-size:0.84rem;color:{fg};opacity:0.85;margin-top:4px;">{summary}</div>'
        f'</div></div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div style="font-size:1rem;font-weight:700;color:var(--text-color);margin-bottom:12px;">'
        'Criterion-by-Criterion Breakdown</div>',
        unsafe_allow_html=True,
    )

    for v in verdicts:
        crit    = crit_map.get(v["criterion_id"])
        verdict = v.get("verdict", "needs_review")
        cbg, cfg_, clabel = _VERDICT_CFG.get(verdict, ("rgba(128,128,128,0.1)", "var(--text-color)", verdict))
        mand_txt = "Mandatory" if (crit and crit.mandatory) else "Optional"
        title    = crit.title if crit else v["criterion_id"]

        with st.container(border=True):
            left, right = st.columns([1, 3])
            with left:
                st.markdown(
                    f'<div style="background:{cbg};border-radius:8px;padding:14px;'
                    f'text-align:center;min-height:80px;display:flex;flex-direction:column;'
                    f'align-items:center;justify-content:center;gap:6px;">'
                    f'<div style="font-weight:800;font-size:0.82rem;color:{cfg_};">{clabel}</div>'
                    f'<div style="font-size:0.7rem;color:{cfg_};opacity:0.75;">{mand_txt}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
                confidence_bar(v.get("combined_confidence", 0.0), "Certainty")
            with right:
                st.markdown(
                    f'<div style="font-weight:700;font-size:0.9rem;color:var(--text-color);">'
                    f'{v["criterion_id"]}: {title}</div>',
                    unsafe_allow_html=True,
                )
                explanation = _explain(v, crit)
                if explanation:
                    st.markdown(
                        f'<p style="font-size:0.875rem;color:var(--text-color);'
                        f'opacity:0.85;margin:8px 0;">{explanation}</p>',
                        unsafe_allow_html=True,
                    )
                src = v.get("source") or {}
                if src:
                    doc, page = src.get("doc_name", ""), src.get("page", "")
                    tier_labels = {"text_pdf": "typed PDF", "tesseract": "Tesseract OCR",
                                   "vision_llm": "Vision LLM"}
                    tier = tier_labels.get(src.get("source_type", ""), "")
                    st.markdown(
                        f'<div style="display:inline-flex;align-items:center;gap:6px;'
                        f'background:rgba(128,128,128,0.08);border:1px solid rgba(128,128,128,0.2);'
                        f'border-radius:6px;padding:5px 10px;font-size:0.78rem;">'
                        f'<span>📄</span>'
                        f'<strong style="color:#3B82F6;">{doc}</strong>'
                        f'<span style="color:var(--text-color);opacity:0.5;">page {page}</span>'
                        f'<span style="color:var(--text-color);opacity:0.3;">·</span>'
                        f'<span style="color:var(--text-color);opacity:0.6;">{tier}</span>'
                        f'</div>',
                        unsafe_allow_html=True,
                    )
                    doc_path = DATA_DIR / "bidders" / bid / doc
                    if doc_path.exists() and doc_path.suffix.lower() == ".pdf":
                        with st.expander(f"View source: {doc}, page {page}", expanded=False):
                            try:
                                img = render_page_to_image(doc_path, int(page))
                                st.image(img, caption=f"{doc} — Page {page}",
                                         use_column_width=True)
                            except Exception:
                                st.caption("Page preview unavailable.")
                    elif doc_path.exists() and doc_path.suffix.lower() in {".png", ".jpg"}:
                        with st.expander(f"View: {doc}", expanded=False):
                            st.image(str(doc_path), use_column_width=True)

    st.divider()

    st.markdown(
        '<div style="font-size:1rem;font-weight:700;color:var(--text-color);margin-bottom:4px;">'
        'Ask About This Evaluation</div>'
        '<p style="font-size:0.82rem;color:var(--text-color);opacity:0.6;margin-bottom:12px;">'
        'Answers cite specific documents and pages.</p>',
        unsafe_allow_html=True,
    )

    with st.expander("Example questions", expanded=False):
        for e in ["Why was this bidder rejected?",
                  "What turnover figure was found, and from which document?",
                  "Does this bidder have a valid ISO 9001:2015 certificate?",
                  "Why is the turnover verdict in review?"]:
            st.markdown(f"- _{e}_")

    question = st.text_input("", placeholder="Ask anything about this bidder's evaluation…",
                             key=f"qa_{bid}", label_visibility="collapsed")
    if st.button("Get Answer", type="primary", key=f"qa_btn_{bid}"):
        if not question.strip():
            st.warning("Please enter a question.")
        else:
            context = _qa_context(bid, verdicts, criteria)
            with st.spinner("Looking up the answer…"):
                answer = _answer(question, context)
            st.markdown(
                f'<div style="background:rgba(37,99,235,0.08);'
                f'border:1px solid rgba(37,99,235,0.2);border-radius:10px;'
                f'padding:16px 18px;margin-top:8px;">'
                f'<div style="font-size:0.72rem;font-weight:700;color:#3B82F6;'
                f'text-transform:uppercase;letter-spacing:0.07em;margin-bottom:8px;">Answer</div>'
                f'<div style="font-size:0.9rem;color:var(--text-color);line-height:1.7;">'
                f'{answer}</div></div>',
                unsafe_allow_html=True,
            )
            with st.expander("Full context used", expanded=False):
                st.code(context, language="text")
