"""Embedders.

An embedder turns a list of texts into a list of vectors of equal length.

- FakeEmbedder works offline and is deterministic, so tests and demos are
  repeatable. It hashes words into a fixed number of buckets and normalises
  the result, which is enough for the similarity search to behave sensibly.
- OpenAIEmbedder calls the real API. It is only imported when used.
"""

from __future__ import annotations

import hashlib
import math
import re
from typing import Protocol

from .config import Config


class Embedder(Protocol):
    dimension: int
    name: str

    def embed(self, texts: list[str]) -> list[list[float]]: ...


def _tokenise(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def _l2_normalise(vector: list[float]) -> list[float]:
    length = math.sqrt(sum(v * v for v in vector))
    if length == 0:
        return vector
    return [v / length for v in vector]


class FakeEmbedder:
    """Deterministic offline embedder using the hashing trick."""

    name = "fake"

    def __init__(self, dimension: int = 256) -> None:
        self.dimension = dimension

    def embed(self, texts: list[str]) -> list[list[float]]:
        return [self._embed_one(text) for text in texts]

    def _embed_one(self, text: str) -> list[float]:
        vector = [0.0] * self.dimension
        for token in _tokenise(text):
            digest = hashlib.md5(token.encode("utf-8")).digest()
            bucket = int.from_bytes(digest[:4], "big") % self.dimension
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[bucket] += sign
        return _l2_normalise(vector)


class OpenAIEmbedder:
    """Wraps the OpenAI embeddings API."""

    name = "openai"

    # Output dimensions for the common models.
    _DIMENSIONS = {
        "text-embedding-3-small": 1536,
        "text-embedding-3-large": 3072,
        "text-embedding-ada-002": 1536,
    }

    def __init__(self, api_key: str, model: str) -> None:
        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover - depends on optional extra
            raise RuntimeError(
                "openai package not installed. Run: uv sync --extra openai"
            ) from exc

        self._client = OpenAI(api_key=api_key)
        self.model = model
        self.dimension = self._DIMENSIONS.get(model, 1536)

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        response = self._client.embeddings.create(model=self.model, input=texts)
        # The API returns items in the same order as the input.
        return [item.embedding for item in response.data]


def get_embedder(config: Config) -> Embedder:
    if config.use_openai:
        return OpenAIEmbedder(config.openai_api_key, config.openai_embedding_model)
    return FakeEmbedder()
