"""Document Indexer package.

The indexing half of a RAG pipeline: chunk a document, embed the chunks and
store the vectors so they can be searched by meaning.
"""

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
