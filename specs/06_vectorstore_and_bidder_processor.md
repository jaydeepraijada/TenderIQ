# Spec 06 — Vector Store and Bidder Processor

**Step:** 8 of 15  
**Time budget:** ~25 min  
**Checkpoint:** `process_bidder("bidder_a", ...)` indexes all docs; `gather_evidence("bidder_a", turnover_criterion)` returns chunks mentioning the turnover figure.

---

## Goal

Implement `core/vectorstore.py` (ChromaDB persistent client helpers) and `core/bidder_processor.py` (document ingestion + evidence retrieval per criterion).

---

## `core/vectorstore.py`

Uses ChromaDB persistent client with `sentence-transformers/all-MiniLM-L6-v2` embeddings.

### `get_client()`

```python
@st.cache_resource
def get_client():
    import chromadb
    from core.config import CHROMA_DIR
    return chromadb.PersistentClient(path=CHROMA_DIR)
```

### `get_collection(name: str)`

```python
def get_collection(name: str):
    client = get_client()
    return client.get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"},
    )
```

Note: ChromaDB default embedding function uses `all-MiniLM-L6-v2` (~80 MB, downloaded on first run).

### `add_chunks(collection, chunks: list[dict], metadatas: list[dict]) -> None`

- IDs: `hashlib.sha256(chunk["text"].encode()).hexdigest()[:16]` — deduplicates across reruns.
- Calls `collection.upsert(documents=[c["text"] for c in chunks], ids=ids, metadatas=metadatas)`.

### `query(collection, text: str, k: int = 4, where: dict | None = None) -> list[dict]`

- Calls `collection.query(query_texts=[text], n_results=k, where=where)` (omit `where` if None).
- Returns `[{"text": doc, "metadata": meta, "distance": dist}, ...]` from the first result set.
- Handle the case where fewer than `k` documents are in the collection (ChromaDB raises if `n_results > len(collection)`).

---

## `core/bidder_processor.py`

### `process_bidder(bidder_id: str, files: list[Path]) -> None`

For each file in `files`:
1. `pages = ocr_pipeline.extract_document(file)`.
2. `chunks = chunker.chunk_bidder(pages, bidder_id, file.name)`.
3. Build metadatas list — one per chunk:
   ```python
   {"bidder_id": bidder_id, "doc_name": file.name,
    "page": chunk["page"], "source_type": chunk["source_type"],
    "ocr_confidence": chunk["ocr_confidence"]}
   ```
4. `collection = vectorstore.get_collection("bidder_chunks")`.
5. `vectorstore.add_chunks(collection, chunks, metadatas)`.
6. `audit.log("bidder_processed", bidder_id=bidder_id, doc_name=file.name, chunk_count=len(chunks))`.

### `gather_evidence(bidder_id: str, criterion: Criterion, k: int = 4) -> list[Evidence]`

1. Build query string: `f"{criterion.title} {' '.join(criterion.query_hints)}"`.
2. `collection = vectorstore.get_collection("bidder_chunks")`.
3. `results = vectorstore.query(collection, query, k=k, where={"bidder_id": bidder_id})`.
4. Map each result to `Evidence`:
   ```python
   Evidence(
       bidder_id=bidder_id,
       doc_name=meta["doc_name"],
       page=meta["page"],
       text=result["text"],
       source_type=meta["source_type"],
       ocr_confidence=meta.get("ocr_confidence"),
   )
   ```
5. Return list.

---

## Acceptance Criteria

1. `process_bidder("bidder_a", [path1, path2, ...])` completes without error and logs audit entries.
2. `gather_evidence("bidder_a", c1_criterion)` returns at least 1 `Evidence` object.
3. The strongest evidence for Bidder A's turnover mentions "6,20,00,000" or "INR".
4. Calling `process_bidder` twice on the same files does not duplicate chunks (upsert).
