#!/usr/bin/env python3
"""TenderIQ v4 — Modern Gradient (PDF via reportlab)"""
import os
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import cm, mm
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle

W, H = landscape(A4)   # 841.89 × 595.28 points

# Palette
C_PUR1  = colors.HexColor("#667EEA")
C_PUR2  = colors.HexColor("#764BA2")
C_BLU1  = colors.HexColor("#0EA5E9")
C_BLU2  = colors.HexColor("#2563EB")
C_DARK  = colors.HexColor("#0F172A")
C_WHITE = colors.white
C_GRY   = colors.HexColor("#64748B")
C_GRY2  = colors.HexColor("#E2E8F0")
C_GRN   = colors.HexColor("#10B981")
C_RED   = colors.HexColor("#F43F5E")
C_AMB   = colors.HexColor("#FBBF24")
C_CARD  = colors.HexColor("#FFFFFF")

M = 1.8 * cm   # margin


def grad_rect(c, x, y, w, h, col1, col2, steps=40):
    """Approximate horizontal gradient with filled rects."""
    sw = w / steps
    from reportlab.lib.colors import Color
    r1, g1, b1 = col1.red, col1.green, col1.blue
    r2, g2, b2 = col2.red, col2.green, col2.blue
    for i in range(steps):
        t = i / (steps - 1)
        r = r1 + t * (r2 - r1)
        g = g1 + t * (g2 - g1)
        b = b1 + t * (b2 - b1)
        c.setFillColor(Color(r, g, b))
        c.rect(x + i * sw, y, sw + 1, h, fill=1, stroke=0)


def page_num(c, n):
    c.setFont("Helvetica", 9)
    c.setFillColor(C_GRY)
    c.drawRightString(W - M, 0.8 * cm, str(n))


def header_band(c, title, n):
    """Gradient header band for content slides."""
    bh = H * 0.18
    grad_rect(c, 0, H - bh, W, bh, C_BLU1, C_BLU2)
    c.setFillColor(C_WHITE)
    c.setFont("Helvetica-Bold", 22)
    c.drawString(M, H - bh + 0.55 * cm, title)
    page_num(c, n)


def card(c, x, y, w, h, accent=None):
    """White card with optional top accent border."""
    c.setFillColor(C_CARD)
    c.setStrokeColor(C_GRY2)
    c.setLineWidth(0.5)
    c.roundRect(x, y, w, h, 4, fill=1, stroke=1)
    if accent:
        c.setFillColor(accent)
        c.setStrokeColor(accent)
        c.roundRect(x, y + h - 4, w, 4, 2, fill=1, stroke=0)


def wrapped(c, text, x, y, width, font="Helvetica", size=12, color=C_DARK, leading=16):
    style = ParagraphStyle('s', fontName=font, fontSize=size, leading=leading,
                           textColor=color)
    p = Paragraph(text.replace("\n", "<br/>"), style)
    _, used = p.wrapOn(c, width, 999)
    p.drawOn(c, x, y - used)
    return used


def label(c, text, x, y, sz=10, font="Helvetica", color=C_GRY, align="left"):
    c.setFont(font, sz)
    c.setFillColor(color)
    if align == "center":
        c.drawCentredString(x, y, text)
    elif align == "right":
        c.drawRightString(x, y, text)
    else:
        c.drawString(x, y, text)


# ── Slide 1 ─────────────────────────────────────────────────────────────────
def s1(c):
    grad_rect(c, 0, 0, W, H, C_PUR1, C_PUR2)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 72)
    c.drawCentredString(W / 2, H / 2 + 1.5 * cm, "TenderIQ")
    c.setFont("Helvetica", 22)
    c.drawCentredString(W / 2, H / 2 - 0.5 * cm,
                        "Explainable AI for Government Tender Evaluation")
    c.setFont("Helvetica", 14)
    c.setFillColor(colors.HexColor("#DDD6FE"))
    c.drawCentredString(W / 2, H / 2 - 1.6 * cm, "CRPF Hackathon  ·  Theme 3")
    # divider
    c.setStrokeColor(colors.HexColor("#A78BFA"))
    c.setLineWidth(1.5)
    c.line(W / 2 - 5 * cm, H / 2 - 2.2 * cm, W / 2 + 5 * cm, H / 2 - 2.2 * cm)
    c.setFont("Helvetica-Oblique", 13)
    c.setFillColor(colors.white)
    c.drawCentredString(W / 2, H / 2 - 3.0 * cm,
                        "From days to minutes. Every decision traceable.")
    page_num(c, 1)
    c.showPage()


