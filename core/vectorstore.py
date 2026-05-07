import hashlib

import streamlit as st

from core.config import CHROMA_DIR


@st.cache_resource
def get_client():
    import chromadb
    # EphemeralClient (in-memory) avoids all ChromaDB 0.5.x tenant/SQLite
    # compatibility issues. The index is rebuilt each evaluation run, so
    # persistence is not needed.
    return chromadb.EphemeralClient()


def get_collection(name: str):
    client = get_client()
    return client.get_or_create_collection(
        name=name,
        metadata={"hnsw:space": "cosine"},
    )


def add_chunks(collection, chunks: list[dict], metadatas: list[dict]) -> None:
    if not chunks:
        return
    ids = [
        hashlib.sha256(c["text"].encode()).hexdigest()[:16]
        for c in chunks
    ]
    collection.upsert(
        documents=[c["text"] for c in chunks],
        ids=ids,
        metadatas=metadatas,
    )


def query(
    collection, text: str, k: int = 4, where: dict | None = None
) -> list[dict]:
    count = collection.count()
    if count == 0:
        return []
    n = min(k, count)
    kwargs: dict = {"query_texts": [text], "n_results": n}
    if where:
        kwargs["where"] = where
    results = collection.query(**kwargs)
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    dists = results["distances"][0]
    return [
        {"text": doc, "metadata": meta, "distance": dist}
        for doc, meta, dist in zip(docs, metas, dists)
    ]
