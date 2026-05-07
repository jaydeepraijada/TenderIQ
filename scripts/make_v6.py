#!/usr/bin/env python3
"""TenderIQ v6 — Infographic (PDF via reportlab)"""
import os
import math
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle

W, H = landscape(A4)

# Palette
C_BG   = colors.white
C_STR  = colors.HexColor("#F8FAFC")
C_BLU  = colors.HexColor("#2563EB")
C_GRN  = colors.HexColor("#22C55E")
C_RED  = colors.HexColor("#EF4444")
C_AMB  = colors.HexColor("#F59E0B")
C_PUR  = colors.HexColor("#8B5CF6")
C_TXT  = colors.HexColor("#0F172A")
C_SUB  = colors.HexColor("#64748B")
C_DIV  = colors.HexColor("#E2E8F0")

M = 1.8 * cm


def para(c, text, x, y, width, font="Helvetica", size=12, color=C_TXT, leading=16, align="left"):
    style = ParagraphStyle(
        'p', fontName=font, fontSize=size, leading=leading, textColor=color,
        alignment={"left": 0, "center": 1, "right": 2}.get(align, 0))
    p = Paragraph(text.replace("\n", "<br/>"), style)
    _, used = p.wrapOn(c, width, 1000)
    p.drawOn(c, x, y - used)
    return used


def circ_progress(c, cx, cy, r, pct, fg, bg=C_DIV, thickness=8):
    """Draw a circular progress arc."""
    c.setStrokeColor(bg)
    c.setLineWidth(thickness)
    c.circle(cx, cy, r, fill=0, stroke=1)
    c.setStrokeColor(fg)
    c.setLineWidth(thickness)
    extent = 360 * pct
    c.arc(cx - r, cy - r, cx + r, cy + r, startAng=90, extent=-extent)
    c.setFillColor(fg)
    c.setFont("Helvetica-Bold", int(r * 0.5))
    c.drawCentredString(cx, cy - r * 0.18, f"{int(pct * 100)}%")


def header_strip(c, title, n):
    c.setFillColor(C_STR)
    c.rect(0, H - 1.3 * cm, W, 1.3 * cm, fill=1, stroke=0)
    c.setStrokeColor(C_BLU)
    c.setLineWidth(2)
    c.line(0, H - 1.3 * cm, W, H - 1.3 * cm)
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(C_BLU)
    c.drawString(M, H - 1.0 * cm, title)
    c.setFont("Helvetica", 10)
    c.setFillColor(C_SUB)
    c.drawRightString(W - M, H - 1.0 * cm, f"TenderIQ  ·  CRPF Hackathon  ·  {n} / 8")


def footer_line(c):
    c.setStrokeColor(C_DIV)
    c.setLineWidth(0.5)
    c.line(M, 0.9 * cm, W - M, 0.9 * cm)


def big_num(c, val, label, cx, cy, color=C_BLU):
    c.setFont("Helvetica-Bold", 52)
    c.setFillColor(color)
    c.drawCentredString(cx, cy, val)
    c.setFont("Helvetica", 11)
    c.setFillColor(C_SUB)
    # All-caps label
    for i, line in enumerate(label.split("\n")):
        c.drawCentredString(cx, cy - 1.3 * cm - i * 0.45 * cm, line.upper())


def icon_label(c, icon, label, cx, cy, color=C_BLU, icon_sz=36, lbl_sz=11):
    c.setFont("Helvetica-Bold", icon_sz)
    c.setFillColor(color)
    c.drawCentredString(cx, cy, icon)
    c.setFont("Helvetica", lbl_sz)
    c.setFillColor(C_TXT)
    c.drawCentredString(cx, cy - 1.2 * cm, label)


def stage_row(c, icon, title, desc, y, color=C_BLU):
    # Icon circle
    c.setFillColor(color)
    c.circle(M + 0.9 * cm, y + 0.45 * cm, 0.45 * cm, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.white)
    c.drawCentredString(M + 0.9 * cm, y + 0.3 * cm, icon)
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(color)
    c.drawString(M + 1.8 * cm, y + 0.55 * cm, title)
    c.setFont("Helvetica", 11)
    c.setFillColor(C_TXT)
    c.drawString(M + 1.8 * cm, y + 0.18 * cm, desc)


