"""Configuration, loaded from environment variables (and a .env file)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

_PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Load this project's .env by absolute path so the active backend is the same
# no matter which directory the command is run from.
load_dotenv(_PROJECT_ROOT / ".env")

# Default location for the offline JSON vector store.
_DEFAULT_INDEX_PATH = _PROJECT_ROOT / "data" / "index.json"


@dataclass
class Config:
    openai_api_key: str | None = None
    openai_embedding_model: str = "text-embedding-3-small"

    # Postgres + pgvector. When set, it replaces the local JSON store.
    database_url: str | None = None
    pg_table: str = "document_chunks"

    # Only used by the Postgres integration tests (tests/test_pg_store.py).
    test_database_url: str | None = None

    chunk_size: int = 120       # words per chunk
    chunk_overlap: int = 20     # words shared between neighbouring chunks

    index_path: Path = _DEFAULT_INDEX_PATH

    # Force the offline backends even when a key or DATABASE_URL is set.
    offline: bool = False

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            offline=os.getenv("INDEXER_OFFLINE", "").lower() in {"1", "true", "yes"},
            openai_api_key=os.getenv("OPENAI_API_KEY") or None,
            openai_embedding_model=os.getenv(
                "OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"
            ),
            database_url=os.getenv("DATABASE_URL") or None,
            pg_table=os.getenv("PG_TABLE", "document_chunks"),
            test_database_url=os.getenv("TEST_DATABASE_URL") or None,
            chunk_size=int(os.getenv("CHUNK_SIZE", "120")),
            chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "20")),
            index_path=Path(os.getenv("INDEX_PATH", str(_DEFAULT_INDEX_PATH))),
        )

    @property
    def use_openai(self) -> bool:
        return bool(self.openai_api_key) and not self.offline

    @property
    def use_postgres(self) -> bool:
        return bool(self.database_url) and not self.offline
