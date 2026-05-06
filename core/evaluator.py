import json
from datetime import datetime, timezone

import streamlit as st

from core import audit, bidder_processor, fallback
from core.config import CONFIDENCE_HIGH, CONFIDENCE_REVIEW, MODEL_VERSION
from core.llm_client import LLM, LLMUnavailable
from core.prompts import EVALUATE_CRITERION_PROMPT_SYSTEM
from core.schemas import Criterion, Source, Verdict


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@st.cache_resource
def _get_llm() -> LLM:
    return LLM()


def _combined_confidence(
    llm_confidence: float, source_type: str, ocr_confidence: float | None
) -> float:
    if source_type == "text_pdf":
        return llm_confidence
    elif source_type == "vision_llm":
        return 0.7 * llm_confidence + 0.3 * 0.95
    elif source_type == "tesseract":
        tc = ocr_confidence if ocr_confidence and ocr_confidence >= 0 else 0.3
        return 0.6 * llm_confidence + 0.4 * tc
    return llm_confidence


def _apply_thresholds(verdict: str, combined: float) -> str:
    if verdict == "needs_review":
        return "needs_review"
    if combined >= CONFIDENCE_HIGH:
        return verdict
    if CONFIDENCE_REVIEW <= combined < CONFIDENCE_HIGH and verdict == "not_eligible":
        return "needs_review"
    if combined < CONFIDENCE_REVIEW:
        return "needs_review"
    return verdict


def evaluate(bidder_id: str, criterion: Criterion) -> Verdict:
    evidence = bidder_processor.gather_evidence(bidder_id, criterion)

    if not evidence:
        v = Verdict(
            bidder_id=bidder_id,
            criterion_id=criterion.id,
            verdict="needs_review",
            reason="No matching evidence found in submitted documents.",
            llm_confidence=0.0,
            combined_confidence=0.0,
            model_version=MODEL_VERSION,
            timestamp=_now_iso(),
        )
        audit.log("criterion_evaluated", bidder_id=bidder_id,
                  criterion_id=criterion.id, verdict="needs_review",
                  llm_verdict="needs_review", extracted_value="",
                  llm_confidence=0.0, combined_confidence=0.0,
                  ocr_tier="", escalation_reason="no evidence found", reason=v.reason)
        return v

    evidence_dicts = [
        {
            "doc_name": e.doc_name,
            "page": e.page,
            "ocr_confidence": e.ocr_confidence,
            "source_type": e.source_type,
            "text": e.text[:1500],
        }
        for e in evidence
    ]

    user_prompt = f"""CRITERION:
{criterion.model_dump_json(indent=2)}

RETRIEVED EVIDENCE (top-k chunks from bidder {bidder_id}):
{json.dumps(evidence_dicts, indent=2)}

Return JSON:
{{
  "verdict": "eligible" | "not_eligible" | "needs_review",
  "extracted_value": "<short string as found in evidence>",
  "normalized_value": <number or null>,
  "chosen_source": {{"doc_name": "...", "page": <int>, "snippet": "<= 200 chars", "source_type": "..."}},
  "llm_confidence": <0.0 to 1.0>,
  "reason": "<one or two sentences>"
}}

Rules:
- If evidence directly contains a value satisfying the rule, verdict=eligible with high llm_confidence.
- If evidence directly contradicts the rule, verdict=not_eligible.
- If no relevant evidence retrieved, verdict=needs_review, llm_confidence<=0.4.
- If the source is OCR with low confidence and the value is borderline, lean to needs_review.
"""

    try:
        llm = _get_llm()
        result = llm.chat_json(EVALUATE_CRITERION_PROMPT_SYSTEM, user_prompt)
    except LLMUnavailable:
        audit.log("precomputed_fallback_used", bidder_id=bidder_id,
                  criterion_id=criterion.id, reason="LLMUnavailable in evaluate")
        if "fallback_active" not in st.session_state:
            st.session_state["fallback_active"] = True
        return fallback.load_evaluation(bidder_id, criterion.id)

    llm_verdict = result.get("verdict", "needs_review")
    extracted_value = result.get("extracted_value")
    normalized_value = result.get("normalized_value")
    chosen_src = result.get("chosen_source") or {}
    llm_confidence = float(result.get("llm_confidence", 0.5))
    reason = result.get("reason", "")

    source_type = chosen_src.get("source_type", "text_pdf")
    best_evidence = next(
        (e for e in evidence if e.doc_name == chosen_src.get("doc_name")),
        evidence[0] if evidence else None,
    )
    ocr_confidence = best_evidence.ocr_confidence if best_evidence else None
    if ocr_confidence and ocr_confidence < 0:
        ocr_confidence = None

    source = Source(
        doc_name=chosen_src.get("doc_name", ""),
        page=int(chosen_src.get("page", 1)),
        snippet=chosen_src.get("snippet", "")[:200],
        source_type=source_type,
    ) if chosen_src else None

    combined = _combined_confidence(llm_confidence, source_type, ocr_confidence)
    final_verdict = _apply_thresholds(llm_verdict, combined)

    v = Verdict(
        bidder_id=bidder_id,
        criterion_id=criterion.id,
        verdict=final_verdict,
        extracted_value=extracted_value,
        normalized_value=normalized_value,
        source=source,
        llm_confidence=llm_confidence,
        ocr_confidence=ocr_confidence,
        combined_confidence=round(combined, 4),
        reason=reason,
        model_version=MODEL_VERSION,
        timestamp=_now_iso(),
        review_status="pending",
    )
    escalation_reason = None
    if llm_verdict != final_verdict:
        if combined < CONFIDENCE_REVIEW:
            escalation_reason = f"auto-escalated: combined confidence {combined:.0%} below threshold"
        elif combined < CONFIDENCE_HIGH and llm_verdict == "not_eligible":
            escalation_reason = f"auto-escalated: borderline confidence {combined:.0%} on disqualification"

    audit.log(
        "criterion_evaluated",
        bidder_id=bidder_id,
        criterion_id=criterion.id,
        verdict=final_verdict,
        llm_verdict=llm_verdict,
        extracted_value=extracted_value or "",
        llm_confidence=round(llm_confidence, 4),
        combined_confidence=round(combined, 4),
        ocr_tier=source_type,
        escalation_reason=escalation_reason or "",
        reason=reason,
    )
    return v


def evaluate_bidder(bidder_id: str, criteria: list[Criterion]) -> list[Verdict]:
    return [evaluate(bidder_id, c) for c in criteria]
