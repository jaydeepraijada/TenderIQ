"""Generate TenderIQ_Pitch.pdf — 8-slide pitch deck using reportlab."""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.pdfgen.canvas import Canvas

W, H = A4
NAVY   = colors.HexColor("#0D1B2A")
BLUE   = colors.HexColor("#2563EB")
LBLUE  = colors.HexColor("#DBEAFE")
GOLD   = colors.HexColor("#F0A500")
WHITE  = colors.white
GREY   = colors.HexColor("#64748B")
LGREY  = colors.HexColor("#F1F5F9")
GREEN  = colors.HexColor("#059669")
RED    = colors.HexColor("#DC2626")
AMBER  = colors.HexColor("#D97706")
BORD   = colors.HexColor("#E2E8F0")


def _header_bar(c: Canvas, title: str, subtitle: str = "") -> None:
    c.setFillColor(NAVY)
    c.rect(0, H - 2.8*cm, W, 2.8*cm, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.rect(0, H - 2.85*cm, W, 0.18*cm, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 18)
    c.drawString(1.8*cm, H - 1.7*cm, title)
    if subtitle:
        c.setFont("Helvetica", 10)
        c.setFillColor(colors.HexColor("#94A3B8"))
        c.drawString(1.8*cm, H - 2.3*cm, subtitle)


def _footer(c: Canvas, page: int, total: int = 8) -> None:
    c.setFillColor(LGREY)
    c.rect(0, 0, W, 1.0*cm, fill=1, stroke=0)
    c.setFillColor(GREY)
    c.setFont("Helvetica", 8)
    c.drawString(1.8*cm, 0.35*cm, "TenderIQ  ·  CRPF Hackathon Theme 3  ·  Explainable AI for Government Procurement")
    c.drawRightString(W - 1.8*cm, 0.35*cm, f"{page} / {total}")


def _bullet(c: Canvas, x: float, y: float, text: str,
            size: int = 10, indent: float = 0.5*cm) -> float:
    c.setFillColor(BLUE)
    c.circle(x + 0.15*cm, y + 0.3*cm, 0.12*cm, fill=1, stroke=0)
    c.setFillColor(NAVY)
    c.setFont("Helvetica", size)
    lines = _wrap(text, 85 - int(indent / mm))
    for i, line in enumerate(lines):
        c.drawString(x + indent, y - i * (size + 3) * 0.035 * cm * 28.35 / 10, line)
    return y - len(lines) * (size + 4) * 0.035 * cm * 28.35 / 10


def _wrap(text: str, width: int) -> list[str]:
    words = text.split()
    lines, cur = [], ""
    for w in words:
        if len(cur) + len(w) + 1 <= width:
            cur = (cur + " " + w).strip()
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines or [""]


def _card(c: Canvas, x: float, y: float, w: float, h: float,
          title: str, body: str, accent: colors.Color = BLUE) -> None:
    c.setFillColor(WHITE)
    c.setStrokeColor(BORD)
    c.roundRect(x, y, w, h, 0.3*cm, fill=1, stroke=1)
    c.setFillColor(accent)
    c.roundRect(x, y + h - 0.35*cm, w, 0.35*cm, 0.3*cm, fill=1, stroke=0)
    c.rect(x, y + h - 0.35*cm, w, 0.2*cm, fill=1, stroke=0)
    c.setFillColor(WHITE)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(x + 0.3*cm, y + h - 0.25*cm, title)
    c.setFillColor(GREY)
    c.setFont("Helvetica", 8.5)
    lines = _wrap(body, int(w / (0.22*cm)))
    for i, line in enumerate(lines[:5]):
        c.drawString(x + 0.3*cm, y + h - 0.75*cm - i * 0.45*cm, line)


def slide_1_title(c: Canvas) -> None:
    c.setFillColor(NAVY)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    c.setFillColor(BLUE)
    c.rect(0, 0, W, 0.5*cm, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.rect(0, 0.5*cm, W, 0.12*cm, fill=1, stroke=0)

    c.setFillColor(WHITE)
    c.setFont("Helvetica", 40)
    c.drawCentredString(W / 2, H - 6*cm, "⚖️")
    c.setFont("Helvetica-Bold", 36)
    c.drawCentredString(W / 2, H - 8*cm, "TenderIQ")
    c.setFont("Helvetica", 15)
    c.setFillColor(colors.HexColor("#CBD5E1"))
    c.drawCentredString(W / 2, H - 9.2*cm,
                        "Explainable AI for Government Tender Evaluation")

    c.setFillColor(GOLD)
    c.roundRect(W/2 - 5*cm, H - 11.5*cm, 10*cm, 1.1*cm, 0.3*cm, fill=1, stroke=0)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(W / 2, H - 11.0*cm, "CRPF Hackathon  ·  Theme 3")

    c.setFillColor(colors.HexColor("#64748B"))
    c.setFont("Helvetica", 9)
    c.drawCentredString(W / 2, H - 13.5*cm,
                        "Central Reserve Police Force  ·  Ministry of Home Affairs")
    c.drawCentredString(W / 2, H - 14.1*cm,
                        "AI-Based Tender Evaluation and Eligibility Analysis")

    _footer(c, 1)


def slide_2_problem(c: Canvas) -> None:
    _header_bar(c, "The Problem", "Manual tender evaluation is slow, inconsistent, and opaque")
    _footer(c, 2)

    y = H - 4.0*cm
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(NAVY)
    c.drawString(1.8*cm, y, "Government procurement officers today must:")
    y -= 0.6*cm

    problems = [
        "Manually read hundreds of pages of tender documents and bidder submissions",
        "Identify eligibility criteria buried in legal language across multiple sections",
        "Cross-check financial statements, certificates, and project records for each bidder",
        "Handle scanned documents, photographs, and mixed-format submissions",
        "Reach consistent decisions — yet two evaluators routinely disagree on the same bid",
        "Produce an auditable trail for every decision, under compliance and RTI pressure",
    ]
    for p in problems:
        y = _bullet(c, 1.8*cm, y, p)
        y -= 0.25*cm

    y -= 0.3*cm
    c.setFillColor(LBLUE)
    c.roundRect(1.8*cm, y - 1.6*cm, W - 3.6*cm, 1.6*cm, 0.3*cm, fill=1, stroke=0)
    c.setFillColor(BLUE)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(W / 2, y - 0.7*cm,
                        "For one tender, a committee may spend 3–5 days.")
    c.setFont("Helvetica", 10)
    c.setFillColor(GREY)
    c.drawCentredString(W / 2, y - 1.15*cm,
                        "TenderIQ reduces this to minutes, with full explainability.")


def slide_3_solution(c: Canvas) -> None:
    _header_bar(c, "Our Solution", "TenderIQ automates evaluation while preserving human oversight")
    _footer(c, 3)

    pillars = [
        (BLUE,  "📄 Extract",    "DeepSeek LLM reads the tender PDF and structures every eligibility criterion as JSON — category, rule, source clause, query hints."),
        (GREEN, "🔍 OCR & Index","Three-tier pipeline handles any document: PyMuPDF → Tesseract → Vision LLM. All text indexed into ChromaDB with provenance."),
        (AMBER, "⚖️ Evaluate",  "Per-criterion vector search + LLM evaluation. Combined confidence score. Safety rule: never silent disqualification."),
        (RED,   "👤 Review",    "Borderline verdicts surface in a human review queue with full evidence. Every action logged to SQLite for compliance."),
    ]
    cw = (W - 3.6*cm) / 2
    ch = 5.0*cm
    positions = [
        (1.8*cm, H - 9.5*cm),
        (1.8*cm + cw + 0.4*cm, H - 9.5*cm),
        (1.8*cm, H - 9.5*cm - ch - 0.5*cm),
        (1.8*cm + cw + 0.4*cm, H - 9.5*cm - ch - 0.5*cm),
    ]
    for (px, py), (color, title, body) in zip(positions, pillars):
        _card(c, px, py, cw, ch, title, body, color)


def slide_4_architecture(c: Canvas) -> None:
    _header_bar(c, "Architecture", "Single-process Streamlit app — no separate services")
    _footer(c, 4)

    boxes = [
        (1.8*cm,  H - 5.5*cm, 5.0*cm, 1.2*cm, "Tender PDF",       LBLUE, BLUE),
        (8.5*cm,  H - 5.5*cm, 5.5*cm, 1.2*cm, "Criteria (JSON)",  LBLUE, BLUE),
        (15.5*cm, H - 5.5*cm, 4.5*cm, 1.2*cm, "ChromaDB Index",   LGREY, GREY),
        (1.8*cm,  H - 9.0*cm, 5.0*cm, 1.2*cm, "Bidder Docs",      LGREY, GREY),
        (8.5*cm,  H - 9.0*cm, 5.5*cm, 1.2*cm, "OCR Pipeline ×3",  colors.HexColor("#FDF4FF"), colors.HexColor("#7E22CE")),
        (15.5*cm, H - 9.0*cm, 4.5*cm, 1.2*cm, "Verdicts",         colors.HexColor("#F0FDF4"), GREEN),
        (5.5*cm,  H - 13.0*cm, 10*cm, 1.2*cm, "SQLite Audit Log",  colors.HexColor("#FFFBEB"), AMBER),
    ]
    for bx, by, bw, bh, label, fill, stroke in boxes:
        c.setFillColor(fill)
        c.setStrokeColor(stroke)
        c.roundRect(bx, by, bw, bh, 0.25*cm, fill=1, stroke=1)
        c.setFillColor(stroke)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(bx + bw / 2, by + 0.4*cm, label)

    arrows = [
        (6.8*cm, H - 4.95*cm, 8.5*cm, H - 4.95*cm),
        (8.5*cm + 5.5*cm, H - 4.95*cm, 15.5*cm, H - 4.95*cm),
        (1.8*cm + 5.0*cm, H - 8.45*cm, 8.5*cm, H - 8.45*cm),
        (8.5*cm + 5.5*cm, H - 8.45*cm, 15.5*cm, H - 8.45*cm),
        (15.5*cm + 2.25*cm, H - 9.0*cm, 15.5*cm + 2.25*cm, H - 5.5*cm - 1.2*cm),
        (W / 2, H - 9.0*cm - 0, W / 2, H - 13.0*cm + 1.2*cm),
    ]
    c.setStrokeColor(GREY)
    c.setLineWidth(1)
    for x1, y1, x2, y2 in arrows:
        c.line(x1, y1, x2, y2)

    c.setFont("Helvetica", 8.5)
    c.setFillColor(GREY)
    c.drawCentredString(W / 2, H - 14.5*cm,
                        "DeepSeek API  ·  ChromaDB (embedded)  ·  SQLite  ·  No external services")


def slide_5_ocr(c: Canvas) -> None:
    _header_bar(c, "Three-Tier OCR Pipeline",
                "Handles typed PDFs, scanned documents, and photographs")
    _footer(c, 5)

    tiers = [
        (BLUE,  "Tier 1 — PyMuPDF",
         "Cost: free, instant\nTrigger: document is a typed/digital PDF\nConfidence: 1.0 (lossless)\nOutput: exact text with page numbers"),
        (colors.HexColor("#7E22CE"), "Tier 2 — Tesseract OCR",
         "Cost: free, fast\nTrigger: scanned PDF or image file\nConfidence: mean of per-word scores\nOutput: extracted text (quality varies)"),
        (AMBER, "Tier 3 — DeepSeek Vision LLM",
         "Cost: API call, slower\nTrigger: Tesseract confidence < 65%\nConfidence: 0.95\nOutput: faithfully transcribed text\nAudit: vision_ocr_invoked logged"),
    ]
    tw = (W - 4.0*cm) / 3
    for i, (color, title, body) in enumerate(tiers):
        x = 1.8*cm + i * (tw + 0.3*cm)
        y = H - 9.0*cm
        c.setFillColor(color)
        c.roundRect(x, y, tw, 5.5*cm, 0.3*cm, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(x + tw / 2, y + 5.0*cm, title)
        c.setFont("Helvetica", 9)
        for j, line in enumerate(body.split("\n")):
            c.drawString(x + 0.4*cm, y + 4.2*cm - j * 0.5*cm, line)

    y = H - 11.0*cm
    c.setFillColor(LGREY)
    c.roundRect(1.8*cm, y - 1.8*cm, W - 3.6*cm, 1.8*cm, 0.3*cm, fill=1, stroke=0)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(W / 2, y - 0.65*cm, "Demo: Bidder C submits a blurry, rotated CA certificate scan")
    c.setFont("Helvetica", 9)
    c.setFillColor(GREY)
    c.drawCentredString(W / 2, y - 1.2*cm,
                        "Tesseract confidence ~55% → Vision LLM transcribes correctly → combined confidence 0.58 → needs_review")


def slide_6_explainability(c: Canvas) -> None:
    _header_bar(c, "Explainability & Compliance",
                "Every verdict is traceable to a document, page, and model decision")
    _footer(c, 6)

    features = [
        ("Criterion-level verdicts",
         "Each (bidder × criterion) pair has an independent verdict with extracted value, source document, page number, OCR tier, LLM confidence, and plain-English reason."),
        ("Never silent disqualification",
         "The safety threshold rule: if combined confidence is 0.55–0.80 and the LLM says not_eligible, the verdict is downgraded to needs_review and surfaced for human review."),
        ("Full audit trail",
         "Every action is logged to SQLite: criteria_extracted, bidder_processed, criterion_evaluated, human_review_action, vision_ocr_invoked, precomputed_fallback_used."),
        ("Interpretability tab",
         "Plain-English explanation of each verdict with inline PDF page previews. LLM-powered Q&A lets officers ask specific questions with source citations."),
        ("Human review queue",
         "Flagged verdicts show the evidence snippet, extracted value, source page, and OCR tier badge. Officers Approve / Edit & Approve / Reject with audit logging."),
        ("Pre-computed fallback",
         "If the API is unavailable, pre-computed JSON is served transparently. The sidebar shows an amber dot and a banner. No silent failures."),
    ]
    col_w = (W - 4.0*cm) / 2
    for i, (title, body) in enumerate(features):
        col = i % 2
        row = i // 2
        x = 1.8*cm + col * (col_w + 0.4*cm)
        y = H - 4.5*cm - row * 2.8*cm
        c.setFillColor(WHITE)
        c.setStrokeColor(BORD)
        c.roundRect(x, y - 2.0*cm, col_w, 2.0*cm, 0.25*cm, fill=1, stroke=1)
        c.setFillColor(BLUE)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(x + 0.3*cm, y - 0.45*cm, title)
        c.setFillColor(GREY)
        c.setFont("Helvetica", 8)
        lines = _wrap(body, int(col_w / (0.22*cm)))
        for j, line in enumerate(lines[:3]):
            c.drawString(x + 0.3*cm, y - 0.9*cm - j * 0.38*cm, line)


def slide_7_demo(c: Canvas) -> None:
    _header_bar(c, "Demo: Three Test Scenarios",
                "Mock CRPF tender with 5 criteria evaluated against 3 realistic bidders")
    _footer(c, 7)

    scenarios = [
        (GREEN, "✅ Bidder A — Eligible",
         "Apex Constructions Pvt. Ltd.",
         [
             "C1 Turnover: INR 6.37 Cr avg — exceeds 5 Cr threshold",
             "C2 Projects: 5 completed including CRPF barracks (2024)",
             "C3 GST: GSTIN 27AABCA1234F1Z5, Active",
             "C4 ISO 9001:2015: Valid through June 2027",
             "C5 Paramilitary: CRPF Camp Pune project on record",
         ]),
        (RED, "❌ Bidder B — Not Eligible",
         "BuildRight Enterprises",
         [
             "C1 Turnover: INR 1.5 Cr avg — BELOW 5 Cr threshold",
             "C2 Projects: 4 completed — passes",
             "C3 GST: GSTIN 29AABCB5678G1Z3, Active",
             "C4 ISO 9001:2015: Valid through August 2027",
             "C5 Paramilitary: No relevant experience",
         ]),
        (AMBER, "⚠️ Bidder C — Needs Review",
         "Shree Constructions & Services",
         [
             "C1 Turnover: Scanned cert → Tesseract 55% → Vision LLM",
             "    INR 5.4 Cr found, but borderline — human review required",
             "C2 Projects: Exactly 3 — borderline meets threshold",
             "C3 GST: GSTIN 24AABCC9012H1Z1, Active",
             "C4 ISO 9001:2015: Valid through September 2027",
         ]),
    ]
    cw = (W - 4.0*cm) / 3
    for i, (color, title, company, bullets) in enumerate(scenarios):
        x = 1.8*cm + i * (cw + 0.3*cm)
        y_top = H - 3.8*cm

        c.setFillColor(color)
        c.roundRect(x, y_top - 0.9*cm, cw, 0.9*cm, 0.25*cm, fill=1, stroke=0)
        c.setFillColor(WHITE)
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(x + cw / 2, y_top - 0.55*cm, title)

        c.setFillColor(WHITE)
        c.setStrokeColor(BORD)
        c.roundRect(x, y_top - 8.5*cm, cw, 7.6*cm, 0.25*cm, fill=1, stroke=1)
        c.rect(x, y_top - 0.9*cm, cw, 0.2*cm, fill=1, stroke=0)

        c.setFillColor(GREY)
        c.setFont("Helvetica-Oblique", 8)
        c.drawString(x + 0.3*cm, y_top - 1.35*cm, company)

        c.setFont("Helvetica", 8)
        c.setFillColor(NAVY)
        for j, b in enumerate(bullets):
            c.drawString(x + 0.3*cm, y_top - 2.0*cm - j * 0.5*cm, b)


def slide_8_stack(c: Canvas) -> None:
    _header_bar(c, "Technology Stack & Impact",
                "Built for the hackathon — deployable to Streamlit Cloud or HuggingFace Spaces in minutes")
    _footer(c, 8)

    stack = [
        ("UI & Orchestration", "Streamlit 1.39", "Single-process app, tabs, session state"),
        ("LLM",               "DeepSeek API",   "chat_json + chat_vision (OpenAI-compatible)"),
        ("OCR Tier 1",        "PyMuPDF 1.24",   "Lossless text extraction from digital PDFs"),
        ("OCR Tier 2",        "Tesseract",      "Open-source OCR for scanned documents"),
        ("OCR Tier 3",        "DeepSeek Vision","Multimodal LLM for low-confidence scans"),
        ("Vector Store",      "ChromaDB 0.5",   "Embedded, file-backed, all-MiniLM-L6-v2"),
        ("Schemas",           "Pydantic v2",    "Strict validation of all LLM outputs"),
        ("Audit Log",         "SQLite",         "Append-only, exportable as CSV"),
    ]
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 9)
    col_x = [1.8*cm, 6.5*cm, 11.5*cm]
    for x, lbl in zip(col_x, ["Component", "Technology", "Role"]):
        c.drawString(x, H - 4.2*cm, lbl)
    c.setStrokeColor(BORD)
    c.line(1.8*cm, H - 4.4*cm, W - 1.8*cm, H - 4.4*cm)

    for i, (comp, tech, role) in enumerate(stack):
        y = H - 4.9*cm - i * 0.6*cm
        if i % 2 == 0:
            c.setFillColor(LGREY)
            c.rect(1.8*cm, y - 0.1*cm, W - 3.6*cm, 0.55*cm, fill=1, stroke=0)
        c.setFillColor(NAVY);  c.setFont("Helvetica-Bold", 8.5); c.drawString(1.8*cm + 0.2*cm, y + 0.2*cm, comp)
        c.setFillColor(BLUE);  c.setFont("Helvetica", 8.5);      c.drawString(6.5*cm + 0.2*cm, y + 0.2*cm, tech)
        c.setFillColor(GREY);  c.setFont("Helvetica", 8.5);      c.drawString(11.5*cm + 0.2*cm, y + 0.2*cm, role)

    y_impact = H - 10.5*cm
    c.setFillColor(NAVY)
    c.roundRect(1.8*cm, y_impact - 2.8*cm, W - 3.6*cm, 2.8*cm, 0.3*cm, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 11)
    c.drawCentredString(W / 2, y_impact - 0.7*cm, "Business Impact")
    impacts = [
        "⏱  Days of manual evaluation → minutes of automated processing",
        "📋  Criterion-level audit trail satisfies RTI and compliance requirements",
        "🔍  Every verdict traceable to a document, page, OCR tier, and model version",
    ]
    c.setFont("Helvetica", 9.5)
    c.setFillColor(colors.HexColor("#CBD5E1"))
    for j, imp in enumerate(impacts):
        c.drawString(2.5*cm, y_impact - 1.35*cm - j * 0.5*cm, imp)


def main() -> None:
    out = BASE_DIR / "deck" / "TenderIQ_Pitch.pdf"
    out.parent.mkdir(parents=True, exist_ok=True)

    c = Canvas(str(out), pagesize=A4)
    slides = [
        slide_1_title,
        slide_2_problem,
        slide_3_solution,
        slide_4_architecture,
        slide_5_ocr,
        slide_6_explainability,
        slide_7_demo,
        slide_8_stack,
    ]
    for fn in slides:
        fn(c)
        c.showPage()
    c.save()
    print(f"Deck saved: {out}  ({len(slides)} slides)")


if __name__ == "__main__":
    main()