# ── Slide 1 ─────────────────────────────────────────────────────────────────
def s1(c):
    c.setFillColor(C_BG)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    # Left accent bar
    c.setFillColor(C_BLU)
    c.rect(0, 0, 0.6 * cm, H, fill=1, stroke=0)
    # Large icon
    c.setFont("Helvetica-Bold", 80)
    c.setFillColor(C_BLU)
    c.drawCentredString(W / 2, H / 2 + 2.2 * cm, "TenderIQ")
    # Divider
    c.setStrokeColor(C_DIV)
    c.setLineWidth(1.5)
    c.line(W / 2 - 6 * cm, H / 2 + 1.3 * cm, W / 2 + 6 * cm, H / 2 + 1.3 * cm)
    c.setFont("Helvetica", 20)
    c.setFillColor(C_TXT)
    c.drawCentredString(W / 2, H / 2 + 0.55 * cm,
                        "Explainable AI for Government Tender Evaluation")
    c.setFont("Helvetica", 13)
    c.setFillColor(C_SUB)
    c.drawCentredString(W / 2, H / 2 - 0.4 * cm, "CRPF HACKATHON  ·  THEME 3")
    c.setFont("Helvetica-Oblique", 13)
    c.setFillColor(C_BLU)
    c.drawCentredString(W / 2, H / 2 - 1.3 * cm,
                        "From days to minutes. Every decision traceable.")
    footer_line(c)
    c.showPage()


# ── Slide 2 ─────────────────────────────────────────────────────────────────
def s2(c):
    c.setFillColor(C_BG)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    header_strip(c, "The Problem with Manual Tender Evaluation", 2)
    cy = H * 0.5
    third = (W - 2 * M) / 3
    callouts = [
        ("3–5", "days per tender\nevaluation", C_RED),
        ("≠", "inconsistent verdicts\nfrom evaluators", C_AMB),
        ("?", "no audit trail\nfor decisions", C_PUR),
    ]
    for i, (val, lbl, col) in enumerate(callouts):
        cx = M + i * third + third / 2
        big_num(c, val, lbl, cx, cy, col)
    # Divider
    c.setStrokeColor(C_DIV)
    c.setLineWidth(1)
    c.line(M, cy - 2.2 * cm, W - M, cy - 2.2 * cm)
    bullets = [
        "• Mixed document formats: typed PDFs, scanned certificates, phone photographs",
        "• Government procurement worth ₹50 lakh crore+ annually in India",
        "• Project execution delays traced directly to procurement bottlenecks",
    ]
    c.setFont("Helvetica", 12)
    c.setFillColor(C_SUB)
    for i, b in enumerate(bullets):
        c.drawString(M, cy - 2.8 * cm - i * 0.55 * cm, b)
    footer_line(c)
    c.showPage()


# ── Slide 3 ─────────────────────────────────────────────────────────────────
def s3(c):
    c.setFillColor(C_BG)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    header_strip(c, "TenderIQ — Four Stages, End to End", 3)
    # Four icons in a row with arrows
    icons = ["PDF", "OCR", "EVAL", "LOG"]
    labels = ["Extract", "OCR & Index", "Evaluate", "Review & Audit"]
    descs = [
        "DeepSeek LLM reads tender PDF\n→ structured JSON criteria",
        "3-tier pipeline handles any\ndoc format → vector index",
        "Vector search + LLM verdict\n+ safety rule",
        "Human review queue\n+ full audit trail (CSV)",
    ]
    colors_ = [C_BLU, C_PUR, C_GRN, C_AMB]
    step = (W - 2 * M) / 4
    cy = H * 0.52
    for i, (ico, lbl, desc, col) in enumerate(zip(icons, labels, descs, colors_)):
        cx = M + i * step + step / 2
        # Icon circle
        c.setFillColor(col)
        c.circle(cx, cy + 1.0 * cm, 0.9 * cm, fill=1, stroke=0)
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(colors.white)
        c.drawCentredString(cx, cy + 0.88 * cm, ico)
        c.setFont("Helvetica-Bold", 14)
        c.setFillColor(col)
        c.drawCentredString(cx, cy - 0.25 * cm, lbl)
        c.setFont("Helvetica", 11)
        c.setFillColor(C_TXT)
        for j, dl in enumerate(desc.split("\n")):
            c.drawCentredString(cx, cy - 0.82 * cm - j * 0.45 * cm, dl)
        if i < 3:
            c.setFont("Helvetica-Bold", 18)
            c.setFillColor(C_SUB)
            c.drawCentredString(M + (i + 1) * step, cy + 0.9 * cm, "→")

    # Callout
    by = H * 0.19
    c.setFillColor(C_STR)
    c.setStrokeColor(C_BLU)
    c.setLineWidth(1.5)
    c.roundRect(M, by, W - 2 * M, 1.1 * cm, 4, fill=1, stroke=1)
    c.setFont("Helvetica-BoldOblique", 13)
    c.setFillColor(C_BLU)
    c.drawCentredString(W / 2, by + 0.38 * cm,
                        '"Minutes, not days. Every verdict traceable to a document and page."')
    footer_line(c)
    c.showPage()


