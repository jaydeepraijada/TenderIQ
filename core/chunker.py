from core.ocr_pipeline import ExtractedPage


def chunk_tender(pages: list[dict], tender_id: str) -> list[dict]:
    raise NotImplementedError


def chunk_bidder(
    pages: list[ExtractedPage], bidder_id: str, doc_name: str
) -> list[dict]:
    raise NotImplementedError
