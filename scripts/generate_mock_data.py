"""Step 2 — generates mock tender and bidder PDFs + noisy scan PNG."""

import io
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle, PageBreak
)

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def _doc(path: Path) -> SimpleDocTemplate:
    return SimpleDocTemplate(str(path), pagesize=A4,
                             leftMargin=2*cm, rightMargin=2*cm,
                             topMargin=2*cm, bottomMargin=2*cm)


def _styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="Center", alignment=1, fontSize=12,
                              spaceAfter=6))
    styles.add(ParagraphStyle(name="Bold14", fontName="Helvetica-Bold",
                              fontSize=14, spaceAfter=8))
    styles.add(ParagraphStyle(name="Bold12", fontName="Helvetica-Bold",
                              fontSize=12, spaceAfter=6))
    styles.add(ParagraphStyle(name="Body10", fontSize=10, spaceAfter=4,
                              leading=14))
    styles.add(ParagraphStyle(name="Clause", fontSize=10, leftIndent=20,
                              spaceAfter=10, leading=14))
    return styles


def make_tender_pdf(out_path: Path) -> None:
    doc = _doc(out_path)
    s = _styles()
    story = []

    story.append(Paragraph("GOVERNMENT OF INDIA", s["Center"]))
    story.append(Paragraph("MINISTRY OF HOME AFFAIRS", s["Center"]))
    story.append(Paragraph("CENTRAL RESERVE POLICE FORCE", s["Bold14"]))
    story.append(Paragraph(
        "TENDER DOCUMENT FOR CONSTRUCTION OF RESIDENTIAL QUARTERS",
        s["Center"]
    ))
    story.append(Paragraph("Tender No: CRPF/CE/2025-26/RQ/001", s["Center"]))
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph("1. INTRODUCTION", s["Bold12"]))
    story.append(Paragraph(
        "The Central Reserve Police Force (CRPF), under the Ministry of Home Affairs, "
        "Government of India, invites sealed tenders from eligible contractors for the "
        "construction of Residential Quarters at CRPF Camp, New Delhi. The work involves "
        "civil construction, internal electrification, plumbing, and allied works.",
        s["Body10"]
    ))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("2. SCOPE OF WORK", s["Bold12"]))
    story.append(Paragraph(
        "The scope includes: (a) Construction of Type-III Residential Quarters (G+4) — "
        "24 units; (b) Internal roads, drainage, and compound wall; (c) Water supply and "
        "sanitation infrastructure; (d) Landscaping and external works. Estimated project "
        "value: INR 18 Crore. Completion period: 24 months.",
        s["Body10"]
    ))
    story.append(PageBreak())

    story.append(Paragraph("3. ELIGIBILITY CRITERIA", s["Bold12"]))
    story.append(Paragraph(
        "Only bidders fulfilling ALL mandatory eligibility criteria listed below shall be "
        "considered for technical evaluation. Bids not meeting mandatory criteria shall be "
        "rejected summarily without further evaluation.",
        s["Body10"]
    ))
    story.append(Spacer(1, 0.3*cm))

    story.append(Paragraph("3.2 Mandatory and Desirable Criteria", s["Bold12"]))

    criteria_text = [
        ("3.2(a)", "Financial Capability",
         "The bidder shall have a minimum average annual turnover of INR 5 Crore "
         "(Rupees Five Crore only) during the last three financial years (2022-23, "
         "2023-24, 2024-25), as certified by a Chartered Accountant. Documentary "
         "evidence in the form of audited balance sheets, profit & loss account, and "
         "CA certificate shall be submitted. [MANDATORY]"),
        ("3.2(b)", "Technical Experience",
         "The bidder must have successfully completed at least three (3) similar "
         "construction projects of value not less than INR 1 Crore each in the last "
         "five (5) financial years. Completion certificates from clients shall be "
         "submitted along with work orders. [MANDATORY]"),
        ("3.2(c)", "GST Registration",
         "The bidder shall possess a valid Goods and Services Tax (GST) registration "
         "certificate. The GSTIN must be active as on the date of submission. A copy "
         "of the GST registration certificate shall be enclosed with the bid. "
         "[MANDATORY]"),
        ("3.2(d)", "Quality Certification",
         "The bidder shall hold a valid ISO 9001:2015 Quality Management System "
         "certification issued by an accredited certification body, valid as on the "
         "date of bid submission. Copy of the certificate shall be submitted. "
         "[MANDATORY]"),
        ("3.2(e)", "Paramilitary Experience",
         "Preferably, the bidder may have prior experience with construction or "
         "maintenance of paramilitary or defence infrastructure. This is a desirable "
         "criterion and shall not affect mandatory eligibility. Supporting documents "
         "may be submitted for additional credit during evaluation. [DESIRABLE]"),
    ]

    for clause, title, text in criteria_text:
        story.append(Paragraph(f"<b>{clause} {title}</b>", s["Body10"]))
        story.append(Paragraph(text, s["Clause"]))

    story.append(PageBreak())

    story.append(Paragraph("4. SUBMISSION PROCEDURE", s["Bold12"]))
    story.append(Paragraph(
        "Bids shall be submitted in two envelopes: Technical Bid and Financial Bid. "
        "Last date of submission: 30-06-2026. Address for submission: The Inspector "
        "General (Works), CRPF Group Centre, New Delhi – 110077. "
        "EMD of INR 36 Lakh (2% of estimated cost) to be deposited via DD/BG.",
        s["Body10"]
    ))
    story.append(Spacer(1, 0.5*cm))

    story.append(Paragraph("5. EVALUATION METHODOLOGY", s["Bold12"]))
    story.append(Paragraph(
        "Evaluation shall proceed in two stages: (i) Technical Evaluation — bidders "
        "meeting all mandatory criteria in 3.2 shall be declared technically qualified; "
        "(ii) Financial Evaluation — lowest L1 bid among technically qualified bidders "
        "shall be recommended. Desirable criteria (3.2(e)) may be used for tie-breaking.",
        s["Body10"]
    ))
    story.append(PageBreak())

    story.append(Paragraph("6. ANNEXURES", s["Bold12"]))
    story.append(Paragraph("Annexure A — Bid Form", s["Body10"]))
    story.append(Paragraph("Annexure B — Declaration of Non-Blacklisting", s["Body10"]))
    story.append(Paragraph("Annexure C — CA Certificate Format (Turnover)", s["Body10"]))
    story.append(Paragraph("Annexure D — Project Completion Certificate Format", s["Body10"]))

    doc.build(story)


