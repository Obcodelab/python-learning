"""Vector databases store embeddings and find the nearest ones to a query
vector quickly. This file builds a tiny in-memory version with the two
operations such a store provides: upsert(id, vector, metadata) and
query(vector, top_k)."""

import math
import re
from dataclasses import dataclass, field

_VOCAB = ["pinecone", "vector", "database", "chunk", "document", "rag", "model", "weather"]


def embed(text: str) -> list[float]:
    """Toy embedder (same idea as 12_embeddings.py), kept local so this file runs alone.

    Uses `term in word` so a plural or longer form still counts ('chunking'
    contains 'chunk'). A real embedding model would handle meaning properly."""
    words = re.findall(r"[a-z]+", text.lower())
    counts = [
        float(sum(1 for word in words if term in word))
        for term in _VOCAB
    ]
    length = math.sqrt(sum(c * c for c in counts)) or 1.0
    return [c / length for c in counts]


@dataclass
class Match:
    id: str
    score: float
    metadata: dict


@dataclass
class InMemoryIndex:
    _vectors: dict[str, list[float]] = field(default_factory=dict)
    _metadata: dict[str, dict] = field(default_factory=dict)

    def upsert(self, id: str, vector: list[float], metadata: dict | None = None) -> None:
        self._vectors[id] = vector
        self._metadata[id] = metadata or {}

    def query(self, vector: list[float], top_k: int = 3) -> list[Match]:
        scored = [
            Match(id, _cosine(vector, stored), self._metadata[id])
            for id, stored in self._vectors.items()
        ]
        scored.sort(key=lambda m: m.score, reverse=True)
        return scored[:top_k]

    def __len__(self) -> int:
        return len(self._vectors)


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(y * y for y in b)) or 1.0
    return dot / (na * nb)


def main() -> None:
    index = InMemoryIndex()

    facts = {
        "f1": "Pinecone is a vector database that stores embeddings",
        "f2": "Chunking splits a document before it is stored in the database",
        "f3": "RAG retrieves context from the vector store before asking the model",
        "f4": "The weather forecast predicts rain tomorrow afternoon",
    }
    for fact_id, text in facts.items():
        index.upsert(fact_id, embed(text), {"text": text})

    print("stored vectors:", len(index))

    results = index.query(embed("how does a vector database store embeddings"), top_k=3)
    for match in results:
        print(f"  {match.score:.3f}  {match.metadata['text']}")


if __name__ == "__main__":
    main()
