"""Bounded local RAG: normalized hashing embeddings in a Qdrant vector database."""

import hashlib
from pathlib import Path
from uuid import NAMESPACE_URL, uuid5

from pypdf import PdfReader
from qdrant_client import QdrantClient, models
from sklearn.feature_extraction.text import HashingVectorizer


class Corpus:
    def __init__(self, folder="corpus", path=None, chunk_size=900, overlap=150):
        if not 0 <= overlap < chunk_size:
            raise ValueError("Chunk overlap must be smaller than chunk size")
        self.encoder = HashingVectorizer(
            n_features=512, alternate_sign=False, norm="l2", ngram_range=(1, 2)
        )
        self.client = QdrantClient(path=path) if path else QdrantClient(":memory:")
        self.docs = {}
        for file in sorted(Path(folder).rglob("*")):
            if file.suffix not in {".md", ".txt", ".pdf"}:
                continue
            text = (
                "\n".join(page.extract_text() or "" for page in PdfReader(file).pages)
                if file.suffix == ".pdf"
                else file.read_text()
            )
            self.docs[file.stem] = text
        if not self.docs:
            raise ValueError("Corpus has no supported documents")
        identity = repr((self.docs, chunk_size, overlap)).encode()
        self.fingerprint = hashlib.sha256(identity).hexdigest()
        self.collection = "knowledge_" + self.fingerprint[:12]
        if not self.client.collection_exists(self.collection):
            self.client.create_collection(
                self.collection,
                vectors_config=models.VectorParams(size=512, distance=models.Distance.COSINE),
            )
            points = []
            for source_id, text in self.docs.items():
                for offset in range(0, len(text), chunk_size - overlap):
                    chunk = text[offset : offset + chunk_size]
                    vector = self.encoder.transform([chunk]).toarray()[0].tolist()
                    points.append(
                        models.PointStruct(
                            id=str(
                                uuid5(NAMESPACE_URL, f"{source_id}:{offset}:{self.fingerprint}")
                            ),
                            vector=vector,
                            payload={"source_id": source_id, "offset": offset, "text": chunk},
                        )
                    )
            self.client.upsert(self.collection, points)

    def search(self, query, top_k=3, source_id=None):
        if not isinstance(query, str) or not 1 <= len(query) <= 1000:
            raise ValueError("Search query must contain 1–1000 characters")
        if not 1 <= top_k <= 8:
            raise ValueError("top_k must be 1–8")
        filter_ = (
            models.Filter(
                must=[
                    models.FieldCondition(key="source_id", match=models.MatchValue(value=source_id))
                ]
            )
            if source_id
            else None
        )
        vector = self.encoder.transform([query]).toarray()[0].tolist()
        hits = self.client.query_points(
            self.collection, query=vector, query_filter=filter_, limit=top_k, score_threshold=0.03
        ).points
        return [{**hit.payload, "score": float(hit.score)} for hit in hits]

    def read(self, source_id):
        if source_id not in self.docs:
            raise ValueError("Unknown source ID")
        return {"source_id": source_id, "text": self.docs[source_id][:8000]}
