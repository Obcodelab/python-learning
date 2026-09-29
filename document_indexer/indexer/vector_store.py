"""Vector stores keep (id, vector, metadata) records and return the ones
closest to a query vector. InMemoryStore saves to a JSON file; PgVectorStore
uses Postgres + pgvector and only imports its driver when used."""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Protocol

from .config import Config

if TYPE_CHECKING:
    from .embeddings import Embedder


@dataclass
class Record:
    id: str
    vector: list[float]
    metadata: dict


@dataclass
class Match:
    id: str
    score: float
    metadata: dict


class VectorStore(Protocol):
    name: str
    location: str  # where the vectors live: a file path or a table name

    def upsert(self, records: list[Record]) -> None: ...
    def query(self, vector: list[float], top_k: int) -> list[Match]: ...
    def delete_by_source(self, source: str) -> None: ...
    def count(self) -> int: ...


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a))
    nb = math.sqrt(sum(y * y for y in b))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


class InMemoryStore:
    name = "in-memory"

    def __init__(self, path: Path) -> None:
        self._path = path
        self.location = str(path)
        self._records: dict[str, Record] = {}
        self._load()

    def _load(self) -> None:
        if not self._path.exists():
            return
        raw = json.loads(self._path.read_text(encoding="utf-8"))
        for item in raw.get("records", []):
            self._records[item["id"]] = Record(
                id=item["id"], vector=item["vector"], metadata=item["metadata"]
            )

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "records": [
                {"id": r.id, "vector": r.vector, "metadata": r.metadata}
                for r in self._records.values()
            ]
        }
        self._path.write_text(json.dumps(payload), encoding="utf-8")

    def upsert(self, records: list[Record]) -> None:
        for record in records:
            self._records[record.id] = record
        self._save()

    def query(self, vector: list[float], top_k: int) -> list[Match]:
        matches = [
            Match(r.id, _cosine(vector, r.vector), r.metadata)
            for r in self._records.values()
        ]
        matches.sort(key=lambda m: m.score, reverse=True)
        return matches[:top_k]

    def delete_by_source(self, source: str) -> None:
        self._records = {
            rid: r
            for rid, r in self._records.items()
            if r.metadata.get("source") != source
        }
        self._save()

    def count(self) -> int:
        return len(self._records)


def _safe_table_name(name: str) -> str:
    """The table name comes from config, not user input, but keep it strict."""
    if not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*", name):
        raise ValueError(f"invalid PG_TABLE name: {name!r}")
    return name


class PgVectorStore:
    name = "postgres"

    def __init__(self, config: Config, dimension: int, *, table: str | None = None) -> None:
        try:
            import psycopg
            from pgvector import Vector
            from pgvector.psycopg import register_vector
        except ImportError as exc:  # pragma: no cover - optional extra
            raise RuntimeError(
                "Postgres support is not installed. Run: uv sync --extra postgres"
            ) from exc

        # pgvector only adapts its own Vector type (and numpy arrays), not a
        # plain list, so query/insert vectors are wrapped in Vector(...).
        self._Vector = Vector
        self._table = _safe_table_name(table or config.pg_table)
        self.location = self._table

        try:
            self._conn = psycopg.connect(config.database_url, autocommit=True)
        except psycopg.OperationalError as exc:
            raise RuntimeError(f"could not connect to DATABASE_URL: {exc}") from exc

        try:
            self._conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
        except psycopg.errors.InsufficientPrivilege as exc:
            raise RuntimeError(
                "the pgvector extension is missing and this role cannot CREATE "
                "EXTENSION. A superuser needs to run once: CREATE EXTENSION vector;"
            ) from exc

        register_vector(self._conn)
        self._ensure_schema(dimension)

    def _ensure_schema(self, dimension: int) -> None:
        self._conn.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {self._table} (
                id          text PRIMARY KEY,
                source      text NOT NULL,
                chunk_index integer NOT NULL,
                content     text NOT NULL,
                embedding   vector({dimension}) NOT NULL
            )
            """
        )
        self._conn.execute(
            f"""
            CREATE INDEX IF NOT EXISTS {self._table}_embedding_idx
            ON {self._table} USING hnsw (embedding vector_cosine_ops)
            """
        )
        self._conn.execute(
            f"CREATE INDEX IF NOT EXISTS {self._table}_source_idx "
            f"ON {self._table} (source)"
        )
        self._check_dimension(dimension)

    def _check_dimension(self, dimension: int) -> None:
        row = self._conn.execute(
            """
            SELECT format_type(a.atttypid, a.atttypmod)
            FROM pg_attribute a
            JOIN pg_class c ON c.oid = a.attrelid
            WHERE c.relname = %s AND a.attname = 'embedding'
            """,
            (self._table,),
        ).fetchone()
        if not row:
            return
        found = re.search(r"\((\d+)\)", row[0])
        if found and int(found.group(1)) != dimension:
            raise RuntimeError(
                f"table {self._table!r} stores vector({found.group(1)}) but the "
                f"active embedder produces {dimension}-dim vectors. Drop the table "
                f"(DROP TABLE {self._table};) or switch back to that embedder."
            )

    def upsert(self, records: list[Record]) -> None:
        if not records:
            return
        with self._conn.cursor() as cur:
            cur.executemany(
                f"""
                INSERT INTO {self._table} (id, source, chunk_index, content, embedding)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (id) DO UPDATE SET
                    source      = EXCLUDED.source,
                    chunk_index = EXCLUDED.chunk_index,
                    content     = EXCLUDED.content,
                    embedding   = EXCLUDED.embedding
                """,
                [
                    (
                        r.id,
                        r.metadata["source"],
                        int(r.metadata["chunk_index"]),
                        r.metadata["text"],
                        self._Vector(r.vector),
                    )
                    for r in records
                ],
            )

    def query(self, vector: list[float], top_k: int) -> list[Match]:
        query_vec = self._Vector(vector)
        rows = self._conn.execute(
            f"""
            SELECT id, source, chunk_index, content, 1 - (embedding <=> %s) AS score
            FROM {self._table}
            ORDER BY embedding <=> %s
            LIMIT %s
            """,
            (query_vec, query_vec, top_k),
        ).fetchall()
        return [
            Match(
                id=row[0],
                score=float(row[4]),
                metadata={"source": row[1], "chunk_index": row[2], "text": row[3]},
            )
            for row in rows
        ]

    def delete_by_source(self, source: str) -> None:
        self._conn.execute(
            f"DELETE FROM {self._table} WHERE source = %s", (source,)
        )

    def count(self) -> int:
        return int(
            self._conn.execute(f"SELECT count(*) FROM {self._table}").fetchone()[0]
        )


def get_store(config: Config, embedder: Embedder) -> VectorStore:
    if config.use_postgres:
        # One table per embedder: vectors from different models are not
        # comparable, so keep them apart and let you toggle without dropping.
        table = f"{config.pg_table}_{embedder.name}"
        return PgVectorStore(config, embedder.dimension, table=table)
    return InMemoryStore(config.index_path)
