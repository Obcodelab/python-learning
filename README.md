# python-learning

Practice code from the Python phase of my SIWES (Weeks 19–22).

The Python basics were covered in 200 level, so this phase was mostly a
refresher on the language followed by the newer topics needed for the main
project: FastAPI, embeddings, vector databases and RAG.

## Layout

```
python-learning/
├── topics/            # small programs, one topic each
│   ├── 01_syntax_and_basics.py
│   ├── 02_variables_and_data_types.py
│   ├── 03_control_flow.py
│   ├── 04_functions.py
│   ├── 05_lists_and_dicts.py
│   ├── 06_modules_and_packages.py
│   ├── 07_classes_and_objects.py
│   ├── 08_inheritance.py
│   ├── 09_file_handling.py
│   ├── 10_virtual_environments.py
│   ├── 11_fastapi_intro.py
│   ├── 12_embeddings.py
│   ├── 13_vector_databases.py
│   └── 14_rag_concepts.py
└── document_indexer/    # supporting project (see its own README)
```

## Running the topic files

```bash
uv sync
uv run python topics/01_syntax_and_basics.py
```

Most files just print things to show how a feature works. The FastAPI one
starts a small server:

```bash
uv run uvicorn topics.11_fastapi_intro:app --reload
```

## Supporting project

`document_indexer/` combines document chunking, embedding generation and
vector storage into one pipeline. It runs offline with a fake embedder and an
in-memory store, and switches to OpenAI embeddings and a Postgres + `pgvector`
store when `OPENAI_API_KEY` / `DATABASE_URL` are set. See
`document_indexer/README.md`.
