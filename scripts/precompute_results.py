"""Step 11 — runs the full pipeline and writes data/precomputed/*.json."""

import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from core.config import DATA_DIR, DEEPSEEK_API_KEY, PRECOMPUTED_DIR
from core.criteria_extractor import extract_criteria
from core.bidder_processor import process_bidder
from core.evaluator import evaluate_bidder
from core.fallback import _HARDCODED_CRITERIA
from core.schemas import Criterion


def main() -> None:
    if not DEEPSEEK_API_KEY:
        print("ERROR: DEEPSEEK_API_KEY is not set.")
        print("Set it in .env or export it before running this script.")
        sys.exit(1)

    PRECOMPUTED_DIR.mkdir(parents=True, exist_ok=True)

    # Step 1 — Extract criteria
    tender_path = DATA_DIR / "tender" / "crpf_construction_tender.pdf"
    print(f"Extracting criteria from {tender_path.name}...")
    try:
        criteria = extract_criteria(tender_path)
        print(f"  Got {len(criteria)} criteria from LLM.")
    except Exception as e:
        print(f"  LLM extraction failed ({e}), using hardcoded criteria.")
        criteria = [Criterion(**c) for c in _HARDCODED_CRITERIA]

    criteria_file = PRECOMPUTED_DIR / "criteria.json"
    criteria_file.write_text(
        json.dumps({"criteria": [c.model_dump() for c in criteria]},
                   indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"  Saved {criteria_file}")

    # Step 2 — Process + evaluate each bidder
    bidders = ["bidder_a", "bidder_b", "bidder_c"]
    for bidder_id in bidders:
        bidder_dir = DATA_DIR / "bidders" / bidder_id
        files = sorted(bidder_dir.glob("*"))
        files = [f for f in files if f.suffix.lower() in {".pdf", ".png", ".jpg"}]

        print(f"\nProcessing {bidder_id} ({len(files)} files)...")
        process_bidder(bidder_id, files)

        print(f"  Evaluating {bidder_id} against {len(criteria)} criteria...")
        verdicts = evaluate_bidder(bidder_id, criteria)

        eval_file = PRECOMPUTED_DIR / f"eval_{bidder_id}.json"
        eval_file.write_text(
            json.dumps([v.model_dump() for v in verdicts], indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
        print(f"  Saved {eval_file}")
        for v in verdicts:
            print(f"    {v.criterion_id}: {v.verdict} (conf={v.combined_confidence:.2f})")

    print("\nPre-computation complete. Files in data/precomputed/:")
    for f in sorted(PRECOMPUTED_DIR.glob("*.json")):
        print(f"  {f.name} ({f.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