def _simple_pdf(out_path: Path, title: str, paragraphs: list[str],
                table_data: list[list] | None = None) -> None:
    doc = _doc(out_path)
    s = _styles()
    story = []
    story.append(Paragraph(title, s["Bold14"]))
    story.append(Spacer(1, 0.3*cm))
    for para in paragraphs:
        story.append(Paragraph(para, s["Body10"]))
    if table_data:
        story.append(Spacer(1, 0.3*cm))
        tbl = Table(table_data, hAlign="LEFT")
        tbl.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        story.append(tbl)
    doc.build(story)


def make_company_profile(out_path: Path, name: str, gstin: str, reg_year: int,
                         iso: bool = True, extra_lines: list[str] | None = None) -> None:
    paras = [
        f"<b>Company Name:</b> {name}",
        f"<b>GSTIN:</b> {gstin}",
        f"<b>Year of Registration:</b> {reg_year}",
        f"<b>Nature of Business:</b> Civil Construction and Infrastructure Development",
        f"<b>ISO 9001:2015 Certified:</b> {'Yes' if iso else 'No'}",
        "<b>Registered Office:</b> 42, Industrial Area, Phase II, India",
    ]
    if extra_lines:
        paras.extend(extra_lines)
    _simple_pdf(out_path, f"Company Profile — {name}", paras)


