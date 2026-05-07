"""
In-memory vector store.
Primary: sentence-transformers all-MiniLM-L6-v2 + cosine similarity.
Fallback: BM25 keyword retrieval (if sentence-transformers fails to load).
"""
import hashlib
import math
import re
import numpy as np
import streamlit as st


# ── Embedding model (primary) ─────────────────────────────────────────────────

@st.cache_resource(show_spinner="Loading embedding model…")
def _get_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer("all-MiniLM-L6-v2")


def _embed(texts: list[str]) -> np.ndarray | None:
    try:
        model = _get_model()
        embs = model.encode(texts, show_progress_bar=False, convert_to_numpy=True)
        return embs.astype(np.float32)
    except Exception:
        return None


# ── BM25 fallback ─────────────────────────────────────────────────────────────

def _tokenize(text: str) -> list[str]:
    words = re.findall(r"[a-z0-9]+", text.lower())
    bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words) - 1)]
    return words + bigrams


def _bm25_score(q_toks: list[str], doc_toks: list[str],
                df: dict[str, int], n_docs: int) -> float:
    k1, b, avgdl = 1.5, 0.75, 150.0
    dl = len(doc_toks)
    tf: dict[str, int] = {}
    for t in doc_toks:
        tf[t] = tf.get(t, 0) + 1
    score = 0.0
    for term in set(q_toks):
        f = tf.get(term, 0)
        if not f:
            continue
        idf = math.log((n_docs - df.get(term, 0) + 0.5) /
                       (df.get(term, 0) + 0.5) + 1)
        score += idf * f * (k1 + 1) / (f + k1 * (1 - b + b * dl / avgdl))
    return score


# ── Collection ────────────────────────────────────────────────────────────────

class _Collection:
    def __init__(self, name: str):
        self.name     = name
        self._ids:    list[str]         = []
        self._docs:   list[str]         = []
        self._metas:  list[dict]        = []
        self._embs:   np.ndarray        = np.empty((0, 384), dtype=np.float32)
        # BM25 fallback structures
        self._tokens: list[list[str]]   = []
        self._df:     dict[str, int]    = {}

    def count(self) -> int:
        return len(self._docs)

    def upsert(self, documents: list[str], ids: list[str],
               metadatas: list[dict]) -> None:
        new_embs = _embed(documents)  # None if model unavailable

        for i, (doc, did, meta) in enumerate(zip(documents, ids, metadatas)):
            toks = _tokenize(doc)
            if did in self._ids:
                idx = self._ids.index(did)
                for t in set(self._tokens[idx]):
                    self._df[t] = max(0, self._df.get(t, 1) - 1)
                self._docs[idx]   = doc
                self._metas[idx]  = meta
                self._tokens[idx] = toks
                if new_embs is not None and self._embs.shape[0] > idx:
                    self._embs[idx] = new_embs[i]
            else:
                self._ids.append(did)
                self._docs.append(doc)
                self._metas.append(meta)
                self._tokens.append(toks)
                if new_embs is not None:
                    row = new_embs[i:i+1]
                    self._embs = (np.vstack([self._embs, row])
                                  if self._embs.shape[0] else row.copy())
            for t in set(toks):
                self._df[t] = self._df.get(t, 0) + 1

    def query(self, query_texts: list[str], n_results: int,
              where: dict | None = None) -> dict:
        empty = {"documents": [[]], "metadatas": [[]], "distances": [[]]}
        if not self._docs:
            return empty

        candidates = [i for i in range(len(self._docs))
                      if not where or
                      all(self._metas[i].get(k) == v for k, v in where.items())]
        if not candidates:
            return empty

        # Primary: cosine similarity
        if self._embs.shape[0] == len(self._docs):
            q_emb = _embed([query_texts[0]])
            if q_emb is not None:
                q = q_emb[0] / (np.linalg.norm(q_emb[0]) + 1e-9)
                cand_embs = self._embs[candidates]
                norms = np.linalg.norm(cand_embs, axis=1, keepdims=True) + 1e-9
                scores = (cand_embs / norms) @ q
                top_idx = sorted(range(len(candidates)),
                                 key=lambda x: scores[x], reverse=True)[:n_results]
                top = [candidates[x] for x in top_idx]
                return {
                    "documents": [[self._docs[i] for i in top]],
                    "metadatas": [[self._metas[i] for i in top]],
                    "distances": [[float(1 - scores[x]) for x in top_idx]],
                }

        # Fallback: BM25
        q_toks = _tokenize(query_texts[0])
        n = len(self._docs)
        scored = sorted(candidates,
                        key=lambda i: _bm25_score(q_toks, self._tokens[i],
                                                  self._df, n),
                        reverse=True)[:n_results]
        max_s = _bm25_score(q_toks, self._tokens[scored[0]], self._df, n) if scored else 1.0
        return {
            "documents": [[self._docs[i] for i in scored]],
            "metadatas": [[self._metas[i] for i in scored]],
            "distances": [[1 - _bm25_score(q_toks, self._tokens[i],
                                           self._df, n) / max(max_s, 1e-9)
                           for i in scored]],
        }


# ── Public API ────────────────────────────────────────────────────────────────

@st.cache_resource
def _get_store() -> dict[str, _Collection]:
    return {}


def get_collection(name: str) -> _Collection:
    store = _get_store()
    if name not in store:
        store[name] = _Collection(name)
    return store[name]


def add_chunks(collection: _Collection, chunks: list[dict],
               metadatas: list[dict]) -> None:
    if not chunks:
        return
    ids = [hashlib.sha256(c["text"].encode()).hexdigest()[:16] for c in chunks]
    collection.upsert(
        documents=[c["text"] for c in chunks],
        ids=ids,
        metadatas=metadatas,
    )


def query(collection: _Collection, text: str, k: int = 4,
          where: dict | None = None) -> list[dict]:
    if collection.count() == 0:
        return []
    n = min(k, collection.count())
    results = collection.query(query_texts=[text], n_results=n, where=where)
    return [
        {"text": doc, "metadata": meta, "distance": dist}
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        )
    ]