# ── Slide 4 ─────────────────────────────────────────────────────────────────
def s4(c):
    c.setFillColor(C_BG)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    header_strip(c, "System Architecture", 4)
    # Vertical flow infographic
    stages = [
        ("PDF", "Tender PDF + Bidder Documents (PDFs · scans · photos)", C_BLU),
        ("LLM", "DeepSeek LLM — Extract Criteria  |  3-Tier OCR → Vector Index", C_PUR),
        ("EVAL", "DeepSeek LLM — Evaluate each criterion with combined confidence", C_GRN),
        ("AUD", "eligible / not_eligible  |  needs_review → Human Review Queue", C_AMB),
        ("DB", "SQLite Audit Log — every action with timestamp + payload", C_BLU),
    ]
    top_y = H - 2.2 * cm
    row_h = 1.2 * cm
    for i, (ico, desc, col) in enumerate(stages):
        y = top_y - i * row_h
        stage_row(c, ico, "", desc, y - 0.1 * cm, col)
        if i < len(stages) - 1:
            # Connector
            c.setStrokeColor(C_DIV)
            c.setLineWidth(1.5)
            c.line(M + 0.9 * cm, y - 0.1 * cm, M + 0.9 * cm, y - row_h + 0.5 * cm)

    # Key facts side panel
    fx = W / 2 + 1 * cm
    c.setFillColor(C_STR)
    c.setStrokeColor(C_DIV)
    c.setLineWidth(1)
    c.roundRect(fx, H * 0.2, W - M - fx, H * 0.6, 5, fill=1, stroke=1)
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(C_BLU)
    c.drawString(fx + 0.4 * cm, H * 0.76, "Key Technical Facts")
    facts = [
        "Single-process Streamlit app",
        "Streamlit Cloud / HuggingFace deployment",
        "Local storage: SQLite + vector index",
        "Only external dep: DeepSeek API",
    ]
    c.setFont("Helvetica", 11)
    c.setFillColor(C_TXT)
    for i, f in enumerate(facts):
        c.drawString(fx + 0.4 * cm, H * 0.68 - i * 0.65 * cm, f"• {f}")
    footer_line(c)
    c.showPage()


