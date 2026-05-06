import json

import streamlit as st

from core.config import BIDDER_NAMES, DATA_DIR, MODEL_VERSION
from core.fallback import load_criteria
from core.llm_client import LLM, LLMUnavailable
from core.pdf_utils import render_page_to_image
from core.schemas import Criterion

_VERDICT_PLAIN = {
    "eligible":     ("✅", "PASSED",       "green"),
    "not_eligible": ("❌", "FAILED",       "red"),
    "needs_review": ("⚠️", "NEEDS REVIEW", "orange"),
}

_CRITERION_RULE_PLAIN = {
    "numeric_threshold": lambda r: (
        f"must be ≥ {r['value']:,} {r.get('unit') or ''}" if r["operator"] == ">="
        else f"must be ≤ {r['value']:,} {r.get('unit') or ''}"
    ),
    "count_threshold": lambda r: f"must have completed at least {int(r['value'])}",
    "certification_present": lambda _: "valid certificate must be present",
    "document_present": lambda _: "supporting document must be present",
}


def _get_criteria() -> list[Criterion]:
    data = st.session_state.get("criteria")
    if data:
        return [Criterion(**c) for c in data]
    return load_criteria()


def _plain_explanation(v: dict, crit: Criterion | None) -> str:
    verdict = v.get("verdict", "")
    extracted = v.get("extracted_value") or ""
    reason = v.get("reason") or ""
    src = v.get("source") or {}

    if not crit:
        return reason

    icon, label, _ = _VERDICT_PLAIN.get(verdict, ("❓", verdict, "grey"))
    rule = crit.rule

    if verdict == "eligible":
        rule_desc = _CRITERION_RULE_PLAIN.get(rule.type, lambda _: "")(rule.model_dump())
        val_part = f" Found: **{extracted}**." if extracted else ""
        return f"{icon} **{crit.title}** — {label}.{val_part} {reason}"

    elif verdict == "not_eligible":
        rule_desc = _CRITERION_RULE_PLAIN.get(rule.type, lambda _: "")(rule.model_dump())
        val_part = f" Found: **{extracted}** — this does not meet the requirement ({rule_desc})." if extracted else f" Required: {rule_desc}."
        return f"{icon} **{crit.title}** — {label}.{val_part} {reason}"

    else:  # needs_review
        val_part = f" Extracted value: **{extracted}**." if extracted else ""
        return f"{icon} **{crit.title}** — {label}.{val_part} {reason}"


def _source_citation(v: dict) -> str | None:
    src = v.get("source")
    if not src:
        return None
    doc = src.get("doc_name", "")
    page = src.get("page", "")
    tier = src.get("source_type", "")
    tier_labels = {"text_pdf": "typed PDF", "tesseract": "Tesseract OCR",
                   "vision_llm": "Vision LLM OCR"}
    return f"📄 **{doc}**, page {page}  ·  read by _{tier_labels.get(tier, tier)}_"


def _build_qa_context(bidder_id: str, verdicts: list[dict],
                       criteria: list[Criterion]) -> str:
    crit_map = {c.id: c for c in criteria}
    lines = [
        f"BIDDER: {BIDDER_NAMES.get(bidder_id, bidder_id)} ({bidder_id})",
        "",
        "EVALUATION RESULTS:",
    ]
    for v in verdicts:
        crit = crit_map.get(v["criterion_id"])
        crit_title = crit.title if crit else v["criterion_id"]
        mandatory = ("Mandatory" if crit and crit.mandatory else "Optional") if crit else "Unknown"
        lines.append(
            f"  {v['criterion_id']} — {crit_title} [{mandatory}]: "
            f"{v['verdict'].upper()}"
        )
        if v.get("extracted_value"):
            lines.append(f"    Extracted value: {v['extracted_value']}")
        if v.get("source"):
            src = v["source"]
            lines.append(
                f"    Evidence source: {src.get('doc_name')} page {src.get('page')} "
                f"(read by {src.get('source_type')})"
            )
        if v.get("source") and v["source"].get("snippet"):
            lines.append(f"    Evidence snippet: \"{v['source']['snippet'][:200]}\"")
        lines.append(
            f"    Confidence: {v.get('combined_confidence', 0):.0%}  |  "
            f"Reason: {v.get('reason', '')}"
        )
        if crit:
            rule = crit.rule
            rule_desc = _CRITERION_RULE_PLAIN.get(rule.type, lambda _: "")(rule.model_dump())
            lines.append(f"    Requirement: {rule_desc}")
        lines.append("")
    return "\n".join(lines)