# ── Slide 2 ─────────────────────────────────────────────────────────────────
def s2(c):
    c.setFillColor(colors.white)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    header_band(c, "The Problem with Manual Tender Evaluation", 2)

    callouts = [
        ("3–5", "Days per\ntender evaluation", C_PUR1),
        ("≠", "Inconsistent verdicts\nfrom evaluators", C_BLU2),
        ("0", "Zero audit trail\nfor decisions", C_GRN),
    ]
    bw = (W - 2 * M - 1.5 * cm) / 3
    top = H * 0.72
    for i, (big, sub, acc) in enumerate(callouts):
        bx = M + i * (bw + 0.75 * cm)
        by = top - 3.8 * cm
        card(c, bx, by, bw, 3.8 * cm, acc)
        c.setFont("Helvetica-Bold", 52)
        c.setFillColor(acc)
        c.drawCentredString(bx + bw / 2, by + 2.4 * cm, big)
        c.setFont("Helvetica", 12)
        c.setFillColor(C_DARK)
        lines = sub.split("\n")
        for li, line in enumerate(lines):
            c.drawCentredString(bx + bw / 2, by + 1.4 * cm - li * 0.45 * cm, line)

    bullets = [
        "• Mixed document formats: typed PDFs, scanned certificates, phone photographs",
        "• Government procurement worth ₹50 lakh crore+ annually in India",
        "• Project execution delays traced directly to procurement bottlenecks",
    ]
    by2 = top - 5.5 * cm
    c.setFont("Helvetica", 12)
    c.setFillColor(C_GRY)
    for i, b in enumerate(bullets):
        c.drawString(M, by2 - i * 0.55 * cm, b)
    page_num(c, 2)
    c.showPage()


# ── Slide 3 ─────────────────────────────────────────────────────────────────
def s3(c):
    c.setFillColor(colors.white)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    header_band(c, "TenderIQ — Four Stages, End to End", 3)

    stages = [
        ("1 — Extract",
         "DeepSeek LLM reads the tender PDF and returns each criterion as structured JSON: "
         "category, mandatory flag, threshold rule, source clause, query hints.",
         C_PUR1),
        ("2 — OCR & Index",
         "Three-tier pipeline handles any document format. All text chunked and indexed "
         "for semantic retrieval.",
         C_BLU2),
        ("3 — Evaluate",
         "Vector search finds relevant evidence. LLM produces a verdict with confidence. "
         "Safety rule prevents silent disqualification.",
         C_GRN),
        ("4 — Review & Audit",
         "Borderline cases go to human review queue. Every action logged. "
         "Full audit trail exportable as CSV.",
         C_AMB),
    ]
    cw = (W - 2 * M - 1.5 * cm) / 4
    top = H * 0.77
    for i, (title, body, acc) in enumerate(stages):
        cx = M + i * (cw + 0.5 * cm)
        cy = top - 3.5 * cm
        card(c, cx, cy, cw, 3.5 * cm, acc)
        c.setFont("Helvetica-Bold", 13)
        c.setFillColor(acc)
        c.drawString(cx + 0.3 * cm, cy + 3.0 * cm, title)
        wrapped(c, body, cx + 0.3 * cm, cy + 2.8 * cm, cw - 0.6 * cm, size=11, color=C_DARK, leading=15)

    # Callout
    by = top - 5.2 * cm
    grad_rect(c, M, by, W - 2 * M, 1.2 * cm, C_BLU1, C_BLU2)
    c.setFillColor(C_WHITE)
    c.setFont("Helvetica-BoldOblique", 13)
    c.drawCentredString(W / 2, by + 0.38 * cm,
                        '"Minutes, not days. Every verdict traceable to a document and page."')
    page_num(c, 3)
    c.showPage()