# ── Slide 5 ─────────────────────────────────────────────────────────────────
def s5(c):
    c.setFillColor(C_BG)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    header_strip(c, "Three-Tier OCR — Handling Any Document Format", 5)
    tiers = [
        ("Tier 1\nPyMuPDF", "Typed PDF → Free, instant", 1.0, C_BLU),
        ("Tier 2\nTesseract", "Scan / image → Free, local", 0.60, C_PUR),
        ("Tier 3\nVision LLM", "Low confidence → API call", 0.95, C_AMB),
    ]
    step = (W - 2 * M) / 3
    cy = H * 0.55
    for i, (tier, desc, pct, col) in enumerate(tiers):
        cx = M + i * step + step / 2
        # Circular progress
        circ_progress(c, cx, cy + 0.5 * cm, 1.3 * cm, pct, col)
        # Tier label
        c.setFont("Helvetica-Bold", 13)
        c.setFillColor(col)
        for li, ln in enumerate(tier.split("\n")):
            c.drawCentredString(cx, cy - 1.35 * cm - li * 0.45 * cm, ln)
        c.setFont("Helvetica", 11)
        c.setFillColor(C_TXT)
        c.drawCentredString(cx, cy - 2.55 * cm, desc)
        if i < 2:
            c.setFont("Helvetica-Bold", 18)
            c.setFillColor(C_SUB)
            c.drawCentredString(M + (i + 1) * step, cy + 0.5 * cm, "→")

    # Demo callout
    dy = H * 0.19
    c.setFillColor(C_STR)
    c.setStrokeColor(C_AMB)
    c.setLineWidth(2)
    c.roundRect(M, dy, W - 2 * M, 2.2 * cm, 4, fill=1, stroke=1)
    c.setFont("Helvetica-Bold", 12)
    c.setFillColor(C_AMB)
    c.drawString(M + 0.5 * cm, dy + 1.78 * cm, "Demo Scenario")
    c.setFont("Helvetica", 11)
    c.setFillColor(C_TXT)
    demo = ("Bidder C submits a blurry, rotated CA certificate scan.  "
            "Tesseract reads it at ~55% confidence.  Vision LLM transcribes the turnover correctly.  "
            "Combined confidence = 0.58 → routed to human review.  "
            "Borderline evidence requires a human — this is intentional.")
    para(c, demo, M + 0.5 * cm, dy + 1.55 * cm, W - 2 * M - 1 * cm, size=11, color=C_TXT, leading=16)
    footer_line(c)
    c.showPage()


# ── Slide 6 ─────────────────────────────────────────────────────────────────
def s6(c):
    c.setFillColor(C_BG)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    header_strip(c, "Every Decision is Explainable and Auditable", 6)

    half = (W - 2 * M - 0.8 * cm) / 2
    lx = M
    rx = M + half + 0.8 * cm
    top = H - 2.0 * cm
    panel_h = 4.2 * cm

    for px, title, lines, col in [
        (lx, "Criterion-Level Verdicts", [
            "Each (bidder × criterion) pair shows:",
            "• Which criterion was checked",
            "• Document and page providing evidence",
            "• Value extracted (e.g. 'INR 6.2 Cr')",
            "• OCR tier that read the document",
            "• Combined confidence score (0–100%)",
            "• Plain-English reason",
        ], C_BLU),
        (rx, "Audit Trail", [
            "Every action logged with:",
            "• UTC timestamp",
            "• Action type (6 types incl. criteria_extracted,",
            "  vision_ocr_invoked, precomputed_fallback_used)",
            "• Model version & Actor",
            "• Full payload JSON",
            "• Exportable as CSV",
        ], C_BLU),
    ]:
        c.setFillColor(C_STR)
        c.setStrokeColor(col)
        c.setLineWidth(1.5)
        c.roundRect(px, top - panel_h, half, panel_h, 4, fill=1, stroke=1)
        c.setFont("Helvetica-Bold", 13)
        c.setFillColor(col)
        c.drawString(px + 0.4 * cm, top - 0.5 * cm, title)
        c.setFont("Helvetica", 11)
        c.setFillColor(C_TXT)
        for i, ln in enumerate(lines):
            c.setFillColor(C_SUB if i == 0 else C_TXT)
            c.drawString(px + 0.4 * cm, top - 1.0 * cm - i * 0.45 * cm, ln)

    # Safety rule
    sy = top - panel_h - 0.5 * cm - 1.9 * cm
    c.setFillColor(colors.HexColor("#FFFBEB"))
    c.setStrokeColor(C_AMB)
    c.setLineWidth(2.5)
    c.roundRect(M, sy, W - 2 * M, 1.9 * cm, 4, fill=1, stroke=1)
    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(colors.HexColor("#92400E"))
    c.drawString(M + 0.5 * cm, sy + 1.52 * cm, "The Safety Rule:")
    c.setFont("Helvetica", 12)
    c.setFillColor(C_TXT)
    rule = ("If combined confidence is 0.55–0.80 AND verdict is not_eligible, "
            "the verdict is automatically downgraded to needs_review.  "
            "A bidder is NEVER silently disqualified at medium confidence.")
    para(c, rule, M + 0.5 * cm, sy + 1.3 * cm, W - 2 * M - 1 * cm, size=12, color=C_TXT, leading=16)
    footer_line(c)
    c.showPage()