def _answer_question(question: str, context: str) -> str:
    system = """You are a procurement compliance assistant helping an evaluation officer
understand AI-generated eligibility verdicts. Answer questions about the bidder's evaluation
in plain, professional English. Always cite specific document names and page numbers from the
evidence. Be concise (2-4 sentences). Do not invent information not present in the context."""

    user = f"""{context}

OFFICER'S QUESTION: {question}

Answer the question based only on the evaluation results above.
Cite the specific document and page number when referring to evidence."""

    try:
        llm = LLM()
        result = llm.chat_json(
            system + " Return JSON: {\"answer\": \"<your answer>\"}",
            user,
        )
        return result.get("answer", "")
    except LLMUnavailable:
        return _rule_based_answer(question, context)


def _rule_based_answer(question: str, context: str) -> str:
    q = question.lower()
    lines = context.splitlines()

    if any(w in q for w in ["reject", "fail", "not eligible", "disqualif"]):
        fails = [l for l in lines if "NOT_ELIGIBLE" in l or "NEEDS_REVIEW" in l]
        if fails:
            return ("Based on the evaluation: " +
                    "; ".join(f.strip() for f in fails[:3]) +
                    ". See the Bidder Evaluation tab for full details.")
        return "No failing criteria were found in the evaluation."

    if any(w in q for w in ["pass", "eligible", "meet", "satisfy"]):
        passes = [l for l in lines if "ELIGIBLE" in l and "NOT_ELIGIBLE" not in l]
        if passes:
            return ("Criteria passed: " +
                    "; ".join(f.strip() for f in passes[:3]) + ".")
        return "No passing criteria were found."

    if any(w in q for w in ["turnover", "financial", "revenue", "c1"]):
        relevant = [l for l in lines if "C1" in l or "turnover" in l.lower() or
                    "Extracted value" in l]
        if relevant:
            return " ".join(l.strip() for l in relevant[:4])

    return ("I cannot answer that specific question without the live LLM. "
            "The evaluation summary above contains the full details.")