# ── Slide 4 ─────────────────────────────────────────────────────────────────
def s4(c):
    c.setFillColor(colors.white)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    header_band(c, "System Architecture", 4)

    bw, bh = 5.5 * cm, 1.1 * cm
    top = H * 0.74

    def abox(x, y, text, acc=C_BLU2):
        card(c, x, y, bw, bh, acc)
        c.setFont("Helvetica", 10)
        c.setFillColor(C_DARK)
        lines = text.split("\n")
        for li, ln in enumerate(lines):
            c.drawCentredString(x + bw / 2, y + bh - 0.4 * cm - li * 0.35 * cm, ln)

    def arr(x, y):
        c.setStrokeColor(C_BLU2)
        c.setLineWidth(1.5)
        c.line(x + bw / 2, y, x + bw / 2, y - 0.6 * cm)
        # arrowhead
        ax = x + bw / 2
        ay = y - 0.6 * cm
        c.setFillColor(C_BLU2)
        p = c.beginPath()
        p.moveTo(ax - 0.15 * cm, ay)
        p.lineTo(ax + 0.15 * cm, ay)
        p.lineTo(ax, ay - 0.25 * cm)
        p.close()
        c.drawPath(p, fill=1, stroke=0)

    step = 1.7 * cm
    lx = M
    abox(lx, top, "Tender PDF")
    arr(lx, top)
    abox(lx, top - step, "DeepSeek LLM\n(Extract Criteria)")
    arr(lx, top - step)
    abox(lx, top - 2 * step, "Criteria JSON\n(C1–C5 structured)")

    rx = M + 7 * cm
    abox(rx, top, "Bidder Docs\n(PDFs · scans · photos)")
    arr(rx, top)
    abox(rx, top - step, "3-Tier OCR Pipeline\n① PyMuPDF ② Tesseract ③ Vision LLM")
    arr(rx, top - step)
    abox(rx, top - 2 * step, "Vector Index\n(all-MiniLM-L6-v2 embeddings)")

    # Converge
    mid_y = top - 2 * step - bh
    mx = M + 3.5 * cm + bw / 2
    c.setStrokeColor(C_BLU2)
    c.setLineWidth(1.5)
    c.line(lx + bw / 2, mid_y, mx, mid_y - 0.6 * cm)
    c.line(rx + bw / 2, mid_y, mx, mid_y - 0.6 * cm)
    abox(M + 3.5 * cm, mid_y - 1.7 * cm, "DeepSeek LLM — Evaluate\neach criterion")

    eval_y = mid_y - 1.7 * cm
    arr(M + 3.5 * cm, eval_y)

    # Outputs
    out_y = eval_y - step
    c.setFillColor(colors.HexColor("#D1FAE5"))
    c.setStrokeColor(C_GRN)
    c.setLineWidth(1)
    c.roundRect(M + 1 * cm, out_y, 3.5 * cm, bh, 3, fill=1, stroke=1)
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(C_GRN)
    c.drawCentredString(M + 2.75 * cm, out_y + 0.38 * cm, "eligible / not_eligible")

    c.setFillColor(colors.HexColor("#FEF3C7"))
    c.setStrokeColor(C_AMB)
    c.roundRect(M + 5.5 * cm, out_y, 3.8 * cm, bh, 3, fill=1, stroke=1)
    c.setFont("Helvetica-Bold", 10)
    c.setFillColor(C_AMB)
    c.drawCentredString(M + 7.4 * cm, out_y + 0.38 * cm, "needs_review / Review Queue")

    # SQLite
    abox(M + 3.5 * cm, out_y - step, "SQLite Audit Log")

    # Key facts panel
    fx = W - M - 8.5 * cm
    c.setFillColor(colors.HexColor("#EFF6FF"))
    c.setStrokeColor(C_BLU2)
    c.setLineWidth(1)
    c.roundRect(fx, H * 0.18, 8.5 * cm, H * 0.56, 5, fill=1, stroke=1)
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(C_BLU2)
    c.drawString(fx + 0.4 * cm, H * 0.7, "Key Technical Facts")
    facts = [
        "Single-process Streamlit app",
        "Deployable: Streamlit Cloud / HuggingFace",
        "All storage local: SQLite + vector index",
        "Only external dep: DeepSeek API",
    ]
    c.setFont("Helvetica", 11)
    c.setFillColor(C_DARK)
    for i, f in enumerate(facts):
        c.drawString(fx + 0.4 * cm, H * 0.63 - i * 0.65 * cm, f"• {f}")

    page_num(c, 4)
    c.showPage()