def make_financials(out_path: Path, company: str,
                    rows: list[tuple[str, str, int]], ca_name: str,
                    ca_no: str) -> None:
    table_data = [["Financial Year", "Annual Turnover (INR)", "Words"]]
    for fy, words, amount in rows:
        table_data.append([fy, f"{amount:,}", words])
    avg = sum(r[2] for r in rows) // len(rows)
    table_data.append(["Average (3 years)", f"{avg:,}", ""])

    paras = [
        f"<b>Company:</b> {company}",
        "The following statement of annual turnover has been prepared from the "
        "audited accounts and is certified to be true and correct.",
    ]
    paras.append(f"<b>Certified by:</b> {ca_name}, Chartered Accountant, M. No. {ca_no}")
    paras.append("<b>UDIN:</b> 26123456AAAAA0001")
    paras.append("<b>Place:</b> Mumbai &nbsp;&nbsp; <b>Date:</b> 01-04-2026")
    _simple_pdf(out_path,
                "Audited Financial Statement — Annual Turnover Certificate",
                paras, table_data)


def make_project_experience(out_path: Path, company: str,
                             projects: list[dict]) -> None:
    table_data = [["#", "Project Name", "Client", "Value (INR Cr)", "Year", "Status"]]
    for i, p in enumerate(projects, 1):
        table_data.append([
            str(i), p["name"], p["client"],
            str(p["value"]), str(p["year"]), p.get("status", "Completed")
        ])
    paras = [
        f"<b>Company:</b> {company}",
        "The following construction projects have been completed by the organization "
        "in the last five financial years (2020–2025). Completion certificates are "
        "enclosed separately.",
    ]
    _simple_pdf(out_path, "Project Experience Certificate", paras, table_data)


def make_gst_certificate(out_path: Path, gstin: str, company: str,
                          valid_through: str) -> None:
    paras = [
        "<b>GOODS AND SERVICES TAX REGISTRATION CERTIFICATE</b>",
        f"<b>Legal Name of Business:</b> {company}",
        f"<b>GSTIN:</b> {gstin}",
        f"<b>Date of Registration:</b> 01-07-2017",
        f"<b>Valid Through:</b> {valid_through}",
        f"<b>Registration Status:</b> ACTIVE",
        f"<b>Type of Registration:</b> Regular",
        f"<b>Issuing Authority:</b> Assistant Commissioner CGST, Mumbai",
    ]
    _simple_pdf(out_path, "GST Registration Certificate", paras)


def make_iso_certificate(out_path: Path, cert_no: str, company: str,
                          valid_through: str, issuer: str) -> None:
    paras = [
        "<b>ISO 9001:2015 QUALITY MANAGEMENT SYSTEM CERTIFICATE</b>",
        f"<b>Certificate Number:</b> {cert_no}",
        f"<b>This certifies that:</b> {company}",
        "<b>Scope:</b> Design and Construction of Civil Infrastructure including "
        "Residential, Commercial and Industrial Buildings",
        f"<b>Valid Through:</b> {valid_through}",
        f"<b>Issuing Body:</b> {issuer}",
        "<b>Accreditation:</b> National Accreditation Board for Certification Bodies (NABCB)",
        "<b>This certificate is issued in accordance with ISO 9001:2015 standard.</b>",
    ]
    _simple_pdf(out_path, "ISO 9001:2015 Certificate", paras)


