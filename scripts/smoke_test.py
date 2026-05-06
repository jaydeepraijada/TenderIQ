"""Step 13 — programmatic end-to-end check; exits 0 on success."""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))


def check(condition: bool, msg: str) -> None:
    if not condition:
        print(f"FAIL: {msg}")
        sys.exit(1)
    print(f"  OK: {msg}")


def main() -> None:
    print("TenderIQ Smoke Test")
    print("=" * 50)

    # 1. Core imports
    print("\n1. Core module imports")
    from core import config, schemas, prompts
    from core.llm_client import LLM, LLMUnavailable
    from core.pdf_utils import extract_pages, is_text_pdf
    from core.ocr_pipeline import extract_document, ExtractedPage
    from core.chunker import chunk_tender, chunk_bidder
    from core.schemas import Criterion, Verdict, Evidence
    from core import audit
    from core.fallback import load_criteria, load_evaluation
    check(True, "All core modules import without error")

    # 2. Config
    print("\n2. Config")
    check(config.MODEL_VERSION.startswith("deepseek-chat"), "MODEL_VERSION set")
    check(config.CONFIDENCE_HIGH == 0.80, "CONFIDENCE_HIGH = 0.80")
    check(config.CONFIDENCE_REVIEW == 0.55, "CONFIDENCE_REVIEW = 0.55")

    # 3. Schemas
    print("\n3. Schemas")
    c = Criterion(**{
        "id": "C1", "title": "Turnover", "category": "financial",
        "mandatory": True, "description": "test",
        "rule": {"type": "numeric_threshold", "field": "t", "operator": ">=",
                 "value": 50000000, "unit": "INR"},
        "query_hints": ["turnover"], "source_page": 3, "source_clause": "3.2(a)",
    })
    check(c.mandatory is True, "Criterion schema validates")

    v = Verdict(bidder_id="b", criterion_id="C1", verdict="eligible")
    check(v.verdict_id.startswith("V-"), "Verdict auto-generates verdict_id")
    check(v.review_status == "pending", "Verdict defaults to pending")

    # 4. Mock data files
    print("\n4. Mock data files")
    from core.config import DATA_DIR
    tender_pdf = DATA_DIR / "tender" / "crpf_construction_tender.pdf"
    check(tender_pdf.exists(), "Tender PDF exists")
    for bidder in ["bidder_a", "bidder_b", "bidder_c"]:
        bidder_dir = DATA_DIR / "bidders" / bidder
        files = list(bidder_dir.glob("*"))
        files = [f for f in files if not f.name.endswith(".gitkeep")]
        check(len(files) >= 4, f"{bidder} has at least 4 documents")
    scan = DATA_DIR / "bidders" / "bidder_c" / "turnover_certificate_scan.png"
    check(scan.exists(), "Bidder C noisy scan exists")

    # 5. PDF utils
    print("\n5. PDF utils")
    pages = extract_pages(tender_pdf)
    check(len(pages) >= 3, f"Tender PDF has {len(pages)} pages")
    check(is_text_pdf(tender_pdf), "Tender PDF detected as text_pdf")
    img = __import__("core.pdf_utils", fromlist=["render_page_to_image"]).render_page_to_image(tender_pdf, 1)
    check(img.size[0] > 0, f"Page render returns {img.size} image")

    # 6. Chunker
    print("\n6. Chunker")
    chunks = chunk_tender(pages, "tender_001")
    check(len(chunks) > 0, f"chunk_tender returns {len(chunks)} chunks")
    check("text" in chunks[0] and "chunk_id" in chunks[0], "Chunk has text and chunk_id")

    # 7. OCR pipeline
    print("\n7. OCR pipeline")
    fin_pdf = DATA_DIR / "bidders" / "bidder_a" / "audited_financials.pdf"
    ep = extract_document(fin_pdf)
    check(len(ep) > 0, f"extract_document returns {len(ep)} pages")
    check(ep[0].source_type == "text_pdf", "Typed PDF uses Tier 1")
    check(ep[0].confidence == 1.0, "Typed PDF confidence = 1.0")

    ep_scan = extract_document(scan)
    check(len(ep_scan) == 1, "Noisy scan returns 1 page")
    check(ep_scan[0].source_type in ("text_pdf", "tesseract", "vision_llm"),
          f"Scan source_type = {ep_scan[0].source_type}")

    # 8. Fallback
    print("\n8. Fallback")
    criteria = load_criteria()
    check(len(criteria) == 5, f"load_criteria returns {len(criteria)} criteria")
    check(criteria[0].id == "C1", "First criterion is C1")
    mandatory_count = sum(1 for c in criteria if c.mandatory)
    check(mandatory_count == 4, f"{mandatory_count} mandatory criteria")
    optional_count = sum(1 for c in criteria if not c.mandatory)
    check(optional_count == 1, f"{optional_count} optional criterion (C5)")

    va = load_evaluation("bidder_a", "C1")
    check(va.verdict == "eligible", f"Bidder A C1 = {va.verdict}")
    vb = load_evaluation("bidder_b", "C1")
    check(vb.verdict == "not_eligible", f"Bidder B C1 = {vb.verdict}")
    vc = load_evaluation("bidder_c", "C1")
    check(vc.verdict == "needs_review", f"Bidder C C1 = {vc.verdict}")

    # 9. Audit
    print("\n9. Audit")
    rid = audit.log("smoke_test", actor="smoke_test")
    check(isinstance(rid, int) and rid > 0, f"audit.log returns row id {rid}")
    rows = audit.query({"action": "smoke_test"})
    check(len(rows) >= 1, "audit.query filters by action")

    # 10. Evaluator threshold logic
    print("\n10. Evaluator threshold logic")
    from core.evaluator import _apply_thresholds, _combined_confidence
    check(_apply_thresholds("eligible", 0.9) == "eligible", "eligible@0.9 stays eligible")
    check(_apply_thresholds("not_eligible", 0.9) == "not_eligible", "not_eligible@0.9 stays")
    check(_apply_thresholds("not_eligible", 0.6) == "needs_review", "not_eligible@0.6 -> needs_review")
    check(_apply_thresholds("eligible", 0.4) == "needs_review", "eligible@0.4 -> needs_review")
    check(_combined_confidence(0.9, "text_pdf", None) == 0.9, "text_pdf combined = llm_conf")
    c_vis = _combined_confidence(0.9, "vision_llm", None)
    check(0.8 < c_vis < 0.96, f"vision_llm combined = {c_vis:.3f}")

    # 11. Precomputed files
    print("\n11. Precomputed JSON files")
    from core.config import PRECOMPUTED_DIR
    check((PRECOMPUTED_DIR / "criteria.json").exists(), "criteria.json exists")
    for bidder in ["bidder_a", "bidder_b", "bidder_c"]:
        check((PRECOMPUTED_DIR / f"eval_{bidder}.json").exists(), f"eval_{bidder}.json exists")

    print("\n" + "=" * 50)
    print("All checks passed. Smoke test: SUCCESS")
    print("=" * 50)


if __name__ == "__main__":
    main()
