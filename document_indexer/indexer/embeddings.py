"""Embedders: turn a list of texts into a list of equal-length vectors.

FakeEmbedder is deterministic and offline; GeminiEmbedder calls Google's
free-tier Gemini API and is only imported when used."""

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


class GeminiEmbedder:
    """Wraps Google's Gemini embeddings API (gemini-embedding-001).

    Output is truncated to 768 dims (pgvector's HNSW cap is 2000) via MRL and
    re-normalised, since Gemini only guarantees unit length at full dimension."""

    name = "gemini"

    # Output dimension actually used (after MRL truncation for the default model).
    _DIMENSIONS = {
        "gemini-embedding-001": 768,
    }

    def __init__(self, api_key: str, model: str) -> None:
        try:
            from google import genai
            from google.genai import types
        except ImportError as exc:  # pragma: no cover - depends on optional extra
            raise RuntimeError(
                "google-genai package not installed. Run: uv sync --extra gemini"
            ) from exc

        self._client = genai.Client(api_key=api_key)
        self.model = model
        self.dimension = self._DIMENSIONS.get(model, 768)
        self._config = types.EmbedContentConfig(output_dimensionality=self.dimension)

    def embed(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        response = self._client.models.embed_content(
            model=self.model, contents=texts, config=self._config
        )
        # The API returns items in the same order as the input.
        return [_l2_normalise(item.values) for item in response.embeddings]


def get_embedder(config: Config) -> Embedder:
    if config.use_gemini:
        return GeminiEmbedder(config.gemini_api_key, config.gemini_embedding_model)
    return FakeEmbedder()
