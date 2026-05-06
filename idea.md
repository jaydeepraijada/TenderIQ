# TenderIQ: Explainable AI Platform for Automated Tender Evaluation & Eligibility Analysis

**Phase:** Idea Phase (Shortlisted)
**Last updated:** Apr 30, 2026
**Theme:** Theme 3 — AI-Based Tender Evaluation and Eligibility Analysis for Government Procurement by CRPF

---

## Problem Understanding

Government tender evaluation today is a manual, time-consuming, and error-prone process. Procurement officers must review large volumes of unstructured documents — including PDFs, scanned files, and images — to verify whether bidders meet eligibility criteria such as financial thresholds, technical experience, and compliance certifications.

This results in:
- Inconsistent evaluations across reviewers
- High turnaround time (often days per tender)
- Lack of transparency and auditability
- Risk of oversight in critical compliance checks

Our solution addresses these challenges by transforming unstructured tender and bidder data into structured, explainable, and auditable decisions.

---

## Proposed Solution: TenderIQ

TenderIQ is an AI-powered platform designed to automate tender evaluation while ensuring human trust, explainability, and audit readiness. The system follows a four-stage pipeline:

### Stage 1: Tender Understanding (Criteria Extraction)

The platform extracts eligibility criteria from tender documents using a hybrid approach combining LLMs and rule-based parsing. It identifies:
- Financial conditions (e.g., turnover ≥ ₹5 Cr)
- Technical requirements (e.g., project experience)
- Compliance rules (e.g., GST registration, ISO certifications)

Each criterion is:
- Classified as mandatory or optional
- Converted into a structured, machine-readable format

### Stage 2: Bidder Document Processing

The system processes heterogeneous bidder submissions, including:
- Typed PDFs
- Scanned documents
- Images
- Word files

The processing pipeline includes:
- OCR for scanned documents and images
- Layout-aware parsing for tables, forms, and certificates
- Entity extraction for key values such as turnover, certifications, and project count

All extracted information is stored along with:
- Source reference (document and page number)
- Confidence score

### Stage 3: Evaluation and Decision Engine

Each bidder is evaluated on a criterion-by-criterion basis using:
- Rule-based validation (e.g., threshold checks)
- Confidence-aware scoring

The system produces three possible outcomes:
- **Eligible**
- **Not Eligible**
- **Needs Manual Review**

Ambiguous or low-confidence cases are never automatically rejected. Instead, they are flagged for human review to ensure fairness and compliance.

### Stage 4: Explainability and Audit Layer (Key Differentiator)

Every decision is fully explainable and traceable. Each evaluation includes:
- The criterion being checked
- The extracted value
- Source document reference
- Confidence score
- Reason for the decision

**Example:**
```
Criterion:       Minimum Turnover ≥ ₹5 Cr
Extracted Value: ₹6.2 Cr
Source:          Financial Statement (Page 4)
Confidence:      92%
Verdict:         Eligible
```

All system actions are logged with:
- Model version
- Timestamp
- Reviewer actions

This ensures complete end-to-end auditability suitable for government procurement processes.

---

## Human-in-the-Loop Workflow

The system incorporates a mandatory human review layer:
- Low-confidence or conflicting cases are routed to reviewers
- The interface highlights extracted data directly within documents
- Reviewers can: Approve, Edit, or Reject decisions
- All reviewer decisions are captured and used to improve system performance over time

---

## Key Features

- Handles scanned and unstructured documents effectively
- Provides criterion-level explainability for every decision
- Ensures no silent disqualification of bidders
- Maintains a fully auditable decision pipeline
- Scales across departments and tender types

---

## Technology Stack

| Layer | Technology |
|---|---|
| AI/ML | LLMs for extraction, OCR (Tesseract or PaddleOCR), LayoutLM for document understanding |
| Backend | Python (FastAPI) with rule-based evaluation engine |
| Storage | PostgreSQL and vector database for document retrieval |
| Frontend | React-based dashboard |

---

## Risks and Mitigation

| Risk | Mitigation |
|---|---|
| OCR inaccuracies | Confidence scoring and human review |
| Legal language ambiguity | Hybrid LLM and rule-based parsing |
| Data inconsistency across documents | Conflict detection and validation logic |
| Over-automation risk | Human-in-the-loop validation |

---

## Why This Solution Stands Out

- Balances automation with accountability
- Designed specifically for government procurement constraints
- Focuses on trust, explainability, and auditability
- Works effectively with real-world, messy data formats

---

## Future Scope (Round 2)

- Integration with existing procurement systems
- Model improvement through feedback loops
- Multi-language document support
- Advanced fraud detection in bidder submissions

---

## Core Philosophy

The system prioritizes **assistive intelligence over full automation**, ensuring that every decision is explainable, reviewable, and compliant with government procurement standards.