# ── Slide 7 ─────────────────────────────────────────────────────────────────
def s7(c):
    c.setFillColor(C_BG)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    header_strip(c, "Demo: Three Bidders, Three Outcomes", 7)

    bidders = [
        ("ELIGIBLE", C_GRN, colors.HexColor("#D1FAE5"),
         "Bidder A\nApex Constructions Pvt. Ltd.",
         ["C1 Turnover: INR 6.37 Cr avg — PASS",
          "C2 Projects: 5 completed (CRPF) — PASS",
          "C3 GST: Active GSTIN — PASS",
          "C4 ISO 9001:2015: Valid June 2027 — PASS",
          "All typed PDFs, confidence ≥ 93%"]),
        ("NOT ELIGIBLE", C_RED, colors.HexColor("#FEE2E2"),
         "Bidder B\nBuildRight Enterprises",
         ["C1 Turnover: INR 1.5 Cr avg — FAIL",
          "Below required minimum of INR 5 Cr",
          "C2–C4: All pass",
          "Auto-disqualified, conf 95%"]),
        ("NEEDS REVIEW", C_AMB, colors.HexColor("#FEF3C7"),
         "Bidder C\nShree Constructions & Services",
         ["C1: Blurry scan → Vision LLM",
          "INR 5.4 Cr, combined conf 0.58",
          "Safety rule → needs_review",
          "C2: 3 projects (borderline)",
          "C3–C4: Pass"]),
    ]
    step = (W - 2 * M - 2 * cm) / 3
    top = H - 2.0 * cm
    panel_h = 4.3 * cm
    for i, (verdict, col, bgc, name, bullets) in enumerate(bidders):
        cx = M + i * (step + 1 * cm)
        c.setFillColor(bgc)
        c.setStrokeColor(col)
        c.setLineWidth(2)
        c.roundRect(cx, top - panel_h, step, panel_h, 5, fill=1, stroke=1)
        # Outcome icon text
        c.setFont("Helvetica-Bold", 24)
        c.setFillColor(col)
        c.drawCentredString(cx + step / 2, top - 0.6 * cm, verdict)
        # Divider
        c.setStrokeColor(col)
        c.setLineWidth(1)
        c.line(cx + 0.3 * cm, top - 0.9 * cm, cx + step - 0.3 * cm, top - 0.9 * cm)
        # Name
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(C_TXT)
        for li, nl in enumerate(name.split("\n")):
            c.drawCentredString(cx + step / 2, top - 1.3 * cm - li * 0.38 * cm, nl)
        # Bullets
        c.setFont("Helvetica", 11)
        c.setFillColor(C_TXT)
        for j, b in enumerate(bullets):
            c.drawString(cx + 0.3 * cm, top - 2.2 * cm - j * 0.42 * cm, b)

    # Metric strip
    metrics = [("5", "Criteria\nextracted"), ("15", "Bidder docs\nprocessed"),
               ("15", "LLM eval\ncalls"), ("1", "Vision OCR\ninvocations"),
               ("1", "Human review\nitems"), ("20+", "Audit\nentries")]
    sy = H * 0.16
    c.setFillColor(C_STR)
    c.setStrokeColor(C_DIV)
    c.setLineWidth(1)
    c.roundRect(M, sy, W - 2 * M, 1.5 * cm, 4, fill=1, stroke=1)
    mstep = (W - 2 * M) / len(metrics)
    for i, (val, lbl) in enumerate(metrics):
        mx = M + i * mstep + mstep / 2
        c.setFont("Helvetica-Bold", 20)
        c.setFillColor(C_BLU)
        c.drawCentredString(mx, sy + 0.9 * cm, val)
        c.setFont("Helvetica", 9)
        c.setFillColor(C_SUB)
        for li, ln in enumerate(lbl.split("\n")):
            c.drawCentredString(mx, sy + 0.42 * cm - li * 0.28 * cm, ln.upper())
    footer_line(c)
    c.showPage()


