"""Tests for the Document Indexer, using the offline backends only."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from ..indexer import Config, DocumentIndexer, FakeEmbedder, InMemoryStore, Record
from ..indexer.chunking import chunk_text


def test_chunk_text_respects_size_and_overlap():
    text = " ".join(str(i) for i in range(100))
    chunks = chunk_text(text, chunk_size=30, overlap=5)

    assert all(len(c.split()) <= 30 for c in chunks)
    # every word appears somewhere
    seen = {w for c in chunks for w in c.split()}
    assert seen == {str(i) for i in range(100)}
    # neighbouring chunks share the overlap
    first_words = chunks[0].split()
    second_words = chunks[1].split()
    assert first_words[-5:] == second_words[:5]


def test_chunk_text_empty_input():
    assert chunk_text("   ") == []


def test_chunk_text_rejects_bad_overlap():
    with pytest.raises(ValueError):
        chunk_text("a b c", chunk_size=5, overlap=5)


# --- fake embedder ---


def test_fake_embedder_is_deterministic():
    embedder = FakeEmbedder()
    a = embedder.embed(["retrieval augmented generation"])[0]
    b = embedder.embed(["retrieval augmented generation"])[0]
    assert a == b
    assert len(a) == embedder.dimension


def test_fake_embedder_similar_text_scores_higher(tmp_path):
    embedder = FakeEmbedder()
    store = InMemoryStore(tmp_path / "index.json")

    vecs = embedder.embed(
        [
            "chunking splits a document into smaller pieces",
            "the museum opens at nine and closes at five",
        ]
    )
    store.upsert(
        [
            Record("related", vecs[0], {"text": "chunking"}),
            Record("unrelated", vecs[1], {"text": "museum hours"}),
        ]
    )

    query = embedder.embed(["how does document chunking work"])[0]
    matches = store.query(query, top_k=2)
    assert matches[0].id == "related"
    assert matches[0].score >= matches[1].score


# --- end to end ---


@pytest.fixture
def indexer(tmp_path) -> DocumentIndexer:
    config = Config(index_path=tmp_path / "index.json", chunk_size=40, chunk_overlap=10)
    return DocumentIndexer(
        config, embedder=FakeEmbedder(), store=InMemoryStore(config.index_path)
    )


def test_index_and_search_roundtrip(indexer, tmp_path):
    doc = tmp_path / "notes.txt"
    doc.write_text(
        "A vector database stores embeddings and searches them by similarity. "
        "Pinecone is one example. "
        "Separately, the cafeteria serves lunch between noon and two o'clock.",
        encoding="utf-8",
    )

    count = indexer.index_file(doc)
    assert count >= 1

    results = indexer.search("what is a vector database", top_k=2)
    assert results
    assert "vector database" in results[0].text.lower()
    assert results[0].source == "notes.txt"


def test_reindexing_replaces_old_chunks(indexer, tmp_path):
    doc = tmp_path / "doc.txt"
    doc.write_text("first version about embeddings " * 20, encoding="utf-8")
    indexer.index_file(doc)
    first_count = indexer.store.count()

    doc.write_text("second version about retrieval " * 20, encoding="utf-8")
    indexer.index_file(doc)

    # count should reflect only the new version, not both
    assert indexer.store.count() == first_count
    results = indexer.search("retrieval", top_k=1)
    assert "retrieval" in results[0].text.lower()


def test_persistence_between_instances(tmp_path):
    config = Config(index_path=tmp_path / "index.json", chunk_size=40, chunk_overlap=10)
    one = DocumentIndexer(
        config, embedder=FakeEmbedder(), store=InMemoryStore(config.index_path)
    )
    one.index_text("embeddings capture meaning as numbers " * 10, source="a.txt")

    two = DocumentIndexer(
        config, embedder=FakeEmbedder(), store=InMemoryStore(config.index_path)
    )
    assert two.store.count() > 0
    assert two.search("meaning", top_k=1)
