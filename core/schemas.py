from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel, Field
import uuid


class Rule(BaseModel):
    type: Literal["numeric_threshold", "count_threshold", "certification_present", "document_present"]
    field: str
    operator: Literal[">=", "<=", "==", "exists"]
    value: float | int | None = None
    unit: str | None = None


class Criterion(BaseModel):
    id: str
    title: str
    category: Literal["financial", "technical", "compliance"]
    mandatory: bool
    description: str
    rule: Rule
    query_hints: list[str]
    source_page: int
    source_clause: str


class Evidence(BaseModel):
    bidder_id: str
    doc_name: str
    page: int
    text: str
    source_type: Literal["text_pdf", "tesseract", "vision_llm"]
    ocr_confidence: float | None = None


class Source(BaseModel):
    doc_name: str
    page: int
    snippet: str
    source_type: Literal["text_pdf", "tesseract", "vision_llm"]


class Verdict(BaseModel):
    verdict_id: str = Field(default_factory=lambda: f"V-{uuid.uuid4().hex[:8]}")
    bidder_id: str
    criterion_id: str
    verdict: Literal["eligible", "not_eligible", "needs_review"]
    extracted_value: str | None = None
    normalized_value: float | int | None = None
    source: Source | None = None
    llm_confidence: float = 0.0
    ocr_confidence: float | None = None
    combined_confidence: float = 0.0
    reason: str = ""
    model_version: str = ""
    timestamp: str = ""
    review_status: Literal["pending", "approved", "edited", "rejected"] = "pending"


class AuditEntry(BaseModel):
    id: int | None = None
    ts: str
    action: str
    actor: str
    model_version: str | None = None
    bidder_id: str | None = None
    criterion_id: str | None = None
    payload_json: str | None = None
