"""Document Indexer: chunk a document, embed the chunks, store the vectors."""

from .config import Config
from .embeddings import FakeEmbedder
from .pipeline import DocumentIndexer, SearchResult
from .vector_store import InMemoryStore, PgVectorStore, Record

__all__ = [
    "Config",
    "DocumentIndexer",
    "FakeEmbedder",
    "InMemoryStore",
    "PgVectorStore",
    "Record",
    "SearchResult",
]