# ── Slide 8 ─────────────────────────────────────────────────────────────────
def s8(c):
    c.setFillColor(C_BG)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    header_strip(c, "Stack, Impact & What's Next", 8)

    # Icon grid for future work (6 items, 3×2)
    future = [
        ("MULTI", "Multi-tender workspace\nsame bidder pool, multiple tenders"),
        ("GEM", "GeM portal API integration\nlive tender ingestion"),
        ("RANK", "Automated bidder ranking\nwith weighted scoring"),
        ("LLM+", "LayoutLM for complex\nfinancial tables in scans"),
        ("TEAM", "Multi-evaluator workflow\nwith role-based approval"),
        ("AUDIT", "Audit PDF export for\nprocurement oversight"),
    ]
    colors_f = [C_BLU, C_GRN, C_PUR, C_AMB, C_RED, C_BLU]
    gw = (W / 2 - M - 1 * cm) / 3
    gh = 1.8 * cm
    for i, ((ico, desc), col) in enumerate(zip(future, colors_f)):
        row = i // 3
        col_i = i % 3
        gx = M + col_i * (gw + 0.4 * cm)
        gy = H - 2.4 * cm - row * (gh + 0.5 * cm)
        c.setFillColor(C_STR)
        c.setStrokeColor(col)
        c.setLineWidth(1)
        c.roundRect(gx, gy - gh, gw, gh, 3, fill=1, stroke=1)
        c.setFont("Helvetica-Bold", 9)
        c.setFillColor(col)
        c.drawString(gx + 0.25 * cm, gy - 0.5 * cm, ico)
        c.setFont("Helvetica", 10)
        c.setFillColor(C_TXT)
        for li, ln in enumerate(desc.split("\n")):
            c.drawString(gx + 0.25 * cm, gy - 0.95 * cm - li * 0.38 * cm, ln)

    # Tech stack (right half)
    stack = [
        ("UI / Orchestration", "Streamlit 1.39"),
        ("LLM", "DeepSeek API"),
        ("OCR Tiers", "PyMuPDF · Tesseract · Vision LLM"),
        ("Retrieval", "all-MiniLM-L6-v2"),
        ("Validation", "Pydantic v2"),
        ("Audit", "SQLite — Exportable CSV"),
        ("Deploy", "Streamlit Cloud / HuggingFace"),
    ]
    sx = W / 2 + 0.5 * cm
    sw = W - M - sx
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(C_BLU)
    c.drawString(sx, H - 2.1 * cm, "Technology Stack")
    for i, (comp, tech) in enumerate(stack):
        ry = H - 2.75 * cm - i * 0.55 * cm
        c.setFillColor(C_STR if i % 2 == 0 else C_BG)
        c.rect(sx, ry - 0.38 * cm, sw, 0.5 * cm, fill=1, stroke=0)
        c.setFont("Helvetica", 10)
        c.setFillColor(C_SUB)
        c.drawString(sx + 0.2 * cm, ry, comp)
        c.setFillColor(C_TXT)
        c.drawString(sx + sw * 0.42, ry, tech)

    # Impact callout
    iy = H * 0.15
    c.setFillColor(C_BLU)
    c.roundRect(M, iy, W - 2 * M, 1.3 * cm, 5, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(colors.white)
    c.drawCentredString(W / 2, iy + 0.82 * cm,
                        "3–5 days → minutes.  Every verdict traceable to a document, page, and model version.")
    c.setFont("Helvetica", 11)
    c.drawCentredString(W / 2, iy + 0.38 * cm,
                        "Built in one hackathon session. Deployable today.")
    footer_line(c)
    c.showPage()


def main():
    os.makedirs("deck", exist_ok=True)
    out = "deck/TenderIQ_v6_infographic.pdf"
    c = Canvas(out, pagesize=landscape(A4))
    s1(c); s2(c); s3(c); s4(c)
    s5(c); s6(c); s7(c); s8(c)
    c.save()
    size = os.path.getsize(out)
    print(f"OK: Saved {out}  ({size:,} bytes, 8 slides)")


if __name__ == "__main__":
    main()