def _render_ca_cert_to_pil(company: str, gstin: str, avg_amount: int,
                             avg_words: str) -> Image.Image:
    """Render a CA turnover certificate PDF page to PIL image for degradation."""
    import fitz  # PyMuPDF

    buf = io.BytesIO()
    doc = _doc(Path("/tmp/dummy.pdf"))  # path unused for in-memory
    s = _styles()
    story = [
        Paragraph("CHARTERED ACCOUNTANT'S CERTIFICATE", s["Bold14"]),
        Paragraph("(As per Annexure C of Tender No: CRPF/CE/2025-26/RQ/001)", s["Body10"]),
        Spacer(1, 0.5*cm),
        Paragraph(
            f"This is to certify that M/s {company} (GSTIN: {gstin}) is a registered "
            "entity engaged in civil construction activities. Based on the audited "
            "financial statements and books of accounts duly certified under applicable "
            "provisions of the Companies Act, 2013:",
            s["Body10"]
        ),
        Spacer(1, 0.3*cm),
        Paragraph(
            f"The average annual turnover of the firm for the three financial years "
            f"2022-23, 2023-24, and 2024-25 is <b>INR {avg_amount:,} ({avg_words} only)</b>.",
            s["Body10"]
        ),
        Spacer(1, 0.3*cm),
    ]

    table_data = [
        ["Financial Year", "Annual Turnover (INR)", "In Words"],
        ["2022-23", "4,80,00,000", "Four Crore Eighty Lakh"],
        ["2023-24", "5,40,00,000", "Five Crore Forty Lakh"],
        ["2024-25", "6,00,00,000", "Six Crore"],
        [f"Average (3 years)", f"{avg_amount:,}", avg_words],
    ]
    tbl = Table(table_data)
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(tbl)
    story.extend([
        Spacer(1, 0.5*cm),
        Paragraph("Certified by:", s["Body10"]),
        Paragraph("<b>CA Vikram Shah</b>", s["Body10"]),
        Paragraph("M. No. 098765", s["Body10"]),
        Paragraph("FRN: 100001W", s["Body10"]),
        Paragraph("Place: Ahmedabad &nbsp;&nbsp; Date: 05-04-2026", s["Body10"]),
        Paragraph("UDIN: 26098765BBBBB0002", s["Body10"]),
    ])

    buf = io.BytesIO()
    pdf_doc = SimpleDocTemplate(buf, pagesize=A4,
                                leftMargin=2*cm, rightMargin=2*cm,
                                topMargin=2*cm, bottomMargin=2*cm)
    pdf_doc.build(story)
    buf.seek(0)

    fitz_doc = fitz.open(stream=buf.read(), filetype="pdf")
    page = fitz_doc[0]
    mat = fitz.Matrix(150/72, 150/72)
    pix = page.get_pixmap(matrix=mat, colorspace=fitz.csRGB)
    img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
    fitz_doc.close()
    return img


def make_noisy_scan(out_path: Path) -> None:
    img = _render_ca_cert_to_pil(
        company="Shree Constructions & Services",
        gstin="24AABCC9012H1Z1",
        avg_amount=5_40_00_000,
        avg_words="Five Crore Forty Lakh",
    )

    # Apply degradation
    img = img.filter(ImageFilter.GaussianBlur(radius=1.5))

    arr = np.array(img, dtype=np.uint8)
    rng = np.random.default_rng(seed=42)
    noise_mask = rng.random(arr.shape[:2])
    arr[noise_mask < 0.025] = 0
    arr[noise_mask > 0.975] = 255
    img = Image.fromarray(arr)

    img = img.rotate(-2, expand=True, fillcolor=(255, 255, 255))

    jpeg_buf = io.BytesIO()
    img.convert("RGB").save(jpeg_buf, format="JPEG", quality=40)
    jpeg_buf.seek(0)
    img = Image.open(jpeg_buf).copy()

    img.save(str(out_path), format="PNG")