def render() -> None:
    st.header("Interpretability")
    st.caption(
        "Plain-English explanations of why each bidder was evaluated the way it was, "
        "with full source citations. Ask any question about the evaluation."
    )

    verdicts_data = st.session_state.get("verdicts", {})
    if not verdicts_data:
        st.info("No evaluation results yet. Run the evaluation in Bidder Evaluation tab or "
                "click **Load Pre-computed Demo** in the Overview tab.")
        return

    criteria = _get_criteria()
    crit_map = {c.id: c for c in criteria}

    bidder_id = st.selectbox(
        "Select bidder",
        options=list(verdicts_data.keys()),
        format_func=lambda x: BIDDER_NAMES.get(x, x),
    )

    verdicts = verdicts_data.get(bidder_id, [])
    if not verdicts:
        st.warning("No verdicts available for this bidder.")
        return

    # ── Overall summary ───────────────────────────────────────────────────────
    mandatory_verdicts = [v for v in verdicts
                          if crit_map.get(v["criterion_id"]) and
                          crit_map[v["criterion_id"]].mandatory]
    failed = [v for v in mandatory_verdicts if v["verdict"] == "not_eligible"]
    review = [v for v in mandatory_verdicts if v["verdict"] == "needs_review"]
    passed = [v for v in mandatory_verdicts if v["verdict"] == "eligible"]

    friendly = BIDDER_NAMES.get(bidder_id, bidder_id)

    if failed:
        st.error(
            f"**{friendly} — NOT ELIGIBLE**\n\n"
            f"Failed {len(failed)} mandatory criterion/criteria. "
            f"A bidder must meet all mandatory criteria to qualify."
        )
    elif review:
        st.warning(
            f"**{friendly} — NEEDS REVIEW**\n\n"
            f"Passed {len(passed)} mandatory criteria, but {len(review)} could not be "
            f"automatically confirmed and require officer verification."
        )
    else:
        st.success(
            f"**{friendly} — ELIGIBLE**\n\n"
            f"All {len(passed)} mandatory criteria satisfied."
        )

    st.divider()

    # ── Per-criterion plain-English cards ─────────────────────────────────────
    st.subheader("Criterion-by-Criterion Breakdown")

    for v in verdicts:
        crit = crit_map.get(v["criterion_id"])
        _, label, color = _VERDICT_PLAIN.get(v["verdict"], ("❓", v["verdict"], "grey"))
        mandatory_tag = "🔴 Mandatory" if (crit and crit.mandatory) else "🟡 Optional"

        with st.container(border=True):
            col_status, col_detail = st.columns([1, 4])

            with col_status:
                if color == "green":
                    st.success(label)
                elif color == "red":
                    st.error(label)
                else:
                    st.warning(label)
                st.caption(mandatory_tag)
                conf = v.get("combined_confidence", 0.0)
                st.caption(f"Confidence: {conf:.0%}")

            with col_detail:
                explanation = _plain_explanation(v, crit)
                st.markdown(explanation)

                citation = _source_citation(v)
                if citation:
                    st.markdown(citation)

                    # Page preview
                    src = v.get("source", {})
                    doc_name = src.get("doc_name", "")
                    page_no = src.get("page", 1)
                    bidder_dir = DATA_DIR / "bidders" / bidder_id
                    doc_path = bidder_dir / doc_name

                    if doc_path.exists() and doc_path.suffix.lower() == ".pdf":
                        with st.expander(f"View source page ({doc_name}, p{page_no})",
                                         expanded=False):
                            try:
                                img = render_page_to_image(doc_path, page_no)
                                st.image(img, caption=f"{doc_name} — Page {page_no}",
                                         use_column_width=True)
                            except Exception:
                                st.caption("Page preview unavailable.")
                    elif doc_path.exists() and doc_path.suffix.lower() in {".png", ".jpg"}:
                        with st.expander(f"View source image ({doc_name})", expanded=False):
                            st.image(str(doc_path), caption=doc_name,
                                     use_column_width=True)

    st.divider()

    # ── Q&A section ───────────────────────────────────────────────────────────
    st.subheader("Ask About This Evaluation")
    st.caption(
        "Ask any question about why this bidder was evaluated the way it was. "
        "Answers cite specific documents and pages."
    )

    suggestions = [
        "Why was this bidder rejected?",
        "Which criteria did this bidder fail?",
        "What turnover figure was found and which document was it from?",
        "Is this bidder ISO certified?",
        "Why is the turnover verdict in review?",
    ]
    with st.expander("Example questions", expanded=False):
        for s in suggestions:
            st.markdown(f"- _{s}_")

    question = st.text_input(
        "Your question",
        placeholder="e.g. Why was this bidder's turnover flagged for review?",
        key=f"qa_input_{bidder_id}",
    )

    if st.button("Get Answer", type="primary", key=f"qa_btn_{bidder_id}"):
        if not question.strip():
            st.warning("Please enter a question.")
        else:
            context = _build_qa_context(bidder_id, verdicts, criteria)
            with st.spinner("Looking up the answer…"):
                answer = _answer_question(question, context)

            st.markdown("**Answer:**")
            st.info(answer)

            with st.expander("Full evaluation context used to answer", expanded=False):
                st.code(context, language="text")
