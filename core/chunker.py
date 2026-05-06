import re

from core.ocr_pipeline import ExtractedPage

_MAX_CHUNK_CHARS = 2000


def chunk_tender(pages: list[dict], tender_id: str) -> list[dict]:
    chunks = []
    for page_dict in pages:
        page_no = page_dict["page"]
        text = page_dict["text"].strip()
        if not text:
            continue
        if len(text) <= _MAX_CHUNK_CHARS:
            pieces = [text]
        else:
            # Split on clause headings or double newlines
            splits = re.split(r'(?m)(?=^\d+(\.\d+)*\s+)', text)
            pieces = []
            current = ""
            for s in splits:
                if len(current) + len(s) <= _MAX_CHUNK_CHARS:
                    current += s
                else:
                    if current:
                        pieces.append(current)
                    current = s
            if current:
                pieces.append(current)

        for i, piece in enumerate(pieces):
            piece = piece.strip()
            if not piece:
                continue
            chunks.append({
                "text": piece,
                "tender_id": tender_id,
                "page": page_no,
                "chunk_id": f"{tender_id}_p{page_no}_c{i}",
            })
    return chunks


def chunk_bidder(
    pages: list[ExtractedPage], bidder_id: str, doc_name: str
) -> list[dict]:
    chunks = []
    for page in pages:
        text = page.text.strip() if page.text else ""
        if not text:
            continue
        safe_doc = doc_name.replace("/", "_").replace("\\", "_")
        chunks.append({
            "text": text,
            "bidder_id": bidder_id,
            "doc_name": doc_name,
            "page": page.page,
            "source_type": page.source_type,
            "ocr_confidence": page.confidence,
            "chunk_id": f"{bidder_id}_{safe_doc}_p{page.page}",
        })
    return chunks
