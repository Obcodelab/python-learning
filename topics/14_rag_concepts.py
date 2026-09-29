"""RAG (Retrieval-Augmented Generation) lets a model answer questions about a
document it was never trained on, by retrieving the relevant passages first
and putting them in front of the model at question time. This file runs a
small end-to-end version using word overlap as a stand-in for embeddings."""

from __future__ import annotations

import re

_STOPWORDS = {
    "the", "a", "an", "and", "or", "of", "to", "in", "is", "are", "it", "that",
    "this", "for", "on", "with", "as", "so", "how", "what", "why", "does", "do",
    "from", "can", "we", "you", "only", "each", "into", "be",
}


def content_words(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z]+", text.lower()) if w not in _STOPWORDS}


# --- phase 1: indexing (once per document) ---
#   document -> split into chunks -> turn each chunk into a vector -> store

def split_into_chunks(document: str) -> list[str]:
    """Here a chunk is one sentence. A real system uses fixed-size word windows."""
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", document.strip()) if s.strip()]


def build_index(document: str) -> list[tuple[str, set[str]]]:
    """The 'vector' for each chunk is its set of content words."""
    return [(chunk, content_words(chunk)) for chunk in split_into_chunks(document)]


# --- phase 2: answering (for every question) ---
#   question -> vector -> find closest chunks -> use as context -> answer,
#   or say the answer is not there

def retrieve(index: list[tuple[str, set[str]]], question: str, top_k: int = 2):
    q_words = content_words(question)
    scored = [(len(q_words & words), chunk) for chunk, words in index]
    scored.sort(key=lambda pair: pair[0], reverse=True)
    return [(score, chunk) for score, chunk in scored[:top_k] if score > 0]


def answer(question: str, retrieved) -> str:
    if not retrieved:
        return "The document does not contain the answer to that."
    # Grounded: the answer is just the best-matching sentence from the document.
    return retrieved[0][1]


DOCUMENT = (
    "Retrieval-Augmented Generation retrieves relevant chunks from a document "
    "and passes them to a model as context. "
    "The model is instructed to answer using that context and nothing else. "
    "Chunking splits the document into smaller pieces so retrieval can return "
    "the exact passage that matters instead of a whole page. "
    "Embeddings turn each chunk into a vector, which lets similar meaning be "
    "compared even when the wording is different. "
    "A grounded answer comes only from the retrieved context, and the bot says "
    "when the context does not contain the answer."
)


def main() -> None:
    index = build_index(DOCUMENT)
    print(f"indexed {len(index)} chunks\n")

    for question in [
        "why is chunking used",
        "what makes an answer grounded",
        "what is the capital of France",
    ]:
        retrieved = retrieve(index, question)
        print(f"Q: {question}")
        for score, chunk in retrieved:
            print(f"   retrieved (overlap {score}): {chunk}")
        print(f"A: {answer(question, retrieved)}\n")


if __name__ == "__main__":
    main()
