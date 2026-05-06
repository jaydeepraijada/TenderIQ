from pathlib import Path


class ExtractedPage:
    page: int
    text: str
    source_type: str  # "text_pdf" | "tesseract" | "vision_llm"
    confidence: float
    raw_tier_results: dict


def extract_document(file_path: Path) -> list[ExtractedPage]:
    raise NotImplementedError
