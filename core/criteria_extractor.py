import json
from pathlib import Path

import streamlit as st

from core import audit, fallback
from core.config import MODEL_VERSION
from core.llm_client import LLM, LLMUnavailable
from core.pdf_utils import extract_pages
from core.prompts import EXTRACT_CRITERIA_PROMPT_SYSTEM
from core.schemas import Criterion


@st.cache_resource
def _get_llm() -> LLM:
    return LLM()


def extract_criteria(tender_pdf_path: Path) -> list[Criterion]:
    pages = extract_pages(tender_pdf_path)
    tender_text = "\n\n".join(
        f"--- PAGE {p['page']} ---\n{p['text']}" for p in pages
    )

    user_prompt = f"""{tender_text}

---
Return JSON in this exact format:
{{"criteria": [
  {{"id": "C1", "title": "...", "category": "financial|technical|compliance",
   "mandatory": true, "description": "...",
   "rule": {{"type": "numeric_threshold|count_threshold|certification_present|document_present",
            "field": "...", "operator": ">=|<=|==|exists", "value": null, "unit": null}},
   "query_hints": ["...", "...", "..."],
   "source_page": 1, "source_clause": "3.2(a)"}},
  ...
]}}
Each criterion must have all fields. Assign sequential IDs C1, C2, ...
"""

    try:
        llm = _get_llm()
        result = llm.chat_json(EXTRACT_CRITERIA_PROMPT_SYSTEM, user_prompt)
        raw_list = result.get("criteria", [])
        criteria = [Criterion(**c) for c in raw_list]
        audit.log(
            "criteria_extracted",
            model_version=MODEL_VERSION,
            count=len(criteria),
            source=str(tender_pdf_path.name),
        )
        return criteria
    except LLMUnavailable:
        audit.log("precomputed_fallback_used", reason="LLMUnavailable in extract_criteria")
        st.session_state["fallback_active"] = True
        return fallback.load_criteria()
