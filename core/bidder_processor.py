from pathlib import Path

from core import audit, vectorstore
from core.chunker import chunk_bidder
from core.ocr_pipeline import extract_document
from core.schemas import Criterion, Evidence


def process_bidder(bidder_id: str, files: list[Path]) -> None:
    collection = vectorstore.get_collection("bidder_chunks")
    for file in files:
        pages = extract_document(file)
        chunks = chunk_bidder(pages, bidder_id, file.name)
        if not chunks:
            continue
        metadatas = [
            {
                "bidder_id": bidder_id,
                "doc_name": chunk["doc_name"],
                "page": chunk["page"],
                "source_type": chunk["source_type"],
                "ocr_confidence": float(chunk["ocr_confidence"])
                if chunk["ocr_confidence"] is not None else -1.0,
            }
            for chunk in chunks
        ]
        vectorstore.add_chunks(collection, chunks, metadatas)
        audit.log(
            "bidder_processed",
            bidder_id=bidder_id,
            doc_name=file.name,
            chunk_count=len(chunks),
        )


def gather_evidence(bidder_id: str, criterion: Criterion, k: int = 4) -> list[Evidence]:
    query_text = f"{criterion.title} {' '.join(criterion.query_hints)}"
    collection = vectorstore.get_collection("bidder_chunks")
    results = vectorstore.query(
        collection, query_text, k=k, where={"bidder_id": bidder_id}
    )
    evidence = []
    for r in results:
        meta = r["metadata"]
        ocr_conf = meta.get("ocr_confidence")
        if ocr_conf is not None and ocr_conf < 0:
            ocr_conf = None
        evidence.append(Evidence(
            bidder_id=bidder_id,
            doc_name=meta["doc_name"],
            page=meta["page"],
            text=r["text"],
            source_type=meta["source_type"],
            ocr_confidence=ocr_conf,
        ))
    return evidence
