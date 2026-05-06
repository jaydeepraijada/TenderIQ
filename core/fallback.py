import json

from core.config import PRECOMPUTED_DIR
from core.schemas import Criterion, Verdict

_HARDCODED_CRITERIA = [
    {
        "id": "C1", "title": "Minimum Annual Turnover",
        "category": "financial", "mandatory": True,
        "description": "The bidder shall have a minimum average annual turnover of INR 5 Crore during the last three financial years (2022-23, 2023-24, 2024-25).",
        "rule": {"type": "numeric_threshold", "field": "annual_turnover_inr",
                 "operator": ">=", "value": 50000000, "unit": "INR"},
        "query_hints": ["annual turnover", "total revenue", "INR crore", "audited financials", "CA certificate"],
        "source_page": 2, "source_clause": "3.2(a)",
    },
    {
        "id": "C2", "title": "Completed Construction Projects",
        "category": "technical", "mandatory": True,
        "description": "The bidder must have successfully completed at least three (3) similar construction projects of value not less than INR 1 Crore each in the last five financial years.",
        "rule": {"type": "count_threshold", "field": "completed_projects",
                 "operator": ">=", "value": 3, "unit": None},
        "query_hints": ["completed projects", "construction experience", "work order", "completion certificate", "similar projects"],
        "source_page": 2, "source_clause": "3.2(b)",
    },
    {
        "id": "C3", "title": "GST Registration",
        "category": "compliance", "mandatory": True,
        "description": "The bidder shall possess a valid Goods and Services Tax (GST) registration certificate. The GSTIN must be active as on the date of submission.",
        "rule": {"type": "certification_present", "field": "gstin",
                 "operator": "exists", "value": None, "unit": None},
        "query_hints": ["GSTIN", "GST certificate", "GST registration", "tax registration"],
        "source_page": 2, "source_clause": "3.2(c)",
    },
    {
        "id": "C4", "title": "ISO 9001:2015 Certification",
        "category": "compliance", "mandatory": True,
        "description": "The bidder shall hold a valid ISO 9001:2015 Quality Management System certification issued by an accredited certification body.",
        "rule": {"type": "certification_present", "field": "iso_9001",
                 "operator": "exists", "value": None, "unit": None},
        "query_hints": ["ISO 9001", "quality management", "ISO certificate", "QMS certification"],
        "source_page": 2, "source_clause": "3.2(d)",
    },
    {
        "id": "C5", "title": "Paramilitary Infrastructure Experience",
        "category": "technical", "mandatory": False,
        "description": "Preferably, the bidder may have prior experience with construction or maintenance of paramilitary or defence infrastructure.",
        "rule": {"type": "document_present", "field": "paramilitary_experience",
                 "operator": "exists", "value": None, "unit": None},
        "query_hints": ["paramilitary", "defence infrastructure", "CRPF", "BSF", "security forces"],
        "source_page": 2, "source_clause": "3.2(e)",
    },
]


def load_criteria() -> list[Criterion]:
    criteria_file = PRECOMPUTED_DIR / "criteria.json"
    if criteria_file.exists():
        data = json.loads(criteria_file.read_text(encoding="utf-8"))
        return [Criterion(**c) for c in data.get("criteria", data)]
    return [Criterion(**c) for c in _HARDCODED_CRITERIA]


def load_evaluation(bidder_id: str, criterion_id: str) -> Verdict:
    eval_file = PRECOMPUTED_DIR / f"eval_{bidder_id}.json"
    if eval_file.exists():
        data = json.loads(eval_file.read_text(encoding="utf-8"))
        verdicts = data if isinstance(data, list) else data.get("verdicts", [])
        for v in verdicts:
            if v.get("criterion_id") == criterion_id:
                return Verdict(**v)
    # Return a needs_review verdict as safe default
    from core.config import MODEL_VERSION
    from datetime import datetime, timezone
    return Verdict(
        bidder_id=bidder_id,
        criterion_id=criterion_id,
        verdict="needs_review",
        reason="Pre-computed evaluation not available. Manual review required.",
        model_version=MODEL_VERSION,
        timestamp=datetime.now(timezone.utc).isoformat(),
        combined_confidence=0.0,
    )
