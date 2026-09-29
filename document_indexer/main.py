"""Command-line interface for the Document Indexer.

    python document_indexer/main.py <index PATH | search QUERY | info>"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Allow running the file directly: add this folder to the import path.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from indexer import DocumentIndexer


def cmd_index(args: argparse.Namespace) -> int:
    indexer = DocumentIndexer()
    path = Path(args.path)
    if not path.exists():
        print(f"file not found: {path}", file=sys.stderr)
        return 1
    count = indexer.index_file(path)
    print(f"indexed {count} chunk(s) from {path.name}")
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    indexer = DocumentIndexer()
    results = indexer.search(args.query, top_k=args.top_k)
    if not results:
        print("no results - index a document first")
        return 0
    for rank, result in enumerate(results, start=1):
        preview = result.text[:200] + ("..." if len(result.text) > 200 else "")
        print(f"\n#{rank}  score={result.score:.3f}  "
              f"[{result.source} chunk {result.chunk_index}]")
        print(f"    {preview}")
    return 0


def cmd_info(_: argparse.Namespace) -> int:
    for key, value in DocumentIndexer().info().items():
        print(f"{key:15} {value}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Document Indexer")
    sub = parser.add_subparsers(dest="command", required=True)

    p_index = sub.add_parser("index", help="index a text document")
    p_index.add_argument("path", help="path to a .txt / .md file")
    p_index.set_defaults(func=cmd_index)

    p_search = sub.add_parser("search", help="search the index")
    p_search.add_argument("query")
    p_search.add_argument("--top-k", type=int, default=3)
    p_search.set_defaults(func=cmd_search)

    p_info = sub.add_parser("info", help="show active backends and chunk count")
    p_info.set_defaults(func=cmd_info)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
