"""The pipeline that ties the steps together.

    index_file(path)  ->  read -> chunk -> embed -> store
    search(query)     ->  embed query -> store.query -> ranked chunks
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from pathlib import Path

from .chunking import chunk_text
from .config import Config
from .embeddings import Embedder, get_embedder
from .vector_store import Match, Record, VectorStore, get_store


@dataclass
class SearchResult:
    score: float
    text: str
    source: str
    chunk_index: int

    @classmethod
    def from_match(cls, match: Match) -> "SearchResult":
        meta = match.metadata
        return cls(
            score=match.score,
            text=meta.get("text", ""),
            source=meta.get("source", "unknown"),
            chunk_index=int(meta.get("chunk_index", 0)),
        )


class DocumentIndexer:
    def __init__(
        self,
        config: Config | None = None,
        *,
        embedder: Embedder | None = None,
        store: VectorStore | None = None,
    ) -> None:
        self.config = config or Config.from_env()
        self.embedder = embedder or get_embedder(self.config)
        self.store = store or get_store(self.config, self.embedder)

    # --- indexing ---

    def index_file(self, path: str | Path) -> int:
        path = Path(path)
        text = path.read_text(encoding="utf-8")
        return self.index_text(text, source=path.name)

    def index_text(self, text: str, source: str) -> int:
        chunks = chunk_text(
            text,
            chunk_size=self.config.chunk_size,
            overlap=self.config.chunk_overlap,
        )
        if not chunks:
            return 0

        # Replace any existing chunks for this source so re-indexing is clean.
        self.store.delete_by_source(source)

        vectors = self.embedder.embed(chunks)
        records = [
            Record(
                id=self._chunk_id(source, i),
                vector=vector,
                metadata={
                    "text": chunk,
                    "source": source,
                    "chunk_index": i,
                },
            )
            for i, (chunk, vector) in enumerate(zip(chunks, vectors))
        ]
        self.store.upsert(records)
        return len(records)

    # --- searching ---

    def search(self, query: str, top_k: int = 3) -> list[SearchResult]:
        query_vector = self.embedder.embed([query])[0]
        matches = self.store.query(query_vector, top_k=top_k)
        return [SearchResult.from_match(m) for m in matches]

    # --- misc ---

    def info(self) -> dict:
        return {
            "embedder": self.embedder.name,
            "dimension": self.embedder.dimension,
            "store": self.store.name,
            "location": self.store.location,
            "chunks_stored": self.store.count(),
            "chunk_size": self.config.chunk_size,
            "chunk_overlap": self.config.chunk_overlap,
        }

    @staticmethod
    def _chunk_id(source: str, index: int) -> str:
        digest = hashlib.sha1(f"{source}:{index}".encode("utf-8")).hexdigest()[:16]
        return f"{source}-{index}-{digest}"
