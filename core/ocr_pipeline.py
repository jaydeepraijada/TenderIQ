import dataclasses
import hashlib
import io
import json
from pathlib import Path

from core import audit
from core.config import OCR_CACHE_DIR, OCR_TESSERACT_MIN_CONF
from core.llm_client import LLM, LLMUnavailable
from core.prompts import VISION_OCR_PROMPT_SYSTEM, VISION_OCR_USER

_IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".bmp", ".tiff", ".tif"}


@dataclasses.dataclass
class ExtractedPage:
    page: int
    text: str
    source_type: str  # "text_pdf" | "tesseract" | "vision_llm"
    confidence: float
    raw_tier_results: dict


def _cache_path(file_path: Path) -> Path:
    h = hashlib.md5(file_path.read_bytes()).hexdigest()
    OCR_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    return OCR_CACHE_DIR / f"{h}.json"


def _load_cache(file_path: Path) -> list[ExtractedPage] | None:
    cp = _cache_path(file_path)
    if cp.exists():
        data = json.loads(cp.read_text(encoding="utf-8"))
        return [ExtractedPage(**d) for d in data]
    return None


def _save_cache(file_path: Path, pages: list[ExtractedPage]) -> None:
    cp = _cache_path(file_path)
    cp.write_text(
        json.dumps([dataclasses.asdict(p) for p in pages], ensure_ascii=False),
        encoding="utf-8",
    )


def _tesseract_extract(pil_image) -> tuple[str, float]:
    try:
        import pytesseract
        data = pytesseract.image_to_data(
            pil_image, output_type=pytesseract.Output.DATAFRAME
        )
        valid = data[data["conf"] != -1]
        mean_conf = float(valid["conf"].mean()) / 100 if len(valid) > 0 else 0.0
        text = " ".join(str(w) for w in valid["text"] if str(w).strip())
        return text, mean_conf
    except Exception:
        return "", 0.0


def _vision_extract(pil_image) -> str | None:
    buf = io.BytesIO()
    pil_image.convert("RGB").save(buf, format="PNG")
    buf.seek(0)
    try:
        llm = LLM()
        result = llm.chat_vision(VISION_OCR_PROMPT_SYSTEM, VISION_OCR_USER, buf.getvalue())
        return result
    except LLMUnavailable:
        return None


def _process_image(pil_image, page_no: int) -> ExtractedPage:
    text, conf = _tesseract_extract(pil_image)
    if conf >= OCR_TESSERACT_MIN_CONF and len(text.strip()) >= 20:
        return ExtractedPage(
            page=page_no,
            text=text,
            source_type="tesseract",
            confidence=conf,
            raw_tier_results={"tesseract_conf": conf, "vision_used": False},
        )
    # Tier 3
    vision_text = _vision_extract(pil_image)
    if vision_text:
        audit.log("vision_ocr_invoked", page=page_no,
                  tesseract_conf=round(conf, 3))
        return ExtractedPage(
            page=page_no,
            text=vision_text,
            source_type="vision_llm",
            confidence=0.95,
            raw_tier_results={"tesseract_conf": conf, "vision_used": True},
        )
    # Tier 3 failed — use Tier 2 result as-is
    return ExtractedPage(
        page=page_no,
        text=text,
        source_type="tesseract",
        confidence=conf,
        raw_tier_results={"tesseract_conf": conf, "vision_used": False},
    )


def extract_document(file_path: Path) -> list[ExtractedPage]:
    cached = _load_cache(file_path)
    if cached is not None:
        return cached

    suffix = file_path.suffix.lower()

    if suffix in _IMAGE_SUFFIXES:
        from PIL import Image
        img = Image.open(file_path).convert("RGB")
        pages = [_process_image(img, 1)]
    else:
        from core.pdf_utils import extract_pages, is_text_pdf, render_page_to_image

        if is_text_pdf(file_path):
            raw_pages = extract_pages(file_path)
            pages = [
                ExtractedPage(
                    page=p["page"],
                    text=p["text"],
                    source_type="text_pdf",
                    confidence=1.0,
                    raw_tier_results={"tesseract_conf": None, "vision_used": False},
                )
                for p in raw_pages
                if p["text"].strip()
            ]
        else:
            import fitz
            doc = fitz.open(str(file_path))
            n_pages = doc.page_count
            doc.close()
            pages = []
            for i in range(1, n_pages + 1):
                img = render_page_to_image(file_path, i)
                pages.append(_process_image(img, i))

    _save_cache(file_path, pages)
    return pages