# ── Slide 5 ─────────────────────────────────────────────────────────────────
def s5(c):
    c.setFillColor(colors.white)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    header_band(c, "Three-Tier OCR — Handling Any Document Format", 5)

    tiers = [
        ("Tier 1 — PyMuPDF",
         "Trigger: Typed / digital PDF\nCost: Free, instant\nConfidence: 1.0 (lossless)\nLabel: Typed PDF",
         C_BLU2),
        ("Tier 2 — Tesseract",
         "Trigger: Scanned PDF or image\nCost: Free, local, fast\nConfidence: Mean per-word OCR\nLabel: Tesseract",
         colors.HexColor("#7C3AED")),
        ("Tier 3 — DeepSeek Vision LLM",
         "Trigger: Tesseract confidence < 65%\nCost: One API call\nConfidence: 0.95\nLabel: Vision LLM\nLogged: vision_ocr_invoked",
         colors.HexColor("#EA580C")),
    ]
    cw = (W - 2 * M - 2 * cm) / 3
    top = H * 0.74
    for i, (title, body, acc) in enumerate(tiers):
        cx = M + i * (cw + 1 * cm)
        cy = top - 3.2 * cm
        card(c, cx, cy, cw, 3.2 * cm, acc)
        c.setFont("Helvetica-Bold", 13)
        c.setFillColor(acc)
        c.drawString(cx + 0.35 * cm, cy + 2.75 * cm, title)
        wrapped(c, body.replace("\n", "<br/>"), cx + 0.35 * cm, cy + 2.55 * cm,
                cw - 0.7 * cm, size=11, color=C_DARK, leading=15)

    # Demo callout
    by = H * 0.27
    grad_rect(c, M, by, W - 2 * M, 1.95 * cm, C_BLU1, C_BLU2, steps=30)
    c.setFillColor(C_WHITE)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(M + 0.4 * cm, by + 1.58 * cm, "Demo Scenario")
    c.setFont("Helvetica", 11)
    demo = ("Bidder C submits a blurry, rotated CA certificate scan.  Tesseract reads it at ~55% confidence.  "
            "Vision LLM transcribes the turnover figure correctly.  Combined confidence = 0.58 → routed to "
            "human review.  This is intentional — borderline evidence requires a human.")
    wrapped(c, demo, M + 0.4 * cm, by + 1.35 * cm, W - 2 * M - 0.8 * cm,
            size=11, color=C_WHITE, leading=15)
    page_num(c, 5)
    c.showPage()


# ── Slide 6 ─────────────────────────────────────────────────────────────────
def s6(c):
    c.setFillColor(colors.white)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    header_band(c, "Every Decision is Explainable and Auditable", 6)

    half = (W - 2 * M - 0.8 * cm) / 2
    lx = M
    rx = M + half + 0.8 * cm
    top = H * 0.76
    ch = 3.4 * cm

    card(c, lx, top - ch, half, ch, C_BLU2)
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(C_BLU2)
    c.drawString(lx + 0.35 * cm, top - 0.45 * cm, "Criterion-Level Verdicts")
    left_lines = [
        "Each (bidder × criterion) pair shows:",
        "• Which criterion was checked",
        "• Document and page providing evidence",
        "• Value extracted (e.g. 'INR 6.2 Cr')",
        "• OCR tier that read the document",
        "• Combined confidence score (0–100%)",
        "• Plain-English reason",
    ]
    c.setFont("Helvetica", 11)
    c.setFillColor(C_DARK)
    for i, ln in enumerate(left_lines):
        c.drawString(lx + 0.35 * cm, top - 0.9 * cm - i * 0.42 * cm, ln)

    card(c, rx, top - ch, half, ch, C_BLU2)
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(C_BLU2)
    c.drawString(rx + 0.35 * cm, top - 0.45 * cm, "Audit Trail")
    right_lines = [
        "Every action logged with:",
        "• UTC timestamp",
        "• Action type (criteria_extracted /",
        "  bidder_processed / criterion_evaluated /",
        "  vision_ocr_invoked / precomputed_fallback)",
        "• Model version & Actor",
        "• Full payload JSON — Exportable as CSV",
    ]
    c.setFont("Helvetica", 11)
    c.setFillColor(C_DARK)
    for i, ln in enumerate(right_lines):
        c.drawString(rx + 0.35 * cm, top - 0.9 * cm - i * 0.42 * cm, ln)

    # Safety rule
    sy = top - ch - 0.4 * cm - 1.8 * cm
    c.setFillColor(colors.HexColor("#FEF3C7"))
    c.setStrokeColor(C_AMB)
    c.setLineWidth(2)
    c.roundRect(M, sy, W - 2 * M, 1.8 * cm, 4, fill=1, stroke=1)
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(colors.HexColor("#92400E"))
    c.drawString(M + 0.4 * cm, sy + 1.35 * cm, "The Safety Rule:")
    c.setFont("Helvetica", 12)
    c.setFillColor(C_DARK)
    rule = ("If combined confidence is 0.55–0.80 AND verdict is not_eligible, the verdict is "
            "automatically downgraded to needs_review.  A bidder is NEVER silently disqualified at medium confidence.")
    wrapped(c, rule, M + 0.4 * cm, sy + 1.1 * cm, W - 2 * M - 0.8 * cm, size=11, color=C_DARK, leading=15)
    page_num(c, 6)
    c.showPage()


