# Document Indexer

Supporting project for the SIWES Python phase (Weeks 21–22).

It takes a document and turns it into something that can be searched by meaning:

```
document -> extract text -> chunk -> embed each chunk -> store vectors
                                                          |
                                        search(query) ----+--> closest chunks
```

This is the **indexing half** of a RAG system. The main project (`pdf-rag-bot`) adds the answering half on top of the
same steps.

## Backends

Both the embedder and the vector store are pluggable, so the project runs with nothing installed and upgrades
automatically when configured.

| Component    | Offline default                        | Real backend                    | Switches on          |
|--------------|----------------------------------------|---------------------------------|----------------------|
| Embedder     | `FakeEmbedder` (deterministic hashing) | OpenAI `text-embedding-3-small` | `OPENAI_API_KEY` set |
| Vector store | `InMemoryStore` (JSON file on disk)    | Postgres + `pgvector`           | `DATABASE_URL` set   |

`INDEXER_OFFLINE=1` forces the offline backends even when the others are configured.

## Setup

```bash
uv sync
# optional, only for the real backends:
uv sync --extra openai --extra postgres
```

Configuration comes from environment variables (a `.env` file is read automatically). See `.env.example`.

### Postgres

`DATABASE_URL` is a standard libpq connection string, e.g.
`postgresql:///siwes_rag` (local socket) or
`postgresql://user:pass@host:5432/dbname`. The `vector` extension must be
available on the server; the indexer runs `CREATE EXTENSION IF NOT EXISTS
vector` and creates its table with an HNSW cosine index on first use.

Each embedder gets its own table, `<PG_TABLE>_<embedder>` — e.g.
`document_chunks_fake` (256-dim) and `document_chunks_openai` (1536-dim) — so
toggling `OPENAI_API_KEY` / `INDEXER_OFFLINE` never collides and you never have
to drop anything. `uv run python document_indexer/main.py info` prints the
active table.

## Usage

```bash
# index a document (repeatable; re-indexing the same source replaces its chunks)
uv run python document_indexer/main.py index document_indexer/sample.txt

# search the index
uv run python document_indexer/main.py search "how does chunking work" --top-k 3

# show what backends are active and how many chunks are stored
uv run python document_indexer/main.py info
```

With the offline defaults the index is written to
`document_indexer/data/index.json`.

## Tests

```bash
uv run pytest
```
