"""ChromaDB + sentence-transformers retrieval layer (in-memory, one collection per session)."""
import sys

import streamlit as st

EMBED_MODEL = "all-MiniLM-L6-v2"


@st.cache_resource(show_spinner=False)
def _model():
    from sentence_transformers import SentenceTransformer

    return SentenceTransformer(EMBED_MODEL)


@st.cache_resource(show_spinner=False)
def _client():
    # Streamlit Cloud ships an old sqlite3; swap in pysqlite3 when available.
    try:
        __import__("pysqlite3")
        sys.modules["sqlite3"] = sys.modules.pop("pysqlite3")
    except Exception:
        pass
    import chromadb

    return chromadb.EphemeralClient()


def _collection():
    name = f"studymate_{st.session_state.sid}"
    return _client().get_or_create_collection(name=name, metadata={"hnsw:space": "cosine"})


def _embed(texts):
    return _model().encode(texts, batch_size=32, show_progress_bar=False, normalize_embeddings=True).tolist()


def add_document(doc_id, doc_name, chunks):
    col = _collection()
    for start in range(0, len(chunks), 128):
        batch = chunks[start:start + 128]
        col.add(
            ids=[f"{doc_id}-{start + i}" for i in range(len(batch))],
            documents=batch,
            embeddings=_embed(batch),
            metadatas=[{"doc_id": doc_id, "doc_name": doc_name, "chunk": start + i} for i in range(len(batch))],
        )


def query(question, k=4, doc_id=None):
    """Return the most relevant chunks. Safe on an empty collection."""
    col = _collection()
    if doc_id:
        total = len(col.get(where={"doc_id": doc_id}, include=[])["ids"])
    else:
        total = col.count()
    if total == 0:
        return []
    kwargs = {"query_embeddings": _embed([question]), "n_results": min(k, total)}
    if doc_id:
        kwargs["where"] = {"doc_id": doc_id}
    res = col.query(**kwargs)
    docs = res.get("documents", [[]])[0]
    metas = res.get("metadatas", [[]])[0]
    dists = res.get("distances", [[]])[0]
    return [
        {"text": t, "doc_name": m.get("doc_name", "Document"), "distance": d}
        for t, m, d in zip(docs, metas, dists)
    ]


def delete_document(doc_id):
    try:
        _collection().delete(where={"doc_id": doc_id})
    except Exception:
        pass


def reset():
    try:
        _client().delete_collection(f"studymate_{st.session_state.sid}")
    except Exception:
        pass