# ── Slide 7 ─────────────────────────────────────────────────────────────────
def s7(c):
    c.setFillColor(colors.white)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    header_band(c, "Demo: Three Bidders, Three Outcomes", 7)

    bidders = [
        ("Bidder A\nApex Constructions Pvt. Ltd.", C_GRN, "ELIGIBLE",
         colors.HexColor("#D1FAE5"),
         ["C1 Turnover: INR 6.37 Cr avg — PASS",
          "C2 Projects: 5 completed (CRPF) — PASS",
          "C3 GST: GSTIN active — PASS",
          "C4 ISO 9001:2015 valid June 2027 — PASS",
          "Confidence ≥ 93% on all criteria"]),
        ("Bidder B\nBuildRight Enterprises", C_RED, "NOT ELIGIBLE",
         colors.HexColor("#FEE2E2"),
         ["C1 Turnover: INR 1.5 Cr — FAIL",
          "Below required minimum of INR 5 Cr",
          "C2–C4: All pass",
          "Disqualified at high confidence (95%)"]),
        ("Bidder C\nShree Constructions & Services", C_AMB, "NEEDS REVIEW",
         colors.HexColor("#FEF3C7"),
         ["C1 Turnover: Blurry scan submitted",
          "Tesseract ~55% → Vision LLM: INR 5.4 Cr",
          "Combined confidence 0.58 → safety rule",
          "C2: Exactly 3 projects (borderline)",
          "C3–C4: Pass"]),
    ]
    cw = (W - 2 * M - 2 * cm) / 3
    top = H * 0.76
    for i, (name, color, verdict, vbg, bullets) in enumerate(bidders):
        cx = M + i * (cw + 1 * cm)
        cy = top - 3.5 * cm
        card(c, cx, cy, cw, 3.5 * cm, color)
        c.setFont("Helvetica-Bold", 12)
        c.setFillColor(C_DARK)
        for li, nl in enumerate(name.split("\n")):
            c.drawString(cx + 0.35 * cm, cy + 3.2 * cm - li * 0.4 * cm, nl)
        # verdict chip
        c.setFillColor(vbg)
        c.setStrokeColor(color)
        c.setLineWidth(1)
        c.roundRect(cx + 0.3 * cm, cy + 2.5 * cm, cw - 0.6 * cm, 0.5 * cm, 3, fill=1, stroke=1)
        c.setFont("Helvetica-Bold", 11)
        c.setFillColor(color)
        c.drawCentredString(cx + cw / 2, cy + 2.65 * cm, verdict)
        c.setFont("Helvetica", 10)
        c.setFillColor(C_DARK)
        for j, b in enumerate(bullets):
            c.drawString(cx + 0.35 * cm, cy + 2.15 * cm - j * 0.42 * cm, b)

    # Metric strip
    metrics = [
        ("Criteria extracted", "5"),
        ("Bidder docs processed", "15"),
        ("LLM evaluation calls", "15"),
        ("Vision OCR invocations", "1"),
        ("Human review items", "1"),
        ("Total audit entries", "20+"),
    ]
    sy = H * 0.18
    grad_rect(c, M, sy, W - 2 * M, 1.5 * cm, C_BLU1, C_BLU2, steps=30)
    mw = (W - 2 * M) / len(metrics)
    for i, (lbl, val) in enumerate(metrics):
        mx = M + i * mw + mw / 2
        c.setFont("Helvetica-Bold", 20)
        c.setFillColor(C_WHITE)
        c.drawCentredString(mx, sy + 0.85 * cm, val)
        c.setFont("Helvetica", 9)
        c.setFillColor(colors.HexColor("#BFDBFE"))
        c.drawCentredString(mx, sy + 0.3 * cm, lbl)

    page_num(c, 7)
    c.showPage()


