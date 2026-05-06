# Spec 11 — Mock Data Generation

**Step:** 2 of 15  
**Time budget:** ~25 min  
**Checkpoint:** `data/` directory populated; `turnover_certificate_scan.png` is a visibly noisy scan that Tesseract reads with low confidence (~50–65%).

---

## Goal

`scripts/generate_mock_data.py` is a single deterministic script that produces:
1. One tender PDF (`data/tender/crpf_construction_tender.pdf`)
2. Five PDFs for Bidder A (clearly eligible)
3. Five PDFs for Bidder B (clearly ineligible — turnover too low)
4. Four PDFs + one noisy scan PNG for Bidder C (needs review)

All files are entirely synthetic and self-contained — no external assets required. The script must run in under 30 seconds.

---

## Dependencies

- `reportlab` — PDF generation
- `Pillow` — image manipulation
- `numpy` — salt-and-pepper noise

---

## Output Files

```
data/
  tender/
    crpf_construction_tender.pdf
  bidders/
    bidder_a/
      company_profile.pdf
      audited_financials.pdf
      project_experience.pdf
      gst_certificate.pdf
      iso_9001.pdf
    bidder_b/
      company_profile.pdf
      audited_financials.pdf
      project_experience.pdf
      gst_certificate.pdf
      iso_9001.pdf
    bidder_c/
      company_profile.pdf
      project_experience.pdf
      gst_certificate.pdf
      iso_9001.pdf
      turnover_certificate_scan.png
```

---

## Tender PDF — `crpf_construction_tender.pdf`

`reportlab` SimpleDocTemplate, 5–6 pages with formal government tender language.

### Sections

1. **Introduction** — "Central Reserve Police Force, Ministry of Home Affairs, Government of India. Tender for Construction of Residential Quarters."
2. **Scope of Work** — brief description of construction project.
3. **Eligibility Criteria** — Section 3.2, contains five criteria (see table below).
4. **Submission Procedure** — dates, contact details.
5. **Evaluation Methodology** — how bids will be scored.
6. **Annexures** — supporting forms.

### Five Criteria (exact text in Section 3.2)

| ID | Clause | Verbatim Text | Mandatory | Category |
|---|---|---|---|---|
| C1 | 3.2(a) | "The bidder shall have a minimum average annual turnover of INR 5 Crore (Rupees Five Crore only) during the last three financial years (2022-23, 2023-24, 2024-25), as certified by a Chartered Accountant." | Yes | financial |
| C2 | 3.2(b) | "The bidder must have successfully completed at least three (3) similar construction projects of value not less than INR 1 Crore each in the last five (5) financial years. Completion certificates from clients shall be submitted." | Yes | technical |
| C3 | 3.2(c) | "The bidder shall possess a valid Goods and Services Tax (GST) registration certificate. The GSTIN must be active as on the date of submission." | Yes | compliance |
| C4 | 3.2(d) | "The bidder shall hold a valid ISO 9001:2015 Quality Management System certification issued by an accredited certification body, valid as on the date of bid submission." | Yes | compliance |
| C5 | 3.2(e) | "Preferably, the bidder may have prior experience with construction or maintenance of paramilitary or defence infrastructure. This is a desirable criterion and shall not affect mandatory eligibility." | No | technical |

C5 uses "preferably" and "desirable" → tests the mandatory-vs-optional classifier.

---

## Bidder A — Clearly Eligible

### `company_profile.pdf`
- Company: "Apex Constructions Pvt. Ltd."
- GSTIN: 27AABCA1234F1Z5
- Registered: 2010
- ISO 9001:2015 certified: Yes

### `audited_financials.pdf`
- FY 2022-23: Annual Turnover INR 5,80,00,000 (Rupees Five Crore Eighty Lakh)
- FY 2023-24: Annual Turnover INR 6,20,00,000 (Rupees Six Crore Twenty Lakh)
- FY 2024-25: Annual Turnover INR 7,10,00,000 (Rupees Seven Crore Ten Lakh)
- Average: INR 6,36,66,667 — exceeds INR 5 Crore threshold
- Certified by: CA Ramesh Kumar, M. No. 123456

### `project_experience.pdf`
- 5 projects listed (2020–2025), each ≥ INR 1 Crore
- Includes one CRPF project (2023): "Construction of barracks, CRPF Camp, Pune, INR 3.5 Crore"

### `gst_certificate.pdf`
- GSTIN: 27AABCA1234F1Z5
- Valid through: 31-03-2027
- Status: Active

### `iso_9001.pdf`
- Certificate No: ISO-2021-9001-APEX
- Valid through: 15-06-2027
- Issued by: Bureau Veritas

