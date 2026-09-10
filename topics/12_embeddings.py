"""Embeddings.

An embedding is a list of numbers that represents the meaning of a piece of
text. Texts with similar meaning end up close together in vector space, so we
can compare them with a similarity measure instead of matching exact words.

This file uses a small hand-made embedder (word counting) just to show the
idea. Real models like OpenAI's text-embedding-3-small return vectors with
hundreds of dimensions.
"""

import math
import re

VOCAB = ["python", "recipe", "embedding", "vector", "database", "search", "rag", "model"]


def embed(text: str) -> list[float]:
    """Very rough embedding: how often each vocab term appears, normalised.

    The check is `term in word` rather than `word == term`, so a plural or
    longer form still counts ('databases' contains 'database'). A real
    embedding model handles plurals, synonyms and meaning properly; this is
    just enough to make the demo behave sensibly.
    """
    words = re.findall(r"[a-z]+", text.lower())
    counts = [
        float(sum(1 for word in words if term in word))
        for term in VOCAB
    ]
    length = math.sqrt(sum(c * c for c in counts)) or 1.0
    return [c / length for c in counts]


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """1.0 means identical direction, 0.0 means unrelated."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a)) or 1.0
    norm_b = math.sqrt(sum(y * y for y in b)) or 1.0
    return dot / (norm_a * norm_b)


def main() -> None:
    query = "how do vector databases help search"
    documents = [
        "Pinecone is a vector database used for similarity search",
        "This recipe needs two cups of flour and one egg",
        "An embedding model turns text into a vector",
    ]

    query_vec = embed(query)
    print("query vector:", [round(x, 2) for x in query_vec])

    ranked = sorted(
        documents,
        key=lambda doc: cosine_similarity(query_vec, embed(doc)),
        reverse=True,
    )

    print("\nmost relevant first:")
    for doc in ranked:
        score = cosine_similarity(query_vec, embed(doc))
        print(f"  {score:.3f}  {doc}")


if __name__ == "__main__":
    main()
