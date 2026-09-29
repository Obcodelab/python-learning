"""Postgres + pgvector integration tests, skipped unless TEST_DATABASE_URL is
set. Each test uses its own table and drops it afterwards.

    TEST_DATABASE_URL=postgresql:///siwes_rag uv run pytest -k pg_store"""

from __future__ import annotations

import sys
import uuid
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ..indexer import Config, DocumentIndexer, FakeEmbedder, PgVectorStore, Record

# Comes from TEST_DATABASE_URL (shell env or this project's .env).
TEST_DATABASE_URL = Config.from_env().test_database_url

pytestmark = pytest.mark.skipif(
    not TEST_DATABASE_URL,
    reason="set TEST_DATABASE_URL to run the Postgres integration tests",
)


@pytest.fixture
def store():
    table = f"test_chunks_{uuid.uuid4().hex[:8]}"
    config = Config(database_url=TEST_DATABASE_URL, pg_table=table)
    embedder = FakeEmbedder()
    pg = PgVectorStore(config, embedder.dimension)
    try:
        yield pg, embedder
    finally:
        pg._conn.execute(f"DROP TABLE IF EXISTS {table}")
        pg._conn.close()


def test_upsert_query_and_count(store):
    pg, embedder = store
    texts = ["chunking splits a document", "the cafeteria serves lunch at noon"]
    vectors = embedder.embed(texts)
    pg.upsert(
        [
            Record(f"a-{i}", v, {"source": "a.txt", "chunk_index": i, "text": t})
            for i, (t, v) in enumerate(zip(texts, vectors))
        ]
    )

    assert pg.count() == 2

    hits = pg.query(embedder.embed(["how does document chunking work"])[0], top_k=1)
    assert hits and hits[0].metadata["text"] == "chunking splits a document"
    assert hits[0].metadata["source"] == "a.txt"


def test_upsert_is_idempotent_and_delete_by_source(store):
    pg, embedder = store
    rec = Record(
        "x-0",
        embedder.embed(["hello"])[0],
        {"source": "x.txt", "chunk_index": 0, "text": "hello"},
    )
    pg.upsert([rec])
    pg.upsert([rec])  # same id again
    assert pg.count() == 1

    pg.delete_by_source("x.txt")
    assert pg.count() == 0


def test_pipeline_end_to_end_on_postgres(store, tmp_path):
    pg, embedder = store
    config = Config(
        database_url=TEST_DATABASE_URL,
        pg_table=pg._table,
        chunk_size=30,
        chunk_overlap=5,
    )
    indexer = DocumentIndexer(config, embedder=embedder, store=pg)

    doc = tmp_path / "notes.txt"
    doc.write_text(
        "A vector database stores embeddings and searches them by similarity. "
        "Pinecone is one hosted example; Postgres with pgvector is another.",
        encoding="utf-8",
    )
    assert indexer.index_file(doc) >= 1

    results = indexer.search("what stores embeddings", top_k=2)
    assert results
    assert "vector database" in results[0].text.lower()