# ── Slide 8 ─────────────────────────────────────────────────────────────────
def s8(c):
    c.setFillColor(colors.white)
    c.rect(0, 0, W, H, fill=1, stroke=0)
    header_band(c, "Stack, Impact & What's Next", 8)

    stack = [
        ("UI & orchestration", "Streamlit 1.39"),
        ("LLM", "DeepSeek API (OpenAI-compatible)"),
        ("OCR Tier 1", "PyMuPDF 1.24"),
        ("OCR Tier 2", "Tesseract"),
        ("OCR Tier 3", "DeepSeek Vision LLM"),
        ("Semantic retrieval", "sentence-transformers all-MiniLM-L6-v2"),
        ("Data validation", "Pydantic v2"),
        ("Audit log", "SQLite"),
        ("Deployment", "Streamlit Cloud / HuggingFace Spaces"),
    ]
    lx = M
    row_h = 0.5 * cm
    top = H * 0.76
    # Header
    grad_rect(c, lx, top - row_h, 12.5 * cm, row_h, C_BLU1, C_BLU2, steps=20)
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(C_WHITE)
    c.drawString(lx + 0.2 * cm, top - 0.38 * cm, "Component")
    c.drawString(lx + 5.5 * cm, top - 0.38 * cm, "Technology")
    for i, (comp, tech) in enumerate(stack):
        ry = top - row_h - (i + 1) * row_h
        bg_c = colors.white if i % 2 == 0 else colors.HexColor("#EFF6FF")
        c.setFillColor(bg_c)
        c.rect(lx, ry, 12.5 * cm, row_h, fill=1, stroke=0)
        c.setFont("Helvetica", 10)
        c.setFillColor(C_GRY)
        c.drawString(lx + 0.2 * cm, ry + 0.13 * cm, comp)
        c.setFillColor(C_DARK)
        c.drawString(lx + 5.5 * cm, ry + 0.13 * cm, tech)

    # Future work
    fx = W - M - 11 * cm
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(C_BLU2)
    c.drawString(fx, top - 0.4 * cm, "What's Next")
    future = [
        "Multi-tender workspace — same bidder pool, multiple tenders",
        "GeM portal API integration — live tender ingestion",
        "Automated bidder ranking with weighted scoring",
        "LayoutLM for complex financial tables in scanned statements",
        "Multi-evaluator workflow with role-based approval",
        "Review queue email/SMS notifications",
        "Audit PDF export for procurement oversight submissions",
    ]
    c.setFont("Helvetica", 11)
    c.setFillColor(C_DARK)
    for i, f in enumerate(future):
        c.drawString(fx, top - 0.9 * cm - i * 0.52 * cm, f"• {f}")

    # Impact
    iy = H * 0.19
    grad_rect(c, M, iy, W - 2 * M, 1.2 * cm, C_BLU1, C_BLU2, steps=30)
    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(C_WHITE)
    c.drawCentredString(W / 2, iy + 0.65 * cm,
                        "3–5 days → minutes.  Every verdict traceable to a document, page, and model version.")
    c.setFont("Helvetica", 11)
    c.drawCentredString(W / 2, iy + 0.28 * cm,
                        "Built in one hackathon session. Deployable today.")
    page_num(c, 8)
    c.showPage()


def main():
    os.makedirs("deck", exist_ok=True)
    out = "deck/TenderIQ_v4_modern_gradient.pdf"
    c = Canvas(out, pagesize=landscape(A4))
    s1(c); s2(c); s3(c); s4(c)
    s5(c); s6(c); s7(c); s8(c)
    c.save()
    size = os.path.getsize(out)
    print(f"OK: Saved {out}  ({size:,} bytes, 8 slides)")


if __name__ == "__main__":
    main()