---

## Bidder B — Clearly Ineligible (turnover too low)

Same structure as Bidder A, but financials are below threshold.

### `company_profile.pdf`
- Company: "BuildRight Enterprises"
- GSTIN: 29AABCB5678G1Z3

### `audited_financials.pdf`
- FY 2022-23: Annual Turnover INR 1,20,00,000 (Rupees One Crore Twenty Lakh)
- FY 2023-24: Annual Turnover INR 1,50,00,000 (Rupees One Crore Fifty Lakh)
- FY 2024-25: Annual Turnover INR 1,80,00,000 (Rupees One Crore Eighty Lakh)
- Average: INR 1,50,00,000 — **below** INR 5 Crore threshold
- Certified by: CA Suresh Patel, M. No. 654321

### `project_experience.pdf`
- 4 projects listed (2021–2025), each ≥ INR 1 Crore — passes C2

### `gst_certificate.pdf`
- GSTIN: 29AABCB5678G1Z3, valid through 2027, Active

### `iso_9001.pdf`
- Certificate No: ISO-2022-9001-BR
- Valid through: 20-08-2027

---

## Bidder C — Needs Review (scanned turnover certificate)

No typed `audited_financials.pdf`. Instead: a deliberately noisy scan PNG.

### `company_profile.pdf`
- Company: "Shree Constructions & Services"
- GSTIN: 24AABCC9012H1Z1

### `project_experience.pdf`
- Exactly 3 projects (borderline meets count threshold for C2)
- Values: INR 1.2 Cr, INR 1.5 Cr, INR 2.1 Cr

### `gst_certificate.pdf`
- GSTIN: 24AABCC9012H1Z1, valid through 2027, Active

### `iso_9001.pdf`
- Certificate No: ISO-2023-9001-SCS
- Valid through: 10-09-2027

### `turnover_certificate_scan.png` — noisy scan generation

This is the OCR demo centerpiece. Steps:

1. Render a `reportlab` page to an in-memory PDF with a CA's turnover certificate:
   - "This is to certify that M/s Shree Constructions & Services ... average annual turnover of INR 5,40,00,000 (Rupees Five Crore Forty Lakh only) for the financial years 2022-23, 2023-24, and 2024-25."
   - Include year-wise breakdown table.
2. Convert that PDF page to a PIL Image at 150 DPI using `fitz` (PyMuPDF).
3. Apply degradation:
   - `ImageFilter.GaussianBlur(radius=1.5)`
   - Salt-and-pepper noise via numpy: randomly set ~5% of pixels to 0 or 255
   - `image.rotate(-2, expand=True, fillcolor=(255,255,255))`
   - Re-save with JPEG compression at quality=40 then reload as PNG
4. Save as `data/bidders/bidder_c/turnover_certificate_scan.png`

**Expected outcome:** Tesseract reads this at mean confidence ~50–65% → triggers Tier-3 vision LLM. The turnover figure (INR 5,40,00,000) is present but partially degraded, making it a realistic "needs human review" case given combined-confidence rules.

---

## Script Design

```python
# scripts/generate_mock_data.py

def make_tender_pdf(out_path: Path) -> None: ...
def make_company_profile(out_path: Path, name: str, gstin: str, year: int) -> None: ...
def make_financials(out_path: Path, rows: list[tuple[str, str, int]]) -> None: ...
def make_project_experience(out_path: Path, projects: list[dict]) -> None: ...
def make_gst_certificate(out_path: Path, gstin: str, valid_through: str) -> None: ...
def make_iso_certificate(out_path: Path, cert_no: str, valid_through: str, company: str) -> None: ...
def make_noisy_scan(out_path: Path) -> None: ...

if __name__ == "__main__":
    # Ensure output dirs exist
    # Generate all files
    print("Mock data generated successfully.")
```

Each helper creates one PDF/PNG. The script is idempotent (re-running overwrites files). No command-line arguments needed.

---

## Acceptance Criteria

1. Running `python scripts/generate_mock_data.py` exits 0 and prints "Mock data generated successfully."
2. All 16 files listed above exist after the run.
3. Each PDF opens in a viewer without errors and contains the text described.
4. `turnover_certificate_scan.png` is visibly degraded (blurry, rotated, noisy).
5. Running `pytesseract.image_to_data(Image.open("data/bidders/bidder_c/turnover_certificate_scan.png"))` returns a dataframe where the filtered mean confidence is between 30 and 70 (i.e., low enough to trigger Tier 3).
6. Script completes in under 30 seconds on any modern machine.
