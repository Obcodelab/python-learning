"""Splitting a document into overlapping chunks.

Chunks are measured in words. A small overlap keeps a sentence that falls on a
boundary from being cut off from its context in both chunks.
"""

from __future__ import annotations

import re


def normalise(text: str) -> str:
    """Collapse whitespace so word counting is predictable."""
    return re.sub(r"\s+", " ", text).strip()


def chunk_text(text: str, chunk_size: int = 120, overlap: int = 20) -> list[str]:
    """Return a list of chunk strings.

    chunk_size: maximum words in a chunk
    overlap:    words repeated from the end of one chunk at the start of the next
    """
    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be >= 0 and smaller than chunk_size")

    words = normalise(text).split()
    if not words:
        return []

    step = chunk_size - overlap
    chunks: list[str] = []
    for start in range(0, len(words), step):
        window = words[start : start + chunk_size]
        if not window:
            break
        chunks.append(" ".join(window))
        if start + chunk_size >= len(words):
            break
    return chunks