def main() -> None:
    # Ensure output dirs exist
    for d in [
        DATA_DIR / "tender",
        DATA_DIR / "bidders" / "bidder_a",
        DATA_DIR / "bidders" / "bidder_b",
        DATA_DIR / "bidders" / "bidder_c",
        DATA_DIR / "precomputed",
    ]:
        d.mkdir(parents=True, exist_ok=True)

    # Tender
    make_tender_pdf(DATA_DIR / "tender" / "crpf_construction_tender.pdf")

    # ── Bidder A ─────────────────────────────────────────────────────────────
    a = DATA_DIR / "bidders" / "bidder_a"
    make_company_profile(a / "company_profile.pdf",
                         "Apex Constructions Pvt. Ltd.", "27AABCA1234F1Z5", 2010)
    make_financials(a / "audited_financials.pdf",
                    "Apex Constructions Pvt. Ltd.",
                    [
                        ("2022-23", "Five Crore Eighty Lakh", 5_80_00_000),
                        ("2023-24", "Six Crore Twenty Lakh", 6_20_00_000),
                        ("2024-25", "Seven Crore Ten Lakh", 7_10_00_000),
                    ],
                    ca_name="CA Ramesh Kumar", ca_no="123456")
    make_project_experience(a / "project_experience.pdf",
                             "Apex Constructions Pvt. Ltd.",
                             [
                                 {"name": "Staff Quarters Block A", "client": "PWD Delhi",
                                  "value": 2.5, "year": 2021},
                                 {"name": "Office Complex Phase 1", "client": "CPWD Mumbai",
                                  "value": 3.2, "year": 2022},
                                 {"name": "Residential Complex", "client": "NBCC Ltd",
                                  "value": 4.1, "year": 2023},
                                 {"name": "Barracks Construction", "client": "CRPF Camp Pune",
                                  "value": 3.5, "year": 2024},
                                 {"name": "Commercial Warehouse", "client": "DDA",
                                  "value": 1.8, "year": 2025},
                             ])
    make_gst_certificate(a / "gst_certificate.pdf", "27AABCA1234F1Z5",
                          "Apex Constructions Pvt. Ltd.", "31-03-2027")
    make_iso_certificate(a / "iso_9001.pdf", "ISO-2021-9001-APEX",
                          "Apex Constructions Pvt. Ltd.", "15-06-2027",
                          "Bureau Veritas Certification India Pvt. Ltd.")

    # ── Bidder B ─────────────────────────────────────────────────────────────
    b = DATA_DIR / "bidders" / "bidder_b"
    make_company_profile(b / "company_profile.pdf",
                         "BuildRight Enterprises", "29AABCB5678G1Z3", 2015)
    make_financials(b / "audited_financials.pdf",
                    "BuildRight Enterprises",
                    [
                        ("2022-23", "One Crore Twenty Lakh", 1_20_00_000),
                        ("2023-24", "One Crore Fifty Lakh", 1_50_00_000),
                        ("2024-25", "One Crore Eighty Lakh", 1_80_00_000),
                    ],
                    ca_name="CA Suresh Patel", ca_no="654321")
    make_project_experience(b / "project_experience.pdf",
                             "BuildRight Enterprises",
                             [
                                 {"name": "Residential Quarters", "client": "Municipal Corp",
                                  "value": 1.1, "year": 2022},
                                 {"name": "School Building Renovation", "client": "KVS",
                                  "value": 1.3, "year": 2023},
                                 {"name": "Community Hall", "client": "NDMC",
                                  "value": 1.2, "year": 2024},
                                 {"name": "Warehouse Shed", "client": "FCI",
                                  "value": 1.0, "year": 2025},
                             ])
    make_gst_certificate(b / "gst_certificate.pdf", "29AABCB5678G1Z3",
                          "BuildRight Enterprises", "31-03-2027")
    make_iso_certificate(b / "iso_9001.pdf", "ISO-2022-9001-BR",
                          "BuildRight Enterprises", "20-08-2027",
                          "TUV SUD South Asia Pvt. Ltd.")

    # ── Bidder C ─────────────────────────────────────────────────────────────
    c = DATA_DIR / "bidders" / "bidder_c"
    make_company_profile(c / "company_profile.pdf",
                         "Shree Constructions & Services", "24AABCC9012H1Z1", 2012)
    make_project_experience(c / "project_experience.pdf",
                             "Shree Constructions & Services",
                             [
                                 {"name": "Housing Complex Phase 1", "client": "GIDC",
                                  "value": 1.2, "year": 2023},
                                 {"name": "Commercial Plaza", "client": "Ahmedabad MC",
                                  "value": 2.1, "year": 2024},
                                 {"name": "Road & Drainage Works", "client": "NHAI",
                                  "value": 1.5, "year": 2025},
                             ])
    make_gst_certificate(c / "gst_certificate.pdf", "24AABCC9012H1Z1",
                          "Shree Constructions & Services", "31-03-2027")
    make_iso_certificate(c / "iso_9001.pdf", "ISO-2023-9001-SCS",
                          "Shree Constructions & Services", "10-09-2027",
                          "DNV Business Assurance India Pvt. Ltd.")
    make_noisy_scan(c / "turnover_certificate_scan.png")

    print("Mock data generated successfully.")


if __name__ == "__main__":
    main()
